# Стенд этапа 3: источники (цены, установка, монтаж и проверщики)

Отчёты субагентов от 27.11.2026, собраны по страницам через пересказ. Для обзора; перед оплатой и включением в стек — проверить по первоисточнику (AGENTS.md).

---

## Цены и условия для теста инструментов (на 2026-11-27)

Метод: страницы получены через WebFetch (ответ малой модели по странице, не сырой текст). Всё, что ниже помечено «проверить», на страницах не найдено. Оплата из России: официальных данных не искал и не нашёл ни по одному зарубежному сервису, кроме Yandex и Postmypost (российские).

## 1. ElevenLabs API
- Источник: https://elevenlabs.io/pricing/api ; https://elevenlabs.io/pricing
- TTS, цена за 1000 символов: Eleven v4 $0.08; v4 Turbo $0.04; v3 $0.08; v3 Conversational $0.04; v2 Multilingual $0.08; Flash/Turbo $0.04.
- STT Scribe, за час: Scribe v3 $0.20; v2 $0.20; v3 Live $0.22; v2 Realtime $0.22.
- Подписки (месяц): Starter $6 (первый месяц $1); Creator $22 (первый $11); Pro $99; Scale $299; Business $990.
- Бесплатный тариф: Free $0, 10k кредитов в месяц; коммерческое использование «Limited».
- Единица оплаты: символы (кредиты на подписках).
- Instant Voice Cloning: нет на Free, появляется с Starter. Professional Voice Cloning: с Creator.
- API-ключ на Free: на страницах не указано, проверить (документация подтверждает только, что запросы идут с ключом). Есть вариант Pay as you go «Start for free».
- Оплата из России: не найдено.
- Стоимость теста: 1000 символов v4 = $0.08 (v4 Turbo $0.04); клон = подписка Starter $6 (первый месяц $1). Бесплатно: TTS в пределах 10k кредитов Free (соотношение кредитов к символам на странице не найдено, проверить); клон бесплатно нельзя.

## 2. Yandex SpeechKit (AI Studio)
- Источники: https://aistudio.yandex.ru/ru/docs/speechkit/pricing ; https://yandex.cloud/ru/docs/billing/concepts/bonus-account
- Синтез API v3: оплата за запрос, блок до 250 символов. Модель general 0.1626 ₽ за запрос; livetts 0.25 ₽ (без НДС). API v1: 1342 ₽ за 1 млн символов.
- Распознавание: единица 15 секунд одноканального аудио. Потоковое и синхронное 0.1626 ₽ за 15 с; асинхронное 0.1515 ₽ за 15 с (посекундно с 16-й); отложенное 0.0381 ₽ за 15 с. Пересчёт на минуту (расчёт, не со страницы): ~0.65 ₽ потоковое.
- Бесплатные квоты SpeechKit: на странице цен не найдено.
- Грант: стартовый грант не менее 4000 ₽ с НДС для резидентов РФ (не менее $30 для нерезидентов). Условия: один раз, при создании первого платёжного аккаунта, нет прошлых покупок, карта привязана при создании. Срок действия на странице не указан. SpeechKit не упомянут явно, «любые сервисы» — проверить.
- API-ключ: не проверялось, проверить.
- Оплата из России: сервис российский, рубли.
- Стоимость теста: 1000 символов = 4 блока по 250 = ~0.65 ₽ (general, если блоки по 250; расчёт). 2 минуты синхронного распознавания = 8 отрезков по 15 с = ~1.30 ₽ (расчёт). Итого ~2 ₽, покрывается грантом.

## 3. fal.ai
- Источники: https://fal.ai/pricing ; страницы моделей https://fal.ai/models/... ; https://fal.ai/mcp
- Новейшие версии в каталоге: Kling 4.0 (kling/v4), Wan 3.0, MiniMax H3 / H3 Max / H3 Max Turbo (Hailuo не найден по имени), Seedance 2.0 (fast) и Seedance 2.5.
- Kling v4 image-to-video: 720p $0.157/с, 1080p $0.235/с. Ролик 5 с 720p = $0.785. (Kling v3 Pro $0.14/с; v2.5 Turbo Pro $0.07/с — со страницы pricing.)
- Wan 3.0 text-to-video: 480p $0.05/с, 720p $0.10/с, 1080p $0.20/с. Ролик 5 с 720p = $0.50.
- MiniMax: H3 Max Turbo $0.015/с (pricing); на странице модели 768p $0.026/с по акции, $0.04/с после 31 октября (акция к сегодняшнему дню закончилась — проверить). 720p в списке нет. 5 с 768p: $0.13 по акции / $0.20 без.
- Seedance 2.0 fast, 720p: $0.2419/с, 5 с ≈ $1.21 (расчёт); standard $0.3024/с. На странице расхождение токенной цены: $0.014 и $0.0112 за 1000 токенов. Варианты mini/lite: цена на странице lite не показана, не найдено.
- Бесплатные кредиты новым аккаунтам: не найдено.
- fal MCP: бесплатен, «pay only for the model runs you trigger».
- API-ключ на бесплатном тарифе: не найдено (модель оплаты pay-as-you-go).
- Оплата из России: не найдено.
- Стоимость теста: клип 5 с 720p — Wan 3.0 $0.50; Kling 4.0 $0.785; MiniMax H3 Max Turbo ~$0.08 по ставке $0.015/с (расчёт, разрешение не проверено); Seedance 2.0 fast ~$1.21.

## 4. HeyGen
- Источники: https://www.heygen.com/pricing ; https://www.heygen.com/api-pricing (редирект на app.heygen.com, содержимое не получено)
- Тарифы приложения: Free $0; Creator $29/мес ($24 при годовой); Pro от $49/мес за 1000 кредитов (до $4300/мес за 100 000); Business $149 + $20 за место; Enterprise по запросу.
- Free: 3 видео/мес с водяным знаком, до 1 минуты, до 3 Photo Avatar, 1 Custom Video Avatar (цифровой двойник), 1 клон голоса, 30+ языков.
- Creator/Pro/Business: 175+ языков и диалектов; Photo Avatar без ограничения.
- Русский язык: на странице не назван явно — проверить.
- Цена минуты через API: не найдено (страница API pricing не отдала данных).
- Бесплатные API-кредиты и API-ключ на Free: не найдено.
- Оплата из России: не найдено.
- Стоимость теста: через приложение бесплатно (Free, водяной знак, до 1 мин); через API — проверить.

## 5. Higgsfield
- Источник: https://higgsfield.ai/pricing.md ; https://docs.higgsfield.ai/
- Индивидуальные планы (USD без НДС, месяц): Free 0 кредитов; Starter 270 кр. $19; Plus 1200 кр. $59 (первый месяц $40; годовая $30/мес); Ultra 3000 кр. $129 (первый $75; годовая $45/мес), также 6000 кр. $250 и 9000 кр. $375. Business: Team $55 за место (2–9 мест, 1000 кр.), Scale $119.99 за место (5–15 мест, 2500 кр.). На странице указана распродажа до 2026-11-27 00:00 UTC (уже закончилась).
- Free: 0 кредитов, одна генерация одновременно, только избранные модели.
- Стоимость генерации видео 5 с в кредитах: не найдено (зависит от модели, длительности, разрешения).
- API: есть (ключи в Higgsfield Console, запрос и опрос/webhook; файлы хранятся минимум 7 дней). Условия по тарифам: на страницах не найдено; в документации упомянут раздел Enterprise API, проверить. MCP/CLI: бесплатные и безлимитные генерации в MCP/CLI недоступны; доступны ли кредитные генерации — не подтверждено.
- Оплата из России: не найдено.
- Стоимость теста: бесплатно нельзя (Free = 0 кредитов); минимум Starter $19/мес.

## 6. Postmypost
- Источники: https://postmypost.io/pricing ; https://postmypost.io/prices
- Тарифы: Standard, Premium, Advanced; суммы в текст страницы не попали (переключатели USD/RUB/KZT, скидка 10% за 12 месяцев) — цены не найдены, проверить в браузере.
- Пробный период: 7 дней без карты.
- Площадки: Instagram, Facebook, ВК, Telegram, X, Threads, TikTok, Reddit, OK, Pinterest, YouTube, Rutube, Viber, LinkedIn, Discord, Bluesky, Medium, Tumblr, Mastodon, Webhook, Bitrix, Max.
- API: заявлен модуль API, на каком тарифе — не указано. MCP: только ссылка в меню, тариф не указан.
- Reels и YouTube Shorts: на страницах не упомянуты, проверить.
- Оплата из России: сервис российский, валюта RUB в выборе.
- Стоимость теста: бесплатно 7 дней (пробный период), включая проверку API/MCP — проверить.

## 7. Remotion
- Источник: https://www.remotion.dev/docs/license/pricing.md
- Free License: $0 для физлиц и компаний до 3 человек.
- Company License (оплата по использованию, можно один или оба): Automators $0.01 за рендер, пакетами по 1000 ($10), минимум $100/мес; Creators $25 за место в месяц.
- Enterprise: от $500/мес.
- Подтверждено по первоисточнику.
- Стоимость теста: $0 (Free License при команде до 3 человек).

## 8. HyperFrames (heygen-com/hyperframes)
- Источник: https://github.com/heygen-com/hyperframes (README)
- Фреймворк бесплатный, open source, Apache 2.0, без платы за рендер и порогов коммерческого использования.
- Pro относится к приложению HyperFrames Studio, не к фреймворку: Pro $25/мес, 25 000 кредитов в месяц, доступ к платным видео-, изображение-, голос- и музыкальным моделям (в README названы HeyGen Video 1, Seedance 2.5, Lyria 3 Pro), встроенный агент (иначе свой Claude Code или Codex). У Studio есть бесплатный план, его лимиты не найдены.
- Стоимость теста: $0 (фреймворк локально).

## Итоговая таблица

| Сервис | Бесплатно можно протестировать? | Стоимость теста | Источник |
|---|---|---|---|
| ElevenLabs | частично (TTS на Free; клон нет) | $0.08 за 1000 симв. v4 + клон от $1 (Starter, 1-й месяц) / $6 | elevenlabs.io/pricing/api |
| Yandex SpeechKit | да (стартовый грант от 4000 ₽, проверить для SpeechKit) | ~2 ₽ (расчёт) | aistudio.yandex.ru/ru/docs/speechkit/pricing |
| fal.ai | нет (бесплатные кредиты не найдены) | 5 с 720p: Wan 3.0 $0.50; Kling 4.0 $0.785; Seedance 2.0 fast ~$1.21; MiniMax H3 Max Turbo ~$0.08 (расчёт) | fal.ai/pricing, fal.ai/models/* |
| HeyGen | частично (Free: водяной знак, до 1 мин; API — проверить) | $0 в приложении; API проверить | heygen.com/pricing |
| Higgsfield | нет (Free = 0 кредитов) | от $19 (Starter) | higgsfield.ai/pricing.md |
| Postmypost | да (7 дней пробный) | $0 за 7 дней | postmypost.io/pricing |
| Remotion | да | $0 (до 3 человек) | remotion.dev/docs/license/pricing.md |
| HyperFrames | да (фреймворк); Studio Pro $25/мес | $0 | github.com/heygen-com/hyperframes |

---

## Установка и запуск инструментов для бесплатного теста (Windows 10/11 x64, macOS)

Дата: 2026-11-27. Источники: README на GitHub, PyPI, страницы Hugging Face, доки ffmpeg. Что не найдено в первоисточнике, помечено «не найдено» или «проверить». Issues на GitHub недоступны (robots), поэтому проблем из issues нет.

## 1. GigaAM v3
- Источник: https://github.com/salute-developers/GigaAM ; https://huggingface.co/ai-sage/GigaAM-v3
- Установка (из README): `git clone https://github.com/salute-developers/GigaAM.git`, `cd GigaAM`, `pip install -e .[torch]`. Нужен ffmpeg в PATH.
- Python: >= 3.10. Рекомендованные версии на HF: torch==2.8.0, torchaudio==2.8.0, transformers==4.57.1, pyannote-audio==4.0.0, torchcodec==0.7.0.
- GPU/VRAM: требований не найдено. CPU: явно не описан (не найдено). Для ONNX: fp16 для GPU; `onnxruntime-gpu==1.22.*`.
- Windows: особых инструкций нет, только «ffmpeg в PATH».
- Запуск (README):
```python
import gigaam
model = gigaam.load_model("v3_e2e_rnnt")
result = model.transcribe(audio_path, word_timestamps=True)
for word in result.words:
    print(f"[{word.start:.2f} - {word.end:.2f}] {word.text}")
```
- Лонгформ: `.transcribe` только до 25 секунд. Нужно `pip install -e ".[longform]"` (pyannote.audio), токен HF с доступом к `pyannote/segmentation-3.0` (принять условия на HF).
```python
os.environ["HF_TOKEN"] = "<токен>"
result = model.transcribe_longform(long_audio_path)
for segment in result:
    print(f"[{gigaam.format_time(segment.start)} - {gigaam.format_time(segment.end)}]: {segment.text}")
```
- Вариант через transformers (HF): `AutoModel.from_pretrained("ai-sage/GigaAM-v3", revision=..., trust_remote_code=True)`, `model.transcribe("example.wav")`. Ревизии: ssl, ctc, rnnt, e2e_ctc, e2e_rnnt (e2e = с пунктуацией и нормализацией текста). Пословные таймкоды и лонгформ на странице HF не описаны.
- Вывод: объект с `words[]` (start, end, text); для лонгформа сегменты (start, end, text).
- Лицензия: код MIT (README); веса MIT (карточка HF, «License: mit»).

## 2. WhisperX
- Источник: https://github.com/m-bain/whisperX
- Установка: `pip install whisperx` (также `uvx whisperx`). Опционально `pip install "whisperx[fast]"` (numba для быстрее выравнивания).
- Python: версия не указана (не найдено). GPU: CUDA toolkit 12.8; для CPU не нужен.
- VRAM: «<8GB для large-v2 при beam_size=5». Уменьшить: меньший batch size, меньшая модель, `--compute_type int8`.
- CPU (README): `whisperx path/to/audio.wav --compute_type int8 --device cpu`. Скорость на CPU: не найдено.
- Русский: в README нет примера. В `alignment.py` для `ru` модель выравнивания `jonatasgrosman/wav2vec2-large-xlsr-53-russian` (скачивается с HF). CLI по аналогии с примером для de: `whisperx audio.wav --model large-v3 --language ru --device cpu --compute_type int8` (команда составлена по README, не взята дословно; проверить).
- Python API: load_model, transcribe, load_align_model, align (пословные таймкоды в `result["segments"][i]["words"]`; диаризация опционально через DiarizationPipeline).
- Формат вывода: segments со словами; `--highlight_words True` для srt. Детали формата в README не описаны.
- Windows: README советует CUDA toolkit 12.8; в репозитории есть CUDNN_TROUBLESHOOTING.md (содержимое не прочитано). Других проблем не найдено.
- Лицензия: код BSD-2-Clause. Веса Whisper и align-модели: лицензии не проверены.

## 3. faster-whisper
- Источник: https://github.com/SYSTRAN/faster-whisper
- Установка: `pip install faster-whisper`. Python >= 3.9. ffmpeg не нужен (PyAV).
- GPU: cuBLAS для CUDA 12 и cuDNN 9. Для Windows README отсылает к Purfview/whisper-standalone-win (архив библиотек NVIDIA, положить в PATH). Для CPU не нужно.
- CPU: бенчмарк README для модели small, 13 мин аудио, i7-12700K, 8 потоков, beam 5: int8 1m42s, int8 с batch_size=8 51s. Для large-v3 цифр нет (не найдено). Потоки: переменная `OMP_NUM_THREADS`.
- Пример (составлен из фрагментов README):
```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.mp3", language="ru", word_timestamps=True)
for segment in segments:
    for word in segment.words:
        print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
```
- Вывод: генератор сегментов; у сегмента `words` (start, end, word).
- Лицензия: код MIT. Веса large-v3 (конверсия CTranslate2): лицензия не проверена.

## 4. Qwen3-TTS
- Источник: https://github.com/QwenLM/Qwen3-TTS ; https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base
- Установка: `conda create -n qwen3-tts python=3.12 -y`, `conda activate qwen3-tts`, `pip install -U qwen-tts`. Из исходников: `git clone ...`, `pip install -e .`. FlashAttention 2 опционально: `pip install -U flash-attn --no-build-isolation` (работает только в fp16/bf16; Windows-сборка не описана).
- Python: 3.12 (в README пример чистого окружения).
- VRAM: не найдено. CPU: не описан, все примеры `device_map="cuda:0"`. Считать, что нужна NVIDIA GPU; проверить.
- Языки: китайский, английский, японский, корейский, немецкий, французский, русский, португальский, испанский, итальянский.
- Модели: Qwen3-TTS-12Hz-1.7B-Base, 0.6B-Base (клон голоса), 1.7B/0.6B-CustomVoice, 1.7B-VoiceDesign, Qwen3-TTS-Tokenizer-12Hz.
- Клон голоса (README, адаптировано):
```python
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel
model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0", dtype=torch.bfloat16)
wavs, sr = model.generate_voice_clone(text="...", language="Russian", ref_audio="ref.wav", ref_text="транскрипт ref.wav")
sf.write("out.wav", wavs[0], sr)
```
  `ref_audio`: путь, URL, base64 или (numpy, sr). `x_vector_only_mode=True` не требует ref_text, качество может упасть. Вызов `from_pretrained` с этими аргументами для Base в README не показан дословно (там пример с device_map/dtype; проверить).
- siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf (https://huggingface.co/siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf): дообучение LoRA (r=16, alpha=32) поверх Qwen3-TTS-12Hz-1.7B-Base для русских ударений. В корне репозитория слитый (merged) чекпоинт, замена базовой модели; адаптер отдельно в `lora/` (35 MB). Подключение: просто указать id этого репо в `Qwen3TTSModel.from_pretrained` (пример автора):
```python
tts = Qwen3TTSModel.from_pretrained("siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf", device_map="cuda:0", dtype=torch.bfloat16)
wavs, sr = tts.generate_voice_clone(text="За́мок стои́т на холме́.", language="Russian", ref_audio="voice.wav", ref_text="transcript of voice.wav")
```
  Ударение: U+0301 после ударной гласной. Автор получал метки через RUAccent (конвертация «+» перед гласной в U+0301). Загрузка отдельного адаптера из `lora/` на странице не описана (не найдено).
- Лицензия: код Apache-2.0; веса Base Apache-2.0 (карточка HF); LoRA Apache-2.0, но автор предупреждает: тексты и 24 референсных клипа из biggest-ru-book без заявленной лицензии, детектор ударений обучен частично на аудио Silero TTS (некоммерческая лицензия); для коммерции проверять.

## 5. silero-stress и RUAccent
silero-stress
- Источник: https://github.com/snakers4/silero-stress
- Установка: `pip install silero-stress`. Python >= 3.10, torch >= 1.12.0, >= 1 GB RAM, x86-64 CPU с AVX. Пакет ~50 MB, GPU не нужен.
- Пример:
```python
from silero_stress import load_accentor
accentor = load_accentor()
print(accentor("Меня зовут Лева Королев. Я из готов."))
```
- Вывод: текст с «+» перед ударной гласной (`Мен+я зов+ут Л+ёва`). Лицензия: MIT (код). Лицензия весов отдельно: не найдено.
- Windows: проблем в README не найдено.

RUAccent
- Источник: https://github.com/Den4ikAI/ruaccent
- Установка: `pip install ruaccent` (или `pip install git+https://github.com/Den4ikAI/ruaccent.git`). Python: не указан. ONNX; CPU по умолчанию (`device="CPU"`), для CUDA нужен `onnxruntime-gpu`. RAM >= 512 MB для tiny.
- Пример:
```python
from ruaccent import RUAccent
accentizer = RUAccent()
accentizer.load(omograph_model_size='turbo3.1', use_dictionary=True, tiny_mode=False)
print(accentizer.process_all('на двери висит замок.'))
```
- Модели: tiny, tiny2, tiny2.1, turbo, turbo2 (по умолчанию), turbo3, turbo3.1, big_poetry. Свой словарь: `custom_dict`. Вывод: текст с «+» перед ударной гласной (по описанию автора Qwen-LoRA). Лицензия: MIT.

## 6. rutextnorm
- Источник: https://pypi.org/project/rutextnorm/
- Установка: `pip install rutextnorm`. Версия 2.1.0 (2026-06-13), Python >= 3.8, зависимостей нет, один файл на `re`, без моделей и сети. Лицензия MIT. CPU, Windows/macOS проблем не заявлено.
- Пример:
```python
from rutextnorm import normalize_russian
print(normalize_russian("У меня есть $1234 и 5678 рублей, 90.50€."))
```
- Вывод: строка, числа/даты/валюты/единицы словами с согласованием падежей. Есть `flag_uncertain()` для спорных фрагментов.

## 7. DeepFilterNet
- Источник: https://github.com/Rikorose/DeepFilterNet
- Установка pip: `pip install torch torchaudio -f https://download.pytorch.org/whl/cpu/torch_stable.html`, затем `pip install deepfilternet`. torch >= 1.9. Python: не указан. Обучение только Linux.
- Бинарник `deep-filter`: есть на странице релизов (последний v0.5.6, 12 ассетов). Имена ассетов не получены, наличие Windows .exe не подтверждено: проверить на https://github.com/Rikorose/DeepFilterNet/releases/tag/v0.5.6.
- Запуск: `deep-filter audio-file.wav` (бинарник, только WAV 48 kHz); `deepFilter path/to/noisy_audio.wav` (Python). Результат в папке `out` (для Python `--output-dir`).
- GPU не требуется (в README не заявлено). Сэмплрейт 48 kHz; ffmpeg-ресемплинг перед запуском.
- Лицензия: код и веса MIT или Apache-2.0 на выбор. README заявляет поддержку Linux, macOS, Windows.

## 8. auto-editor
- Источник: https://github.com/WyattBlue/auto-editor ; https://auto-editor.com/installing
- Установка: pip больше не публикуется («no longer being published on pip»). Windows: скачать бинарник со страницы Releases (последний 31.7.2), переименовать в `auto-editor.exe`; winget не указан. macOS: `brew install auto-editor`, либо бинарник + `chmod +x ./auto-editor`.
- Python не нужен. ffmpeg: для бинарников не указан.
- Вырезка тишины (по умолчанию `--edit audio:threshold=0.04,stream=all`):
  `auto-editor example.mp4`
  `auto-editor example.mp4 --edit audio:-19dB --margin 0.2sec`
- Экспорт: `--export premiere|resolve|final-cut-pro|shotcut|kdenlive|clip-sequence`. Выходной видеофайл по умолчанию с суффиксом `_ALTERED` (из памяти, в README не найдено; проверить).
- Лицензия: Public Domain для репозитория; бинарники в Releases могут иметь другие open source лицензии.

## 9. ffmpeg на Windows
- Источник: https://www.gyan.dev/ffmpeg/builds/ ; https://ffmpeg.org/ffmpeg-filters.html#loudnorm
- Установка: `winget install ffmpeg` (полная сборка gyan.dev); `winget install "FFmpeg (Essentials Build)"` (урезанная). Идентификатор пакета вида Gyan.FFmpeg на странице не приведён (проверить `winget search ffmpeg`). После установки открыть новый терминал.
- Опции loudnorm (дока): I (-70..-5, по умолчанию -24), TP (-9..0, по умолчанию -2), LRA (1..50, по умолчанию 7), measured_I/LRA/TP/thresh, offset, linear (true по умолчанию, нужны все measured_*), print_format summary|json|none.
- Проход 1 (измерение):
```
ffmpeg -hide_banner -i in.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null NUL
```
  На macOS/Linux вместо `NUL` писать `/dev/null`. Лог идёт в stderr, JSON-блок в конце. Поля JSON: input_i, input_tp, input_lra, input_thresh, target_offset (названия полей из практики ffmpeg, в прочитанной части доки не приведены; проверить на реальном выводе).
- Проход 2 (подставить измеренные значения):
```
ffmpeg -i in.wav -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true -ar 48000 out.wav
```
  Двухпроходный режим в доке описан только фразой «Support for both single pass and double pass modes»; конкретная команда составлена по списку опций.
- Лицензия: зависит от сборки (LGPL/GPL); не проверялась.

## 10. Edge TTS
- Источник: https://pypi.org/project/edge-tts/ ; https://github.com/rany2/edge-tts
- Установка: `pip install edge-tts` (или `pipx install edge-tts`). Версия 7.3.1 (2026-10-13), Python >= 3.7. Лицензия LGPLv3. Требуется интернет (облачный сервис Microsoft); GPU не нужен; Windows: edge-playback работает без mpv.
- CLI:
  `edge-tts --list-voices`
  `edge-tts --voice <имя> --text "Привет" --write-media out.mp3 --write-subtitles out.srt`
  Отрицательные значения только в виде `--rate=-50%`.
- Python-пример в README и PyPI не приведён (отсылка к /examples/). Из памяти (проверить): `edge_tts.Communicate(text, voice).save("out.mp3")` через asyncio.
- Русские голоса: в источниках не найдены (список обрезан). Из памяти, не подтверждено: ru-RU-SvetlanaNeural, ru-RU-DmitryNeural; проверить `edge-tts --list-voices | findstr ru-RU`.
- Custom SSML удалён Microsoft. Условия использования сервиса Microsoft для коммерции: проверить.

## Порядок установки для бесплатного теста на Windows
```
winget install ffmpeg
winget install Python.Python.3.12
py -3.12 -m venv bench && bench\Scripts\activate
pip install --upgrade pip
pip install faster-whisper edge-tts rutextnorm silero-stress ruaccent
pip install whisperx
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
git clone https://github.com/salute-developers/GigaAM.git
cd GigaAM && pip install -e ".[torch,longform]" && cd ..
pip install deepfilternet
:: auto-editor: скачать auto-editor.exe со страницы Releases (WyattBlue/auto-editor), положить в PATH
:: deep-filter.exe (опционально): скачать из Releases Rikorose/DeepFilterNet, если есть Windows-ассет
:: Qwen3-TTS: pip install -U qwen-tts (нужна NVIDIA GPU; на CPU не проверено)
set HF_TOKEN=<токен>
```
Замечания: единое окружение может дать конфликт версий torch (GigaAM v3 рекомендует torch 2.8.0, pyannote-audio 4.0.0, whisperx тянет свои зависимости); при конфликте использовать отдельные venv. Совместимость `winget install Python.Python.3.12` и версий пакетов не проверялась.

---

## Факты для теста движков монтажа и проверщиков русского текста

Дата сбора: 2026-11-27.
Метод: raw.githubusercontent.com и gh API недоступны (прокси, 403), поэтому тексты читались через WebFetch (страницы github.com и remotion.dev, ответ пересказывает малая модель, не сырой текст). Код и файлы репозиториев не открывались. Перед включением в стек проверить по первоисточнику локально (git clone).

## Часть А. Движки монтажа

### 1. Remotion (remotion.dev, remotion-dev/remotion, remotion-dev/skills)
- Создание проекта: `npx create-video@latest` (мастер: менеджер пакетов, шаблон, ставить ли Agent Skills). Без вопросов: `npx create-video@latest --yes --blank my-video`. Источник: remotion.dev/docs.
- Node: «at least Node 16 or Bun 1.0.3» (remotion.dev/docs). В README репозитория требования не указаны. Не сверено с текущей страницей установки (docs/installation не открылась).
- Windows: на странице docs/ перечислены только macOS 15+ и Linux (glibc 2.35+); про Windows не найдено. Страница docs/miscellaneous/windows не открылась. Статус: проверить.
- Рендер CLI: `npx remotion render <entry-point|serve-url>? <composition-id> <output-location>`; пример по синтаксису: `npx remotion render src/index.ts MyComposition out/video.mp4`. Без `--codec` — H.264; без output — папка `out`. Источник: docs/cli/render.
- Субтитры: пакет `@remotion/captions`, установка `npx remotion add @remotion/captions` (docs/captions/api).
- Формат Caption (по примеру на docs/captions/create-tiktok-style-captions): `{text, startMs, endMs, timestampMs, confidence}`; `text` слова с ведущим пробелом, кроме первого; `confidence` может быть null. Страница с описанием типа (docs/captions/caption) не открылась — точные типы полей не найдены.
- Пословная анимация: `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds, breakOnSilenceAfterMilliseconds?})` -> `{pages}`; у страницы `text, startMs, durationMs, tokens[{text, fromMs, toMs, pageBreakAfter?}]`. Малое `combineTokensWithinMilliseconds` даёт слово за словом. Нужен `white-space: pre` у контейнера.
- Шрифт с кириллицей: установка `npm i @remotion/google-fonts`; код `import {loadFont} from '@remotion/google-fonts/Lobster'; loadFont('normal', {weights:['400'], subsets:['cyrillic']})`. Страница про кириллицу не говорит; пример с `subsets: ['cyrillic']` — вывод из шаблона, поддержку конкретного шрифта проверять через `getInfo().subsets`. С v5.0 weights и subsets обязательны.
- Скиллы: `npx skills add remotion-dev/skills`; в проекте `npx remotion skills add`; глобально `npx -y skills@latest add remotion-dev/skills -g -y`. В составе: remotion-best-practices, -create, -markup (шрифты), -studio, -render, -maps, -captions, -saas, -interactivity, -docs, -upgrade, -multimedia.
- Лицензия: особая; некоторым пользователям нужна компания-лицензия (README, LICENSE.md, remotion.dev/license). Условия не разбирались — проверить.
- Минимальная последовательность (собрана из фактов выше, целиком не запускалась):
  1. `npx create-video@latest --yes --blank my-video`
  2. `cd my-video`; `npx remotion add @remotion/captions`; `npm i @remotion/google-fonts`
  3. В композиции задать 1080x1920 (поля width/height у `<Composition>` — не проверено по странице), текст русский, шрифт через loadFont с cyrillic
  4. `npx remotion render <entry> <composition-id> out/video.mp4`

### 2. HyperFrames (heygen-com/hyperframes)
- Установка/проект: `npx hyperframes init my-video`, `cd my-video`.
- Предпросмотр: `npx hyperframes preview`. Рендер в MP4: `npx hyperframes render`. Есть также `hyperframes cloud render` и AWS Lambda.
- Требования (README): Node.js 22+ и FFmpeg. Движок снимает кадры через headless Chrome; версия не указана, нужно ли ставить Chrome отдельно — не найдено.
- Windows: для CLI явно не указано. Desktop-приложение Studio: macOS, Windows, Linux (.deb). Есть упоминание установки Git LFS под Windows. Статус: проверить.
- Субтитры по словам: в README только общие упоминания captions/«kinetic captions»; формат и пословные таймкоды не описаны — не найдено.
- Шрифты/кириллица: не найдено.
- Скиллы: `npx skills add heygen-com/hyperframes` (выбор в списке «Core Skills»); `--skill <имя>`; `--all` (9 скиллов). Core: hyperframes, hyperframes-cli, hyperframes-registry, media-use, reverse-any-video, style-sampling. По запросу: figma, slideshow, remotion-to-hyperframes. Без выбора: `npx hyperframes skills update`. Плагин Claude Code: `claude plugin marketplace add heygen-com/hyperframes`, затем `claude plugin install hyperframes@hyperframes`.
- Бесплатное: фреймворк Apache 2.0, «no per-render fees or commercial-use thresholds». Приложение Studio: бесплатный план; Pro $25/мес (25 000 кредитов). Что именно входит в бесплатный план — не найдено.
- Минимальная последовательность: `npx hyperframes init my-video` -> `cd my-video` -> `npx hyperframes render`. Как задать 9:16 и русский текст — не найдено (смотреть скилл hyperframes и шаблоны после init).

## Часть Б. Проверщики русского текста

### 3. Vladimir-Human/humanizer-ru
- CLI: `pip install humanizer-ru`.
- MCP: конфиг `{"mcpServers":{"humanizer-ru":{"command":"uvx","args":["--from","humanizer-ru==3.36.4","humanizer-mcp"]}}}`; локально после pip: `humanizer-mcp`.
- Скилл: каталог `dsh/skills/humanizer-ru`, инструкция в `docs/USAGE.md` (шаги на странице не приведены, не читал). Для агентов с agentskills.io — распаковать текстовый пакет из релиза.
- Скан: `humanizer-markers --scan input.txt`. Вывод: файл, строка, класс (A или B), имя маркера, фрагмент; в конце «Найдено маркеров: N.». Коды выхода: 1 — найдены, 0 — нет, 2 — файл не читается. Опции: `--json` (поля file, line, marker, class, fragment), `--language en|auto`.

### 4. miolamio/agent-skills, ru-editor
- Python: «Pure Python 3.11+, no third-party deps» (README репозитория).
- Скрипт `ru_lint.py` назван в описании ru-editor: 33 проверки (11 HARD_FAIL, 22 WARN).
- Путь к ru_lint.py, команда запуска и формат вывода: не найдено (страницы дерева репозитория закрыты для WebFetch robots/лимит запросов). Проверить через git clone.

### 5. talkstream/ru-text
- Установка: `npx skills add talkstream/ru-text` (все три скилла в проект); один скилл: `npx skillsbd add talkstream/ru-text/ru-text`; плагины для ChatGPT, Claude (.claude-plugin), Codex, Cursor; детали в INSTALL.md (не читал).
- Скрипт или SKILL.md: это скилл (SKILL.md + 10 файлов в `skills/ru-text/references/`: typography, info-style, editorial-punctuation, editorial-grammar, ux-writing, business-writing, anti-patterns, addenda, scoring, sources). Из скриптов на главной назван только `tools/extract-atoms.sh` (считает «атомы» скилла), проверщика текста скриптом нет — оценку выставляет агент.
- Оценка 0–10: запрос агенту «Оцени этот текст по ru-text» или в Claude Code `/ru-text:ru-score`. Формула (references/scoring.md): T Типографика 0.15, Ч Ясность 0.25, Г Грамматика 0.20, С Структура 0.20, Ц Точность для читателя 0.20; ограничения: любая шкала < 3.0 -> итог <= 5.0; Типографика или Грамматика < 4.0 -> <= 7.0. Метки: 9–10 Эталонный, 7–8.9 Хороший, 5–6.9 Средний, 3–4.9 Слабый, 0–2.9 Критический. Вывод: «Оценка: X.X / 10 — метка», таблица по 5 шкалам с цитатами, строка формулы, примечания. Тексты короче 50 слов — предупреждение о низкой надёжности.

## Не найдено / проверить
- Remotion: поля типа Caption (типы), Windows, актуальная версия Node, условия лицензии.
- HyperFrames: Windows для CLI, нужен ли отдельный Chrome, пословные субтитры, кириллица, 9:16, состав бесплатного плана.
- ru-editor: путь, команда и вывод ru_lint.py.
- humanizer-ru: шаги установки скилла (docs/USAGE.md).
