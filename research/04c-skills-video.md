# 04c. Создание видео: скиллы, плагины, MCP, CLI

Дата: 2026-11-27. Метод: WebSearch + WebFetch (README/страницы репозиториев, api.github.com). Сеть из shell закрыта. Второй проход (после сброса лимита) закрыл GigaAM, лицензию remotion-dev/skills, qc-skill, YouTube Clipper, vc.ru, securitylab, Hedra, Higgsfield, safe zones; результаты внесены в таблицы и в раздел 6. Остаток непроверенного — в конце файла; везде «проверить».

Общие оговорки:
- Дата последнего коммита: api.github.com отдал `pushed_at` не для всех репозиториев (для ffmpeg-skill, claude-shorts, op7418 — client_error). Известные даты: GigaAM 2026-08-17, remotion-dev/skills 2026-10-19, qc-skill 2026-11-21, browser-use/video-use 2026-08-26, director-skills 2026-06-02, heygen-com/skills 2026-07-14. Остальные — «проверить».
- Агенты: скилл формата SKILL.md модель-независим (DeepSeek как LLM работает, если агент его поддерживает); реальное ограничение — вызов shell/MCP и OAuth-вход удалённых MCP в конкретном клиенте. Kimi Code и DeepSeek-связки: не проверялись, везде «проверить».
- Ориентир (уже разобрано, не находка): claude-code-video-toolkit, OpenMontage, rea-video, воркшоп (Remotion). Известные: remotion-dev/skills, AgriciDaniel/claude-shorts, capsule-cinema, HyperFrames.

---

## 1. Раскадровка (шот-листы, промпты по кадрам, консистентность)

| Название / ссылка | Тип | Лицензия | Звёзды / коммиты | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| aicontentskills/ai-video-storyboard-skill — https://github.com/aicontentskills/ai-video-storyboard-skill | SKILL.md | MIT | 66 зв., 2 коммита | Бриф -> раскадровка: общий визуальный «тема-слой» (палитра, свет, объектив, моушн), 6-18 шотов, промпты 40-80 слов, аудио-направление, чек-лист постпродакшна | не заявлен; проверить | Claude Code, Cursor, Windsurf; ChatGPT/Claude.ai как проект | ключей нет | Берём идею: тема-слой как приём консистентности. Приёма для лица/персонажа нет. 2 коммита — сыро |
| 0xhughs/director-skills — https://github.com/0xhughs/director-skills | набор из 9 SKILL.md | MIT | 24 зв., 8 коммитов | shotlist-and-visual-breakdown, character-location-prop-bible, cinematic-image/video-prompting, prompt-iteration-and-diagnostics, model-adaptation (подстройка под модель) | не заявлен; проверить | любой агент, читающий папки скиллов (Claude, Codex, Cursor и др.) | ключей нет | Берём идею (character bible + shotlist + шаг «lock continuity»). Кандидат на разбор целиком |
| Gregory-Esman/ai-film-pipeline — https://github.com/Gregory-Esman/ai-film-pipeline | 4 SKILL.md | MIT | 12 зв., 40 коммитов | banana-pro-director (промпты картинок: face lock, character sheet), cinema-worldbuilder (промпты Seedance, 10 блоков), ai-film-director (оркестратор), video-qa | не заявлен; проверить | Claude Code, Cowork, claude.ai (zip) | ключей нет сам; заточен под Higgsfield/Seedance | Берём идею: референс-листы персонажа -> промпты кадров -> QA кадров. Привязка к Higgsfield |
| square-zero-labs/video-prompting-skill — https://github.com/square-zero-labs/video-prompting-skill | SKILL.md | проверить | проверить | «Video Prompting (Agent Skill)» — найден только в выдаче, не открывал | проверить | проверить | проверить | проверить |
| H4pplness/storyboard-skill — https://github.com/H4pplness/storyboard-skill | SKILL.md | проверить | проверить | найден только в выдаче, не открывал | проверить | проверить | проверить | проверить |

Лучший вариант: director-skills (0xhughs) как основа структуры (bible -> shotlist -> промпты -> диагностика) + идея тема-слоя из ai-video-storyboard-skill. Консистентность лица на уровне инструмента решается не скиллом, а моделью (референс-картинки в Seedance/Kling/Higgsfield), скилл лишь дисциплинирует промпты.

---

## 2. Генерация

### 2а. Аватар / говорящая голова

| Название / ссылка | Тип | Лицензия | Звёзды | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| HeyGen MCP — https://developers.heygen.com/mcp/claude-code ; docs https://docs.heygen.com/docs/heygen-mcp-server | удалённый MCP (HTTP, OAuth) | сервис, не OSS | — | Видео с аватаром по описанию: сценарий, выбор аватара, рендер; результат в Projects HeyGen | не заявлен на странице MCP; у translate-скилла «175+ языков»; озвучку RU проверить | Claude Code (`claude mcp add --transport http ... https://mcp.heygen.com/mcp/v1/`); Codex/OpenCode/Kimi — проверить | аккаунт HeyGen; MCP списывает кредиты тарифа; цены не найдены | Берём как платный канал аватара. Качество RU-липсинка проверить |
| heygen-com/skills — https://github.com/heygen-com/skills | 3 SKILL.md | MIT | 443 зв., 264 коммита | heygen-avatar (фото -> цифровой двойник, файл AVATAR-NAME.md), heygen-video (идея -> сценарий -> видео), heygen-translate (дубляж + клон голоса + lipsync) | translate: 175+ языков; RU проверить | Claude Code, Codex, OpenClaw, Cursor; через `gh skill install`: Gemini CLI, Copilot, OpenCode, Cline, Goose и др. | MCP (OAuth) — кредиты плана; CLI с API-ключом — отдельный биллинг API | Берём целиком как скилл-обёртку (хорошая совместимость). Для тиража — считать стоимость |
| Hedra MCP — https://www.hedra.com/docs/pages/developer/v3/mcp.md | удалённый MCP (`https://mcp.hedra.com`) | сервис | — | Инструменты: list_models, get_model, estimate; генерация image/video/speech/music/SFX. Есть CLI `hedra-cli` | страница языки не описывает; проверить | Claude, Claude Code, Codex, Cursor, ChatGPT, Hermes | подписка Hedra или pay-as-you-go (выбор в настройках MCP); CLI/REST — предоплаченный кошелёк API | Берём как альтернативу HeyGen; RU проверить. Уточнение: страница MCP не описывает языки и липсинк-инструмент; в списке клиентов OpenCode нет; Codex: `codex mcp add hedra --url https://mcp.hedra.com`; цены только через `estimate` |
| SamurAIGPT Generative-Media-Skills (muapi) — https://github.com/SamurAIGPT/Generative-Media-Skills | skills + MCP | MIT | 42 зв., 3 коммита | 41 рецепт (видео/картинки/соцсети), lipsync-инструмент в MCP, Seedance 2, AI Clipping | проверить | Claude Code, Cursor, Gemini CLI, Windsurf, OpenCode | ключ muapi.ai, пополнение кредитов, цены не указаны | Берём идею; агрегатор третьей стороны, 3 коммита |
| Открытый lipsync: InfiniteTalk (на Wan 2.1), Wan2.2-S2V — через ComfyUI (https://comfyui-wiki.com/ru/models/wan/infinitetalk) | модели + ComfyUI-воркфлоу, не скилл | проверить | — | Аудио + портрет -> видео с липсинком, локально | аудио-управляемая модель; языко-независима в принципе, RU-качество проверить | вне агентов; скилла/MCP не найдено | нужен GPU; лицензия моделей — проверить | Берём идею (бесплатный вариант). Готового скилла не нашёл |

Лучший вариант: heygen-com/skills (MIT, 443 зв., широкий список агентов) — но платно; бесплатный путь — InfiniteTalk/ComfyUI без агентского скилла.

### 2б. Видео (Kling, Veo, Seedance, Hailuo, Wan, LTX) через агрегаторы и скиллы промптов

| Название / ссылка | Тип | Лицензия | Звёзды | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| fal MCP (официальный) — https://fal.ai/docs/documentation/setting-up/mcp.md | удалённый MCP (`https://mcp.fal.ai/mcp-relay`, OAuth) | сервис | — | search_models, recommend_model, get_model_schema, get_pricing, run_model, submit_job/check_job/get_job_result, upload_file; доступ к каталогу моделей fal | зависит от модели; проверить | установщик ставит в Claude Code, Codex CLI, Cursor, VS Code, Gemini CLI, opencode и др.; Kimi — проверить | MCP бесплатен, платные запуски по кредитам fal, `get_pricing` показывает цену | Берём целиком: лучший универсальный вход к Kling/Veo/Seedance/Wan/LTX (какие именно модели в каталоге — проверить) |
| Replicate MCP (официальный) — https://mcp.replicate.com/ | удалённый MCP (SSE) | сервис | — | search_models, create_predictions, list_hardware (список обрезан) | зависит от модели | Claude Code, Codex (`npx replicate-mcp`), Cursor, Gemini CLI, Windsurf | токен Replicate; цены на странице нет | Берём как резерв к fal |
| Higgsfield MCP / CLI / Skills — https://higgsfield.ai/mcp ; https://higgsfield.ai/skills | удалённый MCP `https://mcp.higgsfield.ai/mcp` + CLI + skills | сервис | — | «30+ моделей картинок/видео», готовые воркфлоу: UGC-обзоры, пересъёмка референс-видео со своим персонажем, варианты хуков | не заявлен | Claude, Claude Code, ChatGPT-плагин, Telegram, CLI; Codex/OpenCode — проверить | ключ не нужен (вход); цены/кредиты на странице не найдены — проверить | Берём идею; полезно для персонажа-референса. Уточнение: страница /mcp упоминает Claude, Claude Code, ChatGPT, Telegram, CLI, «любой MCP-клиент»; Codex/OpenCode не упомянуты, список инструментов и цены не приведены. Сторонняя статья (pexo.ai) утверждает: Soul ID для фиксации персонажа, работает в Codex как MCP или скилл — не подтверждено первоисточником |
| dexhunter/seedance2-skill — https://github.com/dexhunter/seedance2-skill | SKILL.md (промпты Seedance 2.0) | MIT | 4.4k зв., 5 коммитов | Синтаксис @-референсов, язык камеры, шаблоны (реклама, драма, клип, обучение) | EN и ZH; RU нет | Claude Code, Cursor, Cline | ключей не требует (только промпты) | Берём целиком как справочник промптинга Seedance |
| songguoxs/seedance-prompt-skill — https://github.com/songguoxs/seedance-prompt-skill | SKILL.md | проверить | проверить | Аналог по Seedance, только по выдаче | проверить | проверить | — | проверить |
| raveenb/fal-mcp-server (или luminarylane/fal-mcp-server) — https://github.com/raveenb/fal-mcp-server | локальный MCP, community | MIT | 61 зв., 137 коммитов | 18 инструментов: картинки, видео (Kling, Hunyuan, MiniMax, SVD), музыка; README: 600+ моделей. README ссылается на другой владелец — репозиторий мог переехать | не заявлен | любой MCP-клиент | ключ fal | Не берём: есть официальный fal MCP |

Лучший вариант: официальный fal MCP + dexhunter/seedance2-skill для промптов. Hailuo, Veo, LTX и Wan — доступность в fal/Replicate проверить в каталоге. Отдельных агентских скиллов под Kling/Veo/Hailuo кроме обёрток muapi не нашёл (проверить).

### 2в. Голос (озвучка RU, клонирование), музыка

| Название / ссылка | Тип | Лицензия | Звёзды | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| elevenlabs/skills — https://github.com/elevenlabs/skills (wiki: /wiki) | 13 SKILL.md (Agent Skills spec) | MIT | проверить | text-to-speech, speech-to-text (с таймкодами), music, sound-effects, voice-changer, voice-isolator, dubbing; установка `npx skills add elevenlabs/skills` | на странице RU не упомянут; сервис RU поддерживает — проверить качество | «любой совместимый агент»; оценки требуют Cursor Agent CLI | ключ ElevenLabs; платно | Берём целиком (озвучка, музыка, SFX, дубляж). Клонирование голоса в скиллах явно не указано — проверить |
| elevenlabs/elevenlabs-mcp — https://github.com/elevenlabs/elevenlabs-mcp | локальный MCP | MIT | 1.5k зв., 79 коммитов | TTS, клонирование голоса, транскрипция, изоляция звука, speech-to-speech, video-to-music, voice design. **Архивирован 2026-08-20, заменён хостируемым MCP ElevenLabs** | не заявлен | любой MCP-клиент | free tier 10k кредитов/мес | Не берём (архив). Брать хостируемый MCP (ссылку/условия — проверить) |
| QwenLM/Qwen3-TTS — https://github.com/QwenLM/Qwen3-TTS | модель (не скилл) | Apache-2.0 | 14.4k зв., 13 коммитов | Открытый TTS, 10 языков вкл. русский, клон голоса по ~3 сек референса, 0.6B и 1.7B | Да (русский в списке). Хабр: возможны неверные ударения, проблемы с длинными текстами | вне агентов; скилла/MCP не нашёл | локально, GPU (в сборке автора 8+ ГБ VRAM) | Берём для разбора: бесплатный открытый RU-TTS с клоном. Обёртку-скилл писать самим |
| Hedra MCP (speech/music/SFX) — см. 2а | MCP | сервис | — | Речь и музыка в том же MCP | проверить | см. 2а | см. 2а | проверить |
| Fish Speech, F5-TTS, Silero, XTTS | модели | проверить | — | В запросе упомянуты, карточки не открывал | проверить | — | — | проверить |

Лучший вариант: платный путь — elevenlabs/skills; бесплатный — Qwen3-TTS (RU + клон, Apache-2.0). Музыка: music-скилл ElevenLabs; Suno через muapi (SamurAIGPT) — проверить условия.

---

## 3. Нарезка длинного видео в шорты

| Название / ссылка | Тип | Лицензия | Звёзды / коммиты | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| AgriciDaniel/claude-shorts — https://github.com/AgriciDaniel/claude-shorts | SKILL (известен) | MIT | 324 зв., 27 коммитов | 10 шагов: faster-whisper (word timestamps), Claude оценивает 8-12 сегментов по 5 критериям (порог 60), MediaPipe-кроп по лицу/говорящему, Remotion-субтитры (Bold, Bounce, Clean) | не заявлен; faster-whisper знает RU. Шрифты Montserrat/Bangers/Inter — кириллицу проверить | Claude Code; остальные проверить | локально, ключей нет; PyTorch, Remotion, ffmpeg | Лучший по трекингу лица. Нужна проверка кириллицы в шрифтах |
| louisedesadeleer/clipify — https://github.com/louisedesadeleer/clipify | SKILL / слэш-команда `/clipify` | MIT | 612 зв., 6 коммитов | Поиск моментов, нарезка, 16:9 -> 9:16, пословные субтитры; Whisper; говорящий определяется по движению рта через ffmpeg (без модели лиц); всё локально | не заявлен; проверить | Claude Code | локально, ключей нет | Берём идею (трекинг по движению рта без MediaPipe). Проверить RU и кириллицу |
| AgriciDaniel/claude-video (claude-video-shorts) — https://github.com/AgriciDaniel/claude-video | набор из ~15 суб-скиллов | MIT | 31 зв., 8 коммитов | edit, transcode, caption (Whisper, анимированные пословные субтитры), analyze, shorts, export, generate, promo; 3 агента-определения | RU не упомянут | Claude Code | AI-генерация — ключи проверить | Берём идею (структура), перекрывается с уже разобранным toolkit |
| browser-use/video-use — https://github.com/browser-use/video-use | SKILL.md + Python | MIT | 31.4k зв., 23 коммита | Редактирование видео агентом: вырезка слов-паразитов и пауз, цвет-грейд, 30 мс аудио-фейды, субтитры, оверлеи (HyperFrames, Remotion, Manim, PIL), память в project.md. Транскрипция — ElevenLabs Scribe | Scribe мультиязычный; RU проверить | Claude Code, Codex, Hermes, Openclaw, любой агент с shell | ключ ElevenLabs (платно), ffmpeg | Берём целиком для разбора: вырезка пауз и слов-паразитов. Зависимость от платного ASR |
| SamurAIGPT muapi-ai-clipping / muapi-youtube-shorts — https://github.com/SamurAIGPT/Generative-Media-Skills | SKILL (облако) | MIT | 42 зв. | AI-клиппинг через muapi API | проверить | Claude Code, OpenCode и др. | ключ muapi, платно | Не берём (облако, непрозрачно) |
| gooseworks-ai/goose-skills video-clipper — https://tessl.io/registry/skills/github/gooseworks-ai/goose-skills/video-clipper | SKILL | проверить | проверить | найден только в выдаче | проверить | проверить | проверить | проверить |

Лучший вариант: claude-shorts (пайплайн + трекинг) с заменой/добавлением clipify-приёма; ASR заменить на GigaAM/WhisperX для RU. Это слабое место: оба используют Whisper-класс, RU-тесты не заявлены.

---

## 4. Монтаж (Remotion, FFmpeg, субтитры, Whisper/GigaAM, паузы)

| Название / ссылка | Тип | Лицензия | Звёзды / коммиты | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| remotion-dev/skills — https://github.com/remotion-dev/skills | набор SKILL (известен) | у репозитория не указана (API: license null, файла LICENSE в корне не видно); сам Remotion — отдельная лицензия | 5.5k зв., 92 коммита, pushed_at 2026-10-19 | remotion-best-practices, remotion-captions, markup (аудио, композиции), multimedia (Mediabunny), render, create и др. Установка `npx skills add remotion-dev/skills` | субтитры общие; кириллица зависит от шрифта | любой агент с `npx skills`; конкретные — проверить | Remotion: бесплатно для частных лиц и малых команд, иначе лицензия — проверить условия | Берём целиком (уже известен) |
| kajisho5/ffmpeg-skill — https://github.com/kajisho5/ffmpeg-skill | SKILL.md + MCP + CLI | MIT | 5.2k зв., 513 коммитов | 42 инструмента FFmpeg: нарезка, субтитры, рефрейм, нормализация громкости, экспорт по платформам. Локально, только stdlib Python, без ключей | не специфично; кириллица в burn-in зависит от шрифта — проверить | Claude Code, Cursor, Codex, любой SKILL.md-агент, любой MCP-клиент, манифест Gemini CLI | бесплатно | Берём целиком: лучший кандидат на FFmpeg-слой и платформенный экспорт. Нужен разбор |
| browser-use/video-use — см. раздел 3 | | MIT | 31.4k зв. | Вырезка пауз, слов-паразитов, субтитры | RU через Scribe, проверить | Claude Code, Codex и др. | ElevenLabs | Берём (разбор) |
| theplasmak/faster-whisper — https://github.com/theplasmak/faster-whisper | OpenClaw-скилл + CLI | MIT | 11 зв., 68 коммитов | faster-whisper, word timestamps (выравнивание wav2vec2), SRT/VTT/ASS/LRC/JSON, диаризация pyannote, 99+ языков | Да (99+ языков, авто-детект); качество RU не измерено | OpenClaw-скилл; как CLI на Linux/macOS/Windows | бесплатно, GPU желателен (distil-large-v3.5 ~2 ГБ VRAM) | Берём идею (форматы ASS/SRT); для агентов Claude/Codex переупаковать |
| ASR для русского: GigaAM v3 (Sber) — https://github.com/salute-developers/GigaAM ; HF: https://huggingface.co/ai-sage/GigaAM-v3 ; сравнение https://habr.com/ru/articles/1042574/ | модель + Python-пакет | MIT (код, API); веса на HF — MIT | 785-937 зв. (страница / API), pushed_at 2026-08-17 | Модели v1/v2/v3 (ctc, rnnt, e2e) и multilingual (70+ языков, новость 2026/06). Пословные таймкоды есть: `model.transcribe(path, word_timestamps=True)` (новость 2026/04). `.transcribe` ограничен 25 с; длинное аудио — `transcribe_longform` через pyannote (нужен токен HF и принятие условий `pyannote/segmentation-3.0`). HF-карточка: WER v3_RNNT 8.4%, Whisper 25.1% (средние по наборам авторов). Хабр: GigaAM 10.38% против 13.25% у Whisper large-v3-turbo; на шумных YouTube 26.9% против 28.3% | Да, русский (v1-v3) | вне агентов; скилла/MCP не нашёл (обёртку писать самим) | бесплатно, локально; CPU в 20+ раз быстрее Whisper (Хабр) | Берём: основной RU-ASR для субтитров. Проверить: качество пословных таймкодов на реальных роликах, лицензия pyannote-модели |
| aystream/gigaam-mlx — https://github.com/aystream/gigaam-mlx | CLI | MIT | 13 зв. | MLX-порт GigaAM-v3 для Apple Silicon, выдаёт .srt/.txt; пословные таймкоды на странице не подтверждены | Да | CLI, любой агент с shell | бесплатно, только macOS M1+ | Берём идею (Mac). Для Linux не подходит |
| Qeca/GigaAM-mgt — https://github.com/Qeca/GigaAM-mgt | форк GigaAM | MIT | 0 зв., 31 коммит | Форк; показывает API `result.words` со start/end/text | Да | — | бесплатно | Не берём (форк); использовать upstream |
| clawhub remotion-word-highlight-subtitles — https://clawhub.ai/skills/remotion-word-highlight-subtitles | SKILL | проверить | проверить | Субтитры с подсветкой слов в Remotion; не открывал | проверить | OpenClaw/ClawHub | проверить | проверить |
| Скилл WhisperX (theplasmak) — https://skills.cat/skills/theplasmak/whisperx | SKILL | проверить | проверить | Найден, не открывал | проверить | проверить | проверить | проверить |
| moviepy-скиллы | — | — | — | Отдельного значимого скилла не нашёл | — | — | — | проверить |

Лучший вариант: связка remotion-dev/skills (рендер + субтитры) + kajisho5/ffmpeg-skill (FFmpeg, громкость, экспорт) + GigaAM/Whisper для RU-ASR. Ни один скилл не заявляет проверку кириллицы в субтитрах — проверять вручную (шрифт с кириллицей, переносы).

---

## 5. Проверка качества

| Название / ссылка | Тип | Лицензия | Звёзды / коммиты | Что делает | Русский | Агенты | Ключи / цена | Пригодность |
|---|---|---|---|---|---|---|---|---|
| kajisho5/qc-skill — https://github.com/kajisho5/qc-skill | CLI/скилл, измеритель | MIT | 6 зв. (API), 12 коммитов, pushed_at 2026-11-21 | Всегда: целостность декодирования, клиппинг, битые cue субтитров. Возможности: freeze, чёрные кадры, формат/разрешение, аудио (целостность, клиппинг, раскладка каналов, тишина, громкость), тайминг субтитров, целостность доставки. Вызов: `qc contract --json`, `qc doctor --json`, `qc run request.json --json` (operation inspect/check/validate, rules задаёт вызывающий). Результаты PASS/WARN/FAIL/UNKNOWN. Только измеряет; решения — у video-production-agent. Safe zones отсутствуют. docs/checks.md не открыт | не специфично | агентонезависим (CLI, JSON) | бесплатно, нужен ffmpeg/ffprobe | Берём на разбор как измерительный слой QC (громкость, чёрные кадры, субтитры). Safe zones дописывать самим. Часть экосистемы kajisho5/AI-video-production-OS (автор называет её незавершённой) |
| Gregory-Esman/ai-film-pipeline / video-qa — https://raw.githubusercontent.com/Gregory-Esman/ai-film-pipeline/main/video-qa/SKILL.md | SKILL.md | MIT | 12 зв. | ffmpeg вытаскивает кадры (1 fps, 2 fps для ключевых), сравнивает с референс-листами: дрейф персонажа, непрерывность; оценка 0-100, вердикт Ship/Hold/Block. Громкость и субтитры не проверяет | не специфично | Claude Code, Cowork, claude.ai | бесплатно (ffmpeg) | Берём идею визуальной проверки кадров агентом. Привязка к Higgsfield |
| kajisho5/ffmpeg-skill (loudness normalization, экспорт по платформам) | см. раздел 4 | MIT | 5.2k | Нормализация громкости и платформенные пресеты | — | см. раздел 4 | — | Берём (громкость); проверка целевого LUFS и safe zones — проверить |
| gooseworks-ai normalize-loudness — https://www.skills.sh/gooseworks-ai/gooseworks-ads-skills/normalize-loudness | SKILL | проверить | проверить | найден в выдаче, не открывал | проверить | проверить | проверить | проверить |
| agensi.io video-export-qa — https://agensi.io/skills/video-export-qa | SKILL (маркетплейс) | проверить | проверить | найден в выдаче, не открывал | проверить | проверить | возможно платный | проверить |

Лучший вариант: собственный QA-скилл из трёх частей: ffmpeg-skill (loudnorm) + qc-skill (измерения) + приём кадров-на-проверку из video-qa. Готового скилла «safe zones Reels/Shorts/TikTok» не нашёл.

---

## Русские и китайские источники
- vc.ru «Claude Code и Remotion» — https://vc.ru/ai/2872593-claude-code-i-remotion-sozdanie-video-shortsev — ОТКРЫТ. Упоминает remotion-dev/skills, digitalsamba/claude-code-video-toolkit, jhartquist/claude-remotion-kickstart. Про русские субтитры ничего. Ограничения по статье: лицензия Remotion (бесплатно до 3 человек, компаниям от 4 — платно), первый рендер 2-3 итерации, 30-40 мин на ролик, шрифты могут не подгрузиться, Claude путает секунды и кадры.
- securitylab.ru (PixelbyPixel) — https://www.securitylab.ru/blog/personal/PixelbyPixel/362417.php — ОТКРЫТ. Перечень: remotion-dev/skills, browser-use/video-use (нужен ключ ElevenLabs; локальная транскрибация в отдельном PR), Moh4696/freecut (форк video-use на Whisper), kajisho5/ffmpeg-skill, OpenClip-App/agent-skills, ElSalvatore-sys/video-editor-plugin (экспериментальный), kajisho5/AI-video-production-OS. Про русский язык данных нет, автор советует проверять ASR на своих материалах.
- teletype.in/@ythemark/claude-editor, teletype.in/@ailabshow/P8bOOdDAjCp (не открыл)
- vc.ru «50 лучших скиллов для Claude Code» — https://vc.ru/id5888266/2919293-50-luchshikh-skillov-dlya-claude-code-tablica-s-opisaniyami (не открыл)
- CSDN «YouTube Clipper Skill» — https://deepseek.csdn.net/6a3e1120662f9a54cb84a1f0.html — ОТКРЫТ. Репозиторий: https://github.com/op7418/Youtube-clipper-skill (MIT, 2.3k зв., 2 коммита, README en/zh). Скачивает готовые английские субтитры через yt-dlp (ASR нет), режет по смыслу на главы 2-5 мин, переводит субтитры пакетами по 20 строк (по умолчанию на китайский, целевой язык в .env), вшивает двуязычные субтитры через libass. Для RU-контента не подходит как есть (нет ASR); берём идею пакетного перевода и вшивки через libass. Только Claude Code (`~/.claude/skills/`).
- bilibili «1 Skill для авто-субтитров» — https://www.bilibili.com/read/cv49864155 (не открыл)
- Агрегаторы для дальнейшего поиска: https://vibehackers.io/claude-code/category/media-video , https://agentskillsfinder.com/category/video-editing , https://skills.sh (поиск по "video") — обход не завершён.
- wilwaldon/Claude-Code-Video-Toolkit — https://github.com/wilwaldon/Claude-Code-Video-Toolkit (найден, не открывал; не путать с digitalsamba)

## 6. Дополнения второго прохода

### 6.1 Safe zones Reels/Shorts/TikTok
Готового агентского скилла или CLI с проверкой safe zones не найдено. Найдено:
| Название / ссылка | Тип | Лицензия | Что делает | Пригодность |
|---|---|---|---|---|
| portel-dev/skills vertical-video-design — https://skills.sh/portel-dev/skills/vertical-video-design | SKILL (правила) | не указана | Правила, не проверка: центральные 70% кадра безопасны, внешние 30% за платформой; субтитры, соотношения, Remotion. Пошагового числа по платформам не видно; 4 установки, 1 зв., с 2026-04-16 | Берём идею как справочник правил для Remotion-шаблона; 4 установки — сыро |
| WaveSpeed Vertical Safe Zone Checker — https://wavespeed.ai/free-tools/vertical-safe-zone-checker | веб-инструмент, в браузере | не указана; открытость кода не подтверждена | 6 пресетов; для 1080x1920 самый безопасный: сверху 14% (269 px), снизу 25% (480 px); колонка кнопок справа; выгрузка PNG-оверлея и таблицы отступов. Самим сервисом названы консервативными ориентирами, не официальными | Берём числа и идею; CLI/API нет, автоматизировать нельзя |
| reap.video — https://reap.video/blog/short-form-video-safe-zones | статья | — | Рабочие отступы: верх ~15% (288 px), низ 25-35% (480-672 px), бока 10-15% (108-162 px). Автор: единой зоны нет, значения не официальные | Источник чисел |
| blitzcutai.com — https://blitzcutai.com/blog/safe-zones-youtube-shorts-reels-tiktok | статья | — | Справа ~15-20% (Shorts), ~20% (Reels, TikTok); низ 25-30%; лица и текст — в верхних 60% кадра. Пиксели в статье не даны | Источник чисел |
| Kapwing, Tella, Flixier, Pallyy, NovusTools (dev.to) | веб-превью с оверлеем | — | Визуальные превью; код NovusTools (vanilla JS) не опубликован | Не автоматизируются |
Вывод: проверку safe zones реализовать самим — скрипт: кадры ffmpeg + проверка bbox текста/лица (OCR или из разметки Remotion) против зон из таблицы (верх 14-15%, низ 25-30%, справа 15-20%, слева 10%). Значения не официальные; сверять на реальном телефоне.

### 6.2 Новые находки
| Название / ссылка | Лицензия | Звёзды | Что делает | Русский | Агенты | Цена | Вывод |
|---|---|---|---|---|---|---|---|
| heygen-com/hyperframes — https://github.com/heygen-com/hyperframes | Apache-2.0 | 90.7k, 8171 коммит | HTML/CSS/GSAP -> детерминированный MP4 (headless Chrome + FFmpeg), 9 скиллов (`/hyperframes`, `/media-use`); `npx skills add heygen-com/hyperframes`; Studio бесплатно, Pro $25/мес | кириллица не упомянута; проверить | Claude Code, Codex, Cursor, Gemini CLI, Copilot | бесплатно (CLI) | Берём на сравнение с Remotion: лицензия свободнее (нет порога по размеру команды) |
| jhartquist/claude-remotion-kickstart — https://github.com/jhartquist/claude-remotion-kickstart | MIT | 120, 4 коммита | Шаблон Remotion: компоненты слайдов/кода/субтитров, `/generate-image`, `/generate-video` (Replicate), `/transcribe` (Deepgram), озвучка ElevenLabs MCP; автор называет проект экспериментом | нет | Claude Code | ключи Replicate/Deepgram/ElevenLabs по необходимости | Берём идею; сам Remotion требует лицензию от 3 сотрудников |
| Moh4696/freecut — https://github.com/Moh4696/freecut | MIT | 286, 2 коммита | Форк video-use: вместо ElevenLabs Scribe — локальный Whisper (mlx-whisper на Apple Silicon, иначе faster-whisper), без диаризации; вырезка слов-паразитов и пауз, субтитры | не заявлен; Whisper знает RU | Claude Code, Codex (симлинк), Hermes, Openclaw | бесплатно | Берём: бесплатная замена платному ASR в video-use; RU проверить |
| OpenClip-App/agent-skills — https://github.com/OpenClip-App/agent-skills | MIT (скиллы); сервис коммерческий | 1 | Скиллы к облачному MCP OpenClip (31 инструмент): транскрибация, монтаж, нарезка клипов, миниатюры, удаление фона; нарезка — по подписке | не заявлен | Claude Code, Codex, Cursor, ChatGPT, Claude, Perplexity, OpenClaw | 5 скиллов бесплатно с аккаунтом, нарезка платно | Не берём (облако, 1 звезда); идея |
| kajisho5/AI-video-production-OS — https://github.com/kajisho5/AI-video-production-OS | не указана (UNKNOWN) | 2, 84 коммита | 10 skill-репозиториев (ffmpeg, video-editing, audio-production, color-grading, subtitle, motion-graphics, thumbnail, qc, media-analysis, transcription на faster-whisper) + video-production-agent (LLM не подключена, заглушка). Автор: не проверено на втором агенте/провайдере | не специфично | заявлено как агентонезависимое; не подтверждено | бесплатно | Берём как референс архитектуры (контракты, PASS/WARN/FAIL/UNKNOWN); не production |
| ElSalvatore-sys/video-editor-plugin — https://github.com/ElSalvatore-sys/video-editor-plugin | проверить | 1, 12 коммитов | FFmpeg + Remotion + Whisper, по статье securitylab — экспериментальный | проверить | проверить | — | Не берём |
| WaveSpeedAI/wavespeed-cli (+ WaveSpeed skill) — https://wavespeed.ai/blog/ai-workflows/use-wavespeed-in-opencode/ | MIT (CLI) | проверить | `npm i -g @wavespeed/cli`, `wavespeed skill install` пишет SKILL.md в `.claude/skills`, откуда его читает OpenCode; поиск моделей, `price` до запуска, `balance`. В каталоге на сайте: Seedance, Wan, Kling, Veo, Hailuo, InfiniteTalk (lipsync), Speech | не заявлен | Claude Code, Cursor, Codex, OpenCode | ключ + кредиты | Берём: единственный найденный скилл, явно описанный для OpenCode; агрегатор моделей видео/аватар/голос |
| veniceai/skills (venice-video, venice-audio-speech, venice-audio-transcription) — https://github.com/veniceai/skills | проверить | проверить | Видео, TTS, транскрибация | проверить | проверить | ключ Venice | Только по списку VoltAgent/awesome-agent-skills, не открыт |
| fal-ai-community/fal-audio — https://officialskills.sh/fal-ai-community/skills/fal-audio | проверить | проверить | TTS и STT через fal | проверить | проверить | ключ fal | Только по списку, не открыт |
| NousResearch hyperframes / manim-video / kanban-video-orchestrator / audiocraft-audio-generation (список vibehackers) | проверить | — | Скиллы Hermes Agent: HTML-видео, Manim, оркестратор видео-пайплайна на канбане, MusicGen | проверить | Hermes | — | Идея оркестратора; не открыты |
| MiniMax-AI/mmx-cli, netease-youdao/seedance (список vibehackers) | проверить | — | Видео/речь/музыка MiniMax; Seedance через Volcengine | проверить | проверить | ключи провайдеров | Не открыты |
| Pexo (pexo.ai, скилл для Codex) | сервис | — | По статье pexo.ai: полный пайплайн с автовыбором модели, мультишот, музыка | проверить | Codex (`~/.agents/skills/`) | ключ, цены на pexo.ai/pricing | Статья написана самим вендором; не берём без проверки |
| wilwaldon/Claude-Code-Video-Toolkit — https://github.com/wilwaldon/Claude-Code-Video-Toolkit | MIT | 101, 3 коммита | Подборка (awesome-список): Remotion, Manim, YouTube Clipper, FFmpeg skill, ElevenLabs; не код | нет | Claude Code | — | Только как указатель |

### 6.3 Реестры и агенты
- Kimi Code CLI (https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html): скиллы берутся из `~/.kimi-code/skills/`, `~/.agents/skills/`, проектных `.kimi-code/skills/` и `.agents/skills/`; формат — директория с SKILL.md (поля name, description, type, whenToUse и др.). Каталоги `.claude`/`.codex` на странице не названы. Раздел MCP в доках есть, содержимое не открывалось. Вывод: SKILL.md из `.agents/skills/` годится и для Kimi Code, и для Codex (`~/.agents/skills/` по pexo.ai-статье) — общий путь, но работу конкретных скиллов в Kimi не проверял.
- OpenCode: по статье WaveSpeed, читает скиллы из `.claude/skills`; подтверждено только этим источником.
- Codex: `~/.agents/skills/`, `/skills`, вызов `$имя` (источник — статья pexo.ai, не документация OpenAI).
- DeepSeek: отдельного агента-реестра не найдено; применимо как LLM внутри OpenCode и др. (не проверялось).
- skills.sh и mcp.so закрыты для WebFetch (robots_disallowed), smithery.ai — client_error. Через поиск найдены карточки skills.sh и smithery (madappgang/ffmpeg-core, openclaw/ffmpeg-video-editor) — не открыты. mcpservers.org/agent-skills/category/media: открыт, в категории ace-step (музыка), ai-avatar-video, ai-video-generation, ai-music, character-design-sheet, controlnet-pose от агрегаторов runcomfy/101-skills/doany-ai и др.; subtitles/QA/safe zones там нет.
- Awesome-списки: VoltAgent/awesome-agent-skills открыт частично (первые 100k из 253k символов): remotion, venice, fal-audio, microsoft podcast/transcription; ffmpeg, субтитров, аватаров, нарезки в просмотренной части нет. vibehackers.io media-video открыт (1-я страница из 3): hyperframes, manim, seedance, mmx-cli, citedy-video-shorts и др. из LeoYeAI (китайский рынок).

## Что осталось непроверенным
- Даты коммитов: kajisho5/ffmpeg-skill, AgriciDaniel/claude-shorts, op7418/Youtube-clipper-skill, большинство остальных (api.github.com вернул client_error).
- Лицензия remotion-dev/skills: API null, файл LICENSE не виден — вывод «не указана», подтверждение через полный список файлов не получено.
- kajisho5/qc-skill docs/checks.md не открыт (точные имена правил).
- Русское качество: HeyGen, Hedra, Higgsfield, Qwen3-TTS, ElevenLabs, claude-shorts, clipify, freecut.
- Высокоуровневые карточки не открыты: square-zero-labs/video-prompting-skill, H4pplness/storyboard-skill, songguoxs/seedance-prompt-skill, gooseworks video-clipper/normalize-loudness, agensi video-export-qa, clawhub remotion-word-highlight-subtitles, theplasmak/whisperx, SVS696/vidscribe (rate limit), Fish Speech, F5-TTS, Silero, XTTS, hosted MCP ElevenLabs.
- Совместимость с Kimi Code и DeepSeek на практике; MCP-раздел доков Kimi.
- Hailuo/Veo/LTX в каталогах fal/Replicate; цены HeyGen, Higgsfield.
- mcp.so, smithery.ai, skills.sh (закрыты для WebFetch); Codex/OpenCode реестры как таковые не найдены.
- Лицензии pyannote-моделей для GigaAM longform.

---

## Топ-5 для скачивания и разбора
1. kajisho5/ffmpeg-skill — FFmpeg-слой, громкость, платформенный экспорт, MCP, без ключей, много агентов (MIT, 5.2k зв.).
2. browser-use/video-use — вырезка пауз/слов-паразитов, субтитры, оверлеи; нужен ElevenLabs Scribe, RU проверить (MIT, 31.4k зв.).
3. AgriciDaniel/claude-shorts (+ приём трекинга по рту из louisedesadeleer/clipify) — нарезка в 9:16 с трекингом; заменить ASR на RU-модель.
4. elevenlabs/skills — озвучка, музыка, SFX, дубляж по Agent Skills spec (MIT); плюс официальный fal MCP как вход к видеомоделям.
5. 0xhughs/director-skills — раскадровка: character bible, shotlist, промпты, диагностика (MIT); в паре с Gregory-Esman video-qa для проверки кадров.

Запасные: heygen-com/skills (аватар, платно), QwenLM/Qwen3-TTS (бесплатный RU-TTS с клоном, не скилл), dexhunter/seedance2-skill (промпты Seedance), GigaAM v3 (RU-ASR).
