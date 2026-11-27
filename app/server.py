"""Локальный интерфейс конвейера контента. Только стандартная библиотека Python 3.10+.

Запуск:
  python app/server.py                 # откроет браузер на http://127.0.0.1:8765 (или следующем свободном порту)
  python app/server.py --section bench # сразу раздел «Тесты»
  python app/server.py --no-browser    # без браузера (для проверки)
Остановить — закрыть окно или Ctrl+C.
"""
from __future__ import annotations

import argparse
import re
import sys
import threading
import webbrowser
from pathlib import Path

if sys.version_info < (3, 10):
    sys.exit("Нужен Python 3.10 или новее. Сейчас: " + sys.version.split()[0])

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.http import App, bind  # noqa: E402
from core.paths import ROOT  # noqa: E402
from core.registry import load_modules  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--section", default="", help="раздел для открытия, например bench")
    a = ap.parse_args()
    if a.section and not re.fullmatch(r"[a-z0-9-]{1,32}", a.section):
        sys.exit("--section: латиница, цифры, дефис")

    app = App()
    app.modules = load_modules(app)
    srv = bind(app, a.port)
    url = f"http://127.0.0.1:{app.port}/" + (f"#{a.section}" if a.section else "")
    print(f"Интерфейс конвейера: {url}")
    print(f"Папка проекта: {ROOT}")
    print("Не закрывайте это окно, пока работаете. Остановить — Ctrl+C или закрыть окно.")
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nОстанавливаю…")
    finally:
        app.jobs.stop_all()
        srv.server_close()


if __name__ == "__main__":
    main()
