# 07. Голос на русском: запись, обработка, TTS и клон (на 27.11.2026)

Метки: [П] — открыт первоисточник; [1И] — один вторичный источник; [З] — только заголовок или выдача поиска.
Цена за минуту — оценка: ~1000 символов русского текста на 1 минуту речи; кириллица в UTF-8 занимает 2 байта на символ.

## Перепроверка того, что уже было известно

| Утверждение | Статус | Источник |
|---|---|---|
| GigaAM v3, MIT, пословные таймкоды | Подтверждено. v3 вышла в 2025/11, `word_timestamps=True` добавили в 2026/04. В 2026/06 вышла GigaAM Multilingual на 70+ языков. Против Whisper есть только сравнение LLM-судьёй, 70:30 в пользу e2e-моделей GigaAM; цифр WER в README нет. Для записей длиннее 25 с нужны `transcribe_longform`, pyannote и HF-токен | [П] github.com/salute-developers/GigaAM |
| SpeechKit ≈0,65 ₽ за 1000 символов | Подтверждено для API v3 `general`: 0,1626 ₽ за единицу в 250 символов, это 0,65 ₽ за 1000 символов. API v1 стоит 1342 ₽ за 1 млн символов, то есть 1,34 ₽ за 1000 | [П] aistudio.yandex.ru/ru/docs/speechkit/pricing |
| SaluteSpeech закрывается 30.11.2026, переезд на cloud.ru | Подтверждено. В changelog от 24.11.2026: пакеты не продаются с 01.11.2026, постоплата работает до 30.11.2026, «после этой даты запросы к SaluteSpeech API обрабатываться не будут», модели ASR и TTS теперь на cloud.ru. Физлиц отключили раньше, 15.07.2026 | [П] developers.sber.ru/docs/ru/salutespeech/changelog/latest; [1И] reymer.ai |
| Silero CC BY-NC | Подтверждено. Основные модели под CC BY-NC 4.0; исключение — `base`-модели для СНГ под MIT. Последняя русская модель — `v5_6_ru` | [П] github.com/snakers4/silero-models |
| Qwen3-TTS: Apache-2.0, русский, клон по ~3 с, ошибки ударений | Подтверждено. 10 языков, среди них русский; размеры 0.6B и 1.7B; релиз 22.01.2026. На Хабре 26.11.2026 описали LoRA для ударений (см. раздел 3) | [П] github.com/QwenLM/Qwen3-TTS; [П] habr.com/ru/articles/989244, /1112584 |
| elevenlabs-mcp архивирован 20.08.2026; есть elevenlabs/skills и хостируемый MCP | Подтверждено. Замена — `https://api.elevenlabs.io/v1/mcp` с OAuth; в `mcp.json` репозитория skills указан `api.us.elevenlabs.io/v1/mcp`. В skills 12 навыков, MIT, 512 звёзд | [П] github.com/elevenlabs/elevenlabs-mcp, github.com/elevenlabs/skills |
| **Новое:** в ElevenLabs вышла Eleven v4 | 28.09.2026 вышли `eleven_v4` и `eleven_v4_turbo`: 90+ языков, русский поддерживается. В документации лимит 100 000 символов, во вторичном источнике — 10 000 | [П] elevenlabs.io/docs/overview/models; [1И] eesel.ai |
| **Новое:** у OpenAI TTS есть дата отключения | `tts-1`, `tts-1-hd` и `gpt-4o-mini-tts` устарели и отключаются 06.01.2027. Замена — `gpt-realtime-2.1-mini` через Realtime API, `/v1/audio/speech` её не поддерживает | [П] developers.openai.com/api/docs/guides/text-to-speech |

## 1. Запись своим голосом и обработка

**Микрофоны.** Подборка Engadget (обновлена 16.12.2025) [П]:
- беспроводные: DJI Mic 3, RØDE Wireless GO Gen 3 (32-bit float, своя память), бюджетный BOYA Mini 2 (до $50);
- проводные петлички: Sennheiser Pro XS Lav с USB-C подключается к телефону напрямую;
- USB-микрофоны: Shure MV7+ — динамический, подходит для неподготовленной комнаты; RØDE NT-USB Mini — конденсаторный, сильнее ловит шум комнаты.

Причины плохого звука в Reels по postium.ru: шумное место, микрофон далеко от источника, грязный микрофон телефона. В редакторе Instagram есть встроенное «Улучшение голоса» 0–100 (статья от 08.08.2024) [1И].

**Шумоподавление и восстановление речи:**
- **DeepFilterNet** — MIT или Apache-2.0, это относится и к весам; около 5,0k звёзд. CLI `deep-filter file.wav` принимает только WAV 48 кГц. Есть real-time-версия и LADSPA-плагин для PipeWire. Работает локально на CPU [П].
- **RNNoise** — в ffmpeg есть фильтры `arnndn` (RNNoise, нужен файл модели), `afftdn` (FFT-шумодав, по умолчанию nr 12 dB), `loudnorm` и `silenceremove`. Список фильтров открыт, но подробно прочитано описание только `afftdn` [П, частично].
- **Resemble Enhance** — MIT, около 2,5k звёзд: шумоподавление плюс восстановление полосы. Требования к GPU в README не указаны, коммитов всего 13 [П].
- **Adobe Podcast Enhance Speech v2** (февраль 2025): два ползунка — сила обработки и уровень фона. В Premium до 4 часов в день и файлы до 1 ГБ, план Firefly Pro. Лимиты бесплатного тарифа не указаны, API на странице нет [П].
- **ElevenLabs Voice Isolator** — $0,12/мин по API; есть навык `voice-isolator` в elevenlabs/skills [П].

**Громкость.** Официальных LUFS-целей для соцвидео платформы не публикуют. Наблюдаемое значение для YouTube — около −14 LUFS при −1 dBTP; YouTube только приглушает громкие ролики и не поднимает тихие. У TikTok и Meta адаптивная громкость. Практическая цель: −14 LUFS, true peak −1 dBTP; итог проверять измерителем BS.1770 после lossy-кодирования [1И forasoft.com, 2026]. Цифра −16 LUFS в этом источнике не встретилась.

**Паузы и слова-паразиты.**
- **auto-editor** — Unlicense, около 5,7k звёзд, написан на Nim. Режет тишину по громкости и экспортирует монтаж в Premiere, Resolve, FCP, Shotcut и Kdenlive [П].
- Готового открытого инструмента, который удаляет «эээ / ну / как бы» в русском, не нашёл. Есть облачные: Kapwing Smart Cut, VEED, Filmora [З].
- Рабочая схема: ASR с пословными таймкодами (GigaAM v3 или WhisperX) → список паразитов → вырезать отрезки через ffmpeg. Сохраняет ли конкретная ASR-модель «эээ» в расшифровке, нужно проверить на своих записях: в источниках этого нет.

**Телесуфлёр.** Textream — MIT, около 4,1k звёзд, macOS 15+ и iOS-компаньон. Режим Word Tracking построен на распознавании речи macOS, работа офлайн не гарантирована, поддержка русского не указана [П]. Другие варианты: autocue и smart-teleprompter на GitHub, VoicePrompter [З].

**Скиллы и MCP для записи.**
- Из подтверждённого только `voice-isolator` в elevenlabs/skills (требуется `ELEVENLABS_API_KEY`) [П].
- Отдельных скиллов для «шумодав + loudnorm + вырезка пауз» не нашёл. Цепочка ffmpeg + DeepFilterNet + auto-editor — это CLI-команды, их можно звать из любого агента через shell.

## 2. Генерация голоса на русском

**ElevenLabs** [П docs/pricing]
- Модели с русским: v4, v4 Turbo, v3, v3 Conversational, Multilingual v2, Flash v2.5. Flash v2 — только английский.
- API: v4, v3 и Multilingual v2 стоят $0,08 за 1000 символов; v4 Turbo, v3 Conversational и Flash — $0,04.
- Тарифы: Starter $6, Creator $22, Pro $99. Бесплатный план — только для личного использования, коммерческая лицензия начинается со Starter [1И vc.ru, 05.07.2026].
- SSML в v3 и v4 не поддерживается [1И eesel]. Управление — аудиотеги в квадратных скобках.
- Ударения: в v4 нет разметки. Ударение правят переформулировкой, буквой «ё» и прослушиванием; заглавная гласная («зАмок») срабатывает «почти всегда», но не на каждом голосе [1И Хабр/oplatym, 22.10.2026, рекламная статья; 1И dtf.ru, 04.11]. Числа лучше писать словами, англицизмы — так, как они звучат [1И dtf].
- Проблемы на практике: теги иногда пропускаются или зачитываются; голоса, созданные под английский, на русском шепелявят; на длинных текстах плавает темп [1И dtf].
- Клон: Instant — 1–2 минуты образца, Professional — от 30 минут и только своего голоса [1И tproger 16.11.2026; 1И oplatym].
- В v4 PVC поддерживается, но выкатывается не всем сразу. v4 точнее воспроизводит и дефекты записи, поэтому старые клоны нужно перепроверить [1И eesel].
- Доступ из РФ: elevenlabs.io перенаправляет на «Access restricted» [1И tproger]. Платят через посредников с комиссией от +350 ₽ до ~13% [1И vc.ru], либо пользуются российскими обёртками (Umnik AI и др.) [1И].
- Пословные таймкоды: эндпоинт `with-timestamps` возвращает посимвольные `alignment` и `normalized_alignment` [П].

**Yandex SpeechKit** [П]
- Цены: v3 — 0,1626 ₽ за 250 символов (~0,65 ₽/мин); модель `livetts` — 0,25 ₽; v1 — 1342 ₽ за 1 млн символов.
- Разметка для русского в v3 и v1: `+` перед ударной гласной, паузы `sil<[t]>` (до 7000 мс), `<[small]>`, акцент `**слово**`, фонемы `[[...]]`. Разметка — подсказка синтезу, а не точная команда.
- Brand Voice Lite (с 11.07.2025): 20–40 минут записи диктора, модель готова за 7 дней, нужно согласие диктора. Цена в анонсе не указана [П блог].
- Brand Voice Premium — по заявке для бизнеса [П прайс]. Частному лицу, по оценке tproger, не подходит [1И].
- MCP: `theYahia/yandex-speechkit-mcp` (MIT, 0 звёзд) архивирован 18.08.2026, разработка перенесена в `theYahia/YaAll` [П].

**cloud.ru (бывший SaluteSpeech)**
- Сбер объявил, что модели ASR и TTS доступны на cloud.ru [П changelog].
- В описании услуги Foundation Models cloud.ru (версия 250922) есть только ASR с оплатой за секунды; TTS там не упоминается [П PDF]. Цены и условия TTS на cloud.ru подтвердить не удалось.
- SSML у SaluteSpeech был [З developers.sber.ru].

**MTS AI / MWS, T-Bank VoiceKit:** есть только выдача поиска (toolfox.ru) [З]. Актуальных цен и данных о клоне не нашёл.

**Открытые модели**
- **Qwen3-TTS** — Apache-2.0, 14,4k звёзд, клон по ~3 с [П].
  - Автор Хабра (27.01.2026) пишет: азиатский акцент, ошибки в йотированных словах, слабые числа и даты в клонах, уступает моделям OpenAI и Google [П].
  - LoRA `siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf` (Apache-2.0): ударение ставится знаком U+0301 после гласной; размеченное против словаря ударение выполняется в 96% случаев против 17% без адаптера. Оценка детектором, а не людьми [П Хабр 26.11.2026; П HF].
  - Оговорка из карточки адаптера: у части данных нет лицензии, детектор обучен в том числе на аудио Silero (NC). Перед коммерческим использованием это нужно проверить [П].
  - Железо: работает на RTX 3060 Laptop 6 ГБ; на CPU нужно около 7 ГБ RAM [П Хабр].
- **F5-TTS** — код MIT, веса CC BY-NC из-за датасета Emilia, 15,6k звёзд [П].
  - `Misha24-10/F5-TTS_RUSSIAN`: CC BY-NC 4.0, около 5000 часов RU/EN, ударение `+` перед гласной, рекомендуется RUAccent [П].
  - `ESpeech/ESpeech-TTS-1_SFT-256K`: в карточке Apache-2.0, архитектура F5-TTS, RUAccent встроен, образец до 12 с, работает на CPU и CUDA. Базовые веса в карточке не названы, поэтому лицензионную чистоту нужно проверить [П].
- **XTTS-v2** — лицензия CPML разрешает только некоммерческое использование модели и её выходов. Так ответил мейнтейнер форка idiap (31.01.2025). Русский поддерживается, клон по ~6 с [П]. Coqui закрылась [З analyticsindiamag].
- **Fish Speech / Fish Audio** [П]
  - Новый флагман — Drama 3 (35B-A3B). Предыдущее поколение S2-Pro: клон по 10–30 с, запускается на потребительском GPU.
  - Лицензии: Fish Audio Community License; для S2-Pro — Research License. Русский в README не назван.
  - API: s2.1-pro — $15 за 1 млн байт (~$0,03/мин для кириллицы); drama-3 — $50, по акции $10 до 30.11.2026; s1 отключают 31.12.2026. Список языков на странице цен не приведён.
  - Сайт из РФ открывается, есть 8000 бесплатных кредитов в месяц [1И tproger].
- **CosyVoice** — Fun-CosyVoice 3.0 (0.5B, 2025/12), Apache-2.0, русский среди 9 языков, 24,2k звёзд [П].
- **Chatterbox Multilingual V3** — MIT, русский среди 23+ языков. Неотключаемый водяной знак Perth на каждом файле. Nano работает на CPU. 27,1k звёзд [П]. По tproger, проект «заморожен с августа 2026» [1И, на странице репозитория не подтвердил].
- **Silero v5_6_ru** — автоударения, омографы, SSML, очень быстрая; CC BY-NC [П].
- **edge-tts** — GPL-3.0 (файл лицензии), 12,6k звёзд. Пишет субтитры (`--write-subtitles`). Свободный SSML убран: доступны только rate, volume и pitch [П]. Это неофициальный клиент сервиса Microsoft Edge; условия использования на странице не описаны. Русские голоса на странице не показаны, потому что список обрезан.

**Облачные API, кроме ElevenLabs**
- **MiniMax Speech 2.8 HD** (через fal) — $0,10 за 1000 символов. Есть `language_boost` для Russian, `pronunciation_dict`, теги вроде (laughs), паузы `<#x#>` [П fal].
  - Клон: плата при первом синтезе этим голосом; клон удаляется, если за 168 ч им не синтезировали. Требования к длине образца не указаны [П].
  - MiniMax-MCP: MIT, 1,6k звёзд, инструменты `text_to_audio`, `voice_clone`, `voice_design` [П].
- **Google Gemini TTS** — `gemini-3.8-flash-tts` и `-flash-lite-tts`, русский поддерживается [П].
  - Voice replication: клон по эталонной записи плюс запись согласия, ID голоса хранится 1 год.
  - Управление стилем: поле `style` и инлайн-теги в угловых скобках.
  - Цена TTS на странице прайса не найдена [П, без цены]. Доступ из РФ через AI Studio, ограничений в статье нет [1И t-j.ru].
- **OpenAI TTS** — 13 голосов, оптимизированы под английский, русский поддерживается [П].
  - Custom voices — по записи согласия, условия в отдельном руководстве.
  - Отключение 06.01.2027, поэтому для нового конвейера не подходит.
- **Cartesia Sonic 3.6** — 44 языка, русский заявлен; цены в долларах [1И t-j.ru]. Сайт из РФ не открылся, ответ 403 [1И tproger].

**Бенчмарки.** Artificial Analysis (на 13.11.2026): первое место у Eleven v4 и v4 Turbo, второе у Qwen-Audio-3.1. Отдельного рейтинга русской речи нет [1И t-j.ru, 16.11.2026].

## 3. Ударения и нормализация текста

| Инструмент | Что делает | Лицензия | Статус |
|---|---|---|---|
| ruaccent | Ударения и омографы; модели tiny–turbo3.1; GPU через onnxruntime-gpu | MIT | [П] 207★ |
| silero-stress | Ударения, омографы, буква ё. 100% на ~4 млн известных словоформ, около 94% на ~2,2 тыс. омографов, 60–70% на неизвестных словах. CPU с AVX | MIT | [П] 162★ |
| rutextnorm 2.1.0 (13.06.2026) | Числа, даты, деньги, единицы, проценты, аббревиатуры, латиница с согласованием падежей. Без зависимостей, ~0,17 мс на предложение. `flag_uncertain()` отправляет спорные места в LLM | MIT | [П] PyPI |
| russian-tts-normalization 1.0.2 | Один файл на регулярках; «Google» → «гугл», «GPS» → «джи пи эс» | MIT (словарь из NeMo, Apache-2.0) | [П], архивирован 13.06.2026 |
| num2words | Числа словами. Пример: нормализатор MWS AI для MMS-TTS построен на num2words плюс правила | — | [1И Хабр 27.02.2026] |

Форматы разметки у разных движков:
- SpeechKit, Silero, F5-RU, ESpeech: `+` перед гласной.
- LoRA для Qwen3-TTS: U+0301 после гласной; `+` из RUAccent нужно сконвертировать.
- ElevenLabs v4: разметки нет, правят переформулировкой, буквой «ё» и заглавной гласной (ненадёжно).
- MiniMax: словарь произношений `pronunciation_dict`.
- SpeechKit: фонемы `[[...]]`.

Практика из статей: числа писать словами или пропускать текст через LLM-нормализатор, англицизмы писать так, как они звучат, вручную держать список «рискованных» слов (у автора Хабра 81 слово) [1И].

## 4. Клон голоса эксперта: право и риски

**РФ**
- Закон 243-ФЗ от 26.07.2026 «О поддержке развития технологий ИИ» [1И sostav.ru, 03.08.2026]:
  - основная часть действует с 01.09.2026, положения о маркировке — с 01.03.2027;
  - автор не обязан ставить пометку; обязанность у площадок с суточной аудиторией больше 500 тыс. — дать пользователю инструмент для пометки;
  - закон охватывает аудио и визуальный контент от фундаментальных моделей, текст не регулирует;
  - штрафов нет; законопроект о штрафах для юрлиц отклонён 10.06.2026.
- Проект о принудительной маркировке пользователями обсуждался в августе 2026, это ещё не закон [1И CNews, 18.08.2026].
- Охрана голоса: законопроект № 718834-8 (ст. 152.3 ГК) не принят на октябрь 2026, правительство его не поддержало [1И kadr-ai, 14.10.2026; 1И oplatym].
- Чужой голос защищён и без отдельного закона: охрана исполнений, биометрические персональные данные, защита чести; обман с помощью клона квалифицируется по ст. 159 УК [1И kadr-ai].
- Свой голос эксперт может клонировать свободно. Если голос клонирует подрядчик, нужен письменный договор с прямым разрешением синтеза [1И].

**Площадки**
- **YouTube:** пометка «Использование ИИ» нужна для реалистичного контента, где человек говорит то, чего не говорил. Клон собственного голоса для закадра или дубляжа прямо назван незначительным изменением, которое отмечать не нужно [П support.google.com/youtube/answer/14328491].
- **TikTok:** нужно помечать весь реалистичный ИИ-контент, включая «AI-generated speech» реального человека. Метка может ставиться автоматически по C2PA, и снять её нельзя [П support.tiktok.com].
- Политики Meta (Reels, Threads) и Telegram не открывал.

**Требования сервисов к согласию**
- Yandex: согласие диктора [П].
- Gemini: запись согласия [П].
- OpenAI: запись согласия [П].
- ElevenLabs PVC: только свой голос [1И].
- Chatterbox: водяной знак ставится на каждый файл [П].

**Риски**
- Клон утечёт и станет инструментом мошенничества. Рекомендация kadr-ai: не публиковать длинные чистые записи без необходимости [1И].
- Некоммерческие лицензии (Silero, F5 base, XTTS) и неясная лицензия данных адаптера ударений для Qwen.
- Посредники для оплаты ElevenLabs: аккаунт и данные в серой зоне.

## 5. Синхронизация: озвучка → субтитры → липсинк

- **Таймкоды из TTS:**
  - ElevenLabs `with-timestamps` — посимвольно [П];
  - edge-tts — субтитры при синтезе [П];
  - у открытых моделей таймкодов на выходе в README не нашёл.
- **Таймкоды из ASR или выравнивания:**
  - GigaAM v3 `word_timestamps=True`, MIT [П];
  - WhisperX: BSD-2, 25,1k звёзд, выравнивание через wav2vec2. Русская модель выравнивания на странице прямо не названа, нужно проверить `DEFAULT_ALIGN_MODELS_HF` [П];
  - батчинг в Whisper отбрасывает пословные метки [1И Хабр 03.03.2026].
- **Липсинк:** LatentSync 1.6 (11.06.2025), Apache-2.0, около 18 ГБ VRAM (у версии 1.5 — 8 ГБ), аудиопризнаки берёт из Whisper; языковая независимость не заявлена [П].
- **Типовая связка по найденным источникам:** текст → нормализация и ударения → TTS (или запись эксперта → DeepFilterNet → loudnorm −14 LUFS) → GigaAM или WhisperX для слов с таймкодами → ASS/SRT-субтитры → LatentSync или облачный аватар. Описанную целиком такую связку для русского в одном источнике не нашёл; это сборка из частей.

## 6. Что считают лучшим по цене и качеству (отзывы)

- **ElevenLabs v4** — лидер по качеству и для русского. Минусы: оплата через посредников, нет разметки ударений, кредиты списываются за каждый дубль [1И Хабр oplatym, рекламная; 1И dtf; П Хабр 1112584].
- **Qwen3-TTS + LoRA ударений** — локальная бесплатная альтернатива на 6 ГБ GPU. Автор Хабра (26.11.2026) называет её заменой ElevenLabs для своей игры; языков 10 против 90+ у ElevenLabs [П].
- **SpeechKit** — дешёвый и легальный в РФ вариант с точной разметкой `+`, но клон только как Brand Voice для бизнеса от 20 минут записи [П].
- **Silero** — самый быстрый локальный вариант с автоударениями, но только некоммерческий [П].
- Рейтинги на dtf.ru и vc.ru — субъективные «личные тесты» с партнёрскими ссылками, ориентироваться на них не стоит [1И].
- Reddit и Telegram: релевантных свежих обсуждений по русскому TTS через поиск не нашёл; канал habr_ai — только агрегатор ссылок [З].

## Сравнение TTS

| Модель / сервис | Русский (ударения, ё, числа, англицизмы) | Клон (образец) | Лицензия для коммерции | Цена/мин (оценка) | API / MCP / скилл | Локально |
|---|---|---|---|---|---|---|
| ElevenLabs v4 / v4 Turbo | Лучший по отзывам; разметки ударений нет, числа писать словами, англицизмы читает непредсказуемо [1И] | IVC 1–2 мин; PVC от 30 мин, только свой голос | Платные тарифы, со Starter $6 | v4 ~$0,08; Turbo ~$0,04 | API; хостируемый MCP; elevenlabs/skills (MIT) | Нет |
| Yandex SpeechKit v3 | `+`, фонемы, паузы; бывают «проглоченные» окончания [1И dtf] | Brand Voice Lite: 20–40 мин, 7 дней | Да, договор Yandex Cloud | ~0,65 ₽ (v3) | API; MCP архивирован | Есть SpeechKit Hybrid для бизнеса [З] |
| SaluteSpeech → cloud.ru | SSML [З] | YourVoice [1И] | — | Не подтверждено | API Сбера отключается 30.11.2026 | Нет |
| Qwen3-TTS 1.7B (+ru-stress LoRA) | Акцент и ошибки в числах у клонов; с LoRA ударения 96% | ~3 с | Apache-2.0; у LoRA есть данные без лицензии | Бесплатно (свой GPU) | Нет официального MCP | Да, от 6 ГБ VRAM |
| F5-TTS RU (Misha24-10) | `+`, RUAccent | Эталонный аудиоклип | **Нет** (CC BY-NC) | — | — | Да |
| ESpeech-TTS-1 (F5) | RUAccent встроен | ≤12 с | Apache-2.0 в карточке, происхождение весов проверить | — | Gradio | Да, CPU и CUDA |
| XTTS-v2 | Русский есть | ~6 с | **Нет** (CPML) | — | — | Да |
| Fish Audio S2.1-pro / Drama 3 | Русский не подтверждён | 10–30 с (S2-Pro) | API — да; веса под Community/Research License | ~$0,03 (s2.1-pro) | API | S2-Pro на потребительском GPU |
| Fun-CosyVoice 3.0 0.5B | Русский среди 9 языков; качество RU не проверено | Да (zero-shot) | Apache-2.0 | — | — | Да |
| Chatterbox Multilingual V3 | Русский среди 23 языков | ~10 с (по примеру) | MIT, водяной знак Perth | — | — | Да; Nano на CPU |
| Silero v5_6_ru | Автоударения, омографы, SSML | Нет | **Нет** (CC BY-NC) | — | — | Да, CPU |
| MiniMax Speech 2.8 HD | `language_boost` для RU, словарь произношений | Да, длина не указана | Платный API | ~$0,10 (fal) | API; MiniMax-MCP (MIT) | Нет |
| Gemini 3.8 Flash TTS | Русский есть; стиль и теги | Voice replication + запись согласия | Платный API | Не найдено | API | Нет |
| OpenAI gpt-4o-mini-tts | Русский есть, голоса под английский | Custom voice по согласию | — | — | Отключение 06.01.2027 | Нет |
| edge-tts | Голоса Microsoft; только rate, volume, pitch | Нет | GPL-3.0, неофициальный клиент; условия сервиса неясны | Бесплатно | CLI, субтитры | Нет (облако MS) |

## Что это значит для конвейера

**Шаг 8 — генерация голоса**
- Приоритет — запись эксперта. На случай TTS держать два движка:
  - облачный: ElevenLabs v4 по API или хостируемому MCP, с клоном IVC, а PVC только по записи самого эксперта; для РФ-юрлица запасной вариант — SpeechKit v3;
  - локальный: Qwen3-TTS 1.7B + LoRA ru-stress на GPU от 6 ГБ.
- Перед TTS отдельный подшаг «текст для озвучки»:
  1. rutextnorm для чисел, дат и аббревиатур (спорные места через `flag_uncertain` отправить в LLM);
  2. silero-stress или ruaccent для ударений и ё;
  3. конвертер разметки под движок: `+` для SpeechKit, U+0301 для Qwen-LoRA, переформулировка или «ё» для ElevenLabs;
  4. ручной словарь «рискованных» слов эксперта.
- Все эти шаги — Python CLI, поэтому одинаково работают из Claude Code, Codex, OpenCode, Kimi и DeepSeek-агентов. MCP для этого не нужен.
- Не брать для коммерции: Silero, F5 (Misha24-10), XTTS-v2. Не брать OpenAI TTS (отключение 06.01.2027) и SaluteSpeech (отключение 30.11.2026).

**Шаг 10 — монтаж**
- Запись эксперта: DeepFilterNet (48 кГц WAV) или ElevenLabs Voice Isolator → ffmpeg `loudnorm` до −14 LUFS / −1 dBTP → auto-editor для пауз.
- Слова-паразиты: GigaAM v3 с пословными таймкодами → вырезка по списку. Открытого готового инструмента для русского нет, писать свой скрипт.
- Субтитры: пословно из GigaAM или WhisperX, для TTS — из `with-timestamps` ElevenLabs.
- Липсинк: LatentSync 1.6 при наличии около 18 ГБ VRAM.

**Шаг 11 — проверка**
- Автопроверка озвучки: обратно распознать GigaAM и сравнить с исходным текстом (пропуски, числа, англицизмы).
- Отдельно прослушивать слова из словаря ударений.
- Измерить LUFS и true peak после финального кодирования.
- Юридический чек-лист:
  - есть письменное согласие эксперта на синтез его голоса;
  - TikTok: метка AI-generated, если голос синтетический и реалистичный;
  - YouTube: клон своего голоса для закадра помечать не нужно;
  - лицензия выбранной модели разрешает коммерцию;
  - водяной знак Chatterbox учтён, если модель используется.

## Источники

- GigaAM — https://github.com/salute-developers/GigaAM [П]
- Тарифы SpeechKit — https://aistudio.yandex.ru/ru/docs/speechkit/pricing [П]
- Разметка SpeechKit — https://aistudio.yandex.ru/docs/ru/speechkit/tts/markup/tts-markup [П]
- Brand Voice Lite — https://yandex.cloud/ru/blog/brand-voice-lite [П]; https://kod.ru/yandex-b2b-tech-brand-voice-lite [1И]
- Changelog SaluteSpeech — https://developers.sber.ru/docs/ru/salutespeech/changelog/latest [П]; https://reymer.ai/tools/salutespeech [1И]; https://tospeech.ru/posts/salute-speech-api [1И]; https://salutespeechai.ru/ [1И]
- Foundation Models cloud.ru — https://cdn.cloud.ru/docs/legal/contracts/terms-of-service/evolution/future-version/description-foundation-models.pdf [П]
- ElevenLabs: модели https://elevenlabs.io/docs/overview/models [П]; цены API https://elevenlabs.io/pricing/api [П]; with-timestamps https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps [П]; https://github.com/elevenlabs/skills [П]; https://github.com/elevenlabs/elevenlabs-mcp [П]; https://www.eesel.ai/blog/eleven-v4 [1И]; https://vc.ru/services/3012451-elevenlabs-kak-polzovatsya-v-rossii [1И]
- https://habr.com/ru/companies/oplatym/articles/1098128/ [1И, рекламная]; https://dtf.ru/howto/5391895-elevenlabs-neurosset-kak-ispolzovat-v4-dlya-ozvuchki-teksta-na-russkom [1И]
- Бенчмарки — https://t-j.ru/kakaia-neiroset-luchshe-ozvuchivaet-tekst/ [1И]
- Клонирование голоса, цены и доступ — https://tproger.ru/articles/nejroseti-dlya-klonirovaniya-golosa-v-2026-godu-ceny-i-dostup-iz [1И]
- https://habr.com/ru/articles/1018962 [1И]; https://dtf.ru/craft/5188069-neyroseti-dlya-sinteza-golosa [1И]
- Qwen3-TTS — https://github.com/QwenLM/Qwen3-TTS [П]; https://habr.com/ru/articles/989244/ [П]; https://habr.com/ru/articles/1112584/ [П]; https://huggingface.co/siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf [П]
- F5-TTS — https://github.com/SWivid/F5-TTS [П]; https://huggingface.co/Misha24-10/F5-TTS_RUSSIAN [П]; https://huggingface.co/ESpeech/ESpeech-TTS-1_SFT-256K [П]
- XTTS-v2 — https://huggingface.co/coqui/XTTS-v2 [П]; https://github.com/coqui-ai/TTS/discussions/4145 [П]; https://analyticsindiamag.com/deep-tech/conversational-ai-startup-coqui-shuts-down/ [З]
- Fish Audio — https://github.com/fishaudio/fish-speech [П]; https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits [П]
- CosyVoice — https://github.com/FunAudioLLM/CosyVoice [П]
- Chatterbox — https://github.com/resemble-ai/chatterbox [П]
- Silero — https://github.com/snakers4/silero-models [П]; https://github.com/snakers4/silero-stress [П]
- ruaccent — https://github.com/Den4ikAI/ruaccent [П]
- Нормализаторы — https://pypi.org/project/rutextnorm/ [П]; https://pypi.org/project/russian-tts-normalization/ [П]; https://habr.com/ru/articles/1004144 [1И]
- edge-tts — https://github.com/rany2/edge-tts [П]
- MiniMax — https://fal.ai/models/fal-ai/minimax/speech-2.8-hd/llms.txt [П]; https://platform.minimax.io/docs/api-reference/voice-cloning-intro [П]; https://github.com/MiniMax-AI/MiniMax-MCP [П]
- Gemini TTS — https://ai.google.dev/gemini-api/docs/speech-generation [П]; https://aistudio.google.com/docs/pricing [П, цены TTS нет]
- OpenAI TTS — https://developers.openai.com/api/docs/guides/text-to-speech [П]
- yandex-speechkit-mcp — https://github.com/theYahia/yandex-speechkit-mcp [П]
- Обработка звука — https://github.com/Rikorose/DeepFilterNet [П]; https://github.com/resemble-ai/resemble-enhance [П]; https://podcast.adobe.com/en/guides/latest-updates [П]; https://ffmpeg.org/ffmpeg-filters.html [П, частично]
- auto-editor — https://github.com/WyattBlue/auto-editor [П]
- Громкость — https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026 [1И]
- Микрофоны — https://www.engadget.com/best-mobile-microphones-for-recording-with-a-phone-154536629.html [П]
- «Улучшение голоса» в Reels — https://postium.ru/uluchshenie-zvuka-reels/ [1И]
- Телесуфлёр — https://github.com/f/textream [П]
- Синхронизация — https://github.com/m-bain/whisperX [П]; https://github.com/bytedance/LatentSync [П]; https://habr.com/en/articles/1006060 [1И]
- Маркировка ИИ — https://www.sostav.ru/blogs/289407/99420 [1И]; https://www.cnews.ru/news/top/2026-08-18_polzovatelej_mogut_obyazat [1И]
- Клонирование голоса и закон — https://kadr-ai.ru/blog/klonirovanie-golosa-neyrosetyu [1И]
- Правила площадок — https://support.google.com/youtube/answer/14328491 [П]; https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content [П]
- Облачные сервисы удаления пауз — https://www.kapwing.com/ru/tools/smart-cut/filler-words [З]
- MTS AI / T-Bank VoiceKit — https://toolfox.ru/services/s/mts-ai-api [З]
