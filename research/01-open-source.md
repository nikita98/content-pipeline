# Открытые проекты для «конвейера контента»: что есть и что взять

Дата ресёрча: 26.11.2026. Источники: README на GitHub, страницы n8n.io и openalternative.co, сайт Remotion. Всё смотрел через WebFetch. Ничего не скачивал и не запускал.

**Про цифры.** Звёзды взяты со страниц репозиториев на дату ресёрча. Даты последних коммитов GitHub для большинства репозиториев не отдал: API и atom-ленты были закрыты для этой сессии. Где дату узнать не удалось, так и написано: «дата не проверена». Точная дата есть только у MoneyPrinterTurbo и remotion-dev/skills (из GitHub API).

Шаги нашего конвейера (дальше ссылаюсь на номера):
1 ресёрч конкурентов → 2 идеи → 3 тексты (TG/Threads/описания) → 4 карусели → 5 сценарии Reels → 6 раскадровка/промпты → 7 генерация (аватар, клипы, озвучка) → 8 монтаж кодом + субтитры → 9 QA → 10 публикация → 11 аналитика → 12 воронка по кодовому слову в директе.

---

## Сводная таблица

| # | Проект | Тип | ★ | Лицензия | Шаги конвейера |
|---|---|---|---|---|---|
| 1 | OpenMontage | агентная видеостудия для Claude Code/Codex/Cursor | ~72.4k | AGPL-3.0 | 1*, 5, 6, 7, 8, 9 (сильно), 10 частично |
| 2 | claude-code-video-toolkit | рабочее пространство Claude Code (скиллы и команды) | ~2.4k | MIT | 5, 6, 7 (вкл. аватар), 8, 9 частично, 10? |
| 3 | MoneyPrinterTurbo | монолит «тема → ролик» | ~145k | MIT | 5, 7, 8, 10 |
| 4 | Pixelle-Video | монолит «тема → ролик» на ComfyUI | ~29.5k | Apache-2.0 | 5, 6, 7, 8 |
| 5 | ShortGPT | фреймворк для shorts-каналов | ~8.1k | MIT | 5, 7, 8, перевод/дубляж |
| 6 | short-video-maker | MCP/REST-сервер рендера shorts | ~1.3k | MIT | 7 (TTS), 8 |
| 7 | OpenShorts | open-source аналог OpusClip | ~9.7k | MIT (+ коммерческая `cloud/`) | 8, 10, 7 (UGC-аватары) |
| 8 | remotion-dev/skills | официальные скиллы Remotion | ~5.5k | не указана (Remotion под своей лицензией) | 8 |
| 9 | head-of-content | скиллы ресёрча для Claude Code/Cowork | ~274 | MIT | 1, 2 |
| 10 | Ootto-AI/claude-content-skills | набор скиллов для Instagram-контента | ~48 | MIT | 1, 2, 3, 5, 12* |
| 11 | coreyhaines31/marketingskills | 53 маркетинговых скилла | ~60.2k | MIT | 2, 3 (копирайт, соцсети) |
| 12 | OpenReply | open-source аналог ManyChat | ~3.1k | MIT | 12 |
| 13 | Шаблоны n8n (faceless shorts) | low-code воркфлоу | — | платные шаблоны $5–7 | 5–8 через SaaS |

\* частично или косвенно.

---

## 1. OpenMontage — самый близкий по архитектуре

- **Ссылка:** https://github.com/calesthio/OpenMontage. ~72.4k★, 9.4k форков. Лицензия **AGPL-3.0**. Дата последнего коммита не проверена.
- **Что это.** Автор называет проект «первой open-source агентной системой видеопроизводства». Он превращает ИИ-ассистента для кода (Claude Code, Codex, Cursor, Copilot, Windsurf) в видеостудию. Видео описывают словами, а агент сам делает ресёрч, сценарий, ассеты, монтаж и рендер.
- **Покрытие.** 11–12 пайплайнов: Animated Explainer, Avatar Spokesperson, Talking Head, Clip Factory, Podcast Repurpose, Localization & Dub, Screen Demo, Documentary Montage и др. Внутри каждого стадии research → proposal → script → scene_plan → assets → edit → compose.
  - **Есть:** 5, 6, 7 (TTS, видео, картинки, аватар, липсинк, музыка), 8 и очень сильный 9.
  - **Нет:** ресёрча соцсетей конкурентов в нашем смысле (у них research — это ресёрч темы), текстов для TG/Threads, каруселей, аналитики и воронки. Публикация есть только как шаг с одобрением и профили платформ (YouTube Shorts, Reels, TikTok). Интеграции загрузки в README не описано.
- **Технологии:**
  - Оркестратор — сам агент, кодового оркестратора нет. Агент читает YAML-манифесты (`pipeline_defs/`) и Markdown-скиллы (`skills/pipelines|creative|core|meta`).
  - Больше 100 инструментов в `tools/` с автообнаружением. Больше 20 JSON Schema в `schemas/` — это контракты между стадиями.
  - Стили видео описаны в YAML (`styles/`).
  - TTS: ElevenLabs, Google TTS, OpenAI TTS, Piper (локально, бесплатно), Azure, Fish Audio и др.
  - Видео: Kling, Seedance, Veo 3.1, Runway Gen-4, MiniMax, HeyGen, локальные WAN, Hunyuan и LTX-Video.
  - Аватары и липсинк: SadTalker/MuseTalk, Wav2Lip, Kling Avatar/Lip Sync, HeyGen.
  - Монтаж: Remotion, HyperFrames (HTML/CSS/GSAP) и FFmpeg.
  - Субтитры: WhisperX с пословными таймкодами, TikTok-стиль в Remotion, SRT/VTT.
- **Запуск.** `git clone` → `make setup`. Нужны Python 3.10+, FFmpeg, Node 18+ (для HyperFrames — 22+). API-ключи необязательны: Piper и бесплатные стоки работают без ключей.
- **Что взять:**
  - Ручные «ворота» одобрения на proposal, script, scene plan, assets и publish.
  - Чекпоинты в JSON, чтобы прогон можно было продолжить. Лог решений и учёт затрат.
  - Проверку до рендера и самопроверку после: ffprobe, вытаскивание кадров, анализ звука, проверка субтитров.
  - Оценку «риска слайдшоу» и бюджетные лимиты.
  - Выбор провайдера по 7 критериям с записью причин.
  - Отдельные файлы инструкций под каждого агента: CLAUDE.md, CODEX.md, CURSOR.md и общий AGENT_GUIDE.md. Это прямо отвечает нашему требованию «работает в Claude и других нейронках».
- **Слабые места:**
  - Лицензия AGPL: если мы отдадим клиенту изменённый код или сервис на его основе, придётся открыть исходники. Безопаснее брать идеи и паттерны, а не код.
  - Проект огромный. Числа в README расходятся (11 или 12 пайплайнов).
  - Локальные LLM пока помечены как «coming soon».
  - Русский язык отдельно не заявлен. Есть README_zh-CN, а у Google TTS «50+ языков».

## 2. claude-code-video-toolkit (digitalsamba) — родной формат Claude Code

- **Ссылка:** https://github.com/digitalsamba/claude-code-video-toolkit. ~2.4k★. **MIT**. Последний релиз v0.20.2 от 2 октября; год на странице не указан, предположительно 2026.
- **Что это.** «AI-native» рабочее пространство для видеопроизводства в Claude Code: от концепта до готового MP4.
- **Покрытие.**
  - **Есть:** 5, 6, 7, 8, команда `/scene-review` (частично шаг 9) и команда `/publish`. Что именно делает `/publish`, из README не ясно — нужна проверка.
  - **Нет:** ресёрча, текстов для соцсетей, каруселей, аналитики и воронки.
- **Технологии:**
  - Скиллы в `.claude/skills/`: remotion, elevenlabs, ffmpeg, moviepy, playwright-recording, frontend-design, qwen-edit, ideogram4, acestep, ltx2, runpod.
  - Команды в `.claude/commands/`: `/setup`, `/video`, `/scene-review`, `/design`, `/brand`, `/template`, `/generate-voiceover`, `/redub`, `/voice-clone`, `/thumbnail`, `/publish`, `/versions` и др.
  - TTS: ElevenLabs или свой Qwen3-TTS с клонированием голоса (около $0.01 за озвучку).
  - Аватар: SoulX-FlashHead (около $0.0024/с) и SadTalker.
  - Картинки: FLUX.2, Ideogram 4 (для текста на картинке). Видео: LTX-2.3 (около $0.23 за клип). Музыка: ACE-Step.
  - GPU в облаке: Modal или RunPod.
  - Монтаж: Remotion (React), для одного шаблона MoviePy, FFmpeg опционально.
  - Отдельного инструмента для субтитров в README нет. В примерах упоминаются вшитые караоке-субтитры.
- **Устройство.** Папки `templates/` (sprint-review, product-demo, concept-explainer-short и др.), `brands/` (бренд-киты), `lib/` (компоненты, переходы, темы), `tools/` (Python CLI). Запуск: `git clone` → `uv sync` → `claude` → `/setup`, `/video`. Демо рендерится без ключей.
- **Что взять:**
  - Схему «скиллы = знания, команды = действия».
  - Бренд-киты в `brands/`. Аналог для нас — профиль клиента.
  - Версионирование через `/versions`.
  - Дешёвый собственный TTS с клонированием и дешёвый аватар на арендованном GPU.
  - Ideogram для текста на картинках. Пригодится для каруселей.
- **Слабые места:**
  - Шаблоны заточены под продуктовые и корпоративные видео (sprint review, демо), а не под Reels.
  - Нужен Remotion: бесплатно только для физлиц и компаний до 3 человек, дальше платная лицензия (см. п. 8).
  - Русский язык не заявлен.

## 3. MoneyPrinterTurbo — эталон пайплайна «тема → ролик»

- **Ссылка:** https://github.com/harry0703/MoneyPrinterTurbo. ~145k★. **MIT**. Последний push 23.11.2026 (GitHub API). Python.
- **Покрытие.**
  - **Есть:** 5 (сценарий по теме или свой текст, на разных языках), 7 (TTS и подбор футажа), 8 (монтаж, субтитры, музыка), 10 (автозагрузка в TikTok, Instagram и YouTube Shorts; заголовки, тексты и хэштеги пишет LLM).
  - **Нет:** ресёрча, каруселей, текстов для TG/Threads, аналитики и воронки. Аватара в списке тоже нет.
- **Технологии:**
  - LLM — очень широкий список: OpenAI, Anthropic Claude, Gemini, DeepSeek, Qwen, Moonshot, Grok, MiniMax и др. Плюс Ollama, OpenRouter и LiteLLM.
  - TTS: Edge TTS (бесплатный, без ключа), Azure, ElevenLabs, Gemini, Fish Audio, Kokoro, Chatterbox, VoxCPM (клонирование) и др.
  - Видео: стоки Pexels, Pixabay, Coverr; свои файлы; ИИ-генерация через MiniMax, Seedance, WaveSpeed и др.
  - Субтитры: по таймкодам Edge TTS (быстро, без GPU) или faster-whisper (точнее, модель около 1.6–3 ГБ).
  - Монтаж на FFmpeg. Форматы 9:16, 16:9 и 1:1.
- **Устройство.** Четыре режима: AI Agent, WebUI, HTTP API (с документацией в `/docs`) и CLI с пакетной обработкой JSON/JSONL. Есть pip-пакет `mpt`, Docker-образ в GHCR, Windows one-click и Colab. Запустить очень просто.
- **Русский.** В README список языков не приведён. Edge TTS вообще умеет русские голоса, но в README MPT это прямо не сказано — **проверить**.
- **Что взять:**
  - Пакетный CLI из JSONL: один ролик на строку.
  - Две стратегии субтитров: «быстро по TTS» и «точно по Whisper».
  - Абстракцию над LLM через OpenAI-совместимые шлюзы (LiteLLM, OpenRouter).
  - Генерацию метаданных под каждую платформу.
- **Слабые места.** Это монолитное приложение, а не скиллы. Визуальный ряд в основном из стоков, получается «faceless»-ролик. Работы с личным брендом и аватаром нет.

## 4. Pixelle-Video (AIDC-AI → сейчас ATH-MaaS/Pixelle-Video)

- **Ссылка:** https://github.com/AIDC-AI/Pixelle-Video (открывается как ATH-MaaS/Pixelle-Video). ~29.5k★. **Apache-2.0**. Последняя датированная запись в changelog — 2026-06-01. Последний коммит не проверен.
- **Покрытие.**
  - **Есть:** 5 (сценарий по теме или фиксированный текст), 6 (планирование кадров), 7 (картинки и видео через ComfyUI или API, TTS), 8 (сборка, BGM).
  - **Нет:** субтитров (в README не упомянуты — проверить), публикации, ресёрча и аналитики.
- **Технологии:**
  - LLM: OpenAI, Qwen, DeepSeek, Ollama.
  - TTS: Edge-TTS и Index-TTS (с клонированием голоса).
  - Картинки и видео: workflow ComfyUI (локально или через RunningHub) либо прямые API — GPT Image, Wan, Seedream/Seedance, Kling.
  - Кадры оформляются **HTML-шаблонами** (`static_*`, `image_*`, `video_*`, в трёх форматах).
  - UI на Streamlit. Запуск `uv run streamlit run web/app.py`, есть Windows-пакет и Dockerfile.
- **Что взять.** HTML-шаблоны кадров — та же идея подойдёт для **каруселей**: HTML → PNG. Ещё модульные стадии, которые можно заменять, и ComfyUI-workflow как подключаемые JSON-файлы.
- **Слабые места.** README и сообщество в основном китайские. Нет публикации и QA.

## 5. ShortGPT

- **Ссылка:** https://github.com/RayVentura/ShortGPT. ~8.1k★. **MIT**. Последний релиз v0.3.0 «Gemini API Support» от 10 февраля, год не указан. Открыто 74 issue и 12 PR. Активность, судя по всему, низкая — **проверить**.
- **Покрытие.**
  - **Есть:** 5, 7 (TTS и подбор ассетов из Pexels, Bing Image и веба), 8 (MoviePy, субтитры), перевод и дубляж готовых видео.
  - **Нет:** загрузки на платформы (только YouTube-метаданные), ресёрча и аналитики.
- **Технологии.** LLM — OpenAI (в релизе 0.3.0 добавлен Gemini). TTS — ElevenLabs и EdgeTTS. **Русский прямо указан** в списке языков озвучки. Память на TinyDB. UI на Gradio. Есть Docker и Colab.
- **Что взять.** Свой «Editing Markup Language»: монтаж описывается JSON-блоками, которые генерирует LLM. Это предшественник подхода «монтаж кодом». Ещё ContentTranslationEngine для дубляжа на другие языки.
- **Слабые места.** MoviePy медленный. Документация, по словам самого README, неполная. Проект выглядит малоактивным.

## 6. short-video-maker (gyoridavid)

- **Ссылка:** https://github.com/gyoridavid/short-video-maker. ~1.3k★. **MIT**. Опубликованных GitHub-релизов нет. Дата не проверена.
- **Покрытие.** Только 7 (озвучка) и 8. На вход подаётся текст сцен, на выходе получается видео 9:16 с субтитрами, фоновым видео и музыкой.
- **Технологии.** TypeScript. TTS — Kokoro (kokoro-js). Субтитры — whisper.cpp. Монтаж — **Remotion**. Фон — Pexels.
- **Устройство.** **MCP-сервер** (SSE, инструменты `create-short-video` и `get-video-status`) плюс REST API. Docker-образы tiny, normal и cuda. Есть примеры для n8n. Нужно 3–4 ГБ RAM и 2 vCPU.
- **Что взять.** Рендер как отдельный MCP-сервис, который может вызывать Claude или n8n. Асинхронные задачи со статусом. Связку Remotion + whisper.cpp.
- **Слабые места.** **Озвучка только на английском** (ограничение kokoro-js), так что для русского аудитории проект в таком виде не годится. Фон только из Pexels. Windows не поддерживается.

## 7. OpenShorts (open-source аналог OpusClip)

- **Ссылка:** https://github.com/mutonby/openshorts. ~9.7k★. Лицензия **MIT** на ядро. Папка `cloud/` под source-available коммерческой лицензией: нельзя предлагать её третьим лицам как платный сервис. По данным openalternative.co на момент ресёрча, последний коммит был «1 день назад» и +2.7k★ за 30 дней. Проект активный.
- **Покрытие.**
  - Нарезка длинного видео на 3–15 клипов с оценкой виральности: Gemini читает транскрипт и смены сцен.
  - Рефрейминг в 9:16 по лицу (MediaPipe, YOLOv8).
  - Пословные субтитры (faster-whisper или Parakeet). Хуки и FFmpeg-эффекты. Дубляж через ElevenLabs.
  - **Публикация** через Upload-Post API: TikTok, Instagram, YouTube, Facebook, LinkedIn, **Threads**, Bluesky.
  - «AI Shorts»: UGC-ролики с ИИ-актёрами через fal.ai (Flux 2 Pro, Hailuo + VEED Lipsync или Kling Avatar). Около $0.65–2 за ролик.
  - **Нет:** ресёрча конкурентов, каруселей и аналитики.
- **Технологии.** Python 3.11 + FastAPI. Фронт на React и Vite. Docker Compose, опционально S3.
- **Устройство.** Встроенный **MCP-сервер** `/mcp` (инструменты `process_video`, `publish_clip`, `add_subtitles`, `recut_clip` и др.), плюс REST, CLI, вебхуки, Agent Skill и пример для n8n. Запуск: `docker compose up --build`. Нужен ключ Gemini; можно подключить локальный OpenAI-совместимый LLM, но функциям, работающим по кадрам, всё равно нужен Gemini.
- **Что взять.** Ветку «длинное → короткие» (у нас её нет, а для эксперта с эфирами и подкастами она ценна). Публикацию через единый агрегатор API. MCP-инструменты для агентной работы.
- **Слабые места.** Завязан на Gemini, ElevenLabs и платный Upload-Post. Часть функций (Autopilot) есть только в облаке.

## 8. remotion-dev/skills (официальные скиллы Remotion)

- **Ссылка:** https://github.com/remotion-dev/skills. ~5.5k★. Последний push 19.10.2026 (GitHub API). Поле license в API пустое — **лицензия репозитория не указана**.
- **Состав.** 12 скиллов: `remotion-best-practices`, `remotion-create`, `remotion-render`, `remotion-captions` (субтитры), `remotion-studio`, `remotion-interactivity`, `remotion-docs`, `remotion-multimedia` (Mediabunny), `remotion-saas`, `remotion-maps`, `remotion-markup`, `remotion-upgrade`.
- **Установка.** `npx skills add remotion-dev/skills`. Работают в Claude Code, Codex, Cursor и др.
- **Покрытие.** Только шаг 8, зато это «первоисточник» знаний по Remotion.
- **Важно про лицензию самого Remotion.** Бесплатно для физлиц и компаний до 3 человек. Остальным нужна Company License: «Automators» $0.01 за рендер с минимумом $100 в месяц или «Creators» $25 в месяц за место ([remotion.dev/docs/license/pricing](https://www.remotion.dev/docs/license/pricing)). Это нужно учесть, если клиент — компания больше 3 человек.
- **Что взять.** Ставить как есть в шаг монтажа. `remotion-captions` закрывает субтитры.

## 9. head-of-content (bradautomates) — ресёрч конкурентов

- **Ссылка:** https://github.com/bradautomates/head-of-content. ~274★. **MIT**. 7 коммитов, это небольшой проект. Дата не проверена.
- **Покрытие.** Шаги 1–2: ресёрч X, Instagram, YouTube и TikTok, поиск статистических выбросов, ИИ-разбор видео и контент-план. **Telegram нет.**
- **Скиллы (файлы `.skill`):** `x-research`, `instagram-research`, `youtube-research`, `tiktok-research`, `video-content-analyzer`, `content-planner` (запускает все четыре и сводит результат).
- **Технологии.** Скрейпинг через Apify (Instagram, TikTok, X), YouTube через TubeLab, разбор видео через Gemini. Python 3.8+.
- **Устройство.** Отслеживаемые аккаунты лежат в `.claude/context/`. Каждый запуск пишет папку с датой: `raw.json` → `outliers.json` → `video-analysis.json` → `report.md`. Контент-план пишется в `content-plans/<дата>/content-ideas.md` вместе с плейбуками по платформам.
  - Скоринг: X — взвешенные сигналы (закладки ×4, ответы ×3, ретвиты ×2, лайки ×1). YouTube — z-score с затуханием 5% в день. Выброс — всё выше среднего + 2σ.
  - Сделан **под Cowork**: «Work in a folder» и загрузка `.skill` через Settings → Capabilities → Skills.
- **Что взять.** Почти готовый шаблон нашего шага 1: формулы выбросов, структуру артефактов по датам, контекст-файлы конкурентов.
- **Слабые места.** Платные Apify и TubeLab. В README заявлены только macOS и план Max. Нет Telegram и русского.

## 10. Ootto-AI/claude-content-skills

- **Ссылка:** https://github.com/Ootto-AI/claude-content-skills. ~48★. **MIT**. Дата не проверена.
- **Покрытие.** Instagram-контент: 30 скиллов в группах Study, Create, Distribute и Grow.
  - Content Factory (весь цикл одной командой), Reel Analyzer, Going Viral (выбор цели и эмоции), Viral Hook Writer (10 ранжированных хуков), Hook Mining (из CSV своих хуков), Reel Scripter, Reel Builder (по битам: текст на экране и визуал), Caption & Hashtags, Content Repurposer, Content Calendar, Competitor Teardown, Trend Spotter.
  - **Comment Responder:** публично отвечает без ссылки, а ресурс отправляет в DM. Это логика нашей воронки (шаг 12), но только на уровне текстов, без автоматизации.
  - Память — Obsidian-хранилище через MCP-коннектор файловой системы («AI Brain»). Удачные ролики сохраняются обратно.
  - **Нет:** генерации видео и монтажа.
- **Установка.** `/plugin marketplace add Ootto-AI/claude-content-skills`, либо `install.sh` (копирует в `~/.claude/skills/`), либо вставить промпты в claude.ai.
- **Что взять.** Разбиение шагов 2 и 5 на мелкие скиллы (хук → сценарий → билд → подпись). Петлю обучения «победители → память». Упаковку как плагин-маркетплейс.
- **Слабые места.** Проект маленький, качество промптов нужно проверять вручную. Всё на английском и под Instagram.

## 11. coreyhaines31/marketingskills

- **Ссылка:** https://github.com/coreyhaines31/marketingskills. ~60.2k★. **MIT**. Версия v2.0. Дата не проверена.
- **Покрытие.** Шаги 2–3: `copywriting`, `content-strategy`, `social` (LinkedIn, X, Instagram, TikTok, Facebook), `copy-editing`, email, SEO, CRO и др. Всего 53 скилла. Видео нет.
- **Устройство.** Каждый скилл — папка с `SKILL.md`. Есть **общий контекстный файл** `.agents/product-marketing.md`: его сначала читает каждый скилл (продукт, аудитория, позиционирование).
  - Установка: `npx skills add`, плагин Claude Code, плагин Codex, ZIP для claude.ai. Совместим со спецификацией Agent Skills, то есть работает в Claude Code, Codex, Cursor и Windsurf.
- **Что взять.** Паттерн «один общий файл контекста клиента, на который ссылаются все скиллы». Мультиплатформенную упаковку одного набора скиллов. Раздел «Related Skills» в каждом скилле.
- **Слабые места.** Ориентация на SaaS и англоязычный маркетинг. Telegram и Threads отдельно не покрыты.

## 12. OpenReply — воронка по кодовому слову

- **Ссылка:** https://github.com/diwenne/openreply. ~3.1k★. **MIT**. Дата не проверена.
- **Покрытие.** Шаг 12: комментарий с ключевым словом → личное сообщение со ссылкой (+ публичный ответ). Ещё триггеры по DM и ответам на сторис, трекинг кликов, follow-gate и несколько аккаунтов.
- **Технологии.** **Официальный Instagram API** (private replies): без скрейпинга и паролей. Next.js 16, Prisma и PostgreSQL, BullMQ и Redis (воркер отправки), Auth.js.
- **Запуск.** `npm install`, `.env`, `docker-compose up -d`, миграции, `npm run dev` и `npm run worker`. Нужны публичный HTTPS, бизнес- или креатор-аккаунт IG и своё Meta-приложение (или платный провайдер Zernio).
- **Ограничения.** Лимит Meta 750 private replies в час. Ответы из дашборда работают только внутри 24-часового окна. Чтобы перейти с ManyChat, нужно передать владение диалогами. Follow-gate при сбое отправляет ссылку всё равно.
- **Что взять.** Готовую self-hosted замену ManyChat для нашей воронки и описание подводных камней Meta API.

## 13. Шаблоны n8n для faceless-видео (для сравнения)

- **[n8n #21952](https://n8n.io/workflows/21952-create-narrated-faceless-youtube-shorts-with-openai-flux-kling-and-elevenlabs/)** — «narrated faceless shorts», **платный, $5**.
  - Схема: Google Sheets (очередь сценариев) → OpenAI делит на 3–6 сцен → **ручное одобрение раскадровки** → ElevenLabs с проверкой длины 30–60 с → тайминги субтитров по таймкодам символов → FLUX 2 Pro и Kling 2.5 через fal → рендер в Shotstack → проверка PNG и MP4 → ZIP в Google Drive.
  - **Публикации нет.** Удачные детали: лимиты стоимости, повторное использование неизменённых ассетов, манифест раскадровки.
- **[n8n #2971](https://n8n.io/workflows/2971)** — Leonardo AI + Creatomate + ElevenLabs, LLM DeepSeek V3, **$7**. Публикации нет.
- **Общий вывод.** Шаблоны дешёвые, но завязаны на платный SaaS-рендер (Shotstack, Creatomate). Логика тривиальная. Полезны как референс для ворот одобрения и контроля стоимости, качать как основу не стоит.

## Упомянуто, но не разобрано подробно

- **MoneyPrinterV2** — https://github.com/FujiwaraChoki/MoneyPrinterV2. ~32.4k★, **AGPL-3.0**, Python 3.12. Автоматизация YouTube Shorts и Twitter-бота по CRON, партнёрский маркетинг, холодный аутрич. Какие у него LLM, TTS, способ загрузки и монтаж, README не раскрывает — не проверено.
- Других кандидатов (NarratoAI, AI-Youtube-Shorts-Generator, Violyra, Orkas VideoStudio, wilwaldon/Claude-Code-Video-Toolkit, inference-sh/skills для каруселей) поиск выдал, но я их не открывал.

---

## Чего нет ни в одном проекте (наша ниша)

- Ресёрч **Telegram-каналов** конкурентов.
- Тексты под **Telegram и Threads** на **русском**.
- **Карусели** как отдельный шаг. Ближе всего HTML-шаблоны Pixelle и Ideogram в video-toolkit.
- Сквозная **аналитика**, которая возвращается в ресёрч. Только у Ootto есть простая петля «победители → память».
- Конвейер целиком от ресёрча до воронки. Каждый проект закрывает 2–5 шагов.

## Топ-3 для совместного разбора

1. **OpenMontage.** Ближе всех к нашей идее «конвейер на скиллах внутри Claude Code и других агентов»:
   - агент как оркестратор, YAML-пайплайны, Markdown-скиллы и JSON-контракты;
   - ворота одобрения, чекпоинты и бюджет;
   - лучший в выборке шаг QA (ffprobe, кадры, звук, субтитры, «риск слайдшоу»);
   - аватар и липсинк, Remotion, FFmpeg и WhisperX;
   - отдельные файлы инструкций под Claude, Codex и Cursor.

   Минус — AGPL, поэтому берём архитектуру и паттерны, а не копируем код в продукт для клиента. Русский прямо не заявлен.

2. **claude-code-video-toolkit (MIT).** Тот же класс, но компактнее, под лицензией MIT и в родном формате Claude Code (`.claude/skills` + `.claude/commands`, бренд-киты, версии, дешёвый аватар и TTS на арендованном GPU). Хороший образец того, как разложить шаги 6–8 на скиллы и команды. Учесть лицензию Remotion, если в компании клиента больше 3 человек.

3. **head-of-content (MIT) в паре с Ootto-AI/claude-content-skills (MIT).** Закрывают начало конвейера, которого нет у видео-проектов:
   - head-of-content даёт ресёрч конкурентов с формулами выбросов, артефактами по датам и готовой установкой в Cowork;
   - Ootto добавляет цепочку хук → сценарий → билд Reels → подпись → Comment Responder и петлю памяти.

   Оба маленькие и легко читаются, поэтому их удобно разобрать вместе. Telegram и русский язык нужно будет добавить самим.

**Запасные варианты:**
- **MoneyPrinterTurbo (MIT)** — как референс рабочего движка «сценарий → озвучка → футаж → субтитры → загрузка» с Edge TTS и широким выбором LLM; самый простой запуск.
- **OpenReply (MIT)** — готовый модуль для шага 12.
- **OpenShorts (MIT)** — если нужна ветка «длинное видео → клипы» и публикация через Upload-Post, включая Threads.

## Что осталось непроверенным

- Даты последних коммитов почти у всех репозиториев (кроме MoneyPrinterTurbo и remotion-dev/skills).
- Год релизов ShortGPT v0.3.0 и video-toolkit v0.20.2.
- Поддержка русского в MoneyPrinterTurbo, Pixelle-Video, OpenMontage и video-toolkit.
- Что именно делает `/publish` в video-toolkit.
- Лицензия remotion-dev/skills.
