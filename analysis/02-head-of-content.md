# Карточка: head-of-content (bradautomates)

## Что это
- Название: «Claude Cowork - Head of Content» (репозиторий head-of-content).
- Ссылка: https://github.com/bradautomates/head-of-content (автор bradautomates; в README канал YouTube @bradbonanno, X @corpcowboy_).
- Лицензия: MIT, Copyright (c) 2026 bradautomates (файл LICENSE). Код брать можно с сохранением уведомления об авторстве.
- Версия/дата: тегов и номера версии в файлах нет; дата только в LICENSE (2026). Коммиты локально не видны (нет .git) — проверить на GitHub.
- Состав (41 файл): 6 скиллов (x-research, instagram-research, tiktok-research, youtube-research, video-content-analyzer, content-planner), 9 Python-скриптов, 3 шаблона .md, 4 файла контекста, hook stop-sound.sh, .env.example, 6 архивов .skill.
- Суть: ресёрч чужого контента (X, Instagram, TikTok, YouTube) -> поиск выбросов по вовлечённости -> разбор топ-видео Gemini (хуки, структура, CTA) -> отчёты, банк идей, плейбуки площадок.
- Архивы .skill: это zip с папкой <имя-скилла>/. Распакованы в /tmp/hoc_skills. Сравнение с .claude/skills через diff -r: содержимое идентично; отличаются только каталоги __pycache__ (в архивах Instagram и TikTok лежат .pyc от cpython-312, мусор). Расхождений в логике нет.

## Шаги нашего плана, которые покрывает
- 1 (ресёрч конкурентов): полностью, основной вклад репозитория.
- 2 (банк идей и 10 тем): частично — content-planner делает content-ideas.md с тирами и opportunity score. Ровно «10 тем» не формирует: в шаблоне «top 10 X-sourced ideas», 5 кросс-платформенных, по 3 нативных.
- 3 (план и кодовые слова): частично — 2-недельный календарь (платформа, идея, формат, хук) в content-ideas.md. Кодовых слов нет; в анализаторе видео есть тип CTA `comment-keyword`, но он только распознаётся в чужих видео.
- 9, 6, 7 (косвенно): video-content-analyzer возвращает секции видео с `duration_pct`, хуки и формулы хуков — сырьё для сценариев, но сценарии/раскадровки не генерируются.
- Не покрывает: ★, 0, 4, 5, 8, 10, 11, 12, 13, 14, 15. Паспорта бренда нет; близкий аналог — `.claude/context/*.md` (аккаунты для слежения и описание своего YouTube-канала).

## Скиллы / команды (имя -> что делает)
Общая схема: каждый скилл — SKILL.md с frontmatter (`name`, `description` с блоками "Use when" и "Triggers"). Скрипты вызываются через `python3 .claude/skills/<skill>/scripts/...`. Порядок: скрипт fetch -> скрипт analyze -> (video-content-analyzer) -> Claude сам пишет report.md по шаблону из SKILL.md. Слэш-команд отдельных файлов нет: README называет `/x-research` и т.д., но это просто имена скиллов.

### 1. x-research
- Вход: аккаунты из `.claude/context/x-accounts.md` (таблица), либо `--handles`; параметры `--days` (30), `--max-items` (100 на аккаунт), `--threshold` (2.0).
- Алгоритм:
  1. Создать папку `x-research/<YYYY-MM-DD_HHMMSS>/`.
  2. `fetch_tweets.py`: актор Apify `apidojo/tweet-scraper`; вход `twitterHandles`, `maxItems = max_items * число аккаунтов`, `start = сегодня - days`, `sort: "Top"`, `tweetLanguage: "en"` (захардкожен), прочие фильтры выключены. Пишет `raw.json` (список твитов как есть).
  3. `analyze_posts.py`: скоринг, выбросы, темы, паттерны.
  4. Опционально анализ видео (только если в выбросах есть видео).
  5. Claude пишет `report.md`.
- Формула скоринга: `score = likes + 2*retweets + 3*replies + 2*quotes + 4*bookmarks` (поля `likeCount, retweetCount, replyCount, quoteCount, bookmarkCount`).
- Engagement rate: `score / author.followers * 100` (если followers нет, подставляется 1 — rate раздувается).
- Порог выбросов: `rate > mean(rate) + threshold * stdev(rate)`; mean и stdev считаются по ВСЕМ собранным твитам разом (не по аккаунту). Если твитов меньше 2 — все считаются выбросами. Выбросы сортируются по `score` (не по rate).
- Темы: хэштеги top-20, упоминания top-20, ключевые слова top-30 (слова из 4+ латинских букв без стоп-слов; считается по всем твитам, не только по выбросам; кириллица не учитывается).
- Паттерны выбросов (счётчики и проценты): media, link, thread (эмодзи нитки / слово "thread" / "/1"), quote, вопрос ("?"), список (регэксп), длина короткий <100 / средний <200 / длинный >=200 (без ссылок).
- Выход: `outliers.json` (поля ниже), `report.md` (сводка, топ-15 выбросов, хуки, темы, таблица паттернов, 4-6 выводов, список аккаунтов).
- Замечание из SKILL.md: минимум 50 твитов на запрос, между запусками подождать пару минут; для X нужна платная подписка Apify (README).

### 2. instagram-research
- Вход: `.claude/context/instagram-accounts.md`; `--type posts|reels|stories` (в скрипте по умолчанию posts, в SKILL.md указан reels), `--days` 30, `--limit` 50, `--threshold` 2.0.
- Алгоритм: сначала `apify/instagram-profile-scraper` (вход `usernames`) — берёт `followersCount`, `followingCount`, `postsCount`, `fullName`, `biography`, `isVerified`; затем `apify/instagram-scraper` (вход `directUrls` вида instagram.com/<user>/, `resultsType`, `resultsLimit`, `onlyPostsNewerThan`). К каждому элементу подмешиваются `ownerFollowersCount`, `ownerFollowingCount`.
- Скоринг: `score = likesCount + 3*commentsCount + 0.1*(videoViewCount или videoPlayCount)`.
- Rate: `score / ownerFollowersCount * 100`; если подписчиков 0 — rate = score (нормализации нет, такие посты попадают в выбросы).
- Порог: mean + threshold*stdev по всем постам; сортировка по score.
- Темы: хэштеги (из поля hashtags и из caption) top-20, ключевые слова top-30 (стоп-слова включают link, bio, comment, follow, check).
- Выход: `outliers.json` с полным сырым объектом поста + `_engagement_score`, `_engagement_rate` (не «слим»), `video-analysis.json` по топ-5, `report.md`.
- Видео-анализ: `--max-videos 5`.

### 3. tiktok-research
- Вход: `.claude/context/tiktok-accounts.md`; `--days` 30, `--limit` 50, `--sorting latest|popular|oldest` (latest), `--threshold` 2.0.
- Алгоритм: актор Apify по ID `GdWCkxBtKWOsKjdch` (в комментарии: clockworks/tiktok-scraper). Вход: `profiles`, `resultsPerPage`, `profileScrapeSections: ["videos"]`, `profileSorting`, `oldestPostDateUnified`, `excludePinnedPosts: False`, скачивание видео и обложек выключено. Результат нормализуется в плоские поля: `id, text, createTime, createTimeISO, webVideoUrl, diggCount, shareCount, playCount, commentCount, collectCount, authorUsername, authorNickname, authorFollowers, authorFollowing, authorHearts, authorVerified, videoDuration, videoHeight, videoWidth, coverUrl, hashtags, mentions, isPinned, isAd, musicName, musicAuthor, musicOriginal, _raw`.
- Скоринг: `score = diggCount + 3*commentCount + 2*shareCount + 2*collectCount + 0.05*playCount`.
- Rate: `score / authorFollowers * 100` (при 0 подписчиков rate = score). Порог mean + 2.0*stdev, сортировка по score.
- Темы: хэштеги (с фильтром fyp, foryou, foryoupage, viral, trending, xyzbca), звуки top-10 (`musicName`), ключевые слова top-30.
- Выход: `outliers.json` (ключ `total_videos`, не `total_posts`), `video-analysis.json` топ-5, `report.md` (в т.ч. таблица со Shares и блок Top Sounds).

### 4. youtube-research
- Вход: `.claude/context/youtube-channel.md` (свой канал, нужен 24-символьный Channel ID).
- Алгоритм (8 шагов в SKILL.md):
  1. Папка `youtube-research/<ts>/`.
  2. Прочитать channel ID.
  3. `get_channel_videos.py CHANNEL_ID --format summary` -> GET `https://public-api.tubelab.net/v1/channel/videos/{channel_id}` (заголовок `Authorization: Api-Key <key>`); выдаёт title, description, handle и список (title, viewCount, publishedAt).
  4. Claude анализирует канал по `references/channel-analysis-schema.md` и выдаёт JSON: `audience[]` (who, objections, transformation, stake; 2-3 профиля), `keywords` (4, прямая ниша), `adjacent-keywords` (4, смежные темы той же аудитории), `titles`, `formulas` (шаблоны заголовков с [PLACEHOLDER]), `voice`.
  5. `find_outliers.py` — два поиска в TubeLab: GET `https://public-api.tubelab.net/v1/search/outliers` с параметрами `type=video, language=en, publishedAtFrom=<today-days>, viewCountFrom, size=20, sortBy=zScore, sortOrder=desc, query=<kw>` (до 4 query). Прямая ниша: viewCountFrom 5000; смежная: 10000.
  6. Ранжирование: `score = zScore * recency_boost`, `recency_boost = max(0.3, 1 - 0.05*days_old)` (потолок 0.3 достигается через 14 дней). Берётся top N (`--top` 5) в каждой группе; из смежной убираются дубли прямой.
  7. Для топа скачиваются обложки (`thumbnails/<id>.jpg`, берётся thumbnails.high/medium/default) и транскрипты через GET `/v1/video/transcript/{video_id}` (в `transcripts/<id>.txt`, строки `[MM:SS] текст`; 404 = нет транскрипта).
  8. Claude отбирает максимум 3 релевантных видео (приоритет прямой ниши) и пишет `filtered-outliers.json` (`outliers[]`, `filter_reason`); затем анализ Gemini (`--platform youtube --max-videos 3`); затем `report.md` (хуки, структуры, CTA, таблицы Direct/Adjacent с zScore).
- Выход: `outliers.json` (поля: id, videoId, url, title, description, channelTitle, viewCount, likeCount, commentCount, zScore, publishedAt, channelSubs, transcript_path; плюс keywords, adjacent_keywords, total_videos), `report.md` (базовый), `thumbnails/`, `transcripts/`, опц. `raw-data.json` (`--json`), `filtered-outliers.json`, `video-analysis.json`.
- Особенности: zScore считает сам TubeLab (отклонение видео от среднего по каналу), локально статистики нет; язык поиска `en` зашит; путь в SKILL.md смешанный (`python scripts/...` и `python .claude/skills/...`).

### 5. video-content-analyzer
- Вход: `--input` (список или `{"outliers":[...]}`), `--output`, `--platform instagram|tiktok|youtube`, `--max-videos` (5).
- Алгоритм: маппинг полей по платформе (таблица PLATFORM_MAPPINGS) -> фильтр «это видео» -> для каждого: (а) пробует передать URL прямо в Gemini; при исключении (б) скачивает файл requests (таймаут 60 с, без проверки размера), грузит в Gemini File API (mime video/mp4), ждёт ACTIVE (до 300 с, шаг 5 с), анализирует, удаляет файл. Пауза 2 с между видео. Если ответ не JSON — кладётся `{"raw_analysis": text}`; такой результат при прямой попытке считается неуспехом и переходит к скачиванию.
- Модель: `gemini-2.5-flash` (константа GEMINI_MODEL), `response_modalities=["TEXT"]`.
- Промпт (дословная структура JSON-ответа):
  - `hook`: `technique` (один из 10: pattern-interrupt, question, bold-claim, story-tease, visual-shock, curiosity-gap, direct-address, controversial-take, relatable-pain, transformation-preview), `opening_line` (первые 3 с), `attention_grab`, `replicable_formula`.
  - `content_structure`: `format` (problem-solution, listicle, story, tutorial, before-after, day-in-life, reaction, transformation, hot-take, tool-demo), `sections[]` (name, duration_pct, description), `pacing` (rapid-fire, fast, moderate, slow), `retention_techniques[]`.
  - `delivery_style`: `speaking` (direct-to-camera, voiceover, text-only, mixed, no-speech), `energy` (high-energy, conversational, calm-authority, urgent), `text_overlays` (bool), `visual_style`.
  - `cta_strategy`: `type` (comment-keyword, link-bio, follow, save, share, dm, none), `cta_text`, `placement`.
  - `why_it_works` (2-3 предложения).
- Подпись/caption обрезается до 1000 символов.
- Выход `video-analysis.json`: массив объектов `post_id, username, url, platform, engagement_score, engagement_rate, likes, comments, views, analysis{...}` или `error`.

### 6. content-planner (координатор репозитория)
- Вход: все файлы `.claude/context/`; ключи Apify/TubeLab/Gemini.
- Алгоритм:
  1. Прочитать контекст.
  2. Создать `content-plans/<ts>/`.
  3. Запустить 4 субагента параллельно (Task tool): X, Instagram, YouTube, TikTok; каждый выполняет свой скилл и возвращает JSON-сводку (`run_folder`, `total_posts`/`total_videos`, `outlier_count`, `top_topics` — топ-5).
  4. Прочитать `outliers.json` и `video-analysis.json` последних папок каждой платформы.
  5. Сгенерировать `content-ideas.md` по `references/content-ideas-template.md`.
  6. Сгенерировать 4 плейбука по `references/playbook-template.md`.
  7. Показать пользователю итог (объём, число выбросов, 2-3 кросс-вывода, топ-3 идеи из X, ссылки на файлы).
- Формула в SKILL.md: `opportunity_score = (x_engagement * 1.5) / (instagram_saturation + youtube_saturation + tiktok_saturation + 1)`.
  - `x_engagement`: нормализованный rate на X по шкале 0-10 «по перцентилю выбросов» (способ нормализации в шаблоне описан одной строкой; точная процедура не задана — проверить).
  - Насыщенность: 0 нет в выбросах площадки; 0.5 низкая (1-2 выброса); 1.0 средняя (3-5); 1.5 высокая (6+). В шаблоне формула двухплатформенная (без TikTok), в SKILL.md — трёхплатформенная: несогласованность.
- Кросс-платформенный матчинг тем: ключевые слова/хэштеги каждой площадки -> нормализация (lower, без # и @, «stem common variations») -> термины, встречающиеся минимум на 2 площадках -> ранг по суммарному вовлечению.
- Структура `content-ideas.md` (шаблон): Executive Summary; Tier 1 «Emerging (X-sourced)» — таблица (идея, X engagement, присутствие в IG/YT, opportunity score) + карточки топ-10 (source tweet, why it's working, engagement proof, cross-platform potential, 3 suggested angles); Tier 2 «Cross-Platform Winners» топ-5 (платформы, лучший формат на каждой, суммарное вовлечение); Tier 3 «Platform-Specific Hits» (IG топ-3, YT топ-3); тренды (кросс-платформенные и по площадкам); календарь на 2 недели (день, платформа, идея, формат, хук); источники данных.
- Структура плейбука (шаблон): Quick Stats; Winning Hooks (5-10; создатель, opening line, why it works, формула, метрики, ссылка, как применить в 3 шагах, 2 вариации); Content Formats (распределение формат/кол-во/%/ср. вовлечение; топ-5 форматов); Structure Patterns (тайминги 0-3 с, 3-7 с, 7-45 с, 45-60 с; топ-3 паттерна и «success rate»); CTA Strategies; тренды/хэштеги/слова (+ звуки для TikTok); топ-15 выбросов; действия на неделю; хуки для теста; аккаунты; метаданные запуска.
- Ошибка в тексте: путь указан как «`head-of-marketing` working directory» (старое имя проекта).

## Библиотеки и программы
- Язык: Python 3.8+ по README; в коде используются аннотации `list[dict]`, `str | None` — реально нужен Python 3.10+ (для `str | None` в find_outliers.py). Проверить.
- Пакеты (CLAUDE.md): `apify-client`, `google-genai`, `requests`, `python-dotenv`, `opencv-python-headless`, `mediapipe`, `Pillow`, `numpy`. Версии нигде не зафиксированы; requirements.txt и pyproject нет.
- Фактически импортируются в скриптах: `apify_client`, `google.genai`, `requests`, `dotenv` (необязательный; без него работают переменные окружения). YouTube-скрипты используют только стандартную библиотеку (urllib).
- opencv, mediapipe, Pillow, numpy в коде НЕ используются; CLAUDE.md упоминает «thumbnail generation» и `.claude/context/reference_images/` (фото лица, имена с позой) и `*.task` MediaPipe — соответствующих скриптов в репозитории нет (остатки удалённой функции, в .gitignore строки сохранены).
- ffmpeg, Node, Remotion, Whisper не используются.
- macOS: hook `afplay` (звук Glass.aiff), README требует macOS.

## Внешние сервисы
- Apify (платно/бесплатно): токен `APIFY_TOKEN`. Акторы: `apidojo/tweet-scraper` (X; README: нужна платная подписка), `apify/instagram-profile-scraper`, `apify/instagram-scraper`, TikTok `GdWCkxBtKWOsKjdch` (clockworks/tiktok-scraper). Стоимость по README: free tier $5/мес; прогон обычно $0.10-$0.50. Расчёт по каждому актору не приведён.
- TubeLab (YouTube): `TUBELAB_API_KEY`. Эндпоинты: `GET /v1/channel/videos/{id}`, `GET /v1/search/outliers`, `GET /v1/video/transcript/{id}` на `public-api.tubelab.net`. README: есть бесплатный тариф, платные от ~$29/мес. В README и .env.example ссылки на получение ключа разные (tubelab.net/settings/api и tubelab.net/developers).
- Google Gemini API: `GEMINI_API_KEY`; README: free tier «60 запросов в минуту» (актуальность лимита проверить). Используются generate_content и Files API.
- В README и коде ссылки реферальные (fpr=ih20xe для Apify, ref=brad для TubeLab) — при копировании текста убрать.
- Прочего (TTS, видео-генераторы, публикация, платежи) нет.

## Модели
- LLM для разбора видео: Google `gemini-2.5-flash` (единственная зашитая модель).
- LLM для отчётов, плана, выводов: «тот агент, в котором запущен скилл» (в README — Claude; модель не указана).
- TTS, генерация видео, генерация изображений: нет. (CLAUDE.md упоминает Gemini для «thumbnail generation», но кода нет.)

## Агенты, в которых работает
- Заявлено: только Claude Cowork (Claude Desktop, macOS, план Max для кастомных скиллов) и Claude Code (CLAUDE.md). Установка — загрузка .skill-файлов через Settings -> Capabilities -> Skills.
- Что мешает переносу:
  - Формат SKILL.md с frontmatter (`name`, `description`) совместим по идее с другими агентами, поддерживающими SKILL.md; пути жёстко `.claude/skills/...` и `.claude/context/...` в SKILL.md и в значениях по умолчанию скриптов (`--accounts-file .claude/context/x-accounts.md`) — для Codex/Kimi/OpenCode нужно параметризовать.
  - content-planner использует «Task tool» для запуска 4 параллельных субагентов — в Codex/Kimi/OpenCode имена и семантика другие (проверить), нужен запасной последовательный режим.
  - `.claude/settings.json`: один хук Stop, команда `"$CLAUDE_PROJECT_DIR"/.claude/hooks/stop-sound.sh`. Скрипт: если `CLAUDE_DELEGATED=1`, то `afplay /System/Library/Sounds/Glass.aiff` (только macOS), всегда exit 0. Переменная `$CLAUDE_PROJECT_DIR` специфична для Claude Code. Для переноса хук просто не нужен.
  - CLAUDE.md: правило «никогда не использовать web search/WebFetch для ресёрча соцсетей» (запрещены встроенные инструменты); режим делегирования `CLAUDE_DELEGATED=1` и протокол callback (обновить task-файл статусом `complete`/`in-progress`, ключевые находки, абсолютные пути) — завязан на внешний проект «second-brain» и путь `~/Documents/GitHub/head-of-content/...`. В других агентах аналог — AGENTS.md; CLAUDE.md придётся перенести.
  - Скиллы запускаются с рабочим каталогом = корень репозитория (относительные пути, `.env` читается из cwd через `load_dotenv()`; YouTube-скрипты ищут `.env` вверх от файла скрипта до 10 уровней). Субагентам нужно `export $(cat .env | grep -v '^#' | xargs)`.
  - Имена инструментов (Read, Task, Bash) в тексте SKILL.md не перечислены явно, кроме «Task tool» в content-planner — перенос в основном лёгкий.
  - Нет разрешений/allowlist в settings.json (только хук).
  - Скрипты Python — агент-независимы (CLI с argparse).

## Файлы между шагами
Структура папок (создаётся в корне репозитория; в .gitignore):
```
x-research/<ts>/{raw.json, outliers.json, video-analysis.json, report.md}
instagram-research/<ts>/{raw.json, outliers.json, video-analysis.json, report.md}
tiktok-research/<ts>/{raw.json, outliers.json, video-analysis.json, report.md}
youtube-research/<ts>/{outliers.json, filtered-outliers.json, video-analysis.json, report.md, thumbnails/*.jpg, transcripts/*.txt, [raw-data.json]}
content-plans/<ts>/{content-ideas.md, x-playbook.md, instagram-playbook.md, youtube-playbook.md, tiktok-playbook.md}
.claude/context/{x-accounts.md, instagram-accounts.md, tiktok-accounts.md, youtube-channel.md}   # ввод пользователя
```
- `<ts>` = `YYYY-MM-DD_HHMMSS` (date +%Y-%m-%d_%H%M%S).
- Контекст — таблицы Markdown `| Username | Niche | Notes |`; `@example` пропускается. Парсер ищет первую колонку, начинающуюся с `@`.
- raw.json: массив объектов Apify (X: сырой; IG: сырой + ownerFollowersCount/ownerFollowingCount; TikTok: нормализованный + `_raw`).
- outliers.json (X, слим): `generated, total_posts, outlier_count, threshold, topics{hashtags[[tag,count]], mentions, keywords}, content_patterns{counts{has_media, has_link, has_thread, is_quote, question, list_format, short_tweet, medium_tweet, long_tweet}, percentages{...}}, accounts[], outliers[{url, text, created_at, is_retweet, is_quote, metrics{likes, retweets, replies, quotes, bookmarks, views}, engagement_score, engagement_rate (округл. до 2 знаков), author{username, name, followers}, media[]}]`.
- outliers.json (Instagram): `generated, total_posts, outlier_count, threshold, topics{hashtags, keywords}, accounts, outliers[полные посты + _engagement_score + _engagement_rate]`.
- outliers.json (TikTok): то же, но `total_videos`, `topics{hashtags, sounds, keywords}`.
- outliers.json (YouTube): `outliers[{id, videoId, url, title, description, channelTitle, viewCount, likeCount, commentCount, zScore, publishedAt, channelSubs, transcript_path}], keywords, adjacent_keywords, total_videos`.
- video-analysis.json: см. раздел video-content-analyzer.
- Склейка content-planner: берёт «latest» папку каждой платформы (способ выбора latest — по сортировке имён, явно не описан).
- Связи в формате: единого схемного файла нет; единственный жёсткий контракт — поля, которые ждёт video-content-analyzer (PLATFORM_MAPPINGS).

## Берём
(лицензия MIT — код и тексты можно использовать с сохранением notice)
- Для шага 1 (ресёрч конкурентов):
  - Схему «fetch -> outliers -> анализ видео -> report» и привычку писать в timestamp-папки с `raw.json`/`outliers.json`/`report.md`.
  - Статистический порог выброса `mean + 2.0*stdev` по rate (rate = взвешенное вовлечение / подписчики) и весовые коэффициенты по площадкам как стартовые значения; для Telegram и Threads веса придётся задать самим.
  - YouTube: идею `zScore * recency_boost (5%/день, минимум 0.3)` и два набора запросов (прямая ниша / смежная аудитория, пороги 5K/10K просмотров); схему анализа канала (`channel-analysis-schema.md`: audience[who, objections, transformation, stake], keywords, adjacent-keywords, formulas, voice) — подходит как ядро шага 0 (паспорт бренда) и входа шага 1.
- Для шагов 1, 6, 7: промпт и JSON-схему video-content-analyzer (10 типов хука, 10 форматов, структура с `duration_pct`, `cta_strategy`, `replicable_formula`) — готовая основа для «разбора видео конкурентов» и для шаблонов хуков в сценариях. Модель заменяемая; видеовход есть не у всех агентов, поэтому нужен вариант на транскрипте (идея из youtube-research: транскрипт в файл + разбор текстом).
- Для шагов 2 и 3: шаблон `content-ideas-template.md` (тиры идей, таблица возможностей, календарь на 2 недели) и `opportunity_score` как простую метрику «высокий отклик / низкая насыщенность»; плейбук-шаблон (хук -> как применить в 3 шага -> вариации) как формат выхода банка хуков.
- Для ★ (координатор): паттерн content-planner — параллельные субагенты, каждый возвращает короткий JSON-сводку (`run_folder`, `total`, `outlier_count`, `top_topics`), координатор читает файлы с диска, а не результаты чата.
- Для шага 15 (косвенно): наблюдение, что тип CTA `comment-keyword` отдельным значением в классификаторе — можно использовать при разборе чужих воронок «кодовое слово».
- Код `fetch_*`/`analyze_posts.py` брать только как референс (см. слабые места); `analyze_posts.py` у Instagram и TikTok практически идентичны (diff — только поля и веса) — объединить в один скрипт с конфигом площадки.

## Не берём
- Скрипты Apify как есть: привязаны к англоязычным аккаунтам (`tweetLanguage: "en"`, `language=en`, регэксп слов `[a-zA-Z]{4,}` не видит кириллицу) и к западным площадкам; наш рынок — Reels, YouTube, Telegram, Threads, TikTok на русском (без ВК). Нужны другие источники (проверить отдельно).
- Установку через .skill-архивы и Claude Desktop/Cowork (платный план Max, только macOS) — у нас мульти-агентная раздача.
- Hook `stop-sound.sh` и `settings.json` — звук macOS, нужен только для делегирования из «second-brain».
- Режим делегирования и callback из CLAUDE.md — завязан на чужую систему.
- Реферальные ссылки в README.
- Нерабочие/мёртвые части: `opencv`, `mediapipe`, `Pillow`, `numpy`, `reference_images` в CLAUDE.md.
- Генерация и монтаж: в репозитории нет, брать нечего (шаги 4, 5, 8, 10-15).

## Слабые места
1. `x-research` вызывает `analyze_videos.py --platform x`, но у скрипта `choices=['instagram','tiktok','youtube']` — вызов упадёт на argparse (проверено чтением кода, не запуском). Видео из X-выбросов с `media` как список URL не соответствуют ни одному маппингу.
2. `x-research/fetch_tweets.py`: парсер аккаунтов ждёт строку заголовка таблицы, начинающуюся с `| Handle`, а шаблон `x-accounts.md` и README используют `| Username` — по шаблону парсер аккаунтов не включит режим таблицы и вернёт 0 аккаунтов («No valid handles found»); работает только с `--handles` или если переименовать колонку. У Instagram и TikTok парсеры принимают оба варианта.
3. Несогласованность значений по умолчанию: скрипт Instagram по умолчанию `--type posts`, SKILL.md везде `reels`.
4. Нормализация rate: при отсутствии подписчиков Instagram/TikTok rate = абсолютный score (не процент) — такие посты искажают среднее и стандартное отклонение; у X подставляется followers=1.
5. Порог mean + 2σ считается по всей выборке (все аккаунты вместе); один крупный аккаунт с малым числом постов может смещать выборку; на малых выборках (<~20 постов) 2σ даёт 0-1 выбросов, отдельного запасного правила нет (кроме «<2 постов = все выбросы»).
6. Время публикации не учитывается: пост 1 дня и 30 дней сравниваются по накопленной метрике (recency есть только у YouTube).
7. TikTok: в анализатор отдаётся `webVideoUrl` (страница, не файл); в SKILL.md сам признано «Gemini will attempt to analyze from this page URL». Запасной путь скачивает по этой же ссылке HTML как «mp4» — на практике, вероятно, не сработает; проверить. Актор TikTok отключён от скачивания видео (`shouldDownloadVideos: False`).
8. Instagram: `videoUrl` из CDN имеет срок жизни; скачивание без проверки размера; видео в память целиком.
9. Скачивание/анализ видео — чужой контент, ограничений и согласий нет; правовой и политикоплатформенный риск ToS (скрейпинг) — проверить.
10. Отчёты `report.md`, content-ideas и плейбуки пишет сам агент по длинному шаблону без валидации; метрики вроде «Success rate», «saturation 0/0.5/1/1.5», перцентильная нормализация — на усмотрение модели, воспроизводимость низкая.
11. content-planner: формула насыщенности в шаблоне и SKILL.md различается (2 vs 3 площадки); нет шага проверки, что все 4 субагента завершились успешно (кроме описания в CLAUDE.md про `in-progress`); путь «head-of-marketing» устарел.
12. Нет тестов, нет requirements.txt, нет пина версий; Gemini-модель зашита в константе; `.env` ищется по-разному (cwd в Apify-скриптах, вверх от файла в YouTube-скриптах).
13. Несоответствие README и кода: README «6 .skill файлов» и список без x-research в шагах Quick Start (в списке x-research есть, в таблице «Available Skills» нет `video-content-analyzer`); CLAUDE.md описывает «reference_images» и «thumbnail generation», которых нет; в README отмечено «Python 3.8+», код требует 3.10+ (`str | None`).
14. «Только свои данные»: ресёрч идёт по списку аккаунтов, который задаёт пользователь, и только по своему каналу для YouTube; автоматического подбора конкурентов нет.
15. Ключевые слова на английском; тематического/семантического кластеринга нет (подсчёт слов + совпадение строк).

## Открытые вопросы
- Актуальная версия/дата последнего коммита и история на GitHub (нет .git): проверить.
- Как именно Gemini 2.5 Flash принимает прямой URL: поддерживаются ли ссылки Instagram CDN/TikTok page, и как это ведёт себя на практике (лимиты размера/длительности, квоты free tier): проверить.
- Стоимость прогона по каждому актору Apify (особенно X: платная подписка) и актуальные тарифы TubeLab: проверить; TubeLab — есть ли аналог для русскоязычного YouTube (параметр `language`, поддержка `ru`).
- Какие источники заменят Apify для Telegram и Threads (задача нашего шага 1): в репозитории нет. Для Telegram есть `t.me/s/<канал>` из воркшопа.
- Как в Codex / Kimi Code / OpenCode запускать параллельных субагентов и читать каталоги скиллов (`.claude/skills` против других путей); формат frontmatter и допустимая длина description у каждого агента: проверить.
- Нужен ли нам видеоанализ через Gemini или достаточно транскрипта + обложки (для агентов без видеовхода).
- Юридическая сторона: скрейпинг и скачивание чужих видео для анализа (ToS Instagram/TikTok/X): проверить.
- Что в реальности делает «stem common variations» при кросс-платформенном матчинге (в коде отсутствует, описано только в тексте шаблона).
- Нормализация `x_engagement` до шкалы 0-10 «по перцентилю» — точной формулы нет; потребуется своя.
