"""Пути: корень репозитория, рабочие папки, проверка, что путь не выходит за разрешённую папку."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
ROOT = APP_DIR.parent
WEB_DIR = APP_DIR / "web"
RUNS = ROOT / "bench" / "runs"          # тяжёлые файлы, логи, экспорт (в .gitignore)
LOG_DIR = RUNS / "_log"
SETTINGS_FILE = APP_DIR / "settings.local.json"

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

TESTER_RE = re.compile(r"^[a-z0-9-]{1,32}$")


class PathError(ValueError):
    """Путь вне разрешённых папок, с '..' или через символическую ссылку."""


def _norm(p: Path) -> str:
    return os.path.normcase(os.path.normpath(str(p)))


def safe_path(rel: str, allowed: list[Path], must_exist: bool = False) -> Path:
    """Путь от корня репозитория (rel), лежащий внутри одной из папок allowed.

    Отказ: абсолютный путь, '..', символическая ссылка на любом уровне, выход за allowed.
    """
    if not isinstance(rel, str) or not rel or "\x00" in rel:
        raise PathError("пустой путь")
    rel = rel.replace("\\", "/")
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if rel.startswith("/") or re.match(r"^[A-Za-z]:", rel) or any(p == ".." for p in parts):
        raise PathError("путь вне разрешённых папок")
    target = ROOT.joinpath(*parts)
    # лексический путь должен совпасть с реальным: так отсекаются символические ссылки
    cur = ROOT
    for p in parts:
        cur = cur / p
        if cur.is_symlink():
            raise PathError("символическая ссылка")
    if target.exists() and _norm(target.resolve()) != _norm(target):
        raise PathError("символическая ссылка")
    t = _norm(target)
    if not any(t == _norm(a) or t.startswith(_norm(a) + os.sep) for a in allowed):
        raise PathError("путь вне разрешённых папок")
    if must_exist and not target.exists():
        raise PathError("файл не найден")
    return target


def rel(p: Path) -> str:
    """Путь от корня репозитория с прямыми слешами (для интерфейса и argv)."""
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def check_tester(name) -> str:
    if not isinstance(name, str) or not TESTER_RE.match(name):
        raise ValueError("Имя тестировщика: латиница в нижнем регистре, цифры и дефис, до 32 знаков (например, nikita).")
    return name
