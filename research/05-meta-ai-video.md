# 05. Мета-обзор: как делают ИИ-видео и короткий контент с агентами (на 27.11.2026)

## Как читать

- **[П]** — проверено: страница открыта, факт взят из неё (первоисточник или профильная статья с датой).
- **[1И]** — один вторичный источник (блог, агрегатор, часто с коммерческим интересом), не перепроверен.
- **[З]** — источник найден только по заголовку в поиске, страница не открыта.
- **[ОЗ]** — общие знания до середины 2026, в этой сессии не перепроверялись. Перед использованием проверить.

Ограничения: Reddit, X и Telegram напрямую не открывались. linux.do на запросы ответил ошибкой и во втором запуске. Звёзды GitHub со страниц, открытых 27.11.2026; страница могла быть из кэша, поэтому у отдельных репо цифры расходятся с агрегаторами трендов (указано). Второй запуск (27.11.2026) доделал репозитории, русские сервисы, стоки, промпт-библиотеки и тренды. Многие англоязычные «сравнения» написаны продавцами (Pexo, Atlas Cloud, ReelMint и др.), и цифры в них противоречат друг другу.

---

## 0. Проверка тезиса «в основном используют Kimi и Claude»

**Вывод: тезис верен частично.** Для оркестрации видео агентом основной фон — Claude Code. Kimi используют в основном как дешёвую модель внутри Claude Code или Kimi Code. Codex — второй по частоте агент в README видеорепозиториев. Gemini CLI и OpenCode встречаются как совместимые агенты, но собственных видеонаработок у них почти нет. DeepSeek доминирует по общему объёму токенов, но в видеорепозиториях как оркестратор не появляется.

Факты:
- **Claude Code — агент по умолчанию в видеорепозиториях** [П]. HyperFrames даёт гайды для Claude Code, Codex, Cursor, Gemini CLI и Copilot, OpenCode указан среди standalone-скиллов ([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)). video-use называет Claude Code, Codex, Hermes и OpenClaw ([browser-use/video-use](https://github.com/browser-use/video-use)). Китайские video-clipforge и ai-video-workflow сделаны под Claude Code и Codex ([video-clipforge](https://github.com/Johnson-Jia/video-clipforge), [ai-video-workflow](https://github.com/kowloonzh/ai-video-workflow)).
- **Kimi как дешёвый мозг внутри Claude Code** [1И]. Есть инструкция: `ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic`, модель `kimi-k3[1m]`, плюс видеоскилл Pexo. Kimi K3 сам видео не генерирует, он планирует работу и вызывает скилл ([pexo.ai, 26.11.2026](https://pexo.ai/blog/make-videos-claude-code-kimi-k3-6789)). Источник — продавец скилла Pexo.
- **Разделение ролей между LLM для Seedance** [1И]. Kimi разбивает длинный сценарий на 10-секундные биты и ведёт каталог ассетов. Claude строит строгий JSON шотов (камера, свет, звук). GPT проверяет JSON ([Atlas Cloud, 07.08.2026](https://www.atlascloud.ai/blog/tips/seedance-2-5-json-prompts-workflow)). На YouTube есть ролик «Best AI for Seedance 2.0: Kimi K3 vs Claude» ([З](https://www.youtube.com/watch?v=0y5hy3wWnZQ)): тема «Kimi против Claude для промптов видео» действительно обсуждается.
- **Модели Kimi сейчас** [П/1И]:
  - Kimi K3: API с 16.07.2026, открытые веса с 27.07.2026. 2,8T параметров (104B активных), контекст 1M. Цена $3 / $15 за 1M токенов (вход/выход), кэш $0,30 ([morphllm](https://www.morphllm.com/kimi-k3)) [1И].
  - Kimi K3.1 Pro: анонс 23.10.2026, веса 04.11.2026. $2 / $10, кэш $0,20 ([cellcog](https://cellcog.ai/blog/kimi-k3-1-release-date/)) [1И].
  - `kimi-k2.7-code` закрыт для новых регистраций и будет отключён к концу декабря 2026 ([platform.kimi.com](https://platform.kimi.com/docs/guide/kimi-k2-7-code-quickstart.md)) [П].
- **Видеовход у Kimi есть** [П]:
  - Официальная документация: видео принимают `kimi-k3.1-pro` и `kimi-k3`. Файл загружается через Files API (`purpose="video"`) и передаётся как `video_url: ms://<file-id>`. Форматы mp4, mov, webm и др., рекомендованный максимум — 1080p. Видео режется на ключевые кадры, токены считаются динамически ([platform.kimi.ai](https://platform.kimi.ai/docs/guide/use-kimi-vision-model.md)).
  - Раньше у K2.5 видеовход был экспериментальным и работал только через официальный API, не в vLLM/SGLang ([HF Kimi-K2.5](https://huggingface.co/moonshotai/Kimi-k2.5)).
  - Kimi Code CLI (MIT, около 7,4k звёзд) принимает перетащенные в чат записи экрана и демо-ролики, умеет сабагенты, скиллы и MCP ([MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code)).
  - Для сравнения: у Claude видеовхода нет, видео подаётся кадрами [ОЗ]. Это одна из реальных причин брать Kimi или Gemini на шаг «посмотреть референс».
- **Почему Kimi** [1И]: цена ниже Opus в несколько раз, контекст 1M, родное зрение с видео, Anthropic-совместимый эндпоинт (Claude Code работает без переделок), открытые веса. Kimi K3.1 Pro по собственным замерам Moonshot близок к Opus 5.5 на Terminal-Bench 4.0 (65,7 против 66,4), но заметно слабее на Terminal-Bench Science (38,1 против 63,3) ([cellcog](https://cellcog.ai/blog/kimi-k3-1-release-date/)).
- **DeepSeek** [1И]: на OpenRouter за неделю с 09.11.2026 DeepSeek V4.1 Flash набрал 27,8% токенов (первое место). Claude Opus 5.5 — 3,3%, шестое место ([officechai](https://officechai.com/ai/these-are-the-top-ai-models-on-openrouter-by-number-of-tokens-november-2026/)). Это общий трафик, не видео. Kimi в топ-9 этой недели нет.
- **Gemini** — отдельная ниша [1И]. Gemini используют для анализа длинных роликов: OpenShorts требует Gemini для поиска моментов ([dev.to/reelmint](https://dev.to/reelmint/open-source-ai-shorts-generators-the-repos-worth-running-in-2026-2kcp)). Также есть генерация Gemini Omni 1.2 Flash ([ai-0.net](https://ai-0.net/blog/ai-video-image-news-november-2026)).

---

## 1. Типовые связки «от идеи до ролика»

### 1.1. Три семейства пайплайнов
1. **Программный монтаж (код → MP4)**: агент пишет HTML/React, а рендерер собирает видео. Генеративных моделей нет, кадры детерминированы. Инструменты — Remotion, HyperFrames, Manim, Motion Canvas.
   - Remotion-скилл — самый устанавливаемый видеоскилл на skills.sh (более 126 тыс. установок). Для коммерческого продакшена рендерер требует лицензию ([dev.to, май 2026](https://dev.to/hiy_dev/claude-code-video-skills-a-developers-practical-guide-to-all-6-options-2026-4f40)) [1И].
   - HyperFrames (HeyGen): Apache 2.0, около 90k звёзд, 9 скиллов, в том числе `/reverse-any-video` и `/media-use`, плюс около 450 блоков (переходы, кинетическая типографика, субтитры, графики, карты) ([GitHub](https://github.com/heygen-com/hyperframes)) [П].
2. **Генеративный (промпт → клипы → склейка)**: LLM пишет сценарий и шот-лист, затем генерируются ключевые кадры (первый и последний кадр), потом i2v в Seedance, Kling, Veo или Wan, затем склейка в ffmpeg или Remotion/HyperFrames с TTS, музыкой и субтитрами.
   - Пример: китайский скилл ai-video-workflow с 9 стадиями: сюжет → раскадровка и палитра → листы персонажей → первый и последний кадр → промпты и ревью → генерация → пост в коде → оценка → сдача. Модели Seedance, Kling, Jimeng, Runway ([GitHub](https://github.com/kowloonzh/ai-video-workflow)) [П].
3. **Нарезка длинного видео в шортсы и монтаж своих исходников**:
   - video-use (Browser Use): около 31k звёзд, MIT. Вырезает паузы и слова-паразиты, делает цветокор, субтитры и оверлеи через HyperFrames/Remotion/Manim, сам проверяет стыки. Транскрипцию делает ElevenLabs Scribe ([GitHub](https://github.com/browser-use/video-use)) [П].
   - OpenShorts: ~9,7k звёзд, ядро MIT, папка `cloud/` под source-available лицензией (запрещён платный хостинг для третьих лиц). Длинное → 9:16, трекинг лица, субтитры, дубляж, встроенный MCP (`/mcp`), публикация через Upload-Post (TikTok, Instagram, YouTube, Facebook, LinkedIn, Threads, Bluesky). Gemini API обязателен для части функций; выбор моментов можно перевести на локальную LLM через `LLM_BASE_URL` ([GitHub](https://github.com/mutonby/openshorts)) [П].
   - autoclip: MIT, десктоп (Tauri + FastAPI + React, FFmpeg внутри). Ссылка → клипы, обложки, заголовки, хэштеги, ZIP для публикации (Douyin, Xiaohongshu, TikTok, Reels, Shorts, Bilibili). ASR: готовые субтитры, локальный Whisper, SenseVoice или облако; LLM — облачные через OpenAI-совместимый API или локальные через Ollama/LM Studio. Есть CLI, MCP-сервер и скилл. Документация в том числе на русском ([GitHub](https://github.com/zhouxiaoka/autoclip)) [П]. Звёзды: 10,8k на странице GitHub против ~16,1k у gittrend 24.11.2026 — расхождение.

### 1.2. Агрегаторы-скиллы для генерации
По одному обзору от мая 2026 [1И] ([dev.to](https://dev.to/hiy_dev/claude-code-video-skills-a-developers-practical-guide-to-all-6-options-2026-4f40)):
- `heygen-com/skills` [П]: MIT, 443 звезды, 3 скилла — heygen-avatar (цифровой двойник по фото), heygen-video (идея → сценарий → видео с аватаром), heygen-translate (дубляж с клонированием голоса и липсинком, 175+ языков). Нужен аккаунт HeyGen; по API-ключу — оплата как API, через MCP — кредиты тарифа ([GitHub](https://github.com/heygen-com/skills));
- `skillsh/skills` (inference.sh) — шлюз к 40+ видеомоделям, Wan от $0,05–0,11 за ролик;
- Pexo — сквозной пайплайн, 15 секунд из 3 шотов за 8–10 минут;
- `higgsfield-ai/skills` [П]: MIT, ~2,0k звёзд, 9 скиллов (generate на 30+ моделей, в том числе Veo 3.1, Kling 3.0, Seedance 2.5; soul-id; product-photoshoot; brandkit; marketplace-cards; faceless-video; youtube-thumbnail и др.). Агенты: Claude Code, Cursor, Codex. Нужен Higgsfield CLI с авторизацией ([GitHub](https://github.com/higgsfield-ai/skills)). Цифры «5–20 фото» и «17 шаблонов» из dev.to на странице не подтверждены;
- `digitalsamba/claude-code-video-toolkit` — уже разобран в analysis/04.

Также есть MCP gflow-cli для Veo 3.1 через Google Flow (около 720 звёзд, рост в ноябре) ([gittrend](https://gittrend.io/trending/ai-video-generation)) [1И].

### 1.3. Сервисы генерации: состояние на ноябрь 2026
Новое за 15.10–14.11.2026 ([ai-0.net](https://ai-0.net/blog/ai-video-image-news-november-2026)) [1И]:
- Kling 4.0: по официальному блогу Kling (30.09.2026) [П] — ранний доступ с 30.09, широкий запуск в октябре; до 30 секунд за генерацию, до 10 ключевых кадров, до 15 референсов (10 изображений, 5 видео, 7 субъектов), стерео-звук с липсинком; 10-bit HDR в 4K/1080p и продление до 2 минут — «скоро». Kling 4.0 Flash — с 28.09 для подписчиков Ultra Yearly ([kling.ai](https://kling.ai/blog/kling40-kling-visual-realism-creative-control-introducing-storytelling)). Параметры Flash «720p, до 20 секунд» — только ai-0.net [1И].
- Pika H3 Flex на базе MiniMax H3.
- Gemini Omni 1.2 Flash (05.11): 3–15 секунд, $0,07/с в Gemini API. Цену $0,07/с при 720p и клипы 15 с повторяют заголовки нескольких других статей [З].
- FLUX 3 Max (видео).
- Новых релизов Veo, Sora, Seedance, Wan, Runway и Luma в этом окне не найдено.

Рейтинги расходятся [1И]:
- Artificial Analysis, T2V со звуком: 1. Wan 3.0 (Elo 1175, $12/мин), 3. MiniMax H3 768p ($4,80/мин), 5. Seedance 2.5 ($34,12/мин), 6. Gemini Omni Flash 1.2 ($6,26/мин), 9. HeyGen Video 1 ($2,40/мин), 11. Kling 4.0 ($12,60/мин), 14. Seedance 2.0 ($22,45/мин) ([artificialanalysis](https://artificialanalysis.ai/video/leaderboard/text-to-video)). Цены — за минуту на API создателя.
- Arena (06.11): первое место у Gemini Omni 1.2 Flash. Kling 3.0 и Veo 3.1 на обеих досках вне десятки ([teamday.ai, цены на 08.11.2026](https://www.teamday.ai/blog/best-ai-video-models-2026)).

Цены за секунду, 720p, список ([teamday.ai](https://www.teamday.ai/blog/best-ai-video-models-2026)) [1И]:

| Модель | $/с | Звук |
|---|---|---|
| Veo 3.1 Lite (Vertex) | 0,05 | да |
| Gemini Omni 1.2 Flash | ~0,07 | да |
| Seedance 2.0 Mini | ~0,076 | да |
| MiniMax H3 (768p) | 0,08 | да |
| Wan 3.0 | 0,0825 | да |
| LTX-2.5 Fast | 0,09 | да |
| Kling 4.0 Flash | ~0,094 | ? |
| Runway Gen-4.5 (API) | 0,12 | нет |
| Kling 4.0 | ~0,157 | да |
| Seedance 2.0 | ~0,15 | да |
| Seedance 2.5 | ~0,23 | да |
| Veo 3.1 Standard (Vertex) | 0,40 | да |

**Лучшее по цене и качеству на ноябрь 2026** (вывод из двух источников выше, [1И]):
- MiniMax H3 и Gemini Omni 1.2 Flash — дёшево и высоко в рейтингах;
- Wan 3.0 — первое место у AA при средней цене. Цены по TNW (24.08.2026) [П]: 480p $0,05/с, 720p $0,10/с, 1080p $0,20/с (около $12/мин — совпадает с AA). У teamday для 720p указано $0,0825/с — расхождение;
- Seedance 2.5 — для длинных шотов до 30 секунд с большим числом референсов (до 50), но дорого;
- Kling 4.0 — длительность до 30 секунд и ключевые кадры, в рейтинге AA средний.

Veo 3.1 Standard дорогой ($0,40/с — совпадает у teamday и TNW) и в рейтингах уже не лидер. Sora 2 в свежих рейтингах не заметна.

### 1.4. Открытые модели на арендованных GPU
По [tutorial3d.it](https://www.tutorial3d.it/en/ai-artificial-intelligence/comfyui-video-models/) [1И]:
- **LTX-2.5** (11.08.2026): звук, мультишот, 4K, желательно 24 ГБ и больше [1И]. Лицензия LTX-2.x Community License: бесплатно для коммерческого использования при выручке организации (с аффилированными) до $10M в год, выше — платный договор ([HF Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5)) [П]. Требование маркировки ИИ-контента на странице модели не упомянуто, оно только у tutorial3d [1И].
- **LTX-2.3** (март 2026): то же семейство лицензий.
- **Wan 2.2** (июль 2025): Apache 2.0, без звука, версия TI2V 5B влезает в 24 ГБ. Самая свободная лицензия.
- **MiniMax H3** (веса на HF 03.08.2026) [П, 2 источника]: 33B dense, клипы 4–15 с, до 2K, 24 fps, стерео 32 кГц. Территория лицензии — весь мир, кроме ЕС, Великобритании, Республики Корея и США; организации из этих стран могут запросить отдельную лицензию; API доступен глобально. Россия в исключениях не указана. Коммерческим пользователям с выручкой продуктов больше $20 млн в год нужно письменное разрешение. Не OSI-открытая ([rits.shanghai.nyu.edu](https://rits.shanghai.nyu.edu/ai/minimax-ships-h3-weights-with-the-us-and-eu-excluded/), [HF QA-about-License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/QA-about-License.md)). Формулировки в QA противоречивы, MiniMax уже меняла лицензию M2.7 после релиза — читать LICENSE перед использованием. Память: веса 123,6 ГБ в исходной точности, 42,5 ГБ в самых малых вариантах, SGLang рекомендует 4 GPU; цифра «19,5 ГБ в INT8» из tutorial3d этим не подтверждается.
- **HunyuanVideo 1.5**: исключает ЕС, Великобританию и Южную Корею.

Wan 3.0 (24.08.2026) — **веса закрыты** [П]: по TNW доступ поэтапный — бета через Alibaba Cloud Model Studio и Qwen Cloud по заявке, полный API разворачивается; до 30 с, до 1080p, многоязычная речь ([TNW](https://thenextweb.com/news/alibaba-wan3-video-model-after-share-sale)). WaveSpeed (31.08.2026) нашёл репозиторий AlibabaCloud-Official с Apache-2.0, но скачиваемых весов не подтвердил ([wavespeed](https://wavespeed.ai/blog/commercial-compliance/is-wan-30-open-source/)) [1И]. Для своего GPU остаются Wan 2.2, LTX-2.5, MiniMax H3.

Аренда: Modal и RunPod упоминаются как стандарт для claude-code-video-toolkit [1И].

---

## 2. Open-source репозитории и скиллы (последние 2–3 месяца)

Звёзды на дату источника; для [П] — со страницы GitHub 27.11.2026.

| Репо | Звёзды | Лицензия | Что делает | Статус |
|---|---|---|---|---|
| heygen-com/hyperframes | ~90k (+626 за день 24.11) | Apache-2.0 | HTML → MP4, 9 скиллов, ~450 блоков, плагины для Claude Code, Codex, Gemini CLI, Cursor | [П] |
| calesthio/OpenMontage | 72,4k (страница GitHub) / 83k (gittrend 24.11) | AGPL-3.0 | «12 пайплайнов» (в таблице README 11), 100+ инструментов; Claude Code, Cursor, Copilot, Windsurf, Codex. Разобран в analysis/05 | [П] |
| remotion-dev/remotion + remotion-dev/skills | 75,5k движок [1И]; skills 5,5k | Remotion License | React → видео. skills: 12 скиллов (create, markup, render, captions, maps, saas и др.), `npx skills add remotion-dev/skills`. Бесплатно до 3 человек в компании; иначе Automators $0,01/рендер (минимум $100/мес) или Creators $25/мес за место; Enterprise от $500/мес | [П] |
| browser-use/video-use | ~31,4k | MIT | Монтаж своих исходников агентом, ElevenLabs Scribe | [П] |
| hypit-ai/hypit | 26,0k | «Hypit Open Source License» (бейдж «Apache-2.0 with conditions», условия не прочитаны) | Клон референсного ролика в редактируемый проект: футаж, субтитры, b-roll, эффекты, привязка к словам. Claude Code и Codex, скилл `/hypit`, `npx skills add hypit-ai/hypit -g`. Генмодели опциональны (HypiHub или свои; в примерах Seedance 2 Mini, GPT Image 2, WhisperX). Про согласие на лица и голоса в README ничего | [П] |
| JuneYaooo/rea-video | 13,7k | Apache-2.0 | Разбор видео по шотам: снято / ИИ / код, инструкция пересъёмки, VIDEO.md для агента. Режим «только инструменты» офлайн и бесплатно; Gemini/Doubao опционально. Плагины Claude Code и Codex | [П] |
| lemomo-ai/lemo-opuscar | ~21,5k | не названа (REUSE) | 99 кино-стилей в 15 категориях, фильм целиком кодом без видеомодели. Сделан под Claude (Opus/Sonnet), другие модели по README воспроизводят стили хуже | [П] |
| zhouxiaoka/autoclip | 10,8k (GitHub) / ~16,1k (gittrend) | MIT | Нарезка длинного в клипы с субтитрами, обложками и текстами; CLI, MCP, скилл | [П] |
| mutonby/openshorts | ~9,7k | MIT + коммерческая для `cloud/` | Длинное → 9:16, MCP, Upload-Post | [П] |
| kaomei/stickman-video-director | 8,5k | MIT | Сценарий → ролик с человечками; режим A через видеомодели (Google Flow), режим B кодом локально. Claude Code, Codex | [П] |
| shinyobjectz/raea | ~5k | ? | Рендер видео, моушн-графики и 3D из React/TS на своём GPU | [1И] |
| harry0703/MoneyPrinterTurbo | ~143,4k | MIT | Тема → шортс из стоков (Pexels, Pixabay, Coverr) с TTS, субтитрами и музыкой; 9:16/16:9/1:1, пакетно. LLM: в том числе Kimi/Moonshot, Claude, Gemini, DeepSeek, Qwen, OpenRouter, Ollama. TTS: Edge TTS, Azure, ElevenLabs, MiniMax, Kokoro, Fish Audio и др. Есть режим агента и Skill-документ; MCP не упомянут | [П] |
| JuneYaooo/capsule-cinema | 230 | Apache-2.0 | «Видео как шаблон»: раскадровка на ревью → тест одного шота → генерация → план монтажа и локальная QA (разрешение, чёрные кадры, громкость, субтитры, safe area) → точечные переделки → сохранение «рецепта». Агенты: Codex, Claude Code, OpenClaw, Cursor, Trae, Hermes. Каналы: Seedance и Seedream (Volcano Ark), MiniMax H3, Agnes, RunningHub, Doubao TTS, FFmpeg. Демо: ролик на Claude Opus 5.5, повтор по рецепту на GLM 5.3 Flash | [П] |
| JuneYaooo/cheap-claude-video | 80 | Apache-2.0 | Тот же проект Capsule Cinema под другим именем (тот же README и стек, 345 коммитов против 360) | [П] |
| dxawdc/code-video | 8 | MIT | Скилл + CLI `film`: 9 стеков (Canvas 2D, GLSL, Three.js, p5.brush, HTML/GSAP/Lottie, HyperFrames, Remotion, Manim, Blender), TTS-озвучка, проверка тайминга. Claude Code, Codex, WorkBuddy, AGENTS.md | [П] |
| honestTai/auto-video-workflow | 1 | MIT (часть кода Douyin — только для обучения) | 8 шагов: аналитика аккаунта → ресёрч → сценарий → TTS Doubao с посимвольными таймкодами → анимация → сведение → обложка 3:4 → публикация в Douyin и возврат метрик. Пороги: отказ на 2-й секунде ≥35%, на 5-й ≥62% → переписать хук. douyin-video-mcp на 10 инструментов. Агенты: Claude Code, Codex, Antigravity, Kimi Code, WorkBuddy | [П] |
| Johnson-Jia/video-clipforge | 45 | ? | 9-стадийный DAG на Claude Code + HyperFrames, edge-tts, самооценка | [П] |
| kowloonzh/ai-video-workflow | 0 | ? | Скилл «ИИ-режиссёр» для Seedance, Kling, Jimeng | [П] |
| zhuyansen/awesome-claude-video-skills | 1,7k | не названа | Каталог: 427 репо по README (в мета-описании 180), 10 категорий, метки SAFE/CAUTION от Agent Skills Hub. По тесту на 16 скиллах: быстрее всех explainroo (~2 мин), Remotion skills ~4,5 мин, HyperFrames 23,5 мин на тот же бриф | [П] |
| agricidaniel/claude-video (claude-video-shorts) | ? | ? | Скилл нарезки шортсов на skills.sh | [З] |
| openstory-so/openstory | ? | MIT (по ai-bot.cn) | Сценарий → короткая драма: сцены, шоты, изображения, видео, звук, MP4, консистентность персонажей. Модели через fal.ai (Seedance 2.0, Kling 3.0, FLUX), нужны FAL_KEY и OPENROUTER_KEY. Дата публикации на ai-bot.cn 25.08.2026 | [1И] |

Что реально используют:
- По звёздам: MoneyPrinterTurbo, HyperFrames, Remotion, OpenMontage, video-use, Hypit, lemo-opuscar, rea-video, autoclip.
- Hypit — самый крупный из «клонов вирусного видео»: woshipm (23.09.2026) пишет о 10k+ звёзд менее чем за два месяца и о перепродаже услуги на Xianyu ([woshipm](https://www.woshipm.com/AI/6469243.html)) [1И]. menotbobbybrown/hypit — форк с 0 звёзд, оригинал hypit-ai/hypit.
- capsule-cinema / cheap-claude-video — небольшие (230 и 80 звёзд), но подтверждают схему «дорогая модель делает рецепт, дешёвая повторяет» (Opus 5.5 → GLM 5.3 Flash).
- `/reverse-any-video` (HyperFrames) [П, tessl.io]: перестраивает ролик в редактируемый проект HyperFrames с покадровым совпадением — измерение (`measure probe`, `measure cuts`), исходный звук одной дорожкой, просмотр кадров у склеек, пересборка слоёв (текст, графики, UI в HTML; фото и логотипы вырезаются из оригинала; люди переснимаются в HeyGen), `hyperframes diff` оригинала и рендера, отчёт REVERSE.md. **Это функция HyperFrames Pro (платный план)**, требует права на исходное видео ([tessl.io](https://tessl.io/registry/skills/github/heygen-com/hyperframes/reverse-any-video)).
- Китайский сегмент: ai-bot.cn (обновлено 03.07.2026) перечисляет 15 платформ ИИ-микродрам: LibTV, Seko (SenseTime), updream (Bilibili), Jimeng (ByteDance), 蛙蛙漫剧, 白日梦, Pavo (Agnes AI), MOKI (Meitu), SkyReels (Kunlun), OneStory, AutoShorts.ai, Flow Studio, Showrunner (Fable), 神笔马良 (Maoyan), CoCoClip.AI ([ai-bot.cn](https://ai-bot.cn/ai-skit-generation-tools/)) [П]. Это сервисы, у большинства API не заявлен.

---

## 3. Библиотеки контента

### 3.1. Стоки и ассеты

| Ресурс | Что | API | Коммерческое использование | Статус |
|---|---|---|---|---|
| Pexels | фото, видео | Бесплатный API с ключом: 200 запросов/час, 20 000/мес по умолчанию, больше — по запросу; видео через `/v1/videos/`. В API требуется заметная ссылка на Pexels и по возможности автор. Нельзя копировать основную функциональность Pexels | Да, атрибуция не нужна. Нельзя: продавать неизменённые копии, показывать узнаваемых людей в плохом свете, намекать на одобрение людьми или брендами, перепродавать на других стоках, использовать в товарном знаке | [П] |
| Pixabay | фото, видео, музыка, SFX | API только для фото и видео (музыки и SFX в документации нет): 100 запросов за 60 с, кэшировать 24 ч, без постоянного хотлинка, без массовых скачиваний, показывать источник в результатах поиска | Да, без атрибуции, можно изменять. Нельзя: продавать/распространять как есть, коммерчески использовать контент с узнаваемыми брендами, вводить в заблуждение, использовать в товарном знаке. Права третьих лиц на изображённое проверять самому | [П] |
| Unsplash | фото | API: 50 запросов/час в демо, 1000/час после одобрения. Обязательны атрибуция автора и Unsplash, хотлинк через их CDN с `ixid`, вызов `/photos/:id/download` при скачивании | Да | [П] (API) |
| Freesound | звуки | API v2: токен для поиска и превью, OAuth2 для скачивания оригиналов. Лимиты 60/мин и 2000/день; для оригиналов 30/мин и 500/день | Зависит от лицензии конкретного звука (CC0 / CC-BY / CC-BY-NC) [ОЗ]. Фильтровать по лицензии | [П] (API) |
| YouTube Audio Library | музыка, SFX | Нет API (в справке не упомянут). Доступ в YouTube Studio | Треки «copyright-safe» для YouTube, Content ID их не заявляет, монетизация в YPP разрешена. Для CC-треков обязательна атрибуция в описании. Использование вне YouTube справка не разрешает явно | [П] |
| Mixkit (Envato) | видео, музыка, SFX, шаблоны | API не упомянут | Free License: коммерческие проекты (YouTube, соцсети, реклама), без атрибуции; нельзя перепродавать в исходном виде. Restricted License (часть видео): только личные некоммерческие проекты — проверять лицензию каждого ассета. На странице mixkit.co/llm-info есть встроенная инструкция для ИИ-ассистентов рекламировать Envato | [П] |
| Coverr | видео, музыка, изображения | REST API и MCP, коммерческое использование на всех тарифах; на бесплатном Demo-тарифе — атрибуция Coverr и автора; обязательно отправлять статистику скачиваний; флаг `is_ai_generated` | Да, без атрибуции. Нельзя: перепродавать файлы как есть, заявлять через Content ID, обучать ИИ на контенте, делать конкурирующий сток | [П] |
| Uppbeat | музыка (и сток-видео на платных) | Нет, API «скоро» (лист ожидания) | Бесплатно 3 скачивания для своих каналов. Коммерческие и клиентские проекты — с тарифа Pro ($14,99/мес при оплате за год, $24,99 помесячно); Essentials $6,99, Creator $8,99, Business $34,99 | [П] |
| Storyblocks / Envato Elements / Artlist | всё | API у Storyblocks (B2B) | По подписке. Оплата из РФ затруднена | [ОЗ] |
| Google Fonts | шрифты | API | OFL / Apache, в том числе кириллица | [ОЗ] |
| Lucide, Tabler, Iconify, Phosphor | иконки | npm / Iconify API | MIT / ISC и т.п. | [ОЗ] |
| Бесплатные LUT (RocketStock, Freshluts, IWLTBAP) | LUT | Нет | По сайту, часто запрет перепродажи | [ОЗ] |
| HyperFrames registry | ~450 блоков | `npx hyperframes add` | Apache-2.0 | [П] |

MCP для стоков (developer-ishan/mcp-pexels, Unlock-MCP/pixabay-mcp-server, jeanpfs/stock-images-mcp) не открывались [З]. У Coverr MCP официальный [П].

Музыка без стоков: ACE-Step (открытая модель, используется в claude-code-video-toolkit [1И]) или Suno [1И]. Права на треки Suno зависят от тарифа [ОЗ].

### 3.2. Промпт-библиотеки и «рецепты камеры»
- JSON-схема промпта для Seedance 2.5: technical_specs, multimodal_references (@image/@video/@audio), shot_list с shot_id, camera, lighting_and_grade, audio ([Atlas Cloud](https://www.atlascloud.ai/blog/tips/seedance-2-5-json-prompts-workflow)) [1И].
- **YouMind-OpenLab/awesome-seedance-2-prompts** [П]: ~2,1k звёзд, 2000+ промптов Seedance 2.0 (кино, аниме, UGC, реклама, мемы), README на 15+ языках (русского нет в списке), лицензия на странице не названа, интеграции со скиллами нет ([GitHub](https://github.com/YouMind-OpenLab/awesome-seedance-2-prompts)).
- **AtlasCloudAI/awesome-seedance-2.5-prompts-skills** [П]: 260 звёзд, 100+ промптов Seedance 2.5 с превью и устанавливаемый Agent Skill (оптимизация промпта, раскадровка, генерация через Seedance). Продавец API, лицензия не названа ([GitHub](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills)).
- **geekjourneyx/awesome-ai-video-prompts** [П]: 73 звезды, MIT, гайд по промптингу Veo, Sora, Runway, Pika, Kling: киноязык, официальные гайды, синхронизация звука. EN/中文, 4 коммита ([GitHub](https://github.com/geekjourneyx/awesome-ai-video-prompts)).
- Найдены по заголовку [З]: ZeroLu/awesome-seedance (400+ промптов Seedance 2.0), Anil-matcha/awesome-seedance-2.5-api-prompts, dev.to «300 AI video prompts» (Seedance, Kling, Runway, Sora), GitHub topic `video-prompts`, гайд Kapwing по Seedance 2.5, Atlas Cloud prompts-hub.
- HyperFrames `/style-sampling` и `/reverse-any-video` [П]; lemo-opuscar — 99 кино-стилей как промпты + код [П]; capsule-cinema — «рецепт» как переносимый пакет метода [П].
- Higgsfield: Marketing Studio и Virality Predictor в скилле generate [П].
- Вывод: открытые библиотеки промптов есть в основном под Seedance и созданы продавцами API или для привлечения трафика. Единого стандарта нет; русскоязычной библиотеки не найдено.

---

## 4. Русская специфика

- **Агрегаторы.**
  - SYNTX.AI [П]: на сайте публичного API, ключей и документации нет. Доступ через веб и Telegram-бот @syntxaibot (полный функционал — в боте). Видео: Kling, Veo, Seedance и Seedance 2.5, Runway, Luma, Wan, Higgsfield, Hailuo/MiniMax, HeyGen, Grok Imagine, FLUX 3 Video и др. Тарифы FREE / PRO / Enterprise; рублёвые цены на главной не показаны ([syntx.ai](https://syntx.ai/)). B2B (от 15 мест): Pro 680, Elite 1300, Ultra 3000 за пользователя в 30 дней, доступ «через сайт и Telegram», API не упомянут ([b2b.syntx.ai](https://b2b.syntx.ai/)). **Для агентного конвейера SYNTX не подходит** без отдельной договорённости об API.
  - API-агрегаторы с оплатой в РФ продвигаются на dtf.ru, vc.ru, habr, kod.ru через статьи «AI API ключ для нейросетей». Открытая статья на dtf.ru рекламирует RANVIK (api.ranvik.ru): заявлены видеомодели Kling, Luma, Runway, PixVerse, Vidu, HeyGen, MiniMax и др., цены, валюта и OpenAI-совместимость не указаны ([dtf.ru](https://dtf.ru/howto/5241199-ai-api-klyuch-dlya-neyrosetey)) [1И, реклама]. Остальные подобные статьи не открывались [З].
- **Оплата из РФ** [ОЗ]: зарубежные сервисы — через зарубежные карты, посредников или крипту; китайские API требуют международной оплаты или верификации.
- **Распознавание (ASR)**:
  - GigaAM (Сбер) [П]: MIT, 785 звёзд. v3 (ноябрь 2025): `v3_ctc`, `v3_rnnt`, `v3_e2e_ctc`, `v3_e2e_rnnt` (e2e — с пунктуацией и нормализацией). Пословные таймкоды (`word_timestamps=True`). Обычный `transcribe` до ~25 с; длинные файлы через `transcribe_longform` (pyannote, токен HF). По собственным замерам: v3 в среднем на 30% лучше v2 на новых доменах; в side-by-side с Whisper (LLM-судья) 70:30 в пользу GigaAM. Июнь 2026 — GigaAM Multilingual (220M и 600M, 70+ языков) ([GitHub](https://github.com/salute-developers/GigaAM)).
  - T-one (Т-Банк) [П]: Apache-2.0 (код и модели), 273 звезды, 71M параметров, потоковая CTC с чанками 300 мс, заточена под телефонию. WER: колл-центр 8,63, CommonVoice 19 — 5,32; на CommonVoice и OpenSTT GigaAM-RNNT v2 лучше. Таймкоды по фразам, пословные не заявлены ([GitHub](https://github.com/voicekit-team/T-one)). Для субтитров к роликам слабее GigaAM.
  - Whisper large-v3 / turbo + WhisperX [ОЗ]; WhisperX используется в Hypit [П].
  - Для субтитров на русском: GigaAM v3 e2e с пословными таймкодами. ElevenLabs Scribe — платный вариант video-use [П].
- **Озвучка (TTS)**:
  - Silero [П]: лицензия моделей CC BY-NC 4.0 (некоммерческая), кроме `base` CIS-моделей под MIT. Русский v5 (`v5_6_ru` — последний): 5 голосов (aidar, baya, kseniya, xenia, eugene), SSML, 8/24/48 кГц, автоударения и омографы, вопросы с v5_4, восклицания в v5_6 ([GitHub](https://github.com/snakers4/silero-models)). Для коммерческого конвейера клиента — только с отдельной лицензией Silero. Habr 03.08.2026: Silero выпустили модели для 29 языков России (тюркские 14, кавказские 15), русского в них нет ([Habr](https://habr.com/ru/articles/1065252/)) [П].
  - Yandex SpeechKit [П] (документация переехала на aistudio.yandex.ru, дата цен не указана, с НДС): синтез API v3 — за запрос, 0,1626 ₽ за единицу до 250 символов (`general`), `livetts` 0,25 ₽; это ~0,65 ₽ за 1000 символов у `general`. API v1 — 1342 ₽ за 1 млн символов. Распознавание: потоковое и синхронное 0,1626 ₽ за 15 с (~0,65 ₽/мин), асинхронное 0,1515 ₽, отложенное 0,0381 ₽ за 15 с. Brand Voice Lite: 9150 ₽ разово + хостинг от 101 666 ₽/мес ([aistudio.yandex.ru](https://aistudio.yandex.ru/ru/docs/speechkit/pricing)).
  - SaluteSpeech (Сбер) [П]: **на developers.sber.ru (обновлено 25.11.2026) сказано, что API работает до 30.11.2026, после этого запросы обрабатываться не будут; модели доступны на платформе cloud.ru.** С 15.07.2026 новым клиентам пакеты и pay-as-you-go недоступны. Последние цены для юрлиц: синтез 0,000186 ₽/символ (~0,19 ₽ за 1000), распознавание 0,01 ₽/с (~0,60 ₽/мин), минимум 15 000 ₽/мес при использовании. Физлица: продажа пакетов прекращена с 15.07.2026 (был 1 млн символов за 1000 ₽) ([юрлица](https://developers.sber.ru/docs/ru/salutespeech/tariffs/legal-tariffs), [физлица](https://developers.sber.ru/docs/ru/salutespeech/tariffs/individual-tariffs)). Условия на cloud.ru не проверены.
  - ElevenLabs — лучший по качеству, оплата из РФ через посредника [ОЗ].
  - Qwen3-TTS — открытая, в claude-code-video-toolkit [1И]; качество русского не проверено.
  - edge-tts — бесплатно, русские голоса Microsoft; используется в video-clipforge и MoneyPrinterTurbo [П]. Неофициальный доступ.
  - Подборка TTS на Habr (habr.com/ru/articles/991844) не открылась (ошибка сервера).
- Telegram-каналы и Reddit не открывались.

---

## 5. Цены за минуту готового ролика (оценки)

Опорные данные:
- **Сырьё генеративного видео** (только генерация, 1 минута экранного времени, без дублей) [1И]: MiniMax H3 около $4,8, Gemini Omni Flash около $4,2–6,3, Wan 3.0 около $5–12, Kling 4.0 около $9,4–12,6, Seedance 2.5 около $14–34, Veo 3.1 Standard около $24 ([AA](https://artificialanalysis.ai/video/leaderboard/text-to-video), [teamday](https://www.teamday.ai/blog/best-ai-video-models-2026)).
- **Коэффициент дублей**: от 1,7:1 до 2,8:1 сырого к финалу, не больше 3 перегенераций на клип ([MindStudio, 27.03.2026](https://www.mindstudio.ai/blog/ai-filmmaking-cost-breakdown-2026/)) [1И].
- **Короткометражка «под ключ»** на стеке Claude + FLUX/Midjourney + Runway/Kling + ElevenLabs + Suno: около $20–55 за минуту, реалистично $27–43 (там же; цены марта 2026, модели старее) [1И].

Расчётные связки (наш расчёт на основе цифр выше, порядок величины):

| Связка | ~$ за минуту готового |
|---|---|
| Программный монтаж (HyperFrames/Remotion) + стоки + edge-tts / Yandex SpeechKit (Silero — только с коммерческой лицензией) + Kimi или Claude | ~$0,1–2 (только LLM-токены). Лицензия Remotion для компаний платная |
| Faceless из стоков (MoneyPrinterTurbo-подобный) + платный TTS | ~$0,5–3 |
| Генеративный на дешёвых моделях (MiniMax H3 / Omni Flash / Seedance Mini) ×2,5 дубля + TTS + музыка | ~$12–20 |
| Генеративный на Kling 4.0 / Wan 3.0 ×2,5 | ~$25–35 |
| Генеративный премиум (Seedance 2.5 / Veo 3.1 Standard) ×2,5 | ~$40–90 |
| Аватар / говорящая голова (HeyGen Video 1 по AA около $2,4/мин, плюс подписка) | ~$2–10 |
| Своя открытая модель (LTX-2.5 / Wan 2.2) на арендованном GPU | Зависит от часа GPU и скорости. Выгодно при больших объёмах, при малых дороже API |

Агрегаторы в РФ добавляют наценку, она не измерена.

---

## 6. Тренды форматов

- **ИИ-микродрамы и сериалы** [П]:
  - Mobidictum (15.10.2026) по отчёту SocialPeta и BidMatrix: в рекламе ИИ-лайв-экшн-драм число рекламируемых тайтлов выросло с 1479 в январе до 11 962 в июле 2026 (более чем в 7 раз), новых тайтлов — с 378 до 8447. В июле ИИ-тайтлы — 70,62% новых рекламируемых (по всем коротким драмам — 56%). Доля статичных креативов выросла до 1,88% (скриншоты конфликтных сцен) ([mobidictum](https://mobidictum.com/2026-h1-short-drama-advertising-trends-ai/)).
  - TheWrap (11.06.2026): Dashverse (Индия) — DashReels 10 млн MAU, удержание на ИИ-контенте 68%, план 1000 ИИ-сериалов в месяц к концу года; час ИИ-контента $20–30 тыс. против $150 тыс. у лайв-экшн вертикального сериала. В марте 2026 в Douyin добавлено около 50 тыс. ИИ-тайтлов. Инструменты: Seedance 2.0, Veo 3, Luma ([TheWrap](https://www.thewrap.com/?p=8031164)).
  - VML (без даты, после апреля 2026): рынок микродрам Китая 100 млрд юаней в 2025, к началу 2026 более 10 тыс. ИИ-тайтлов в месяц, доля ИИ в топ-чартах выросла с 7% до почти 40% за год; TikTok запустил PineDrama ([VML](https://www.vml.com/insight/ai-micro-dramas)).
  - Цифры по объёму ИИ-тайтлов в Китае расходятся (50 тыс. за март у TheWrap против 10 тыс. в месяц у VML) — разные метрики и площадки.
  - Инструменты: OpenStory (MIT) [1И], 15 китайских платформ на ai-bot.cn [П], capsule-cinema [П].
- **Синтетическая UGC-реклама с ИИ-актёрами** [П] — trends.vc (08.07.2026): обычный UGC-ролик $150–300, ИИ-рендер около $1; креатив выгорает за 2–3 недели, половина объявлений снимается до 28-го дня, выигрывают 4–8%. Игроки: Arcads (1000+ актёров), Creatify ($9M ARR), MakeUGC, HeyGen (~$100M ARR), Captions, Meta Advantage+ (4M+ рекламодателей с генИИ), TikTok Symphony. Регулирование: закон Нью-Йорка о раскрытии синтетических исполнителей в рекламе с 09.06.2026; запрет FTC на фейковые отзывы с октября 2024. ИИ-реклама работает лучше, когда не распознаётся как ИИ; в финансах, здоровье и дорогих покупках люди конвертируют лучше. Автор сам предупреждает, что многие цифры — раунды, а не аудированная выручка ([trends.vc](https://trends.vc/synthetic-ugc-ads-ai-actors-managed-agencies-creative-fatigue/)). Скиллы: heygen-com/skills, higgsfield soul-id [П].
- **Говорящая голова и аватар**: heygen-com/skills [П], OmniHuman и P-Video-Avatar в Kimi skills [1И]. Douyin-пайплайн с аналитикой удержания на 2-й и 5-й секунде — auto-video-workflow [П] (1 звезда, как образец метрик).
- **Faceless из стоков с озвучкой**: самый массовый open-source формат — MoneyPrinterTurbo ~143k [П]; higgsfield-faceless-video [П]; stickman-video-director [П].
- **Нарезка длинного в короткое**: autoclip, OpenShorts [П], video-use [П].
- **«Разбор и пересъёмка залетевшего»**: rea-video (13,7k) [П], Hypit (26k) [П], HyperFrames `/reverse-any-video` (платный Pro) [П]. Устойчивый класс инструментов. Юридический риск (права на исходник, лица и голоса) в README Hypit не освещён; в reverse-any-video право на видео — явное условие [П]. Пост на linux.do не открылся.
- **Моушн-дизайн и объяснялки кодом**: HyperFrames, Remotion, lemo-opuscar, code-video, stickman-video-director (режим B) [П]. Дёшево и детерминированно.
- **Монетизация YouTube**: автоматизация не запрещена, нужна «творческая ценность» ([dev.to/reelmint](https://dev.to/reelmint/open-source-ai-shorts-generators-the-repos-worth-running-in-2026-2kcp)) [1И]. Маркировка ИИ: закон Нью-Йорка для рекламы [П]; требование LTX-2.5 к маркировке на странице модели не подтвердилось.

---

## Что это значит для нашего конвейера

1. **Шаг 1 (ресёрч)**: для разбора референсных роликов брать модель с видеовходом: Kimi K3 или K3.1 Pro через Files API, либо Gemini. Claude видео напрямую не смотрит. Шаблон структуры разбора — rea-video (Apache-2.0, офлайн-режим бесплатен) или `/reverse-any-video` из HyperFrames (только платный Pro).
2. **Шаги 1 и 6 (ресёрч и сценарии)**: разделить «мозги». Claude (Opus или Sonnet) — сценарий и строгие JSON-шот-листы. Kimi K3.x — дешёвые массовые прогоны и длинный контекст (сценарий целиком, каталог персонажей и ассетов). Claude Code работает с Kimi через `ANTHROPIC_BASE_URL`, скиллы переписывать не нужно. Kimi K2.7-code не брать: его отключают в декабре.
3. **Шаг 7 (раскадровка)**: формат шота — JSON со shot_id, camera, lighting_and_grade, audio и @-ссылками на референсы, плюс отдельный «лист персонажа» для консистентности. Делать первый и последний кадр в image-модели до видео: в профильных пайплайнах это стандарт и экономит дубли.
4. **Шаг 8 (генерация)**: держать слой-маршрутизатор моделей, потому что лидер меняется ежемесячно. Черновики и массовые ролики — MiniMax H3 / Gemini Omni Flash / Seedance Mini (около $0,07–0,08/с). Герой-шоты — Seedance 2.5 или Kling 4.0. Veo 3.1 Standard только при требовании к звуку и 4K. Закладывать дубли ×2–3 и лимит 3 перегенерации на клип.
5. **Шаг 8 (генерация, вариант из РФ)**: у SYNTX публичного API нет (только веб и Telegram-бот) — в агентный конвейер он не встраивается. Искать API-агрегатор с рублёвой оплатой (такие рекламируются на dtf/vc/habr, условия не проверены) или платить зарубежным провайдерам через посредника. Запасной путь — открытые LTX-2.5 (бесплатно до $10M выручки), Wan 2.2 (Apache-2.0) или MiniMax H3 (Россия не в исключениях, порог $20M) на арендованном GPU. Wan 3.0 — только API.
6. **Шаг 9 (нарезка)**: для нарезки из длинного взять video-use (MIT) или autoclip / OpenShorts как основу. Транскрипцию для русского сделать на GigaAM v3 e2e (MIT, пословные таймкоды, длинные файлы через longform) или Whisper large-v3 + WhisperX вместо платного ElevenLabs Scribe.
7. **Шаг 10 (монтаж)**: стандартизироваться на HyperFrames (Apache 2.0, ~450 блоков, плагины под Claude Code, Codex, Gemini CLI и OpenCode) как слое сборки. Remotion — если уже есть React-шаблоны, с учётом платной лицензии для компаний. Видео-стоки с API для агента: Pexels (200/час), Pixabay (100/мин, кэш 24 ч), Coverr (REST + MCP, на бесплатном тарифе — атрибуция). Музыка: у Pixabay и Mixkit нет API (скачивать вручную в локальную библиотеку; у Mixkit проверять Free vs Restricted), YouTube Audio Library — только для роликов на YouTube, Uppbeat для клиента — от тарифа Pro. Или генерация ACE-Step. Звуки из Freesound через API (OAuth2 для оригиналов) только с фильтром CC0 или CC-BY.
8. **Шаг 11 (проверка)**: встроить автопроверку по образцу video-use и video-clipforge: просмотр кадров на стыках, машинная оценка, PSNR/SSIM-сравнение версий (скилл video-quality-diff). Финальный просмотр готового MP4 отдать модели с видеовходом (Kimi K3.x).
9. **Шаг 12 (публикация)**: маркировать ИИ-контент (правила площадок; для рекламы с ИИ-актёрами — законы вроде нью-йоркского). Готовые публикаторы — Upload-Post в OpenShorts и Douyin MCP в auto-video-workflow. Для ВК и Telegram нужны свои.
10. **Форматы для клиента**: самые дешёвые и стабильные — моушн и объяснялки кодом, faceless из стоков и нарезка. Самые трендовые — микродрамы и UGC с ИИ-актёрами. Шаблон «рецепт с одного ролика → много вариантов» стоит заложить как режим конвейера: образцы — capsule-cinema (рецепт как пакет: структура, правила, QA-гейты, уроки; Apache-2.0) и Hypit (клон референса, 26k звёзд; лицензия с условиями — прочитать LICENSE).
11. **Озвучка для клиента**: Silero — некоммерческая лицензия, без договора с Silero не брать. SaluteSpeech API закрывается 30.11.2026 (переезд на cloud.ru). Рабочий рублёвый вариант — Yandex SpeechKit (~0,65 ₽ за 1000 символов на v3 `general`). Бесплатно — edge-tts (неофициально).

---

## Источники

Открытые и проверенные [П]:
- https://github.com/heygen-com/hyperframes
- https://tessl.io/registry/skills/github/heygen-com/hyperframes/reverse-any-video
- https://github.com/browser-use/video-use
- https://github.com/MoonshotAI/kimi-code
- https://huggingface.co/moonshotai/Kimi-k2.5
- https://platform.kimi.ai/docs/guide/use-kimi-vision-model.md
- https://platform.kimi.com/docs/guide/kimi-k2-7-code-quickstart.md
- https://github.com/Johnson-Jia/video-clipforge
- https://github.com/kowloonzh/ai-video-workflow
- https://artificialanalysis.ai/video/leaderboard/text-to-video
- https://github.com/JuneYaooo/capsule-cinema
- https://github.com/JuneYaooo/cheap-claude-video
- https://github.com/hypit-ai/hypit (и форк https://github.com/menotbobbybrown/hypit)
- https://github.com/zhouxiaoka/autoclip
- https://github.com/harry0703/MoneyPrinterTurbo
- https://github.com/mutonby/openshorts
- https://github.com/JuneYaooo/rea-video
- https://github.com/calesthio/OpenMontage
- https://github.com/lemomo-ai/lemo-opuscar
- https://github.com/kaomei/stickman-video-director
- https://github.com/dxawdc/code-video
- https://github.com/honestTai/auto-video-workflow
- https://github.com/zhuyansen/awesome-claude-video-skills
- https://github.com/heygen-com/skills
- https://github.com/higgsfield-ai/skills
- https://github.com/remotion-dev/skills
- https://www.remotion.dev/docs/license/pricing.md
- https://kling.ai/blog/kling40-kling-visual-realism-creative-control-introducing-storytelling
- https://thenextweb.com/news/alibaba-wan3-video-model-after-share-sale
- https://huggingface.co/Lightricks/LTX-2.5
- https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/QA-about-License.md
- https://rits.shanghai.nyu.edu/ai/minimax-ships-h3-weights-with-the-us-and-eu-excluded/
- https://ai-bot.cn/ai-skit-generation-tools/
- https://github.com/salute-developers/GigaAM
- https://github.com/voicekit-team/T-one
- https://github.com/snakers4/silero-models
- https://habr.com/ru/articles/1065252/
- https://aistudio.yandex.ru/ru/docs/speechkit/pricing
- https://developers.sber.ru/docs/ru/salutespeech/tariffs/legal-tariffs
- https://developers.sber.ru/docs/ru/salutespeech/tariffs/individual-tariffs
- https://syntx.ai/
- https://b2b.syntx.ai/
- https://www.pexels.com/api/documentation/
- https://www.pexels.com/license/
- https://pixabay.com/api/docs/
- https://pixabay.com/service/license-summary/
- https://unsplash.com/documentation
- https://freesound.org/docs/api/overview.html
- https://support.google.com/youtube/answer/3376882
- https://mixkit.co/llm-info/
- https://coverr.co/license
- https://uppbeat.io/pricing
- https://github.com/YouMind-OpenLab/awesome-seedance-2-prompts
- https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills
- https://github.com/geekjourneyx/awesome-ai-video-prompts
- https://mobidictum.com/2026-h1-short-drama-advertising-trends-ai/
- https://www.thewrap.com/?p=8031164
- https://www.vml.com/insight/ai-micro-dramas
- https://trends.vc/synthetic-ugc-ads-ai-actors-managed-agencies-creative-fatigue/

Открытые, вторичные [1И]:
- https://dev.to/hiy_dev/claude-code-video-skills-a-developers-practical-guide-to-all-6-options-2026-4f40
- https://pexo.ai/blog/make-videos-claude-code-kimi-k3-6789
- https://www.atlascloud.ai/blog/tips/seedance-2-5-json-prompts-workflow
- https://www.atlascloud.ai/blog/tips/cheapest-ai-video-generation-api-2026 (внутренние противоречия в цифрах, не использовался для выводов)
- https://www.buildfastwithai.com/blogs/seedance-2-5-vs-veo-3-1-vs-kling-3-0-best-ai-video-2026
- https://www.teamday.ai/blog/best-ai-video-models-2026
- https://ai-0.net/blog/ai-video-image-news-november-2026
- https://www.tutorial3d.it/en/ai-artificial-intelligence/comfyui-video-models/
- https://www.mindstudio.ai/blog/ai-filmmaking-cost-breakdown-2026/
- https://www.morphllm.com/kimi-k3
- https://cellcog.ai/blog/kimi-k3-1-release-date/
- https://gate.ai/blog/kimi-k2-6-moonshot-ai-specs-pricing-api-use-cases
- https://officechai.com/ai/these-are-the-top-ai-models-on-openrouter-by-number-of-tokens-november-2026/
- https://www.kimi.ai/resources/multimedia-skills-for-agents
- https://gittrend.io/trending/ai-video-generation
- https://www.coddykit.com/pages/blog-detail?id=5129958&slug=github-trending-october-2026-from-ai-video-production-to-local-deepseek-5-repos-
- https://dev.to/reelmint/open-source-ai-shorts-generators-the-repos-worth-running-in-2026-2kcp
- https://ai-bot.cn/openstory/
- https://www.woshipm.com/AI/6469243.html
- https://wavespeed.ai/blog/commercial-compliance/is-wan-30-open-source/
- https://dtf.ru/howto/5241199-ai-api-klyuch-dlya-neyrosetey (реклама RANVIK)

Не открылись (ошибка сайта): linux.do/t/topic/2906539, habr.com/ru/articles/991844, sostav.ru/blogs/287746/99256, github.com/heygen-com/hyperframes/tree/main/skills (robots).

Найдены по заголовку, не открыты [З]:
- https://www.skills.sh/agricidaniel/claude-video/claude-video-shorts
- https://linux.do/t/topic/2341689 (Kimi Code: перетаскивание видео)
- https://linux.do/t/topic/3134369 (туториал по промо-роликам)
- https://linux.do/t/topic/2906539 (инструмент копирования вирусных видео)
- https://www.thepaper.cn/newsDetail_forward_32829833
- https://www.youtube.com/watch?v=0y5hy3wWnZQ
- https://openrouter.ai/alibaba/wan-3.0
- https://vc.ru/ai/2811585-seedance-2-v-syntx-ai
- https://www.sostav.ru/blogs/288343/92425
- https://vc.ru/provod/2976511-neyroseti-dlya-generacii-video-veo-seedance-kling
- https://huggingface.co/ai-sage/GigaAM-v3
- https://habr.com/ru/companies/sberdevices/articles/973160/
- https://3dnews.ru/1126334
- https://habr.com/ru/articles/938438/
- https://github.com/developer-ishan/mcp-pexels
- https://mcpservers.org/servers/Unlock-MCP/pixabay-mcp-server
- https://lobehub.com/mcp/jeanpfs-stock-images-mcp
- https://github.com/ZeroLu/awesome-seedance
- https://github.com/Anil-matcha/awesome-seedance-2.5-api-prompts
- https://dev.to/dawnravenai/300-ai-video-prompts-that-actually-work-seedance-kling-runway-sora-more-4o17
- https://www.kapwing.com/resources/how-to-prompt-seedance-2-5-a-guide-for-ai-video-creators/
- Статьи о Gemini Omni 1.2 Flash $0,07/с (letsdatascience, braindetox.kr, segmind и др.)
