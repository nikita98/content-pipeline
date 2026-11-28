# Правила проекта «Конвейер контента»

Файл для любого ИИ-агента (Claude Code, Codex, OpenCode, Kimi Code и др.). Claude Code читает его через `CLAUDE.md`. Это главная точка входа: карта репозитория, команды и правила.

## Проект
Набор скиллов SKILL.md: полный цикл контента эксперта от ресёрча конкурентов до публикации, аналитики и воронки продаж. Контент на русском; площадки Reels, Shorts и длинное YouTube, TikTok, Threads, Telegram; ВК не делаем. Сначала один эксперт (заказчик), потом тираж.

## С чего начать
1. `docs/status.md` — где мы, что дальше, открытые вопросы. Обновлять после заметного шага.
2. `docs/plan.md` — устройство плана и какой JSON за что отвечает.
3. README нужной папки (`app/`, `installer/`, `bench/`, `skills/`) — перед правкой в ней.

## Карта репозитория
```
AGENTS.md, CLAUDE.md     правила для агентов (этот файл; CLAUDE.md — дополнения только для Claude)
README.md                краткое описание для людей
docs/                    plan.md — устройство плана; status.md — текущее состояние
site/index.html          веб-страница плана (артефакт), данные грузит из site/data/
site/bench.html          страница стенда этапа 3 (отдельный артефакт)
site/data/*.json         ЕДИНСТВЕННЫЙ источник данных плана: шаги, сервисы, итоги, агенты,
                         правила, решения, этапы, стек, библиотека, тесты стенда и их результаты
analysis/                разборы готовых конвейеров, сводка — 00-svodka.md
research/                ресёрч рынка и инструментов, сводка — 00-svodka.md
skills/kp-*/             исходники наших скиллов (сейчас: kp-bench — стенд этапа 3)
bench/                   результаты (results/) и среды (env/) тестировщиков; runs/, tools/ — не в git
app/                     локальный интерфейс в браузере: Python-сервер (только stdlib) + модули разделов
installer/               Windows-установщик (Inno Setup), сборка и смоук-тест
.github/workflows/       CI: сборка установщика (ветка installer, теги v*, ручной запуск)
tools/install_skills.py  копирует skills/ в .claude/skills/ и .agents/skills/ (обе папки не в git)
start*.bat, start*.command  запуск интерфейса двойным кликом (Windows / macOS)
```
Нумерация файлов в `analysis/` и `research/` — порядок появления; пропуск номера (`research/06`) не ошибка.

## Команды
Из корня репозитория. На Windows — `python`, на macOS/Linux — `python3`.
- Проверить JSON после правки: `python -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" site/data/<файл>.json`
- Страница плана локально: `python -m http.server 8000 --directory site` → http://localhost:8000 (через file:// не работает, данные грузятся fetch).
- Интерфейс: `python app/server.py [--section bench] [--no-browser] [--port 8765]`.
- Проверка интерфейса: `python -m py_compile app/server.py app/core/*.py app/modules/*.py app/setup/*.py`.
- Скиллы в папки агентов: `python tools/install_skills.py [kp-bench]`.
- Свод результатов стенда: `python skills/kp-bench/scripts/summary.py` (пишет `site/data/bench_results.json`).
- Установщик: `python installer/build.py --version <x.y.z> [--no-compile] [--no-fetch]` (подробно — `installer/README.md`).

Тестов в виде pytest нет; проверка — py_compile, запуск и evals скиллов.

## Как писать
- Русский язык. Сухо, только факты, без рекламных формулировок и оценочных прилагательных.
- Не выдумывать цифры, цены, лицензии. Не проверено — пиши «проверить».
- Где для одного пункта несколько вариантов — перечисли с плюсами и минусами, решает владелец проекта. Не выбирай за него.

## Данные
- Один источник: `site/data/*.json`. Не дублировать таблицы в markdown — ссылаться на файл.
- Решение владельца — запись в `decisions.json` с датой и шагами.
- Инструмент — запись в `library.json` по схеме `site/data/library.schema.md`, с полем `source` (откуда узнали) и `checked`.
- Отчёты субагентов и поиска — для обзора. Перед включением инструмента в стек проверь факт по первоисточнику: README, документация, код.
- После правки JSON проверь валидность (команда выше). Файлы в UTF-8.
- Новый файл в `site/data/` — добавить строку в таблицу `docs/plan.md`.

## Скиллы
- Имена шагов `kp-<шаг>`: kp-orchestrator, kp-onboarding, kp-research, kp-ideas, kp-plan, kp-copy, kp-carousel, kp-script, kp-storyboard, kp-generate, kp-clips, kp-edit, kp-qa, kp-publish, kp-analytics, kp-leadmagnet, kp-funnel. Служебный, не шаг конвейера: kp-bench (стенд этапа 3).
- Исходник: `skills/<имя>/SKILL.md` + `scripts/`, `references/`, `assets/`, `evals/`. Правим только `skills/`; копии в `.agents/skills/` (Codex, Kimi Code, OpenCode) и `.claude/skills/` (Claude Code) делает `tools/install_skills.py`, руками их не править.
- Frontmatter: только `name`, `description`, `license`, `compatibility`, `metadata`. В `description` — когда срабатывать, русские формулировки запросов.
- Не называть инструменты конкретного агента (Task, TodoWrite и т.п.). Прогресс — в файле в папке клиента.
- Вход и выход шага — файлы в папке клиента; формат фиксируется до написания скилла.
- Остановки человека — явно в тексте скилла; без «да» ничего не публикуется и не оплачивается.
- Скрипты: Python 3.10+ или Node 20+, CLI с аргументами, работают на Windows и macOS, пути без пробелов не предполагать. Проверять кириллицу в текстах, субтитрах, именах файлов.
- Каждый платный сервис — с бесплатной заменой, если она есть.
- Лицензии заимствований: MIT и Apache — можно с уведомлением автора; AGPL — только идеи, код не копировать; CC BY — с атрибуцией.

## Разработка скилла
1. Формат входа и выхода шага, запись в `steps.json` актуальна.
2. Черновик SKILL.md (в Claude — со скиллом skill-creator).
3. 3–5 тестовых запросов на русском в `skills/<имя>/evals/<случай>/` (`case.yaml`, `prompt.md`, `graders/`; образец — `skills/kp-bench/evals/`), прогон со скиллом и без, сравнение.
4. Доработка `description`, чтобы скилл срабатывал на русские запросы.
5. Проверка в Claude Code и ещё одном агенте (Codex, Kimi Code или OpenCode).

## Интерфейс и установщик
- Новый раздел интерфейса — модуль `app/modules/<id>.py` + `app/web/modules/<id>.js`, ядро `app/core/` не трогать без нужды (`app/README.md`, «Как добавить раздел»).
- Компоненты для установки — `app/setup/components.json`; программы установщика — `installer/deps.json` с SHA256.
- Релиз — тег `v*`, ставит владелец на GitHub.

## Субагенты
Если пользователь не указал модель субагента — выбирай сам по задаче.

## Git
Ветка `main`; осмысленные коммиты по-русски: что изменено и зачем. Секреты и `.env` не коммитить. Не в git (см. `.gitignore`): `bench/runs/`, `bench/tools/`, `.venv-*`, `data/`, `app/settings.local.json`, копии скиллов, сборка установщика.
