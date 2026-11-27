"""Модуль «Тесты»: стенд этапа 3 (skills/kp-bench). Переиспользует скрипты skills/kp-bench/scripts/.

Действия белого списка регистрируются в register(). Все команды собираются здесь из проверенных параметров:
тест и вариант — из site/data/bench.json, тестировщик — ^[a-z0-9-]{1,32}$, файлы — внутри bench/runs/.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from core import agents, bundled, gitops, tools
from core.jobs import Cmd, Py
from core.paths import ROOT, RUNS, PathError, check_tester, rel, safe_path

SKILL = ROOT / "skills" / "kp-bench"
SCRIPTS = SKILL / "scripts"
INPUTS = SKILL / "assets" / "inputs"
TESTS_MD = SKILL / "references" / "tests.md"
RESULTS = ROOT / "bench" / "results"
ENV_DIR = ROOT / "bench" / "env"
TOOLS_DIR = ROOT / "bench" / "tools"
GIT_PATHS = ["bench/results", "bench/env", "site/data/bench_results.json"]
VERDICTS = {"ok": "годится", "partial": "с оговорками", "no": "не годится", "fail": "не запустилось"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".webm", ".mp4", ".mov", ".opus"}
VIDEO_EXT = {".mp4", ".mov", ".webm"}
PY = bundled.console_python()   # под pythonw.exe скрипты запускаются через python.exe рядом
RULINT_REPO = "https://github.com/miolamio/agent-skills"
GIGAAM_REPO = "https://github.com/salute-developers/GigaAM.git"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


# --- каталог и проверка параметров ---------------------------------------------------------------

def catalog() -> dict:
    return json.loads((ROOT / "site" / "data" / "bench.json").read_text(encoding="utf-8"))


def test_of(test_id) -> dict:
    t = next((t for t in catalog()["tests"] if t["id"] == test_id), None)
    if not t:
        raise ValueError(f"Нет теста {test_id!r} в bench.json")
    return t


def variant_of(test_id, variant_id) -> dict:
    v = next((v for v in test_of(test_id)["variants"] if v["id"] == variant_id), None)
    if not v:
        raise ValueError(f"У теста {test_id} нет варианта {variant_id!r}")
    return v


def tester(params: dict) -> str:
    return check_tester(params.get("tester"))


def run_dir(kind: str, t: str) -> Path:
    return RUNS / kind / t


def rec_file(t: str, kind: str = "script") -> Path | None:
    d = run_dir("rec", t)
    if not d.is_dir():
        return None
    files = sorted(p for p in d.glob(f"{kind}.*") if p.suffix.lower() in AUDIO_EXT and not p.is_symlink())
    return files[0] if files else None


def need_rec(t: str, kind: str = "script") -> Path:
    f = rec_file(t, kind)
    if not f:
        what = "запись текста script_ru.txt" if kind == "script" else "образец голоса 15 с"
        raise ValueError(f"Нет файла: {what}. Загрузите его в шаге «Подготовка».")
    return f


def has_nvidia() -> bool:
    return bool(shutil.which("nvidia-smi"))


def script(name: str) -> str:
    return str(SCRIPTS / name)


def ffmpeg() -> str:
    exe = tools.exe("ffmpeg")
    if not exe:
        raise ValueError("ffmpeg не найден. Установите его (Подготовка → Среда) и нажмите «Проверить снова».")
    return exe


# --- пакеты в окружениях Python -------------------------------------------------------------------

PACKS = {
    "torch": {"venv": "asr", "dist": "torch", "label": "PyTorch",
              "for": "GigaAM, DeepFilterNet, ударения",
              "downloads": "PyTorch и torchaudio — крупные пакеты, сотни МБ (точный объём — проверить). Без NVIDIA ставится сборка для процессора."},
    "gigaam": {"venv": "asr", "dist": "gigaam", "label": "GigaAM v3", "requires": "torch",
               "for": "распознавание (asr), обратная проверка озвучки",
               "downloads": "Репозиторий GigaAM (git clone в bench/tools/GigaAM) и его зависимости; веса модели скачаются при первом распознавании — размер проверить."},
    "faster-whisper": {"venv": "asr", "dist": "faster_whisper", "label": "faster-whisper",
                       "for": "распознавание (asr)",
                       "downloads": "Пакет faster-whisper; модель large-v3 скачается при первом запуске — размер проверить."},
    "stress": {"venv": "asr", "dist": "ruaccent", "label": "rutextnorm, silero-stress, RUAccent", "requires": "torch",
               "pkgs": ["rutextnorm", "silero-stress", "ruaccent"], "for": "ударения (stress)",
               "downloads": "Три пакета; модели ударений скачаются при первом запуске — размер проверить."},
    "deepfilternet": {"venv": "asr", "dist": "deepfilternet", "label": "DeepFilterNet", "requires": "torch",
                      "for": "очистка записи (voice-clean)",
                      "downloads": "Пакет deepfilternet и модель DeepFilterNet3 — размер проверить."},
    "humanizer": {"venv": "asr", "dist": "humanizer_ru", "pkgs": ["humanizer-ru"], "label": "humanizer-ru",
                  "for": "проверка текста (text-check)", "downloads": "Пакет humanizer-ru (без моделей)."},
    "edge-tts": {"venv": "asr", "dist": "edge_tts", "label": "Edge TTS", "for": "синтез (tts-local)",
                 "downloads": "Пакет edge-tts; синтез идёт через облако Microsoft, нужен интернет."},
    "whisperx": {"venv": "whisperx", "dist": "whisperx", "label": "WhisperX (отдельное окружение)",
                 "for": "распознавание (asr)",
                 "downloads": "WhisperX со своей версией torch — гигабайты (проверить); модели large-v3 и wav2vec2 для русского скачаются при первом запуске."},
    "qwen-tts": {"venv": "tts", "dist": "qwen_tts", "label": "Qwen3-TTS (отдельное окружение)", "gpu": True,
                 "pkgs": ["-U", "qwen-tts", "soundfile", "rutextnorm", "ruaccent"], "for": "синтез (tts-local), только NVIDIA",
                 "downloads": "qwen-tts и torch с CUDA; веса Qwen3-TTS 1.7B скачаются при первом запуске — размер проверить."},
}


def pack_installed(pid: str) -> bool:
    p = PACKS[pid]
    return tools.installed(p["venv"], p["dist"])


def pack_check(pid: str) -> Py:
    """Шаг-проверка: понятная ошибка в логе, если пакет не установлен."""
    def check(job) -> int:
        if pack_installed(pid):
            return 0
        p = PACKS[pid]
        job.log(f"Не установлено: {p['label']}. Откройте «Подготовка → Установка» и нажмите «Установить» у пункта "
                f"«{p['label']}», затем повторите.")
        job.error = f"не установлено: {p['label']}"
        return 1
    return Py(check, label=f"проверка: установлен ли {PACKS[pid]['label']}")


def build_install(params: dict, app):
    pid = params.get("pack")
    if pid not in PACKS:
        raise ValueError(f"Неизвестный пакет: {pid!r}")
    p = PACKS[pid]
    if p.get("gpu") and not has_nvidia():
        raise ValueError("Нужна видеокарта NVIDIA: nvidia-smi не найден.")
    venv = p["venv"]
    steps: list = []
    if not tools.venv_exists(venv):
        steps.append(Cmd([*tools.base_python(), "-m", "venv", str(tools.venv_dir(venv))],
                         label=f"создать окружение {tools.venv_label(venv)}"))
    vpy = str(tools.venv_python(venv))
    pip = [vpy, "-m", "pip", "install", "--disable-pip-version-check"]
    if pid == "torch":
        if has_nvidia():
            steps.append(Cmd([*pip, "torch", "torchaudio"], label="pip install torch torchaudio (проверьте, что torch видит CUDA)"))
        else:
            steps.append(Cmd([*pip, "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"]))
    elif pid == "gigaam":
        git = tools.exe("git")
        if not git:
            raise ValueError("git не найден: он нужен, чтобы скачать GigaAM.")
        if not (TOOLS_DIR / "GigaAM").is_dir():
            steps.append(Cmd([git, "clone", "--depth", "1", GIGAAM_REPO, "bench/tools/GigaAM"]))
        steps.append(Cmd([*pip, "-e", "bench/tools/GigaAM[torch]"]))
    else:
        steps.append(Cmd([*pip, *p.get("pkgs", [pid])]))
    return steps, f"Установка: {p['label']}"


def build_venv(params: dict, app):
    name = params.get("venv")
    if name not in ("asr", "whisperx", "tts"):
        raise ValueError("Окружение: asr, whisperx или tts")
    if tools.venv_exists(name):
        raise ValueError(f"Окружение {tools.venv_label(name)} уже есть.")
    return [Cmd([*tools.base_python(), "-m", "venv", str(tools.venv_dir(name))])], f"Создать окружение {tools.venv_label(name)}"


# --- простые действия -----------------------------------------------------------------------------

def build_check_env(params, app):
    t = tester(params)
    return [Cmd([PY, script("check_env.py"), "--tester", t])], f"Проверка среды ({t})"


def build_summary(params, app):
    return [Cmd([PY, script("summary.py")])], "Свод результатов"


# --- text-check ----------------------------------------------------------------------------------

POST = INPUTS / "post_ru.md"


def find_rulint() -> Path | None:
    base = TOOLS_DIR / "agent-skills"
    if not base.is_dir():
        return None
    found = sorted(p for p in base.rglob("ru_lint.py") if not p.is_symlink())
    return found[0] if found else None


def build_clone_rulint(params, app):
    git = tools.exe("git")
    if not git:
        raise ValueError("git не найден: он нужен, чтобы скачать ru-editor.")
    steps: list = []
    if not (TOOLS_DIR / "agent-skills").is_dir():
        steps.append(Cmd([git, "clone", "--depth", "1", RULINT_REPO, "bench/tools/agent-skills"]))

    def locate(job) -> int:
        p = find_rulint()
        if not p:
            job.log("В bench/tools/agent-skills не найден ru_lint.py. Посмотрите README скилла ru-editor вручную.")
            job.error = "ru_lint.py не найден"
            return 1
        job.log(f"Найден: {rel(p)}")
        job.result["path"] = rel(p)
        return 0
    steps.append(Py(locate, label="поиск ru_lint.py"))
    return steps, "Скачать ru-editor (ru_lint.py)"


def build_textcheck(params, app):
    t = tester(params)
    v = params.get("variant")
    variant_of("text-check", v)
    out = run_dir("text-check", t)
    post = rel(POST)
    if v == "humanizer-ru":
        exe = tools.venv_bin("asr", "humanizer-markers")
        if not exe.is_file():
            alt = agents.find_exe("humanizer-markers")
            if alt:
                return [Cmd([alt, "--scan", post], tee=out / "humanizer-ru.txt", ok_codes=(0, 1))], "text-check: humanizer-ru"
            return [pack_check("humanizer")], "text-check: humanizer-ru"
        # код выхода 1 — маркеры найдены (install.md, раздел 8)
        return [Cmd([str(exe), "--scan", post], tee=out / "humanizer-ru.txt", ok_codes=(0, 1))], "text-check: humanizer-ru"
    if v == "ru-lint":
        p = find_rulint()
        if not p:
            raise ValueError("ru_lint.py ещё не скачан: нажмите «Скачать ru-editor».")
        return [Cmd([PY, str(p), post], tee=out / "ru-lint.txt", ok_codes=(0, 1))], "text-check: ru-lint"
    raise ValueError("ru-text запускается через агента: кнопка «Запустить в агенте».")


RU_TEXT_TASK = """# Задача стенда kp-bench: text-check, вариант ru-text

Оцени этот текст по ru-text и перечисли все проблемы.

Текст — файл skills/kp-bench/assets/inputs/post_ru.md. Не открывай post_ru_key.json и другие файлы из skills/kp-bench/assets/inputs, кроме post_ru.md.
Если скилл ru-text не установлен, напиши первой строкой «ru-text не установлен» (установка: npx skills add talkstream/ru-text) и остановись.
Ничего не меняй в файлах. Ответ — нумерованный список проблем с цитатой из текста и оценка 0–10.
"""


def build_textcheck_agent(params, app):
    t = tester(params)
    agent_id = app.settings().get("agent", "")
    task = agents.task_file(f"ru-text_{t}", RU_TEXT_TASK)
    return [agents.command(agent_id, task, "read", tee=run_dir("text-check", t) / "ru-text.txt")], "text-check: ru-text через агента"


# --- stress --------------------------------------------------------------------------------------

STRESS_PACK = {"rutextnorm-silero": "stress", "rutextnorm-ruaccent": "stress"}


def build_stress(params, app):
    t = tester(params)
    v = params.get("variant")
    variant_of("stress", v)
    out = run_dir("stress", t)
    return [pack_check("stress"),
            Cmd([str(tools.venv_python("asr")), script("stress_run.py"), "--variant", v, "--out", rel(out)],
                tee=out / f"{v}.log")], f"stress: {v}"


# --- asr -----------------------------------------------------------------------------------------

ASR_PACK = {"gigaam": "gigaam", "faster-whisper": "faster-whisper", "whisperx": "whisperx"}


def wer_step(hyp: Path, out_json: Path, ref: Path = INPUTS / "script_ru_spoken.txt") -> Py:
    def run(job) -> int:
        import wer  # skills/kp-bench/scripts/wer.py
        if not hyp.is_file():
            job.log(f"Нет файла распознавания {rel(hyp)}")
            return 1
        res = wer.score(ref.read_text(encoding="utf-8"), hyp.read_text(encoding="utf-8"))
        out_json.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        job.log(f"WER {res['wer']:.1%}, CER {res['cer'] if res['cer'] is None else format(res['cer'], '.1%')} "
                f"(замен {res['substitutions']}, пропусков {res['deletions']}, вставок {res['insertions']})")
        job.result.update(res)
        return 0
    return Py(run, label=f"wer.py: {rel(hyp)} против {rel(ref)}")


def asr_cmd(engine: str, audio: Path, out: Path) -> Cmd:
    venv = "whisperx" if engine == "whisperx" else "asr"
    return Cmd([str(tools.venv_python(venv)), script("asr_run.py"), "--engine", engine, "--audio", str(audio), "--out", rel(out)])


def build_asr(params, app):
    t = tester(params)
    e = params.get("engine")
    variant_of("asr", e)
    ffmpeg()
    audio = need_rec(t)
    out = run_dir("asr", t)
    return [pack_check(ASR_PACK[e]), asr_cmd(e, audio, out),
            wer_step(out / f"{e}.txt", out / f"{e}.wer.json")], f"asr: {e}"


# --- voice-clean ---------------------------------------------------------------------------------

def clean_metrics(variant: str, d: Path, normalized: Path, final: Path) -> Py:
    def run(job) -> int:
        import asr_run  # duration()
        import loudness  # measure()
        m = loudness.measure(str(normalized), -14.0, -1.0, 11.0)
        before = asr_run.duration(d / "rec48.wav")
        after = asr_run.duration(final)
        meta = {"lufs": float(m["input_i"]), "true_peak": float(m["input_tp"]), "lra": float(m["input_lra"]),
                "dur_before": round(before, 2), "dur_after": round(after, 2), "cut_s": round(before - after, 2),
                "file": rel(final)}
        (d / f"{variant}.run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        job.log(f"Громкость {meta['lufs']} LUFS, пик {meta['true_peak']} dBTP; длительность {before:.1f} → {after:.1f} с, "
                f"вырезано {meta['cut_s']} с")
        job.result.update(meta)
        return 0
    return Py(run, label="замер громкости и длительности (loudness.py, asr_run.duration)")


def build_clean(params, app):
    t = tester(params)
    v = params.get("variant")
    variant_of("voice-clean", v)
    ff = ffmpeg()
    src = need_rec(t)
    d = run_dir("clean", t)
    d.mkdir(parents=True, exist_ok=True)
    rec48 = d / "rec48.wav"
    steps: list = [Cmd([ff, "-hide_banner", "-y", "-i", str(src), "-ac", "1", "-ar", "48000", str(rec48)], label="ffmpeg → WAV 48 кГц моно")]
    if v == "dfn-chain":
        ae = tools.exe("auto-editor")
        if not ae:
            raise ValueError("auto-editor не найден. Установите его (Подготовка → Среда) и нажмите «Проверить снова».")
        dfn_dir = d / "dfn"

        def pick(job) -> int:
            wavs = sorted(dfn_dir.glob("*.wav"), key=lambda p: p.stat().st_mtime)
            if not wavs:
                job.log("deepFilter не создал WAV в " + rel(dfn_dir))
                return 1
            shutil.copyfile(wavs[-1], d / "dfn.wav")
            job.log(f"Файл после deepFilter: {rel(wavs[-1])}")
            return 0
        steps += [pack_check("deepfilternet"),
                  Cmd([str(tools.venv_bin("asr", "deepFilter")), str(rec48), "--output-dir", str(dfn_dir)]),
                  Py(pick, label="найти файл после deepFilter"),
                  Cmd([PY, script("loudness.py"), str(d / "dfn.wav"), "--normalize", str(d / "dfn_norm.wav")]),
                  # флаг -o (файл результата) — проверить по auto-editor --help
                  Cmd([ae, str(d / "dfn_norm.wav"), "--edit", "audio:-19dB", "--margin", "0.2sec", "-o", str(d / "dfn-chain.wav")]),
                  clean_metrics(v, d, d / "dfn_norm.wav", d / "dfn-chain.wav")]
    else:
        steps += [Cmd([ff, "-hide_banner", "-y", "-i", str(rec48), "-af",
                       "afftdn=nf=-25,silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-40dB",
                       str(d / "ff_clean.wav")], label="ffmpeg afftdn + silenceremove"),
                  Cmd([PY, script("loudness.py"), str(d / "ff_clean.wav"), "--normalize", str(d / "ffmpeg-only.wav")]),
                  clean_metrics(v, d, d / "ffmpeg-only.wav", d / "ffmpeg-only.wav")]
    return steps, f"voice-clean: {v}"


# --- tts-local -----------------------------------------------------------------------------------

VOICE_RE = re.compile(r"^ru-RU-[A-Za-z]+Neural$")
VOICES_FILE = RUNS / "tts" / "_voices.txt"


def build_tts_voices(params, app):
    exe = tools.venv_bin("asr", "edge-tts")
    if not exe.is_file():
        return [pack_check("edge-tts")], "Edge TTS: список голосов"
    return [Cmd([str(exe), "--list-voices"], tee=VOICES_FILE)], "Edge TTS: список голосов"


def tts_file(t: str, variant: str) -> Path | None:
    d = run_dir("tts", t)
    if not d.is_dir():
        return None
    f = [p for p in d.glob(f"{variant}.*") if p.suffix.lower() in AUDIO_EXT]
    return f[0] if f else None


def build_tts(params, app):
    t = tester(params)
    v = params.get("variant")
    variant_of("tts-local", v)
    out = run_dir("tts", t)
    out.mkdir(parents=True, exist_ok=True)
    text = INPUTS / "script_ru.txt"
    for old in out.glob(f"{v}.*"):
        if old.suffix.lower() in AUDIO_EXT:
            old.unlink()
    if v == "edge-tts":
        voice = params.get("voice") or ""
        if not VOICE_RE.match(voice):
            raise ValueError("Голос Edge TTS вида ru-RU-ИмяNeural. Нажмите «Список голосов» и выберите.")
        return [pack_check("edge-tts"),
                Cmd([str(tools.venv_bin("asr", "edge-tts")), "--voice", voice, "--file", rel(text),
                     "--write-media", rel(out / "edge-tts.mp3")], tee=out / "edge-tts.log")], f"tts-local: Edge TTS ({voice})"
    if not has_nvidia():
        raise ValueError("Qwen3-TTS — только с видеокартой NVIDIA. Запишите вариант как «не запустилось».")
    ff = ffmpeg()
    sample = need_rec(t, "voice_sample")
    ref = run_dir("tts-ref", t)
    ref.mkdir(parents=True, exist_ok=True)
    steps: list = [pack_check("qwen-tts"),
                   Cmd([ff, "-hide_banner", "-y", "-i", str(sample), "-ac", "1", "-ar", "24000", str(ref / "ref.wav")])]
    if not (ref / "gigaam.txt").is_file():
        steps += [pack_check("gigaam"), asr_cmd("gigaam", ref / "ref.wav", ref)]
    cmd = [str(tools.venv_python("tts")), script("tts_qwen.py"), "--text-file", rel(text), "--ref-audio", rel(ref / "ref.wav"),
           "--ref-text-file", rel(ref / "gigaam.txt"), "--out", rel(out / f"{v}.wav")]
    if v == "qwen3-tts-stress":
        cmd += ["--stress", "--model", "siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf"]
    steps.append(Cmd(cmd, tee=out / f"{v}.log"))
    return steps, f"tts-local: {v}"


def build_tts_back(params, app):
    t = tester(params)
    v = params.get("variant")
    variant_of("tts-local", v)
    ffmpeg()
    f = tts_file(t, v)
    if not f:
        raise ValueError(f"Нет синтеза {v}: сначала «Синтезировать».")
    out = run_dir("tts-back", t) / v
    return [pack_check("gigaam"), asr_cmd("gigaam", f, out), wer_step(out / "gigaam.txt", out / "back.wer.json")], f"Обратное распознавание: {v}"


def build_blind_make(params, app):
    t = tester(params)
    src, dst = run_dir("tts", t), run_dir("blind-tts", t)
    if not src.is_dir() or not any(p.suffix.lower() in AUDIO_EXT for p in src.iterdir()):
        raise ValueError("Нет синтезированных файлов в " + rel(src))

    def clear(job) -> int:
        if dst.is_dir():
            shutil.rmtree(dst)
        return 0
    return [Py(clear, label="очистить прошлую слепую оценку"), Cmd([PY, script("blind.py"), "make", rel(src), rel(dst)])], "Слепая оценка: перемешать"


def blind_scores(req):
    t = check_tester(req.body.get("tester"))
    d = run_dir("blind-tts", t)
    key_path = d / "_key.json"
    if not key_path.is_file():
        raise ValueError("Сначала «Перемешать файлы».")
    key = json.loads(key_path.read_text(encoding="utf-8"))
    scores = req.body.get("scores") or {}
    if not isinstance(scores, dict) or set(scores) != set(key):
        raise ValueError("Поставьте оценку каждому файлу: " + ", ".join(sorted(key)))
    clean = {}
    for lab, val in scores.items():
        if not isinstance(val, int) or not 1 <= val <= 5:
            raise ValueError("Оценка — целое от 1 до 5")
        clean[lab] = val
    (d / "_scores.json").write_text(json.dumps(clean, ensure_ascii=False, indent=1), encoding="utf-8")
    return 200, {"reveal": {lab: {"file": key[lab], "variant": Path(key[lab]).stem, "score": clean[lab]} for lab in key}}


# --- edit ----------------------------------------------------------------------------------------

def edit_task_text() -> str:
    """Текст задачи для агента — из tests.md, раздел edit (строки цитаты)."""
    sec = tests_sections().get("edit", "")
    quote = [ln[2:] for ln in sec.splitlines() if ln.startswith("> ")]
    return "\n".join(quote).strip()


def words_file(t: str, engine: str | None = None) -> Path | None:
    d = run_dir("asr", t)
    for e in ([engine] if engine else ["gigaam", "faster-whisper", "whisperx"]):
        p = d / f"{e}.words.json"
        if p.is_file():
            return p
    return None


def build_captions(params, app):
    t = tester(params)
    e = params.get("engine") or None
    if e:
        variant_of("asr", e)
    w = words_file(t, e)
    if not w:
        raise ValueError("Нет слов с таймкодами: сначала пройдите тест asr.")
    return [Cmd([PY, script("captions.py"), rel(w), "--words-per-line", "3"])], f"Субтитры из {w.name}"


def clean_audio(t: str) -> Path | None:
    d = run_dir("clean", t)
    for n in ("dfn_norm.wav", "dfn-chain.wav", "ffmpeg-only.wav"):
        if (d / n).is_file():
            return d / n
    return rec_file(t)


def edit_task(t: str, v: str) -> str:
    """Текст задачи монтажа для агента. ValueError, если не хватает входных файлов."""
    var = variant_of("edit", v)
    w = words_file(t)
    if not w:
        raise ValueError("Нет слов с таймкодами: сначала тест asr и «Подготовить субтитры».")
    base = w.with_suffix("").with_suffix("")
    caps, srt = Path(f"{base}.captions.json"), Path(f"{base}.srt")
    if not caps.is_file():
        raise ValueError("Нет субтитров: нажмите «Подготовить субтитры».")
    audio = clean_audio(t)
    if not audio:
        raise ValueError("Нет записи: сначала «Подготовка» и voice-clean.")
    out = run_dir("edit", t)
    proj = f"bench/tools/{v}-test"
    return f"""# Задача стенда kp-bench: тест edit, вариант {var['name']}

Рабочая папка — корень репозитория (текущая). Правила проекта — AGENTS.md.
Движок: {var['name']}. Установка и команды — skills/kp-bench/references/install.md, раздел 7. Проект движка создай в {proj}.

Задача:
{edit_task_text()}

Входные файлы (если в задаче назван другой файл звука — бери этот):
- звук: {rel(audio)}
- субтитры по словам для Remotion: {rel(caps)}
- субтитры для HyperFrames и редакторов: {rel(srt)}
- слова с таймкодами: {rel(w)}

Результат: готовый ролик положи в {rel(out)}/{v}.mp4.
Время рендера в секундах запиши в {rel(out)}/{v}.run.json в виде {{"render_s": N}}.
Не коммить, не пушь, ничего не публикуй и не оплачивай. Не меняй файлы вне {proj} и {rel(out)}.
В конце кратко: что сделал, какие были проблемы с кириллицей, шрифтом и безопасными зонами.
"""


def build_edit_agent(params, app):
    t = tester(params)
    v = params.get("variant")
    var = variant_of("edit", v)
    task = edit_task(t, v)
    out = run_dir("edit", t)
    out.mkdir(parents=True, exist_ok=True)
    agent_id = app.settings().get("agent", "")
    tf = agents.task_file(f"edit_{v}_{t}", task)
    return [agents.command(agent_id, tf, "write", tee=out / f"{v}.agent.txt")], f"edit: {var['name']} через агента"


# --- запись результата, экспорт, git --------------------------------------------------------------

NOTE_MAX = 2000


def build_record(params, app):
    t = tester(params)
    test, v = params.get("test"), params.get("variant")
    tdef = test_of(test)
    variant_of(test, v)
    verdict = params.get("verdict")
    if verdict not in VERDICTS:
        raise ValueError("Выберите вердикт.")
    known = {m["id"] for m in tdef["metrics"]}
    argv = [PY, script("record.py"), "--test", test, "--variant", v, "--tester", t, "--verdict", verdict]
    metrics = params.get("metrics") or {}
    if not isinstance(metrics, dict):
        raise ValueError("metrics — объект")
    for k, val in metrics.items():
        if k not in known:
            raise ValueError(f"У теста {test} нет метрики {k}")
        if val in (None, ""):
            continue
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise ValueError(f"Метрика {k}: нужно число")
        argv += ["--metric", f"{k}={val}"]
    sm = params.get("setup_min")
    if sm not in (None, ""):
        if isinstance(sm, bool) or not isinstance(sm, (int, float)) or sm < 0:
            raise ValueError("Минуты на установку — число")
        argv += ["--setup-min", str(sm)]
    cost = params.get("cost")
    if cost not in (None, "", 0):
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
            raise ValueError("Стоимость — число")
        argv += ["--cost", str(cost)]
    note = params.get("note") or ""
    if not isinstance(note, str):
        raise ValueError("Заметка — текст")
    note = re.sub(r"[\x00-\x1f\x7f]+", " ", note).strip()[:NOTE_MAX]
    if note:
        argv += ["--note", note]
    files = params.get("files") or []
    if not isinstance(files, list) or len(files) > 20:
        raise ValueError("files — список до 20 путей")
    for f in files:
        argv += ["--file", rel(safe_path(f, [RUNS], must_exist=True))]
    return [Cmd(argv), Cmd([PY, script("summary.py")])], f"Записать: {test} / {v} ({VERDICTS[verdict]})"


def tester_results(t: str) -> list[dict]:
    out = []
    if not RESULTS.is_dir():
        return out
    for p in sorted(RESULTS.glob("*/*.json")):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if r.get("tester") == t:
            out.append({"test": r.get("test"), "variant": r.get("variant"), "date": r.get("date"),
                        "verdict": r.get("verdict"), "metrics": r.get("metrics"), "note": r.get("note", ""), "file": rel(p)})
    return out


def build_export(params, app):
    t = tester(params)

    def make(job) -> int:
        files = [ROOT / r["file"] for r in tester_results(t)]
        env = ENV_DIR / f"{t}.json"
        files += [env, ROOT / "site" / "data" / "bench_results.json"]
        z = gitops.make_zip(files, t)
        job.log(f"Архив: {rel(z)} ({sum(1 for f in files if f.is_file())} файлов)")
        job.result["file"] = rel(z)
        return 0
    return [Py(make, label="zip результатов и среды тестировщика")], f"Архив результатов ({t})"


def commit_message(t: str, files: list[str]) -> str:
    tests, variants = [], []
    for f in files:
        if not f.startswith("bench/results/"):
            continue
        try:
            r = json.loads((ROOT / f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if r.get("test") and r["test"] not in tests:
            tests.append(r["test"])
        if r.get("variant") and r["variant"] not in variants:
            variants.append(r["variant"])
    if not tests:
        return f"Стенд: среда у {t}"
    return f"Стенд: {', '.join(tests)} у {t} — {', '.join(variants)}"


def git_status(req):
    t = check_tester(req.q("tester"))
    info = gitops.git_info(GIT_PATHS)
    info["message"] = commit_message(t, info["files"])
    return 200, info


def build_git_push(params, app):
    t = tester(params)
    info = gitops.git_info(GIT_PATHS)
    if info["problems"]:
        raise ValueError("Отправить в git нельзя: " + " ".join(info["problems"]) + " Скачайте результаты архивом.")
    if not info["files"]:
        raise ValueError("Нет новых результатов для отправки.")
    return gitops.push_steps(GIT_PATHS, commit_message(t, info["files"])), "Отправить в git"


# --- загрузка записи ------------------------------------------------------------------------------

UPLOAD_KINDS = {"script", "voice_sample"}


def upload_target(query: dict, filename: str) -> Path:
    t = check_tester(query.get("tester"))
    kind = query.get("kind")
    if kind not in UPLOAD_KINDS:
        raise ValueError("kind: script или voice_sample")
    ext = Path(filename or "").suffix.lower()
    if ext not in AUDIO_EXT:
        raise ValueError("Нужен аудио- или видеофайл: " + ", ".join(sorted(AUDIO_EXT)))
    return safe_path(f"bench/runs/rec/{t}/{kind}{ext}", [RUNS / "rec"])


# --- чтение состояния -----------------------------------------------------------------------------

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_text(p: Path, limit: int = 30000) -> str | None:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[-limit:]
    except OSError:
        return None


def tests_sections() -> dict:
    """Разделы tests.md по заголовкам «## <id> — ...»; ключ — id теста или 'prep', 'scores'."""
    try:
        text = TESTS_MD.read_text(encoding="utf-8")
    except OSError:
        return {}
    out = {}
    for block in re.split(r"(?m)^## ", text)[1:]:
        head, _, body = block.partition("\n")
        if head.startswith("Подготовка"):
            key = "prep"
        elif head.startswith("Оценки"):
            key = "scores"
        elif head.startswith("Платные"):
            key = "paid"
        else:
            key = re.split(r"\s+[—:-]\s+|\s", head.strip(), maxsplit=1)[0]
        out[key] = "## " + head + "\n" + body.strip()
    return out


def state(req):
    t = check_tester(req.q("tester"))
    env = read_json(ENV_DIR / f"{t}.json")
    nvidia = has_nvidia()
    s: dict = {"tester": t, "env": env, "nvidia": nvidia, "today": date.today().isoformat()}
    s["venvs"] = {n: tools.venv_exists(n) for n in ("asr", "whisperx", "tts")}
    s["packs"] = [{"id": pid, "label": p["label"], "venv": p["venv"], "venv_label": tools.venv_label(p["venv"]), "for": p["for"], "downloads": p["downloads"],
                   "requires": p.get("requires"), "installed": pack_installed(pid),
                   "disabled": "нужна NVIDIA" if p.get("gpu") and not nvidia else ""} for pid, p in PACKS.items()]
    s["rec"] = {k: (rel(f) if (f := rec_file(t, k)) else None) for k in UPLOAD_KINDS}
    s["results"] = tester_results(t)
    # text-check
    tc = run_dir("text-check", t)
    s["text_check"] = {v: {"output": read_text(tc / f"{v}.txt"), "meta": read_json(tc / f"{v}.meta.json")}
                       for v in ("humanizer-ru", "ru-lint", "ru-text")}
    s["rulint"] = rel(p) if (p := find_rulint()) else None
    s["key"] = (read_json(INPUTS / "post_ru_key.json") or {}).get("issues", [])
    s["ru_text_prompt"] = RU_TEXT_TASK
    # stress
    st = run_dir("stress", t)
    s["stress_lines"] = [ln for ln in (read_text(INPUTS / "stress_ru.txt") or "").splitlines() if ln.strip()]
    s["stress"] = {}
    for v in ("rutextnorm-silero", "rutextnorm-ruaccent"):
        body = read_text(st / f"{v}.txt")
        rows = re.findall(r"(?m)^\d+\.\s(.*)\n\s+→\s(.*)$", body or "")
        log = read_text(st / f"{v}.log") or ""
        m = re.search(r"обработка ([\d.]+) с", log)
        s["stress"][v] = {"rows": [{"src": a, "res": b} for a, b in rows], "run_s": float(m.group(1)) if m else None}
    # asr
    ad = run_dir("asr", t)
    s["asr"] = {e: {"run": read_json(ad / f"{e}.run.json"), "wer": read_json(ad / f"{e}.wer.json"),
                    "text": read_text(ad / f"{e}.txt", 4000)} for e in ("gigaam", "faster-whisper", "whisperx")}
    # voice-clean
    cd = run_dir("clean", t)
    s["clean"] = {v: read_json(cd / f"{v}.run.json") for v in ("dfn-chain", "ffmpeg-only")}
    s["clean_src"] = rel(cd / "rec48.wav") if (cd / "rec48.wav").is_file() else None
    # tts
    s["tts"] = {}
    for v in ("qwen3-tts", "qwen3-tts-stress", "edge-tts"):
        f = tts_file(t, v)
        s["tts"][v] = {"file": rel(f) if f else None, "meta": read_json(run_dir("tts", t) / f"{v}.meta.json"),
                       "back": read_json(run_dir("tts-back", t) / v / "back.wer.json")}
    voices = read_text(VOICES_FILE) or ""
    s["voices"] = sorted(set(re.findall(r"\bru-RU-[A-Za-z]+Neural\b", voices)))
    bd = run_dir("blind-tts", t)
    labels = sorted(p for p in bd.glob("*") if p.suffix.lower() in AUDIO_EXT) if bd.is_dir() else []
    scores = read_json(bd / "_scores.json")
    key = read_json(bd / "_key.json") if scores else None
    s["blind"] = {"items": [{"label": p.stem, "file": rel(p)} for p in labels], "scores": scores,
                  "reveal": {lab: {"file": f, "variant": Path(f).stem, "score": (scores or {}).get(lab)} for lab, f in key.items()} if key else None}
    # edit
    w = words_file(t)
    base = w.with_suffix("").with_suffix("") if w else None
    s["edit"] = {"words": rel(w) if w else None,
                 "captions": rel(Path(f"{base}.captions.json")) if base and Path(f"{base}.captions.json").is_file() else None,
                 "srt": rel(Path(f"{base}.srt")) if base and Path(f"{base}.srt").is_file() else None,
                 "audio": rel(a) if (a := clean_audio(t)) else None,
                 "task": edit_task_text(), "runs": {}}
    ed = run_dir("edit", t)
    for v in ("remotion", "hyperframes"):
        vids = sorted(p for p in ed.glob(f"{v}*") if p.suffix.lower() in VIDEO_EXT) if ed.is_dir() else []
        try:
            prompt = edit_task(t, v)
        except ValueError as e:
            prompt = None
            s["edit"]["missing"] = str(e)
        s["edit"]["runs"][v] = {"video": rel(vids[-1]) if vids else None, "meta": read_json(ed / f"{v}.run.json"),
                                "agent": read_text(ed / f"{v}.agent.txt", 8000), "prompt": prompt}
    sel = req.app.settings().get("agent", "")
    s["agent"] = {"selected": sel, "found": bool(sel and agents.find_exe(agents.AGENTS.get(sel, {}).get("exe", "-")))}
    return 200, s


def catalog_route(req):
    return 200, {"catalog": catalog(), "sections": tests_sections(), "verdicts": VERDICTS,
                 "script_text": read_text(INPUTS / "script_ru.txt") or ""}


def results_route(req):
    return 200, read_json(ROOT / "site" / "data" / "bench_results.json") or {"results": []}


# --- регистрация ---------------------------------------------------------------------------------

def register(app) -> None:
    app.section("bench", "Тесты", js="modules/bench.js", order=10, hint="Стенд этапа 3: сравнение инструментов")
    a = app.action
    a("bench.check_env", "Проверка среды", build_check_env, describe="python skills/kp-bench/scripts/check_env.py --tester <t>")
    a("bench.summary", "Свод результатов", build_summary, describe="python skills/kp-bench/scripts/summary.py")
    a("bench.venv", "Создать окружение", build_venv, heavy=True, describe="<python 3.12 или текущий> -m venv .venv-{asr|whisperx|tts}")
    a("bench.install", "Установка", build_install, heavy=True,
      describe="[создать venv], затем <venv>/python -m pip install <пакеты из PACKS>; для GigaAM — git clone salute-developers/GigaAM в bench/tools/GigaAM и pip install -e")
    a("bench.clone_rulint", "Скачать ru-editor", build_clone_rulint, heavy=True,
      describe="git clone --depth 1 https://github.com/miolamio/agent-skills bench/tools/agent-skills; поиск ru_lint.py")
    a("bench.textcheck", "Проверщик текста", build_textcheck,
      describe=".venv-asr/humanizer-markers --scan post_ru.md | python <найденный ru_lint.py> post_ru.md")
    a("bench.textcheck_agent", "ru-text через агента", build_textcheck_agent, heavy=True,
      describe="<агент> в режиме чтения с промптом «Прочитай задачу в файле bench/runs/_agent/…»")
    a("bench.stress", "Ударения", build_stress, heavy=True,
      describe=".venv-asr/python stress_run.py --variant <v> --out bench/runs/stress/<t>")
    a("bench.asr", "Распознавание", build_asr, heavy=True,
      describe="<venv>/python asr_run.py --engine <e> --audio <запись> --out bench/runs/asr/<t>; wer.score() в процессе")
    a("bench.clean", "Очистка записи", build_clean, heavy=True,
      describe="ffmpeg → deepFilter → loudness.py --normalize → auto-editor | ffmpeg afftdn,silenceremove → loudness.py")
    a("bench.tts_voices", "Список голосов Edge TTS", build_tts_voices, describe=".venv-asr/edge-tts --list-voices")
    a("bench.tts", "Синтез", build_tts, heavy=True,
      describe="edge-tts --voice <ru-RU-…Neural> --file script_ru.txt --write-media … | .venv-tts/python tts_qwen.py …")
    a("bench.tts_back", "Обратное распознавание", build_tts_back, heavy=True,
      describe=".venv-asr/python asr_run.py --engine gigaam --audio <синтез>; wer.score()")
    a("bench.blind_make", "Слепая оценка", build_blind_make, describe="python blind.py make bench/runs/tts/<t> bench/runs/blind-tts/<t>")
    a("bench.captions", "Субтитры", build_captions, describe="python captions.py bench/runs/asr/<t>/<e>.words.json --words-per-line 3")
    a("bench.edit_agent", "Монтаж через агента", build_edit_agent, heavy=True,
      describe="<агент> в режиме записи с промптом «Прочитай задачу в файле bench/runs/_agent/…»")
    a("bench.record", "Записать результат", build_record,
      describe="python record.py --test … --variant … --tester … --metric k=v … --verdict …; python summary.py")
    a("bench.export", "Архив результатов", build_export, describe="zip bench/results (этого тестировщика), bench/env/<t>.json, bench_results.json → bench/runs/export/")
    a("bench.git_push", "Отправить в git", build_git_push, heavy=True,
      describe="git add -- bench/results bench/env site/data/bench_results.json; git commit -m «Стенд: …»; git pull --rebase (при сбое rebase --abort); git push")
    app.route("GET", "/api/bench/catalog", catalog_route)
    app.route("GET", "/api/bench/state", state)
    app.route("GET", "/api/bench/results", results_route)
    app.route("GET", "/api/bench/git", git_status)
    app.route("POST", "/api/bench/blind_scores", blind_scores)
    app.upload_target = upload_target
