"""Локальный интерфейс конвейера контента. Только стандартная библиотека Python 3.10+.

Запуск:
  python app/server.py                 # откроет браузер на http://127.0.0.1:8765 (или следующем свободном порту)
  python app/server.py --section bench # сразу раздел «Тесты»
  python app/server.py --no-browser    # без браузера (для проверки)
Остановить — кнопка «Выход» в интерфейсе, Ctrl+C или закрыть окно.

Один сервер на папку: data/server.lock хранит порт и токен. Повторный запуск (второй клик по ярлыку) не
поднимает второй сервер, а открывает браузер на уже работающий. Сервер сам останавливается, если браузер
не присылал запросов --idle-minutes минут (по умолчанию 10) и нет идущей задачи, или если появился файл
data/stop.request (его пишет деинсталлятор перед удалением).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

if sys.version_info < (3, 10):
    sys.exit("Нужен Python 3.10 или новее. Сейчас: " + sys.version.split()[0])

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.paths import DATA, ROOT  # noqa: E402

LOCK = DATA / "server.lock"
STOP_FILE = DATA / "stop.request"
LOG_FILE = DATA / "logs" / "server.log"


def _streams() -> None:
    """Под pythonw.exe нет консоли: sys.stdout и sys.stderr = None. Пишем их в data/logs/server.log."""
    if sys.stdout is None or sys.stderr is None:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        f = open(LOG_FILE, "a", encoding="utf-8", buffering=1)  # noqa: SIM115 — живёт до конца процесса
        sys.stdout = sys.stdout or f
        sys.stderr = sys.stderr or f
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def read_lock() -> dict | None:
    try:
        d = json.loads(LOCK.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def running_instance() -> dict | None:
    """Данные lock-файла, если по указанному порту отвечает наш сервер с тем же instance."""
    d = read_lock()
    if not d or not isinstance(d.get("port"), int):
        return None
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # localhost — без системного прокси
        with opener.open(f"http://127.0.0.1:{d['port']}/api/ping", timeout=2) as r:
            ping = json.loads(r.read().decode("utf-8"))
        if ping.get("app") == "content-pipeline" and ping.get("instance") == d.get("instance"):
            return d
    except Exception:  # noqa: BLE001 — сервер не отвечает: lock устарел
        return None
    return None


def write_lock(app) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = LOCK.with_suffix(".tmp")
    tmp.write_text(json.dumps({"pid": os.getpid(), "port": app.port, "token": app.token, "instance": app.instance,
                               "started": time.strftime("%Y-%m-%dT%H:%M:%S")}), encoding="utf-8")
    os.replace(tmp, LOCK)


def remove_lock(app) -> None:
    d = read_lock()
    if d and d.get("instance") == app.instance:
        try:
            LOCK.unlink()
        except OSError:
            pass


def watchdog(app, srv, idle_minutes: float) -> None:
    """Остановка: файл data/stop.request или нет запросов из браузера idle_minutes минут (если нет задач)."""
    while True:
        time.sleep(3)
        if STOP_FILE.exists():
            try:
                STOP_FILE.unlink()
            except OSError:
                pass
            print("Найден data/stop.request — останавливаю.")
            srv.shutdown()
            return
        if idle_minutes > 0 and time.time() - app.last_seen > idle_minutes * 60:
            busy = any(j.state in ("queued", "running") for j in app.jobs.jobs.values())
            if not busy:
                print(f"Браузер не отвечал {idle_minutes:g} мин — останавливаю.")
                srv.shutdown()
                return


def main() -> None:
    _streams()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--section", default="", help="раздел для открытия, например bench")
    ap.add_argument("--idle-minutes", type=float, default=10.0,
                    help="остановить, если браузер молчит столько минут (0 — не останавливать)")
    a = ap.parse_args()
    if a.section and not re.fullmatch(r"[a-z0-9-]{1,32}", a.section):
        sys.exit("--section: латиница, цифры, дефис")
    suffix = f"#{a.section}" if a.section else ""

    other = running_instance()
    if other:
        url = f"http://127.0.0.1:{other['port']}/{suffix}"
        print(f"Интерфейс уже запущен: {url}")
        if not a.no_browser:
            webbrowser.open(url)
        return

    from core import bundled  # noqa: E402
    bundled.apply_env()       # встроенные программы — в PATH; модели и кэш — в data/ (установленная копия)

    from core.http import App, bind  # noqa: E402
    from core.registry import load_modules  # noqa: E402

    try:
        STOP_FILE.unlink()
    except OSError:
        pass
    app = App()
    app.modules = load_modules(app)
    srv = bind(app, a.port)
    app.on_shutdown = srv.shutdown
    write_lock(app)
    url = f"http://127.0.0.1:{app.port}/{suffix}"
    print(f"Интерфейс конвейера: {url}")
    print(f"Папка проекта: {ROOT}")
    print("Остановить — кнопка «Выход» в интерфейсе, Ctrl+C или закрыть окно.")
    threading.Thread(target=watchdog, args=(app, srv, a.idle_minutes), daemon=True, name="watchdog").start()
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nОстанавливаю…")
    finally:
        app.jobs.stop_all()
        srv.server_close()
        remove_lock(app)
        print("Интерфейс остановлен.")


if __name__ == "__main__":
    main()
