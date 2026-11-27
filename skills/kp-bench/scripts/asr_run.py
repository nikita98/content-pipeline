"""Распознавание записи одним из движков с общим форматом вывода.

Пишет в папку --out:
  <engine>.txt         текст одной строкой (для wer.py)
  <engine>.words.json  [{"text","start","end"}] — секунды, для субтитров и вырезки слов
  <engine>.run.json    время, движок, модель, устройство

Пример:
  python skills/kp-bench/scripts/asr_run.py --engine gigaam --audio bench/runs/rec.wav --out bench/runs/asr/nikita
  python skills/kp-bench/scripts/asr_run.py --engine faster-whisper --audio rec.wav --out out --device cpu
  python skills/kp-bench/scripts/asr_run.py --engine whisperx --audio rec.wav --out out --device cpu

GigaAM распознаёт не больше 25 с за вызов, поэтому скрипт режет запись по паузам на куски до 22 с
(ffmpeg silencedetect) и сдвигает таймкоды. Длинный режим GigaAM с pyannote не нужен.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import _common  # noqa: F401


def ffmpeg() -> str:
    return shutil.which("ffmpeg") or sys.exit("ffmpeg не найден в PATH")


def to_wav16(src: Path, dst: Path) -> None:
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                    "-ac", "1", "-ar", "16000", str(dst)], check=True)


def duration(path: Path) -> float:
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def cut_points(path: Path, max_len: float = 22.0) -> list[tuple[float, float]]:
    """Куски до max_len секунд, границы — середины пауз."""
    out = subprocess.run([ffmpeg(), "-hide_banner", "-nostats", "-i", str(path), "-af",
                          "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    mids = [(a + b) / 2 for a, b in zip(starts, ends)]
    total = duration(path)
    chunks, cur = [], 0.0
    while total - cur > max_len:
        cand = [m for m in mids if cur + 3 < m <= cur + max_len]
        nxt = cand[-1] if cand else cur + max_len
        chunks.append((cur, nxt)); cur = nxt
    chunks.append((cur, total))
    return chunks


def run_gigaam(wav: Path, model_name: str, device: str) -> list[dict]:
    import gigaam  # type: ignore
    model = gigaam.load_model(model_name, device=device) if device else gigaam.load_model(model_name)
    words = []
    with tempfile.TemporaryDirectory() as td:
        for i, (a, b) in enumerate(cut_points(wav)):
            part = Path(td) / f"p{i}.wav"
            subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav),
                            "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-ac", "1", "-ar", "16000", str(part)], check=True)
            res = model.transcribe(str(part), word_timestamps=True)
            for w in getattr(res, "words", []) or []:
                words.append({"text": w.text, "start": round(a + w.start, 3), "end": round(a + w.end, 3)})
    return words


def run_faster_whisper(wav: Path, model_name: str, device: str) -> list[dict]:
    from faster_whisper import WhisperModel  # type: ignore
    model = WhisperModel(model_name, device=device or "cpu", compute_type="int8" if (device or "cpu") == "cpu" else "float16")
    segs, _ = model.transcribe(str(wav), language="ru", word_timestamps=True)
    return [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]


def run_whisperx(wav: Path, model_name: str, device: str) -> list[dict]:
    import whisperx  # type: ignore
    dev = device or "cpu"
    model = whisperx.load_model(model_name, dev, compute_type="int8" if dev == "cpu" else "float16", language="ru")
    audio = whisperx.load_audio(str(wav))
    res = model.transcribe(audio, batch_size=4, language="ru")
    am, meta = whisperx.load_align_model(language_code="ru", device=dev)
    res = whisperx.align(res["segments"], am, meta, audio, dev)
    return [{"text": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3)}
            for s in res["segments"] for w in s.get("words", []) if "start" in w]


ENGINES = {
    "gigaam": (run_gigaam, "v3_e2e_rnnt"),
    "faster-whisper": (run_faster_whisper, "large-v3"),
    "whisperx": (run_whisperx, "large-v3"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", required=True, choices=ENGINES)
    ap.add_argument("--audio", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--model", help="модель движка, по умолчанию: " + ", ".join(f"{k}={v[1]}" for k, v in ENGINES.items()))
    ap.add_argument("--device", default="", help="cpu или cuda; по умолчанию решает движок")
    a = ap.parse_args()
    fn, default_model = ENGINES[a.engine]
    a.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "in16k.wav"
        to_wav16(a.audio, wav)
        audio_s = duration(wav)
        t0 = time.perf_counter()
        words = fn(wav, a.model or default_model, a.device)
        run_s = round(time.perf_counter() - t0, 1)
    text = " ".join(w["text"] for w in words)
    (a.out / f"{a.engine}.txt").write_text(text + "\n", encoding="utf-8")
    (a.out / f"{a.engine}.words.json").write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding="utf-8")
    meta = {"engine": a.engine, "model": a.model or default_model, "device": a.device or "auto",
            "audio_s": round(audio_s, 1), "run_s": run_s, "rtf": round(run_s / max(audio_s, 0.1), 3),
            "words": len(words), "word_timestamps": int(bool(words) and all("start" in w for w in words))}
    (a.out / f"{a.engine}.run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.engine}: {len(words)} слов, {run_s} с на {audio_s:.0f} с аудио (RTF {meta['rtf']}). Файлы в {a.out}")


if __name__ == "__main__":
    main()
