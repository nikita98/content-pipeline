# Установка для бесплатных тестов

Источники: README на GitHub, PyPI, карточки Hugging Face, документация ffmpeg (проверено 27.11.2026). Пометка «проверить» — команда собрана по документации, но не запускалась.

## Содержание
1. Базовое: Python, Node, ffmpeg, git
2. Окружения Python
3. Распознавание: GigaAM, faster-whisper, WhisperX
4. Ударения и нормализация: rutextnorm, silero-stress, RUAccent
5. Синтез: Qwen3-TTS, Edge TTS
6. Очистка звука: DeepFilterNet, auto-editor
7. Монтаж: Remotion, HyperFrames
8. Проверщики текста: humanizer-ru, ru-editor, ru-text

## 1. Базовое
Windows:
```
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install ffmpeg
winget install Git.Git
```
macOS: `brew install python@3.12 node ffmpeg git`.
Проверка: `python skills/kp-bench/scripts/check_env.py --tester <имя>`.
Node: Remotion требует 16+, HyperFrames — 22+. Ставьте LTS 22 или новее.
ID пакетов winget для Node и ffmpeg — проверить (`winget search node`, `winget search ffmpeg`).

## 2. Окружения Python
У GigaAM и WhisperX разные требования к torch (GigaAM v3 на HF рекомендует torch 2.8.0 и pyannote-audio 4.0.0). Делайте два окружения:
```
py -3.12 -m venv .venv-asr        # GigaAM, faster-whisper, rutextnorm, ударения, DeepFilterNet
py -3.12 -m venv .venv-whisperx   # только WhisperX
```
Активация: Windows `.venv-asr\Scripts\activate`, macOS `source .venv-asr/bin/activate`. Папки `.venv-*` в git не попадают.

## 3. Распознавание
**GigaAM v3** (код и веса MIT):
```
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu   # без NVIDIA
git clone https://github.com/salute-developers/GigaAM.git bench/tools/GigaAM
pip install -e bench/tools/GigaAM[torch]
```
За один вызов — до 25 с. `asr_run.py` сам режет запись по паузам, длинный режим (pyannote, токен HF) не нужен. Работу на CPU README явно не описывает — зафиксируйте время.

**faster-whisper** (MIT): `pip install faster-whisper`. На CPU: `compute_type=int8`. Для GPU на Windows нужны cuBLAS и cuDNN 9 (README отсылает к Purfview/whisper-standalone-win).

**WhisperX** (BSD-2) в отдельном окружении: `pip install whisperx`. CPU: `--device cpu --compute_type int8`. Для `ru` выравнивание — jonatasgrosman/wav2vec2-large-xlsr-53-russian, скачивается само. GPU: CUDA 12.8.

## 4. Ударения и нормализация
```
pip install rutextnorm silero-stress ruaccent
```
- rutextnorm — чистый Python, без моделей.
- silero-stress — CPU с AVX, от 1 ГБ RAM.
- RUAccent — ONNX, CPU по умолчанию.
Вывод ударений у обоих — «+» перед ударной гласной.

## 5. Синтез
**Qwen3-TTS** (код и веса Apache-2.0) — только с NVIDIA GPU, все примеры README на `cuda:0`, VRAM не указан:
```
py -3.12 -m venv .venv-tts && .venv-tts\Scripts\activate
pip install -U qwen-tts
```
Клон голоса:
```python
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0", dtype=torch.bfloat16)
wavs, sr = m.generate_voice_clone(text=TEXT, language="Russian", ref_audio="ref.wav", ref_text=REF_TEXT)
sf.write("qwen3-tts.wav", wavs[0], sr)
```
Вариант с ударениями: модель `siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf`, ударение — знак U+0301 после ударной гласной. «+» из RUAccent и silero-stress переводите так: `re.sub(r"\+(\w)", r"\1́", text)`. В данных LoRA есть тексты без заявленной лицензии — для коммерции проверить.

**Edge TTS** (LGPLv3, облако Microsoft, неофициально):
```
pip install edge-tts
edge-tts --list-voices        # найти ru-RU (Windows: | findstr ru-RU)
edge-tts --voice <голос ru-RU> --file script.txt --write-media edge-tts.mp3
```
Имена русских голосов — смотрите в `--list-voices`. Для коммерции не берём, это ориентир бесплатного качества.

## 6. Очистка звука
**DeepFilterNet** (MIT/Apache-2.0):
```
pip install deepfilternet
ffmpeg -i rec.wav -ac 1 -ar 48000 rec48.wav
deepFilter rec48.wav --output-dir bench/runs/clean
```
Вход — только WAV 48 кГц. Есть ли Windows-бинарник `deep-filter.exe` в Releases — проверить.

**auto-editor** (Public Domain) в pip больше не публикуется. Windows — скачать бинарник из github.com/WyattBlue/auto-editor/releases, переименовать в `auto-editor.exe`, положить в PATH. macOS — бинарник оттуда же или `brew install auto-editor` (проверить).
```
auto-editor clean.wav --edit audio:-19dB --margin 0.2sec
```

**Громкость:** `python skills/kp-bench/scripts/loudness.py in.wav --normalize out.wav`.

## 7. Монтаж
**Remotion** (бесплатно до 3 человек):
```
npx create-video@latest --yes --blank bench/tools/remotion-test
cd bench/tools/remotion-test
npx remotion add @remotion/captions
npm i @remotion/google-fonts
npx skills add remotion-dev/skills
npx remotion render <entry> <composition-id> out/video.mp4
```
Кириллица: `loadFont(..., { subsets: ["cyrillic"] })`, поддержку конкретного шрифта проверьте через `getInfo()`. На странице документации названы только macOS и Linux — работу на Windows фиксируйте в тесте.

**HyperFrames** (Apache-2.0, нужны Node 22+, ffmpeg, headless Chrome):
```
npx hyperframes init bench/tools/hyperframes-test
cd bench/tools/hyperframes-test
npx skills add heygen-com/hyperframes
npx hyperframes preview
npx hyperframes render
```
Пословные субтитры, кириллица и 9:16 в README не описаны — это и проверяем.

## 8. Проверщики текста
- **humanizer-ru:** `pip install humanizer-ru`, затем `humanizer-markers --scan post_ru.md` (есть `--json`; код выхода 1 — маркеры найдены).
- **ru-editor (miolamio):** `git clone https://github.com/miolamio/agent-skills bench/tools/agent-skills`; путь к `ru_lint.py` и команду смотрите в README скилла ru-editor (не удалось прочитать, проверить). Python 3.11+, без зависимостей.
- **ru-text (talkstream):** `npx skills add talkstream/ru-text`. Скрипта нет, оценку 0–10 ставит агент: «Оцени этот текст по ru-text».
