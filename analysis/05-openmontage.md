# OpenMontage — карточка конкурента

Источники: GitHub через WebFetch (README, AGENT_GUIDE.md, CLAUDE.md, CODEX.md, CURSOR.md, PROJECT_CONTEXT.md, skills/INDEX.md, skills/meta/checkpoint-protocol.md, skills/meta/reviewer.md, tools/cost_tracker.py, config.yaml, Makefile, requirements*.txt, remotion-composer/package.json, schemas: final_review, checkpoint, brief, decision_log, 3 манифеста). Сверено с локальной распакованной копией пользователя (39 файлов: AGENT_GUIDE, README, 3 манифеста, 10 схем, 16 скиллов). Папки `tools/`, `lib/`, `.agents/`, `.claude/`, `.cursor/`, `backlot/` целиком не читались: дерево GitHub закрыто для WebFetch (robots), API GitHub ограничен.

## Что это

- Название: OpenMontage — «agentic video production system»: превращает ИИ-ассистента для кода в видеостудию.
- Ссылка: https://github.com/calesthio/OpenMontage , сайт openmontage.video
- Лицензия: GNU AGPL-3.0 (бейдж и LICENSE).
- Версия/дата: релизов нет (раздел Releases пуст), 497 коммитов в `main`; манифесты пайплайнов `version: "2.0"`, схемы артефактов `version: "1.0"`. Распакованная копия пользователя датирована ~16.11.2026. Звёзд ~72.4k, форков ~9.4k (по странице GitHub).
- Заявлено: 12 пайплайнов, 100+ инструментов, 700+ файлов скиллов/знаний, 60+ провайдеров.

## Шаги нашего плана, которые покрывает

- Прямо: ★ (оркестрация через executive-producer), 1 (частично — research-director, анализ референс-видео), 3 (proposal/brief, без «кодовых слов»), 6, 7, 8, 9, 10, 11, 12 (только упаковка, без загрузки).
- Частично/косвенно: 0 (style playbooks = визуальный бренд-кит, но не паспорт бренда), 2 (концепт-опции 2–5 шт., но не банк идей).
- Не покрывает: 4 (тексты постов), 5 (карусели), 13 (аналитика), 14 (лид-магниты), 15 (воронка).

## Скиллы / команды / пайплайны

Пайплайны (`pipeline_defs/*.yaml`, у каждого 7–9 скиллов-директоров в `skills/pipelines/<pipeline>/`):

| Имя | Что делает | Шаг нашего плана |
|---|---|---|
| talking-head (beta) | Сырые записи спикера → транскрипт, нарезка, субтитры, улучшение лица/звука, рендер, публикация | 9, 10, 11 |
| avatar-spokesperson (production) | Видео с аватаром-ведущим: TTS → talking_head/lip_sync → монтаж; фолбэк «озвучка поверх графики» | 6, 8, 10 |
| clip-factory (beta) | Длинное видео → ранжированные короткие клипы под платформы | 9, 10, 12 |
| podcast-repurpose (beta) | Подкаст → хайлайты, аудиограммы, цитаты | 9 |
| animated-explainer (production) | Тема → ресёрч → сценарий → генерация → монтаж | 1, 6, 7, 8, 10 |
| animation (production) | Моушн-графика, кинетическая типографика (Manim/Remotion/AI) | 7, 8, 10 |
| screen-demo (production) | Скринкасты, туториалы | 10 |
| cinematic (production) | Трейлеры, тизеры, бренд-ролики | 6–10 |
| documentary-montage (beta) | Монтаж из стоков и открытых архивов | 8, 10 |
| hybrid (production) | Свои исходники + сгенерированные вставки | 8, 10 |
| localization-dub (beta) | Субтитры, перевод, дубляж, опц. липсинк | 8, 10 |
| character-animation (beta) | Риггованные 2D-персонажи, библиотека поз | 8 |
| framework-smoke (test) | Двухстадийный тест каркаса | — |

Мета- и общие скиллы:

| Имя | Что делает | Шаг нашего плана |
|---|---|---|
| `meta/onboarding.md` | Первое общение: обзор возможностей, стартовые промпты | ★ |
| `meta/creative-intake.md` | 7 вопросов до ресёрча (цель, аудитория, платформа, тон, референсы, результат, ограничения) → неформальный `intake_brief` | 0, 3 |
| `meta/video-reference-analyst.md` | Разбор референс-видео (транскрипт, темп, сцены, кадры) → 2–3 отличающиеся концепции | 1, 2 |
| `meta/reviewer.md` | Самопроверка после каждой стадии | 11 |
| `meta/checkpoint-protocol.md` | Чекпоинты, ворота одобрения, возобновление | ★ |
| `meta/taste-direction.md` | Бриф → «ручки вкуса», анти-паттерны | 0, 7 |
| `meta/voice-performance-director.md` | Режиссура озвучки под провайдера (SSML для Google, instructions для OpenAI) | 8 |
| `meta/capability-extension.md` | Правила, когда агенту можно писать свой скрипт/обёртку | ★ |
| `meta/skill-creator.md` | Создание новых скиллов во время прогона | ★ |
| `meta/animation-runtime-selector.md`, `meta/bespoke-composition.md` | Выбор рантайма рендера, ручная авторская композиция | 10 |
| `core/` (ffmpeg, remotion, hyperframes, whisperx, subtitle-sync, color-grading) | Знания по движкам | 10 |
| `creative/` (~35 файлов: storytelling, short-form, long-form, sound-design, typography, video-gen-prompting, prompting/{seedance,veo,sora,grok,ltx,hunyuan}, broll-planning, lip-sync-usage, talking-head-gen-usage и др.) | Ремесленные правила и промптинг под модели | 6, 7, 8, 10 |
| Explainer `publish-director` | SEO-метаданные, главы, превью, локальный export bundle | 12 |

Команды Makefile: `setup` (pip + npm в remotion-composer + piper-tts + проверка hyperframes + копия `.env`), `install`, `install-dev`, `install-gpu`, `test`, `test-contracts`, `lint`, `preflight` (печатает `provider_menu()`), `demo`, `demo-list`, `hyperframes-doctor`, `hyperframes-warm`, `clean`. Доска: `python -m backlot open [<project-id>]`.

## Архитектура

**Оркестрация.** Кодового оркестратора нет: агент читает YAML-манифест и Markdown-скиллы и вызывает Python-инструменты (`BaseTool` → `execute()` → `ToolResult`, обнаружение через `tools/tool_registry.py`). «Rule Zero»: любое производство только через пайплайн; ad-hoc скрипты запрещены, кроме протокола capability-extension (с записью в decision_log). Цикл: манифест → `checkpoint.get_next_stage()` → скилл директора стадии → инструменты → самопроверка (reviewer) → чекпоинт → показ человеку, если стадия под воротами. В режиме `executive-producer` отдельный скилл EP ведёт «кумулятивное состояние» (артефакты, бюджет, счётчики ревизий, лог проблем) и делает возвраты (send-back) на конкретную стадию.

Три слоя знаний: L1 — реестр инструментов (что есть); L2 — `skills/` (как использовать в OpenMontage); L3 — `.agents/skills/` (как устроена технология/провайдер; читать перед вызовом инструмента с полем `agent_skills`).

**Стадии.** Общий вид: `research → proposal → script → scene_plan → assets → edit → compose → publish` (у footage-пайплайнов вместо research/proposal — `idea`). Обязательный preflight: `registry.provider_menu_summary()` → `composition_runtimes`, `capabilities[]` (configured/total), `setup_offers[]`, `runtime_warnings[]`; итог `passed | degraded | blocked`; показывать пользователю «X из Y настроено».

**Манифест YAML** (схема `schemas/pipelines/pipeline_manifest.schema.json`, обязательны `name, version, stages`):
- верхний уровень: `name, version, description, category, stability, default_checkpoint_policy (guided|manual_all|auto_noncreative), compatible_playbooks{recommended, also_works, custom_allowed}, required_skills, production_modes, reference_input, extensions{custom_scripts, custom_playbooks, custom_skills, custom_tools}, orchestration{mode, skill, budget_default_usd, max_revisions_per_stage, max_send_backs, max_wall_time_minutes}, metadata`;
- стадия: `name` (обяз.), `agent, skill, required_artifacts_in, optional_artifacts_in, produces, preferred_tools, fallback_tools, required_tools, optional_tools, tools_available, review_focus, checkpoint_required, human_approval_default, success_criteria, sub_stages`.
- Пример значений: talking-head — `budget_default_usd: 0.50`, ревизий 3, send-back 3; avatar — $2.00, 12 мин; clip-factory — $1.00, 12 мин.

**Контракты JSON Schema** (`schemas/artifacts/`, 20 схем; канонический артефакт стадии обязан проходить валидацию):
- `brief` — обяз. `version, title, hook, key_points[], tone, style, target_platform (youtube|instagram|tiktok|linkedin|generic), target_duration_seconds`; опц. `core_message, cta, target_audience, reference_material, angle_options[2–3]{name, description}, selected_angle`.
- `proposal_packet` — `concept_options[]{id, title, hook, narrative_structure, visual_approach, target_duration_seconds, why_this_works, …}`, `selected_concept`, `production_plan{pipeline, stages, playbook, delivery_promise, renderer_family, render_runtime, composition_mode, music_source, voice_selection, provider_rankings, …}`, `cost_estimate{total_estimated_usd, line_items, budget_verdict, budget_cap_usd, savings_options}`, `approval{status: pending|approved|approved_with_changes|rejected, user_notes, approved_budget_usd}`.
- `script` — `title, total_duration_seconds, sections[]{id, text, start_seconds, end_seconds, label, speaker_directions, delivery_cues, enhancement_cues, pronunciation_guides, source_ref}`, `voice_performance`.
- `scene_plan` — `scenes[]{id, type, description, start_seconds, end_seconds, script_section_id, framing, movement, transition_in/out, shot_language, shot_intent, narrative_role, hero_moment, required_assets, …}`, `style_playbook`.
- `asset_manifest` — `assets[]{id, type, path, source_tool, scene_id, prompt, seed, model, provider, cost_usd, quality_score, license, original_url, voice_performance, …}`, `total_cost_usd`.
- `edit_decisions` — обяз. `cuts[]{id, source, in_seconds, out_seconds, speed, layer, transform, transition_*, reason}`, `render_runtime`; плюс `overlays, audio, subtitles, music, transitions, renderer_family, composition_mode, slideshow_risk_score`.
- `render_report` — `outputs[]{path, format, codec, resolution, fps, duration_seconds, file_size_bytes, platform_target}`, `warnings, verification_notes, final_review_ref, decision_log_ref`.
- `final_review` — см. QA ниже. `publish_log` — `entries[]{platform, status, url, video_id, export_path, timestamp, metadata_used, error}`.
- `decision_log` — `decisions[]{decision_id, stage, category, subject, options_considered[]{option_id, label, score 0–1, reason, rejected_because}, selected, reason, user_visible, user_approved, confidence 0–1}`; 17 категорий (`provider_selection, render_runtime_selection, music_source, voice_selection, fallback_decision, downgrade_approval, budget_tradeoff, approval_policy, capability_extension, visual_accuracy_check, …`). Изменение решения — только дописыванием новой записи, старую не править.
- Также: `research_brief, review, cost_log, source_media_review, video_analysis_brief, character_*`, `pose_library, rig_plan, action_timeline`. Схема плейбука `schemas/styles/playbook.schema.json` (v2, дизайн-токены).

**Чекпоинты.** `lib/checkpoint.py`; файл `projects/<project_id>/checkpoint_<stage>.json`; схема: обяз. `version, project_id, pipeline_type, stage, status (completed|failed|awaiting_human|in_progress), timestamp, artifacts`; опц. `style_playbook, checkpoint_policy, human_approval_required, human_approved, review, cost_snapshot{total_spent_usd, total_reserved_usd, budget_remaining_usd}, error, metadata`. Правила: `in_progress` при входе в стадию; на assets/compose обновлять `metadata.partial_progress` после каждой сцены (для возобновления и доски); устаревшие чекпоинты архивируются в `projects/<id>/history/`. Возобновление: `get_next_stage()` → `read_checkpoint()` → догрузить артефакты → пропустить готовые подзадачи по `partial_progress`.

**Ворота одобрения.** `human_approval_default` в манифесте обязателен для агента («binding»). Обычно гейты: idea/proposal, script, scene_plan, assets, publish; edit и compose — авто (исключение: documentary-montage гейтит edit). При гейте: записать `awaiting_human`, показать «Stage Complete: … — awaiting your approval» (сводка артефакта, находки ревью «N critical (all fixed), N suggestions», затраты spent/total с разбивкой по инструментам, требуемое действие) и **завершить ход**. Запись `completed` без `human_approved=True` → `GATE VIOLATION` в коде. Proposal закрывается, только если `proposal_packet.approval.status` = approved/approved_with_changes. Одобрение действует на один гейт; «одобряю всё» засчитывается только записью в decision_log с `category: "approval_policy"`. Дополнительно — «sample checkpoint»: один пробный ролик `assets/sample/sample_v{N}.mp4` с прогнозом стоимости полного видео; для аватара — пробный TTS и пробный аватар-клип до пакетной генерации (до 3 итераций).

**Учёт бюджета.** `tools/cost_tracker.py`: цикл `estimate → reserve → reconcile` (+ `refund`, `approve_tool`, `cost_snapshot`, `estimate_from_reference`). Режимы `observe | warn (по умолчанию) | cap`. Дефолты (`config.yaml`): `total_usd: 10.00`, `reserve_pct: 0.10` (резерв на ретраи), `single_action_approval_usd: 0.50`, `require_approval_for_new_paid_tool: true`. `reserve()`: выше порога на одно действие или новый платный инструмент → `ApprovalRequiredError`; выход за доступный бюджет → в cap `BudgetExceededError`, в warn флаг `budget_warning`. Лог — `cost_log.json` (`entries[]{id, tool, operation, status, estimated_usd, reserved_usd, actual_usd, timestamp}`). Правила агента: перед каждым платным вызовом объявить инструмент/провайдера/модель/причину/sample или batch; переход sample→batch — только с одобрения; перерасход >30% к смете без переодобрения — critical в ревью; в avatar EP — предупреждение на 90% бюджета.

**Выбор провайдера.** Селекторы `tts_selector`, `image_selector`, `video_selector` сами находят провайдеров по capability в реестре; маршрут «предпочтение пользователя > доступность > порядок обнаружения». Скоринг по 7 измерениям: task fit 30%, output quality 20%, control 15%, reliability 15%, cost 10%, latency 5%, continuity 5% (README); победитель и альтернативы — в decision_log; в proposal поле `provider_rankings`. Музыка: своя библиотека `music_library/` → royalty-free поиск → генерация API → трек пользователя; музыкальный план обязателен уже на proposal. Рантайм рендера (Remotion/HyperFrames/FFmpeg) выбирается на proposal, оба показываются пользователю, фиксируется; тихая подмена — нарушение. Без одобрения нельзя менять провайдера, модель, видео- vs стилл-подход, движок, выкидывать музыку/озвучку. Файл реализации скоринга — проверить (не найден в прочитанном).

**QA.**
- Ревьюер (`skills/meta/reviewer.md`) после каждой стадии: валидация схемы (провал = critical) → пункты `review_focus` → правила плейбука → taste-профиль → `success_criteria` (met/partial/not met). Уровни: critical (обязателен `proposed_fix`), suggestion, nitpick, investigation. Решение: 0 critical → PASS; ≥1 → REVISE; после 2 раундов → PASS_WITH_WARNINGS. Ревьюер «advisory», но findings в чекпоинте.
- Пороги: slideshow risk (6 измерений: повторы, декоративность, слабое движение, shot intent, перегруз типографикой, необоснованные «кинематографичные» заявки) — среднее ≥4.0 fail, ≥3.0 revise; variation ≤2 poor; motion-ratio <50% при обещании «motion-led»; decision log ≥2 опций на решение, все confidence=1.0 — флаг; кадров на проверку ≥4.
- Pre-compose validation (`video_compose._pre_compose_validation`): блокирует рендер при нарушении delivery promise, критичном slideshow risk, отсутствии рендерера.
- `final_review` после рендера (статус `pass|revise|fail`, `recommended_action`): `technical_probe` (ffprobe: контейнер, длительность, разрешение, fps, аудио, кодек, размер), `visual_spotcheck` (≥4 кадра: чёрные кадры, битые оверлеи, нет ассетов, нечитаемый текст), `audio_spotcheck` (озвучка/музыка есть, неожиданная тишина, клиппинг, разборчивость), `promise_preservation` (рантайм, подмена, motion_ratio, тихий даунгрейд), `subtitle_check` (`coverage_ratio` 0–1, дрейф), опц. `transcript_comparison` (`word_accuracy`). Не-pass блокирует publish.
- Talking-head EP финальный QA: длительность ±5% от цели, субтитры ±0.3 с к слову, речь −16 LUFS; инструмент `visual_qa` (операции `review` по таймкодам, `probe` с ожидаемыми width/height/pixel_format, `audio_levels`); словарь исправлений ASR перед прожигом субтитров (передавать `{}`, если правок нет); целевые размеры файлов (Reels <50 МБ/90 с, Shorts <40 МБ, YouTube <25 МБ/мин; CRF 23, поднять до 26–28).
- Звук (`creative/sound-design.md`): диалог −16…−14 LUFS, true peak ≤ −1.5 dBTP, музыка на 18–20 дБ ниже речи, платформы −14 LUFS, подкасты −16.
- Клипы (`clip-factory/script-director`): оценка кандидатов по `hook, coherence, value, energy, platform_fit`; «тест самостоятельности» (нет висячих местоимений, отсылок к контексту, длинных подводок, обрыва до развязки); разнообразие по разделам/спикерам/энергии; хук в первые 2–3 с.
- Аватар: проверка тайминга рта, артефактов лица, дрейфа на длинных секциях; лицо и рот не перекрывать субтитрами/CTA. Числовых порогов липсинка нет.
- Лимиты против зацикливания: ≤3 ревизии на стадию, ≤1 send-back на пару стадий, ≤3 send-back всего; при упоре — продолжать с предупреждениями.
- Тесты: `tests/contracts/` (без ключей), `tests/qa/`, eval harness.

## Библиотеки и программы

- Python 3.10+ (`.python-version`; Makefile создаёт venv 3.10, `uv` если есть). `requirements.txt`: pyyaml≥6.0, pydantic≥2.0, jsonschema≥4.20, python-dotenv, Pillow≥10, numpy, requests, certifi≥2026.10.19, google-auth, google-genai≥1.0, openai≥2.44, fastapi≥0.110, uvicorn, watchfiles, websockets≥14 (доска Backlot), pythainlp≥5.0. GPU: torch≥2.0, torchaudio, torchvision + diffusers, transformers, accelerate.
- Node.js: 22.23.4+ / 24.22.1+ / 26.12.1+ (README в локальной копии; старая формулировка «18+» на GitHub устарела — проверить по актуальному main). HyperFrames требует Node ≥22, ставится через `npx hyperframes`.
- Remotion: `remotion-composer/` — remotion и @remotion/* ^4.0.484 (captions, cli, google-fonts, media, player, transitions), React 18, TypeScript 5.3, d3-geo/topojson/world-atlas. Компоненты: TextCard, StatCard, ProgressBar, CalloutBox, ComparisonCard, charts, TalkingHead, пословные субтитры в стиле TikTok.
- FFmpeg — сборка, кодирование, прожиг субтитров, микс, LUT-грейдинг. ffprobe — QA.
- Транскрипция: faster-whisper (tiny…large-v3, по умолчанию `base`, для продакшна `large-v3`), выравнивание WhisperX + pyannote-диаризация (нужен `HF_TOKEN`). Версия WhisperX — проверить.
- Прочее: Real-ESRGAN, rembg/U2Net, CodeFormer/GFPGAN, CLIP/BLIP-2, scene detect, ManimCE, Blender 4.5 LTS, Piper TTS (офлайн).

## Внешние сервисы и модели

- TTS: ElevenLabs, Google TTS (700+ голосов, 50+ языков), OpenAI TTS, Azure Speech, Kling TTS, DashScope/Doubao/Fish Audio — платные; Piper — бесплатно локально.
- Видео: Kling (fal.ai и официальный API), Seedance 2.0 (Volcengine Ark; помечен как «preferred premium default»), Veo 3.1, Runway Gen-4, Grok Imagine Video, Higgsfield, MiniMax/H3, HeyGen, Atlas Cloud, Gemini Omni Flash — платные; WAN 2.1/2.2, Hunyuan, CogVideo, LTX-Video — бесплатно на своём GPU.
- Изображения: FLUX, Imagen 4, GPT Image 2, Seedream 5.0, Nano Banana 2, Grok, Recraft, Kling — платные; локальный Stable Diffusion бесплатно.
- Аватар/липсинк: SadTalker/MuseTalk, Wav2Lip — локально (GPU); Kling Avatar, Kling Lip Sync, HeyGen — платные.
- Музыка/звук: Suno, ElevenLabs Music, ElevenLabs SFX — платные; библиотека пользователя и royalty-free (Pixabay и др.).
- Стоки и архивы (бесплатно, частично с ключом): Pexels, Pixabay, Unsplash, Wikimedia Commons, Archive.org, NASA.
- LLM оркестратора: ассистент пользователя; в `config.yaml` поле `llm.provider` (anthropic|openai|gemini|openrouter|ollama|mistral|minimax). Ollama/LM Studio — «coming soon».
- Без ключей: Piper, открытые архивы, Remotion/HyperFrames, FFmpeg, автосубтитры.

## Агенты, в которых работает

- Claude Code (`CLAUDE.md`), Codex (`CODEX.md`), Cursor (`CURSOR.md` + `.cursor/rules/`), Copilot (`COPILOT.md` + `.github/copilot-instructions.md`), Windsurf (`.windsurfrules`), общий `AGENTS.md`; есть `.claude/`, `.codex/prompts/`, `.agents/skills/` (содержимое — проверить).
- Устройство: все файлы под агентов — тонкие заглушки на 3–6 строк («MANDATORY: Read AGENT_GUIDE.md before responding to ANY user message… There are no instructions in this file»). Вся логика в одном `AGENT_GUIDE.md` (~50 КБ) + `PROJECT_CONTEXT.md` + Markdown-скиллы, которые агент читает по путям. Никаких agent-специфичных механизмов (хуков, сабагентов, слэш-команд) в прочитанном нет; вызовы инструментов — `python -c "from tools… import …"`.
- Применимость к Kimi Code и OpenCode: паттерн «тонкий файл-указатель → единый гайд» переносится напрямую — OpenCode и Kimi Code читают `AGENTS.md`, который здесь уже есть. Требования к агенту: читать файлы, запускать Python/Node, уметь «закончить ход» на гейте. Ограничение — гайд 50 КБ + многошаговое чтение скиллов нагружают контекст; на слабых/коротких контекстах соблюдение гейтов не гарантировано (защищает только проверка в `lib/checkpoint.py`).

## Файлы между шагами

```
projects/<project-id>/            # kebab-case от названия; init_project() пишет project.json
  project.json
  checkpoint_<stage>.json         # статус + канонический артефакт + review + cost_snapshot
  history/                        # архив заменённых чекпоинтов
  artifacts/                      # research_brief, brief/proposal_packet, script, scene_plan, asset_manifest, edit_decisions, render_report, final_review, publish_log, decision_log
  assets/{images,video,audio,music}/, assets/subtitles.srt, assets/sample/sample_v{N}.mp4
  snapshots/<scene_id>.png        # стоп-кадры сцен для гейта assets
  renders/final.mp4
  (export: metadata.json, chapters.txt, description.txt)
music_library/                    # треки пользователя, gitignored
```
Артефакты стадий: idea→`brief`(+`decision_log`), proposal→`proposal_packet`, script→`script`, scene_plan→`scene_plan`, assets→`asset_manifest`, edit→`edit_decisions`, compose→`render_report`+`final_review`, publish→`publish_log`. Все выходы обязаны лежать внутри `projects/<id>/`. Расхождение: `config.yaml` указывает `checkpoint.storage_dir: pipeline`, а гайд — `projects/` (проверить, что реально используется).

## Русский язык — что известно

- Явных упоминаний русского нет ни в README, ни в гайде; README есть на en, zh-CN, es, pt-BR.
- Косвенно: faster-whisper/WhisperX определяют язык (в состоянии EP есть `transcript_language`); Google TTS 50+ языков, Azure/ElevenLabs/OpenAI мультиязычны; Piper имеет русские голоса — проверить, какие подключены. Пайплайн localization-dub заявляет перевод/дубляж на «10 языков».
- Скиллы, примеры промптов, словари ASR-исправлений и SEO-правила — англоязычные; под RU-площадки (VK, Дзен, Telegram, Rutube) ничего нет. Наличие `pythainlp` говорит о точечной поддержке тайского, аналога для русского нет.

## Берём (только идеи, AGPL — код и тексты не копируем)

- ★ Координатор: «единый гайд + тонкие файлы-указатели под каждого агента» (CLAUDE.md/AGENTS.md/CODEX.md → один источник правды); Rule Zero «всё через пайплайн»; манифест шагов с полями `required_artifacts_in / produces / review_focus / success_criteria / human_approval_default / checkpoint_required`; preflight с итогом `passed/degraded/blocked` и «X из Y настроено»; лимиты против зацикливания (ревизии, send-back) с выходом «продолжить с предупреждениями».
- ★ Ворота: обязательность гейта из манифеста; «показать сводку + находки + затраты и завершить ход»; одобрение на один гейт, «одобряю всё» — только явной записью; статус одобрения внутри артефакта (`approval.status`) как условие закрытия шага.
- ★ Чекпоинты: файл на шаг со статусами `in_progress/awaiting_human/completed/failed`, `partial_progress` для возобновления, архив history; это работает в любом агенте, т.к. это просто файлы.
- 0 Паспорт бренда: структура style playbook (identity/mood/pace, палитра, шрифты, quality_rules как жёсткие ограничения) и 7 вопросов creative-intake.
- 1–2: разбор референс-видео → 2–3 отличающиеся концепции, не копия; `angle_options` в брифе.
- 3: proposal-пакет с концепциями, планом, сметой и полем одобрения; decision_log с альтернативами, оценками и причиной; дописывание вместо правки.
- 6: схема сценария с секциями, таймингами, `delivery_cues`, `pronunciation_guides`; проверка темпа речи (слов/сек).
- 7: scene_plan с `shot_intent/narrative_role/required_assets`; оценка «риска слайд-шоу».
- 8: пробный образец (sample) до пакетной генерации + прогноз полной стоимости; учёт бюджета estimate→reserve→reconcile, порог на одно действие, одобрение нового платного инструмента; весовой скоринг провайдеров с логом; явная лестница фолбэков для аватара (аватар → липсинк на своей записи → озвучка поверх графики, только с согласия); asset_manifest с prompt/seed/model/cost/license.
- 9: ранжирование клипов по hook/coherence/value/energy/platform_fit и «тест самостоятельности»; разнообразие выборки.
- 10: фиксация рантайма рендера на этапе плана, запрет тихой подмены; словарь исправлений ASR перед субтитрами.
- 11: структура final_review (тех. проба, ≥4 кадров, звук, субтитры, сравнение с транскриптом, соблюдение обещания) и числовые пороги (длительность ±5%, субтитры ±0.3 с, −14/−16 LUFS, true peak −1.5 dBTP, музыка −18…−20 дБ к речи, лимиты размера файлов); ревью с severity и обязательным proposed_fix.
- 12: export bundle (metadata.json, chapters.txt, description.txt) и publish_log; не-pass QA блокирует публикацию.

## Не берём

- Код Python/TS, тексты скиллов и схем дословно (AGPL-3.0, сетевое использование тоже триггерит копилефт).
- Тяжёлую локальную инфраструктуру как обязательную: GPU-модели, Blender, 3D, character-animation, Backlot-доску на FastAPI.
- Монолитный гайд на 50 КБ с ВЕРХНИМ РЕГИСТРОМ правил — для наших 4 агентов лучше короткий координатор + подгрузка скиллов по шагу.
- Привязку к вызову Python через `python -c` из чата как единственный путь — в Cowork/облачных агентах окружение может отличаться.
- Пайплайны без нашего сценария (cinematic, documentary-montage, animation 3D, localization-dub как отдельный продукт).

## Слабые места

- Нет шагов 4, 5, 13, 14, 15: тексты, карусели, аналитика, лид-магниты, воронка — только видео.
- Публикация — только локальная упаковка; `export_bundle` «does not upload»; аплоадеры — проверить в `tools/publishers/`.
- Ворота держатся на дисциплине агента; кодом защищена только запись `completed` без `human_approved`. Ревьюер «advisory» — ИИ проверяет сам себя.
- Много пайплайнов в beta (talking-head, clip-factory, podcast-repurpose, localization-dub, documentary-montage). В гайде documentary-montage указан дважды; PROJECT_CONTEXT его не перечисляет — документация расходится.
- Расхождения в конфиге: `storage_dir: pipeline` против `projects/`; бюджет по умолчанию $10 в config против $0.50–$2 в манифестах.
- Липсинк проверяется визуально по кадрам, числовых порогов нет; локальные аватары требуют GPU, облачные — платные.
- Нет поддержки русского как первого языка (скиллы, SEO, площадки).
- Порог входа: Python 3.10 + Node 22+ + FFmpeg + npm; Windows — с оговорками.

## Открытые вопросы

- Где реализован 7-факторный скоринг провайдеров и как считаются баллы (`tools/tool_registry.py`? `lib/`?) — проверить.
- Содержимое `.claude/`, `.codex/prompts/`, `.cursor/rules/`, `.agents/skills/` — есть ли слэш-команды/промпты, кроме заглушек — проверить.
- `tools/publishers/` — есть ли реальная загрузка на YouTube/TikTok — проверить.
- Как `visual_qa` и `final_review` заполняются: автоматически инструментом или агентом вручную — проверить в `tools/analysis/`.
- Какие русские голоса реально доступны через Piper/ElevenLabs в конфигурации по умолчанию и качество WhisperX large-v3 на русском — проверить на прогоне.
- Работает ли схема гейтов в OpenCode/Kimi Code без доработок (чтение `AGENTS.md` есть, но «завершение хода» и длинный контекст — проверить).
- Точная дата последнего коммита main — проверить (страница GitHub даты не отдала).
