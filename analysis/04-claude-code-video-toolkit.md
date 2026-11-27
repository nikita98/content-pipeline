# claude-code-video-toolkit

Метод: сначала WebFetch, затем сверка с локальной копией (папка пользователя, стейджинг в /mnt/user-data/uploads/content pipeline/dev/competitors/claude-code-video-toolkit-main/claude-code-video-toolkit-main/, прочитаны 21 файл: AGENTS.md, CLAUDE.md, pyproject.toml, .claude/settings.json, context7.json, tools/{captions,align_captions,publish_kit,qwen3_tts,voiceover}.py, brands/default/voice.json, templates/{concept-explainer-short/CLAUDE.md,config.json; howto/README.md; product-demo/package.json}, skills parody-short, synthetic-ui-demo, youtube-stats, blender, video-design). Исходное чтение через WebFetch (README, CLAUDE.md, AGENTS.md, registry, команды, pyproject, отдельные tools/*.py, шаблон concept-explainer-short, brand.json). Ничего не скачивалось и не запускалось. Страницы WebFetch отдаёт в пересказе малой модели, поэтому цитаты не дословные. Страницы github.com/tree/ закрыты robots, листинги получены через api.github.com. Не читал: package.json в корне (404), docs/roadmap.md (404), листинг .claude/skills (404), lib/, templates/*/ (кроме concept-explainer-short), brands/default, CONTRIBUTING, docs/*.

## Что это
- Название: claude-code-video-toolkit (Digital Samba). «AI-native» рабочее пространство для видео в Claude Code: скиллы + команды + шаблоны Remotion/moviepy + Python-инструменты, тяжёлые модели на облачных GPU.
- Ссылка: https://github.com/digitalsamba/claude-code-video-toolkit
- Лицензия: MIT (LICENSE, 2024, Digital Samba). Оговорка: Remotion имеет свою лицензию, компаниям может понадобиться коммерческая (https://remotion.dev/license, из skills/remotion).
- Версия/дата: релиз v0.30.0, 2026-11-22 (GitHub API); локальный pyproject.toml тоже 0.30.0. Цифра 0.20.1 из WebFetch (pyproject/registry) была устаревшим кэшем: считать версией 0.30.0. Содержимое registry локально не сверено (файл не в стейджинге), поэтому списки скиллов/инструментов ниже могут быть неполными.

## Шаги нашего плана, которые покрывает
- 6 (сценарии видео): частично, сцены + VOICEOVER-SCRIPT.md под шаблон, не маркетинговый сценарий.
- 7 (раскадровка и промпты): частично, scenes.json/config, скиллы-промптинг ltx2, ideogram4, acestep, qwen-edit; /design и design.md.
- 8 (генерация: аватар, клипы, озвучка, музыка): полностью по инструментам (voiceover, qwen3_tts, ltx2, soulx/sadtalker, music_gen, flux2, ideogram4).
- 9 (нарезка длинного видео): cutdown.py (реформат 16:9 в 9:16/1:1/4:5, вырезка сегментов), highlights.py (эвристический отбор предложений по транскрипту).
- 10 (монтаж Remotion + Whisper, субтитры): Remotion-шаблоны, captions.py (Scribe или Whisper), компонент Captions; русский не проверен (см. раздел).
- 11 (проверка качества): qc.py, /scene-review, copy_lint.py (только английский).
- 12 (публикация): /publish, youtube_upload.py, publish_kit.py, /thumbnail. Только YouTube.
- 13 (аналитика): youtube_stats.py (только YouTube).
- Не покрывает: ★, 0 (частично: brands/ — визуал и голос, не паспорт смыслов), 1, 2, 3, 4, 5 (карусели), 14, 15.

## Скиллы / команды

### Команды (.claude/commands/*.md, 15 файлов; в frontmatter только `description`)
| Имя | Что делает | Шаг плана |
|---|---|---|
| /setup | мастер первой настройки: проверка Node/uv/FFmpeg, .env, выбор Modal/RunPod, R2, деплой GPU-инструментов, голос | вне шагов (установка) |
| /video | список/возобновление/создание проекта: шаблон, бренд, сбор материала, план сцен, копирование шаблона в projects/<name>/, project.json, VOICEOVER-SCRIPT.md, CLAUDE.md | 6, 7, ★ |
| /scene-review | ручной контроль сцен в Remotion Studio до озвучки | 11 |
| /design | задаёт/уточняет визуальное направление, design.md, критика по контактному листу | 7, 11 |
| /brand | список/создание/правка бренд-профиля | 0 (частично) |
| /template | список шаблонов, создание нового | вне шагов |
| /skills | список скиллов, создание нового | вне шагов |
| /contribute | issues/PR/скиллы в репозиторий | вне шагов |
| /record-demo | запись браузерной демо (Playwright) | 8 (скринкаст) |
| /generate-voiceover | озвучка по сценам | 8 |
| /redub | замена голоса в готовом видео | 8 |
| /voice-clone | клон голоса Qwen3-TTS в бренд | 8 |
| /thumbnail | миниатюра 1280x720 через Ideogram 4 | 12 |
| /publish | загрузка на YouTube | 12 |
| /versions | проверка версий Remotion и тулкита | вне шагов |

### Скиллы (по registry из WebFetch, 12; локально дополнительно видны parody-short, synthetic-ui-demo, youtube-stats, blender; AGENTS.md пишет 11 для Codex; также упомянут video-design, в registry-выжимке не виден — проверить)
| Имя | Что делает | Шаг |
|---|---|---|
| remotion-official | официальные знания Remotion, синхронизируются еженедельно (4.0.518) | 10 |
| remotion | паттерны тулкита: переходы, общие компоненты, 30 fps | 10 |
| elevenlabs | TTS, клон голоса, музыка, SFX | 8 |
| ffmpeg | обработка аудио/видео | 9, 10 |
| playwright-recording | запись браузера | 8 |
| frontend-design | визуальная доработка | 7, 10 |
| qwen-edit | промптинг правки изображений | 7, 8 |
| runpod | настройка GPU, Docker, эндпоинты | вне шагов |
| acestep | промптинг музыки, пресеты, лирика | 8 |
| ltx2 | промптинг видео LTX-2.3 | 7, 8 |
| moviepy | сборка видео на moviepy 2.x | 10 |
| ideogram4 | JSON-промпты для картинок с текстом | 7, 8 |
| video-design | дизайн 16:9/9:16, design.md, критика (qc.py + contact sheet) | 7, 11 |
| parody-short | комедийные шорты про команду/группу в жанре (озорная пародия), мастерская с фото и LTX | вне шагов (шаг 6-7 как пример жанровых форматов) |
| synthetic-ui-demo | демо продукта без записи экрана: перестройка UI из исходников + скриптованный курсор в Remotion | вне шагов |
| youtube-stats | статистика YouTube-видео (просмотры, удержание, источники трафика) + разбор, что сработало | 13 |
| blender | 3D-сцены, персонажи, ident по JSON-спеке (Blender 4.2+) | вне шагов |
| video-toolkit (в корневой skills/, для не-Claude агентов) | маршрутизация задач, video_job.py estimate/submit/status/result | ★, 8 |

### Подробно по запрошенным командам
- /video. Первый запуск: подсказка про /setup, если нет .env. Сканирует projects/*/project.json, сверяет статусы сцен с файлами в public/demos и public/audio, считает здоровье проекта (ready/blocked/stale/complete). Новый проект: 1) шаблон (Sprint Review, Product Demo, Concept Explainer Short), бренд, имя; 2) материал (заметки, URL, описание), сообщение, аудитория; 3) план сцен (тип, визуал slide/playwright/external/screenshot, черновик текста, длительность); 4) копирует templates/<t>/ в projects/<name>/, пишет project.json, src/config/brand.ts из бренда, VOICEOVER-SCRIPT.md, копирует логотип, генерирует CLAUDE.md проекта, npm install (кроме concept-explainer-short); 5) список нужных ассетов. Фазы: planning, assets, review, audio, editing, rendering, complete. Сессии пишутся в sessions[]. Полная схема в lib/project/types.ts (не читал).
- /scene-review. Запускает `npm run studio`, ведёт по сценам из config (например demo-config.ts), действия: approve, edit, refine (вызывает frontend-design), flag, skip. Пишет в project.json reviewStatus, reviewIssues, phase=audio. Аргумент: тип сцены или номер. Сама содержимое не оценивает, оценивает человек. Перенос в наш шаг 11 возможен только как идея «ручные ворота».
- /brand. Создание: имя, описание, сайт; цвета тремя способами (извлечь с сайта, из одного hex, вручную); шрифты; логотип; голос (ElevenLabs, встроенный спикер Qwen3, клон). Пишет brands/<name>/brand.json, voice.json, assets/. brand.json: name, description, version, website, colors (primary, primaryLight, primaryDark, accent, textDark/Medium/Light, bgLight, bgAlt, bgDark, bgOverlay, divider, shadow), fonts (primary, mono), spacing xs-xxl, borderRadius, typography h1-h3/body/label, assets (logo, logoLight). voice.json: voiceId, description, settings (stability 0.75, similarityBoost 0.9, style 0.2, useSpeakerBoost), model eleven_multilingual_v2; секция qwen3 (speaker, language, tone, instruct, clone{refAudio, refText}) добавляется /voice-clone. Тон-оф-войс, ЦА, позиционирование не хранятся (кроме опционального copy.json для copy_lint).
- /template. Сканирует templates/*/package.json, показывает сцены и компоненты, создаёт новый шаблон (копия/минимальный Remotion/конвертация проекта). После создания нужен перезапуск Claude Code. Для нас вторично.
- /generate-voiceover. Проверяет, что review пройден (иначе предупреждает), ищет public/audio/scenes/*.txt или VOICEOVER-SCRIPT.md (предлагает разбить на сцены). Провайдер ElevenLabs (по умолчанию stability 0.85, similarity 0.95) или Qwen3-TTS (встроенный спикер с тоном neutral/warm/professional/excited/calm/serious/storyteller/tutorial или клон бренда). Режимы per-scene (рекомендуется) и один файл. Выход: .mp3 на каждый .txt, опционально voiceover-concat.mp3 для SadTalker. Первая строка сцены может быть `[tone: ...]` или `[instruct: ...]`. Флаги voiceover.py: --scene-dir, --concat, --provider qwen3, --speaker, --brand, --tone, --instruct, --dry-run, --json, --max-wpm. Пишет audio.voiceover в project.json. Рекомендует затем captions.py.
- /voice-clone. Только Qwen3-TTS на RunPod. Референс 12-25 с идеально (меньше 8 с — предупреждение), wav/m4a предпочтительны, точная расшифровка обязательна. Копирует в brands/<name>/assets/voice-reference.<ext>, тест в /tmp/voice-clone-test.mp3, пишет секцию qwen3 в voice.json. Советует `--max-wpm 165`, потому что клон наследует темп референса.
- /publish. Только YouTube. Шаги: --check (логин, канал, scopes), чтение project.json, опционально publish_kit.py (SRT + chapters.txt из транскрипции render), сбор блока publish (title, description, tags, category, thumbnail, privacy=private по умолчанию, playlist, chapters, captions, флаг AI-контента), dry-run, загрузка, запись videoId/URL в project.json. Квота около 10 000 единиц в день, примерно 6 загрузок. Shorts определяются по вертикали/квадрату до 3 минут; 16:9 нужно сначала резать cutdown.py.

## Библиотеки и программы
- Python >=3.10, менеджер uv (uv.lock в репо). Ядро (локальный pyproject.toml, пакет 0.30.0): elevenlabs>=2.21.0, python-dotenv>=1.0.0, requests>=2.28.0, boto3>=1.28.0, websocket-client>=1.6.0, pillow>=10.0, moviepy>=2.0, matplotlib>=3.7, numpy>=1.25. Extras: vision (opencv-contrib-python-headless>=4.10,<5; для cutdown --track), whisper (openai-whisper>=20240930, тянет torch, «тяжёлая установка»), prosody (praat-parselmouth>=0.4.3, numpy>=1.24; pick_takes, voice_prosody), modal (modal>=0.64), mcp (mcp>=1.2), youtube (google-api-python-client>=2.100.0, google-auth-oauthlib>=1.2.0, google-auth-httplib2>=0.2.0). Сборочной системы нет намеренно (набор CLI-скриптов, не пакет).
- Node: README «Node.js 18+», /setup «22+ (24 LTS рекомендуется)» — расхождение, проверить. Remotion: шаблоны пинят @remotion/* 4.0.544 (templates/product-demo/package.json), react ^18.2.0, typescript ^5.0.0; скрипты `remotion studio`, `remotion render <Comp> out/x.mp4`, Playwright (папка playwright/), npx.
- FFmpeg/ffprobe: нужны для cutdown, qc, highlights, publish_kit и др. (README помечает «optional», по факту нужен). ImageMagick для locate_watermark. Blender 4.2+ опционально (lecture, experimental). Docker-образы для RunPod в docker/ (например ghcr.io/conalmullan/video-toolkit-qwen3-tts:latest).
- Корневого package.json в списке файлов нет (зависимости Node лежат в templates/*/package.json).

## Внешние сервисы
- Modal (рекомендуется): по README $30/месяц бесплатных вычислений на Starter, типично $1-2/мес. Модальные эндпоинты: qwen3-tts, flux2, upscale (A10G), image-edit (A100), music-gen, sadtalker, soulx, dewatermark (A10G), ltx2 (A100-80GB).
- RunPod (альтернатива, по CLAUDE.md --cloud по умолчанию runpod; по README рекомендуется Modal — расхождение): оплата посекундно, готовые Docker-образы.
- Cloudflare R2 (передача файлов, 10 ГБ бесплатно); без него инструменты используют бесплатные файлообменники.
- ElevenLabs (платно): TTS, клон, музыка, SFX, Scribe для транскрипции (в publish_kit указано $0.40 за час аудио). Тарифы в скиллах не указаны.
- Ideogram 4 (платно, IDEOGRAM_API_KEY): миниатюра около $0.10 при QUALITY.
- 60db TTS: около $0.00002 за символ (минимум $0.01).
- acemusic (ACE-Step хостинг): музыка бесплатно по умолчанию.
- Hugging Face: токен и доступ к Gemma 3 для LTX-2.
- YouTube Data API v3 + Analytics API (OAuth, бесплатно, квота 10 000/день).
- Цены за операцию (registry): qwen3_tts $0.005-0.10; flux2 $0.01-0.03; image_edit $0.01-0.05; upscale $0.005-0.05; sadtalker $0.02-0.30; soulx около $0.0024 за секунду + разовая компиляция; ltx2 $0.20-0.25 за 5-секундный клип; music_gen $0.01-0.10 (acemusic бесплатно); dewatermark $0.05-0.50. Пример из skills/video-toolkit: 45-секундное видео (2 клипа + 2 карточки) около $0.40-0.55.

## Модели
- TTS: Qwen3-TTS (9 встроенных спикеров, клон по референсу, режим VoiceDesign, языки в списке: Auto, English, Chinese, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish); ElevenLabs (eleven_multilingual_v2 по умолчанию, flash_v2_5, v3 alpha, v4 упомянут в voiceover.py); 60db.
- Аватар/говорящая голова: SoulX-FlashHead 1.3B Pro (Modal, сохраняет пропорции, 25 fps); SadTalker (быстрые черновики; для NarratorPiP нужен `--preprocess full`).
- Видео: LTX-2.3 22B (text-to-video, image-to-video, со звуком, 24 fps, 25-193 кадра; LoRA crt-terminal); chain_video.py склеивает клипы по последнему кадру.
- Изображения: FLUX.2 Klein 4B (клейн-9B некоммерческая, Modal opt-in); Qwen-Image-Edit-2511; RealESRGAN; Ideogram 4 (текст в картинке, платный API).
- Музыка: ACE-Step 1.5 (в README XL Turbo 4B), ElevenLabs Music.
- Распознавание: Whisper локально (по умолчанию turbo на CUDA, base на CPU), ElevenLabs Scribe v2.
- Лицензии моделей (FLUX, LTX, Qwen, SoulX) в прочитанном не проверялись — проверить перед коммерческим использованием.

## Агенты, в которых работает
- Claude Code: основной целевой. Скиллы в .claude/skills/*/SKILL.md, команды в .claude/commands/*.md (frontmatter только description, без allowed-tools и disable-model-invocation в прочитанных). Команды используют AskUserQuestion и glob/чтение файлов; после правки нужен перезапуск.
- Codex: есть мост scripts/migrate_to_codex.py + codex/migration_map.json: копирует .claude/skills/* в ~/.codex/skills/, каждую команду превращает в обёртку-скилл со ссылкой на оригинал (не переписывает синтаксис), CLAUDE.md встраивается в AGENTS.md между маркерами. Помечен «experimental». Устанавливает на уровне пользователя (~/.codex), не проекта. AGENTS.md описывает песочницу Codex.
- Kiro CLI: scripts/migrate_to_kiro.py и папка kiro/ (не читал).
- OpenClaw, Hermes, голый API-цикл, MCP-клиент: корневой skills/video-toolkit/SKILL.md (metadata с emoji/os/binaries в стиле OpenClaw) и tools/video_mcp.py (stdio MCP: video_estimate, video_submit, video_status, video_result, video_catalog, video_list, video_cancel, video_resume), mcp 1.x/2.x.
- Kimi Code и OpenCode: в прочитанном не упоминаются. Совместимость OpenCode/Kimi со скиллами в .claude/skills проверить отдельно.
- Что мешает переносу: (1) команды /video и др. написаны как диалоговые сценарии с AskUserQuestion и ожиданием ответов; (2) жёсткая привязка к структуре репо (запуск `uv run tools/...` только из корня, пути относительные); (3) CLAUDE.md-конвенции и авто-регенерация CLAUDE.md проекта; (4) сценарии зависят от Remotion Studio (браузер) и локальных Node/uv/FFmpeg; (5) Cowork/песочницы без GPU и с ограничением сети: все модели вызываются через облачные эндпоинты (Modal/RunPod) и R2, нужны ключи и сеть.

## Файлы между шагами
- projects/<name>/ (gitignored), копия шаблона: project.json, VOICEOVER-SCRIPT.md, CLAUDE.md (генерируется), src/config/brand.ts (из бренда) и *-config.ts (sprint-config.ts, demo-config.ts), public/demos/*, public/audio/voiceover.mp3, public/audio/scenes/NN-slug.txt + .mp3, public/audio/voiceover-concat.mp3, public/images/, design.md, thumbnail/caption.json, out/*.mp4, out/thumbnail.png, out/publish/{video.srt, chapters.txt, kit.json}, <name>.captions.json (массив в форме @remotion/captions Caption, время в мс).
- project.json: name, template, brand, created, updated, phase, scenes[{type, visual{asset}, status, reviewStatus, reviewIssues, designNotes}], audio.voiceover{file,status,mode}, estimates.totalDurationSeconds, sessions[{date,summary}], render.file, publish{...}, thumbnail{...}, design{...}.
- Для вертикальных шортов (concept-explainer-short): scenes.json (id, slug, visual ideogram|ltx, asset, text — одновременно и озвучка, и субтитры), audio/scenes/*.mp3, vo_durations.json, captions/words_*.json, выход out/short.mp4. Скрипты gen_vo.py, gen_captions.py, build.py. 1080x1920, около 2,4 слова/с.
- Бренд-кит: brands/<name>/{brand.json, voice.json, assets/, опционально copy.json}.
- Прочее: .env (ключи и URL эндпоинтов), _internal/toolkit-registry.json (канонический реестр), lecture.json/timeline.json (лекционный шаблон).
- Форматы: JSON, Markdown, MP3, MP4 (H.264/AAC), SRT/VTT, PNG/JPEG. Все видео 30 fps (Remotion).

## Поддержка русского языка
- TTS: Qwen3-TTS декларирует Russian в списке языков (qwen3_tts.py), параметр --language, по умолчанию Auto. Встроенных русских спикеров нет (Ryan, Aiden — английские; Vivian, Serena, Uncle_Fu, Dylan, Eric — китайские; Ono_Anna — японский; Sohee — корейский), поэтому русский — через клон по референсу или Auto. Качество русской речи не проверено. ElevenLabs eleven_multilingual_v2: «29 языков», русский в SKILL.md не назван; в voiceover.py параметр --language относится только к Qwen3 (подтверждено локально), для ElevenLabs языка нет — язык определяется текстом (проверить; по общеизвестным данным ElevenLabs русский поддерживает, но это не из репо). 60db: не проверено.
- Субтитры: captions.py выдаёт JSON с пословными таймингами (Scribe или Whisper), --language принимает код (ru допустим, по логике), автоопределение включено. Подтверждено по локальному коду: norm() в tools/captions.py делает re.sub(r"[^a-z0-9']", "", w.lower()), а _normalize() в tools/align_captions.py — re.sub(r"[^a-z0-9'\s]", " ", s). Для кириллицы все слова превратятся в пустые строки, поэтому выравнивание Whisper/Scribe по тексту сценария для русского ломается (сам текст сценария не пострадает, но совпадения слов не найдутся). Расшифровка без выравнивания по сценарию, вероятно, работает; на тесте не проверено. gen_captions.py локально не читал. В шаблоне concept-explainer-short на экран выводится текст сценария «как написано», выравнивание Whisper-таймингов по скрипту; шрифт не указан. Шрифт бренда по умолчанию Inter (кириллица в Inter есть, это общеизвестно, не из репо).
- copy_lint.py: правила только английские (em-dash, штампы ИИ). Для русского потребуется своя brand copy.json.
- Whisper по умолчанию turbo/base: base плохо подходит для русского — вывод наш, проверить на тесте.

## Берём
- Лицензия MIT, копирование и адаптация допустимы с сохранением уведомления.
- Шаг 10 (монтаж): идея архитектуры «config/scenes.json + покадровые тайминги из реальных длительностей озвучки» (sync_timing.py, vo_durations.json), шаблон concept-explainer-short как основа вертикальных шортов (Python/moviepy, без Node), captions.py как схема (формат @remotion/captions, режим --srt/--vtt, --max-words), компонент Captions. Требует доработки под кириллицу.
- Шаг 9: cutdown.py (blur/crop/pad/track, сегменты, 9:16/1:1/4:5, только FFmpeg, ключи не нужны) — берётся почти как есть; highlights.py как дешёвый черновик отбора (эвристика по редкости слов, на русском с оговорками по пунктуации/токенизации — проверить).
- Шаг 11: qc.py (ассеты, тайминг, WPM, LUFS -14/-1 dBTP, чёрные кадры, контраст текста) — язык-независимая проверка; сам паттерн «один отчёт PASS/WARN/FAIL + --json».
- Шаг 8: voiceover.py как шаблон абстракции провайдеров с --max-wpm и контролем темпа; pick_takes.py (выбор лучшего дубля по темпу и разбросу высоты); Qwen3-TTS клон как путь к русскому голосу без ElevenLabs; video_job.py estimate/submit --max-usd (бюджетный предохранитель) как идея для координатора.
- Шаг 0 (бренд): структуру brands/<name>/{brand.json, voice.json, assets/} и поле copy.json как основу для визуальной части паспорта (цвета, шрифты, голос, запрещённые фразы).
- Шаги 12-13: youtube_upload.py + publish_kit.py + youtube_stats.py (если нужен YouTube; черновик privacy=private, dry-run, квоты) — для остальных платформ не годится.
- ★: идея project.json с фазами и sessions[] как состояния координатора; video-toolkit/SKILL.md как пример агент-агностичного скилла (таблица маршрутов + CLI).
- Шаг 7: /design и design.md (акты, один акцент, пять размеров текста, контактный лист для критики).

## Не берём
- Remotion-шаблоны sprint-review, product-demo, ds-release-notes, lecture (Blender) — узкая тематика (релизы, SaaS-демо).
- /record-demo, playwright, dewatermark, notebooklm_brand, redub (теряет музыку, один спикер), sadtalker (черновик), lecture.py, blender_render.py — вне плана.
- Ideogram/ElevenLabs/60db как обязательные зависимости — платные, русский не подтверждён; брать как опцию.
- copy_lint.py в текущем виде (английские штампы).
- Миграторы Codex/Kiro как есть: wrapper-скилл только указывает на исходную команду.
- Remotion без проверки лицензии для коммерческого использования клиентом.

## Слабые места
- Заточен под английский и под видео вида «релиз/демо/объяснялка»; нет маркетинговых шагов (стратегия, ресёрч, идеи, тексты, карусели, воронка).
- Привязка к облачным GPU и ключам: без Modal/RunPod/R2 генерация не работает; настройка вручную через /setup.
- Русский: нет русских встроенных голосов, выравнивание субтитров ASCII-ориентировано (подтверждено по коду), copy_lint только английский.
- Диалоговые команды (AskUserQuestion, ожидание подтверждений) плохо идут в автономном режиме и в агентах без такого инструмента.
- Расхождения в документации: Node 18+ (README) против 22+ (/setup); RunPod как default (CLAUDE.md) против Modal как рекомендуемого (README); optional FFmpeg против фактической обязательности.
- Мост на Codex экспериментальный, не конвертирует синтаксис, ставит в ~/.codex глобально.
- Remotion: отдельная коммерческая лицензия для компаний; лицензии моделей (FLUX klein-9B non-commercial) нужно проверять.
- Много работающих деталей не закрыто тестами в прочитанном (папка tests/ есть, не читал).

## Открытые вопросы
- Что вошло в 0.30.0 помимо lecture (Blender) и howto: полный changelog не читал.
- .claude/settings.json пустой ({}), то есть хуков и разрешений тулкит не задаёт.
- Читаются ли .claude/skills/*/SKILL.md этого репо в OpenCode и Kimi Code как есть (frontmatter name/description), и работают ли команды из .claude/commands.
- Качество русского у Qwen3-TTS (Auto и клон) и ElevenLabs multilingual_v2/v3 в этом тулките; есть ли русские примеры.
- Ломается ли captions.py/publish_kit.py/gen_captions.py на кириллице (norm()) и какой шрифт даёт кириллицу в Remotion/moviepy шаблонах.
- Содержимое lib/ (components, project/types.ts), templates/*, brands/default, kits/, docs/*, tests/, корневой package.json — не прочитано.
- Как ведёт себя /video вне Claude Code (без AskUserQuestion) и можно ли гнать то же через video_job.py/MCP.
- Лицензии весов моделей (LTX-2.3, SoulX, Qwen3-TTS, ACE-Step, FLUX klein-4B) для коммерческого клиента.
- Реальные затраты на русские ролики (цены приблизительные из registry, не проверялись).
