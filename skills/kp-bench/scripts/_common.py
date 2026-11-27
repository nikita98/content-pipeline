"""Общие функции скриптов kp-bench. Только стандартная библиотека Python 3.10+."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Установленная копия (Windows-установщик): программы встроены в <папка установки>/tools/.
# Ставим их в начало PATH, чтобы скрипты находили их и без интерфейса. В копии из git папок нет — PATH не меняется.
BUNDLED_DIRS = ["python", "python/Scripts", "ffmpeg/bin", "node", "mingit/cmd", "auto-editor"]


def use_bundled_tools() -> list[str]:
    base = Path(__file__).resolve().parents[3] / "tools"
    dirs = [str(base / d) for d in BUNDLED_DIRS if (base / d).is_dir()]
    if dirs:
        rest = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p and p not in dirs]
        os.environ["PATH"] = os.pathsep.join(dirs + rest)
    return dirs


use_bundled_tools()


def repo_root(start: Path | None = None) -> Path:
    """Ищет корень репозитория по файлу site/data/bench.json."""
    env = os.environ.get("KP_BENCH_ROOT")
    if env:
        return Path(env).resolve()
    p = (start or Path.cwd()).resolve()
    for d in [p, *p.parents]:
        if (d / "site" / "data" / "bench.json").is_file():
            return d
    here = Path(__file__).resolve()
    for d in here.parents:
        if (d / "site" / "data" / "bench.json").is_file():
            return d
    sys.exit("Не найден корень репозитория (site/data/bench.json). Запустите из папки репозитория или задайте KP_BENCH_ROOT.")


def load_catalog(root: Path) -> dict:
    return json.loads((root / "site" / "data" / "bench.json").read_text(encoding="utf-8"))


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE)
    return re.sub(r"-+", "-", s).strip("-") or "x"


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
