"""Встроенные программы установленной копии и переменные окружения для дочерних процессов.

Установщик (installer/ContentPipeline.iss) кладёт переносные программы в папку установки:
  tools/python        Python 3.12 (python-build-standalone), python.exe и pythonw.exe
  tools/ffmpeg/bin    ffmpeg.exe, ffprobe.exe
  tools/node          node.exe, npm.cmd, npx.cmd
  tools/mingit/cmd    git.exe (MinGit)
  tools/auto-editor   auto-editor.exe
Поиск программ: сначала встроенные, потом системные (PATH). apply_env() ставит встроенные папки в начало PATH
этого процесса — дочерние процессы (скрипты стенда, pip, агенты) видят те же программы.

В установленной копии всё тяжёлое — внутри папки установки, в data/: окружения Python, модели, кэш pip и npm.
В копии из git (start.bat) переменные моделей и кэша не меняются: всё как раньше.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .paths import BUNDLED, DATA, INSTALLED, IS_WIN

# папки встроенных программ относительно tools/ — в порядке поиска
BUNDLED_DIRS = ["python", "python/Scripts", "ffmpeg/bin", "node", "mingit/cmd", "auto-editor"]

VENV_ROOT = DATA / "venv" if INSTALLED else None
MODEL_ENV = {
    "HF_HOME": DATA / "models" / "huggingface",
    "TORCH_HOME": DATA / "models" / "torch",
    "PIP_CACHE_DIR": DATA / "cache" / "pip",
    "npm_config_cache": DATA / "cache" / "npm",
}


def bundled_dirs() -> list[Path]:
    """Существующие папки встроенных программ (только в папке установки)."""
    return [BUNDLED / d for d in BUNDLED_DIRS if (BUNDLED / d).is_dir()]


def is_bundled(path: str | None) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve().relative_to(BUNDLED.resolve())
        return True
    except (ValueError, OSError):
        return False


def find_bundled(exe: str) -> str | None:
    exts = [".exe", ".cmd", ".bat", ""] if IS_WIN else [""]
    for d in bundled_dirs():
        for ext in exts:
            p = d / f"{exe}{ext}"
            if p.is_file():
                return str(p)
    return None


def bundled_python(windowless: bool = False) -> Path | None:
    """Встроенный Python. windowless — pythonw.exe (без чёрного окна)."""
    d = BUNDLED / "python"
    name = ("pythonw.exe" if windowless else "python.exe") if IS_WIN else "bin/python3"
    p = d / name
    return p if p.is_file() else None


def console_python() -> str:
    """Python для дочерних скриптов: если сервер запущен через pythonw.exe — python.exe рядом с ним."""
    exe = Path(sys.executable)
    if IS_WIN and exe.name.lower() == "pythonw.exe":
        alt = exe.with_name("python.exe")
        if alt.is_file():
            return str(alt)
    return str(exe)


def apply_env() -> None:
    """Встроенные программы — в начало PATH; в установленной копии — модели и кэш в data/."""
    dirs = [str(d) for d in bundled_dirs()]
    if dirs:
        cur = os.environ.get("PATH", "")
        parts = [p for p in cur.split(os.pathsep) if p and p not in dirs]
        os.environ["PATH"] = os.pathsep.join(dirs + parts)
    if INSTALLED:
        for k, v in MODEL_ENV.items():
            os.environ[k] = str(v)
        # pip и Python не должны брать пакеты пользователя из %APPDATA%\Python
        os.environ.setdefault("PYTHONNOUSERSITE", "1")
