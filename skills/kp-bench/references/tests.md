# Порядок тестов

Каталог (варианты, метрики, цены) — `site/data/bench.json`. Здесь — как проводить каждый тест. Все выходные файлы кладите в `bench/runs/<тест>/<тестировщик>/` (папка в git не попадает). Результат каждого прогона записывайте через `record.py`.

Порядок бесплатных: asr → voice-clean → stress → tts-local → edit → text-check. Тест edit использует слова из asr и чистую запись из voice-clean.

## Содержание
- Подготовка: запись эксперта
- asr · voice-clean · stress · tts-local · edit · text-check (бесплатно)
- tts-cloud · asr-cloud · avatar · clips (платно)
- Как ставить оценки 1–5

## Подготовка: запись эксперта
1. Прочитать вслух `assets/inputs/script_ru.txt` (≈45–60 с) обычным темпом, как для ролика: телефон в 20–30 см, комната без эха. Оговорки не исправлять — так ближе к реальной съёмке.
2. Отдельно записать 15 с свободной речи — образец голоса для клона в tts-local и tts-cloud.
3. Сохранить в `bench/runs/rec/<тестировщик>/script.<ext>` и `voice_sample.<ext>`.
Если запись сделал другой человек, в `--note` укажите, чей это голос. Без письменного согласия владельца голоса клон не делаем.

## asr — распознавание
```
python skills/kp-bench/scripts/asr_run.py --engine gigaam --audio bench/runs/rec/<t>/script.m4a --out bench/runs/asr/<t>
python skills/kp-bench/scripts/asr_run.py --engine faster-whisper --audio ... --out bench/runs/asr/<t>
python skills/kp-bench/scripts/asr_run.py --engine whisperx --audio ... --out bench/runs/asr/<t>      # в .venv-whisperx
python skills/kp-bench/scripts/wer.py --ref skills/kp-bench/assets/inputs/script_ru_spoken.txt --hyp bench/runs/asr/<t>/*.txt
```
Метрики: `wer`, `cer` из wer.py; `run_s`, `word_timestamps` из `<engine>.run.json`. Глазами проверьте: «Reels», «CRM», «Telegram», «ЗАМОК», числа — как записаны. Если тестировщик читал с оговорками, поправьте эталон под фактически сказанное и отметьте это в `--note`.

## voice-clean — очистка записи
Вариант dfn-chain:
```
ffmpeg -i script.m4a -ac 1 -ar 48000 rec48.wav
deepFilter rec48.wav --output-dir bench/runs/clean/<t>
python skills/kp-bench/scripts/loudness.py bench/runs/clean/<t>/rec48_DeepFilterNet3.wav --normalize bench/runs/clean/<t>/dfn_norm.wav
auto-editor bench/runs/clean/<t>/dfn_norm.wav --edit audio:-19dB --margin 0.2sec
```
(Имя файла после deepFilter — проверьте в папке.)
Вариант ffmpeg-only:
```
ffmpeg -i rec48.wav -af "afftdn=nf=-25,silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-40dB" ff_clean.wav
python skills/kp-bench/scripts/loudness.py ff_clean.wav --normalize ff_norm.wav
```
Метрики: `lufs` и `true_peak` — из второй строки loudness.py; `cut_s` — разница длительностей до и после; `quality` — на слух: нет ли «металла», не съедены ли концы слов.

## stress — нормализация и ударения
```
python skills/kp-bench/scripts/stress_run.py --variant rutextnorm-silero --out bench/runs/stress/<t>
python skills/kp-bench/scripts/stress_run.py --variant rutextnorm-ruaccent --out bench/runs/stress/<t>
```
`errors` — число строк из 10, где есть ошибка: ударение (зАмок / замОк по смыслу, мУка / мукА), всё/все, число не в том падеже, «₽» и «%» не словами, латиница не прочитана.

## tts-local — синтез голоса
1. Текст: `script_ru.txt` → лучший вариант из stress (через stress_run.py со своим `--input`, или вручную по его выводу).
2. Qwen3-TTS — код из install.md, раздел 5. Образец — `voice_sample` и его расшифровка из asr. Вариант qwen3-tts-stress — тот же код с моделью LoRA и ударениями U+0301.
3. Edge TTS — по install.md.
4. Обратная проверка: `asr_run.py --engine gigaam` по каждому синтезу, затем `wer.py` против `script_ru_spoken.txt` → `back_wer`.
5. Слепое прослушивание: `blind.py make bench/runs/tts/<t> bench/runs/blind-tts/<t>`, оценить 1–5, затем `blind.py reveal ... --scores "A=4,B=3"`. Лучше, если оценивает тот, кто не запускал синтез.
`stress_err` — число слов с неверным ударением на слух.
Без NVIDIA варианты Qwen записывайте с `--verdict fail --note "нет GPU"`, чтобы было видно, что тест не проводился.

## edit — движок монтажа
Вход: чистая запись из voice-clean и слова из asr лучшего движка.
```
python skills/kp-bench/scripts/captions.py bench/runs/asr/<t>/gigaam.words.json --words-per-line 3
```
Remotion берёт `.captions.json`, HyperFrames — `.srt` или те же слова. Задача для агента в каждом движке одна и та же:
> Сделай вертикальный ролик 1080×1920, 30 fps: фон — однотонный, звук — dfn_norm.wav, субтитры по словам с подсветкой текущего слова, шрифт с кириллицей (Montserrat или Inter), субтитры не ниже 1440 px и не выше 270 px от краёв, по бокам не ближе 108 px.
Метрики: `cyrillic_ok` (нет квадратиков и обрезанных букв), `captions_sync` (1–5, на глаз), `safe_zone_ok` (наложите сетку: сверху 14 %, снизу 25 %, по бокам 10 %), `render_s` — время рендера; минуты на установку — `--setup-min`.

## text-check — проверщики текста
Вход `assets/inputs/post_ru.md`, ключ `post_ru_key.json` (16 проблем). Каждый проверщик — на исходном файле:
- humanizer-ru: `humanizer-markers --scan skills/kp-bench/assets/inputs/post_ru.md`
- ru-lint: `python <путь>/ru_lint.py skills/kp-bench/assets/inputs/post_ru.md` (путь — install.md, раздел 8)
- ru-text: в агенте «Оцени этот текст по ru-text и перечисли все проблемы»
Сверьте вывод с ключом: `found` — сколько id из ключа названо (по смыслу, не дословно); `false_pos` — замечания к нормальному тексту. Ключ проверщикам не показывать.

## Платные тесты
Запускаются только после «да» владельца бюджета. Перед каждым:
1. Посчитать стоимость по `site/data/bench.json` (поле `test_cost`) и показать её.
2. Получить явное «да» с суммой. Без него не генерировать.
3. После прогона записать фактическую сумму в `--cost` и `--currency`.

**tts-cloud:** тот же текст, что в tts-local. ElevenLabs v4 — готовый русский голос и клон по `voice_sample` (клон — тариф Starter и выше, проверить). Yandex SpeechKit v3 — голос на выбор. Дальше — как в tts-local, шаги 4–5. `cost_per_min` — цена минуты речи по тарифу.

**asr-cloud:** та же запись, что в asr. ElevenLabs Scribe и Yandex SpeechKit (распознавание). Текст сохранить в `bench/runs/asr/<t>/<variant>.txt`, затем wer.py.

**avatar:** 3–5 фото эксперта и лучшая озвучка. Ролик 15 с, 9:16. HeyGen — сначала на бесплатном плане (3 видео, водяной знак). Higgsfield — от тарифа Starter. Метрики `lipsync`, `likeness` — 1–5, вслепую, если оценивает не автор.

**clips:** один промпт во все модели, 5 с, 9:16, 720p:
> Вертикальный кадр, утро, рабочий стол эксперта у окна: ноутбук, чашка кофе, блокнот с надписью от руки. Камера медленно наезжает. Тёплый естественный свет, без людей в кадре, без текста на экране.
Через fal MCP или сайт fal. `prompt_fit` и `quality` — 1–5, вслепую через blind.py.

## Оценки 1–5
1 — непригодно; 2 — заметные дефекты, клиенту не показать; 3 — годится с правками; 4 — можно публиковать; 5 — не отличить от ручной работы или живого голоса.
Вердикт `--verdict`: ok — годится; partial — с оговорками (в `--note` какими); no — не годится; fail — не запустилось (в `--note` ошибка).
