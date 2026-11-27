# Локальный интерфейс конвейера

Страница в браузере на компьютере пользователя. Сервер — `app/server.py`, только стандартная библиотека Python 3.10+, слушает только `127.0.0.1`. Первый раздел — «Тесты» (стенд этапа 3, `skills/kp-bench`), остальные шаги конвейера из `site/data/steps.json` видны в меню как «скоро».

## Запуск
- Windows: двойной клик по `start.bat` в корне репозитория (`start-bench.bat` — сразу «Тесты»). Если Python нет, окно подскажет `winget install Python.Python.3.12`.
- macOS: `start.command` (`start-bench.command`). Первый раз: правый клик → «Открыть» или в Терминале `chmod +x start.command start-bench.command`.
- Вручную: `python app/server.py [--section bench] [--no-browser] [--port 8765]`. Порт занят — берётся следующий свободный.

Окно с сервером не закрывать, пока идёт работа. Пути с пробелами и кириллицей поддерживаются.

## Устройство
```
app/server.py           запуск: порт, браузер, загрузка модулей
app/core/http.py        HTTP: статика, API ядра, токен, проверка Host и Origin, отдача файлов, загрузка
app/core/registry.py    реестр разделов, действий белого списка и маршрутов; загрузчик модулей
app/core/jobs.py        фоновые задачи: шаги Cmd (argv, shell=False) и Py (функция), лог, «Остановить»
app/core/paths.py       корень, bench/runs, проверка путей (.., символические ссылки, выход за папку)
app/core/tools.py       внешние программы (поиск, команда установки для ОС), окружения venv
app/core/agents.py      ИИ-агенты в фоне: Claude Code, Codex, OpenCode, Kimi Code
app/core/gitops.py      проверка git, отправка (add → commit → pull --rebase → push), zip
app/core/settings.py    app/settings.local.json (в git не идёт): тестировщик, агент
app/modules/<id>.py     модуль раздела: register(app)
app/web/index.html      оболочка; core.js — API, навигация, компоненты; core.css — стили
app/web/modules/<id>.js интерфейс раздела
```

Безопасность:
- случайный токен при каждом запуске; каждый POST — с заголовком `X-Bench-Token`, иначе 403;
- Host только `127.0.0.1:<порт>` или `localhost:<порт>`; Origin, если есть, — тот же;
- клиент не передаёт команды: только id действия и параметры. Неизвестное действие — 400. Команду собирает функция модуля из проверенных параметров;
- файлы отдаются только из `bench/runs/` (с токеном в параметре `t`), без `..` и символических ссылок; загрузка — до 500 МБ в `bench/runs/rec/<тестировщик>/`;
- одна тяжёлая задача за раз, вторая получает отказ с текстом;
- логи задач — `bench/runs/_log/<дата-время>_<действие>.txt`.

Внешние программы (Python, Node, ffmpeg, git, auto-editor) интерфейс не ставит: показывает команду winget или brew с кнопкой «Скопировать». Пакеты Python ставятся кнопкой в окружения `.venv-asr`, `.venv-whisperx`, `.venv-tts` в корне репозитория (в git не идут).

## Агенты
Выбор — «Настройки». Длинная задача пишется в `bench/runs/_agent/<время>_<имя>.md`, агенту уходит короткий промпт со ссылкой на файл. Команды — `app/core/agents.py`, там же источники. Флаги OpenCode для прав не подтверждены — проверить. Если агента нет, интерфейс показывает текст задачи с кнопкой «Скопировать».

## Как добавить раздел
Пример: шаг «Тексты» (`kp-copy` в `steps.json`).

1. `app/modules/copy.py`:
```python
import sys
from core.jobs import Cmd
from core.paths import ROOT, check_tester

def build_lint(params, app):
    t = check_tester(params.get("tester"))
    return [Cmd([sys.executable, str(ROOT / "skills/kp-copy/scripts/lint.py"), "--client", t])], "Проверка текста"

def state(req):
    return 200, {"ok": True}

def register(app):
    # skill связывает раздел с шагом из steps.json: пункт меню станет активным
    app.section("copy", "Тексты", js="modules/copy.js", order=50, skill="kp-copy")
    app.action("copy.lint", "Проверка текста", build_lint, heavy=False, describe="python skills/kp-copy/scripts/lint.py --client <t>")
    app.route("GET", "/api/copy/state", state)
```
2. `app/web/modules/copy.js`:
```js
(() => {
  const { h, step } = KP;
  KP.section("copy", { render(main) {
    main.append(h("h1", {}, "Тексты"), step({ num: 1, id: "lint", title: "Проверка текста",
      why: "…", actions: [{ label: "Проверить", action: "copy.lint", params: () => ({ tester: KP.settings.tester }) }] }));
  } });
})();
```
Ядро менять не нужно: модуль подхватывается при запуске. Общие компоненты `core.js`: `KP.step` (зачем, что нужно, инструкция, кнопки, живой лог), `KP.resultForm` (метрики, вердикт, заметка), `KP.player`, `KP.md`, `KP.codeBlock`, `KP.toolsTable`.

## Проверка
`python -m py_compile app/server.py app/core/*.py app/modules/*.py`; запуск `python app/server.py --no-browser` и открыть адрес из консоли.
