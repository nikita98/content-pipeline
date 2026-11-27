"""Внешние программы и окружения Python (venv).

Внешние программы (Python, Node, ffmpeg, git, auto-editor) интерфейс НЕ ставит: показывает команду для ОС
тестировщика. В установленной копии (Windows-установщик) они встроены в папку tools/ и находятся первыми. Окружения venv создаются и наполняются действиями белого списка (pip install в venv).
Команды winget и brew — из skills/kp-bench/references/install.md; помеченные там «проверить» — проверить.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import bundled
from .agents import find_exe
from .jobs import child_env
from .paths import INSTALLED, IS_MAC, IS_WIN, ROOT

OS_ID = "windows" if IS_WIN else ("macos" if IS_MAC else "linux")

EXTERNAL = {
    "python": {"name": "Python 3.10+", "exe": "python", "version": ["--version"],
               "install": {"windows": "winget install Python.Python.3.12", "macos": "brew install python@3.12",
                           "linux": "sudo apt install python3 python3-venv"}},
    "node": {"name": "Node.js 22+", "exe": "node", "version": ["--version"],
             "install": {"windows": "winget install OpenJS.NodeJS.LTS", "macos": "brew install node",
                         "linux": "sudo apt install nodejs npm"},
             "note": "ID пакета winget — проверить: winget search node"},
    "ffmpeg": {"name": "ffmpeg", "exe": "ffmpeg", "version": ["-version"],
               "install": {"windows": "winget install ffmpeg", "macos": "brew install ffmpeg",
                           "linux": "sudo apt install ffmpeg"},
               "note": "ID пакета winget — проверить: winget search ffmpeg"},
    "git": {"name": "git", "exe": "git", "version": ["--version"],
            "install": {"windows": "winget install Git.Git", "macos": "brew install git", "linux": "sudo apt install git"}},
    "auto-editor": {"name": "auto-editor", "exe": "auto-editor", "version": ["--version"],
                    "install": {"windows": "Скачать auto-editor с github.com/WyattBlue/auto-editor/releases, переименовать в auto-editor.exe и положить в папку из PATH",
                                "macos": "brew install auto-editor",
                                "linux": "Скачать бинарник с github.com/WyattBlue/auto-editor/releases и положить в PATH"},
                    "note": "в pip больше не публикуется; brew — проверить"},
}


def _version(path: str, args: list[str]) -> str:
    try:
        r = subprocess.run([path, *args], capture_output=True, timeout=20, env=child_env(), stdin=subprocess.DEVNULL)
        txt = (r.stdout or r.stderr).decode("utf-8", "replace").strip()
        return txt.splitlines()[0][:100] if txt else ""
    except Exception as e:  # noqa: BLE001
        return f"ошибка: {e.__class__.__name__}"


def detect_external() -> list[dict]:
    out = []
    for tid, t in EXTERNAL.items():
        if tid == "python":
            path, ver = bundled.console_python(), "Python " + sys.version.split()[0]
        else:
            path = find_exe(t["exe"])
            ver = _version(path, t["version"]) if path else None
        install = t["install"].get(OS_ID, "")
        if INSTALLED:
            install = "Входит в установку. Если пропала — запустите установщик ещё раз (папка та же)."
        out.append({"id": tid, "name": t["name"], "found": bool(path), "path": path, "version": ver,
                    "bundled": bundled.is_bundled(path), "install": install,
                    "note": "" if INSTALLED else t.get("note", ""), "os": OS_ID})
    return out


def exe(tid: str) -> str | None:
    if tid == "python":
        return bundled.console_python()
    return find_exe(EXTERNAL[tid]["exe"])


# --- окружения Python ---------------------------------------------------------------------------

def venv_dir(name: str) -> Path:
    """Копия из git — .venv-<имя> в корне; установленная копия — data/venv/<имя>."""
    if bundled.VENV_ROOT is not None:
        return bundled.VENV_ROOT / name
    return ROOT / f".venv-{name}"


def venv_label(name: str) -> str:
    return f"data/venv/{name}" if bundled.VENV_ROOT is not None else f".venv-{name}"


def venv_python(name: str) -> Path:
    d = venv_dir(name)
    return d / "Scripts" / "python.exe" if IS_WIN else d / "bin" / "python"


def venv_bin(name: str, program: str) -> Path:
    d = venv_dir(name)
    return d / "Scripts" / f"{program}.exe" if IS_WIN else d / "bin" / program


def venv_exists(name: str) -> bool:
    return venv_python(name).is_file()


def _site_packages(name: str) -> list[Path]:
    d = venv_dir(name)
    if IS_WIN:
        return [d / "Lib" / "site-packages"]
    return list((d / "lib").glob("python*/site-packages"))


def installed(name: str, dist: str) -> bool:
    """Есть ли пакет в venv: по папке <dist>-*.dist-info, без запуска Python."""
    norm = re.sub(r"[-_.]+", "_", dist).lower()
    for sp in _site_packages(name):
        if not sp.is_dir():
            continue
        for p in sp.iterdir():
            if p.suffix == ".dist-info" and re.sub(r"[-_.]+", "_", p.name.split("-")[0]).lower() == norm:
                return True
    return False


def base_python() -> list[str]:
    """Python для создания venv. Встроенный 3.12, если есть; иначе install.md советует 3.12 (колёса torch);
    если его нет — тот, что запустил интерфейс."""
    bp = bundled.bundled_python()
    if bp:
        return [str(bp)]
    if IS_WIN and shutil.which("py"):
        try:
            r = subprocess.run(["py", "-3.12", "-c", "import sys;print(sys.executable)"], capture_output=True, timeout=20)
            if r.returncode == 0 and r.stdout.strip():
                return [r.stdout.decode("utf-8", "replace").strip()]
        except Exception:  # noqa: BLE001
            pass
    if not IS_WIN:
        p = shutil.which("python3.12")
        if p:
            return [p]
    return [bundled.console_python()]
