"""Проверка среды тестировщика: Python, Node, ffmpeg, git, auto-editor, видеокарта, место на диске.
Встроенные программы установленной копии (папка tools/) находятся первыми — см. _common.use_bundled_tools().

Пример:
  python skills/kp-bench/scripts/check_env.py --tester nikita
Пишет bench/env/<tester>.json и печатает таблицу.
"""
from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from datetime import date

from _common import repo_root, slug, write_json


def run(cmd: list[str]) -> str | None:
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    try:
        out = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=30,
                             encoding="utf-8", errors="replace")
        return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
    except Exception as e:  # noqa: BLE001
        return f"ошибка: {e}"


def gpu() -> dict:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return {"nvidia": False}
    try:
        out = subprocess.run([exe, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=30)
        name, mem, drv = [x.strip() for x in out.stdout.strip().splitlines()[0].split(",")]
        return {"nvidia": True, "name": name, "vram": mem, "driver": drv}
    except Exception as e:  # noqa: BLE001
        return {"nvidia": True, "error": str(e)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tester", required=True, help="имя тестировщика латиницей, например nikita")
    a = ap.parse_args()
    root = repo_root()

    free_gb = round(shutil.disk_usage(root).free / 1024**3, 1)
    env = {
        "tester": slug(a.tester),
        "date": date.today().isoformat(),
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "cpu": platform.processor() or None,
        "python": sys.version.split()[0],
        "node": run(["node", "--version"]),
        "npm": run(["npm", "--version"]),
        "ffmpeg": run(["ffmpeg", "-version"]),
        "git": run(["git", "--version"]),
        "auto_editor": run(["auto-editor", "--version"]),
        "installed": (root / "installed.json").is_file(),
        "gpu": gpu(),
        "disk_free_gb": free_gb,
    }
    write_json(root / "bench" / "env" / f"{env['tester']}.json", env)

    need = {
        "python": sys.version_info >= (3, 10),
        "node": bool(env["node"]) and env["node"].lstrip("v").split(".")[0].isdigit() and int(env["node"].lstrip("v").split(".")[0]) >= 20,
        "ffmpeg": bool(env["ffmpeg"]),
        "git": bool(env["git"]),
        "disk_free_gb": free_gb >= 20,
    }
    print(f"Тестировщик: {env['tester']}   ОС: {env['os']} {env['machine']}")
    for k in ["python", "node", "ffmpeg", "git"]:
        print(f"  {'OK ' if need[k] else 'НЕТ'}  {k:7} {env[k] or 'не найден'}")
    print(f"  {'OK ' if env['auto_editor'] else '-- '}  auto-editor {env['auto_editor'] or 'не найден (нужен для voice-clean)'}")
    g = env["gpu"]
    print(f"  {'OK ' if g.get('nvidia') else '-- '}  gpu     {g.get('name', 'NVIDIA не найдена')} {g.get('vram', '')}")
    print(f"  {'OK ' if need['disk_free_gb'] else 'МАЛО'}  disk    {free_gb} ГБ свободно (нужно от 20 ГБ на модели)")
    if not g.get("nvidia"):
        print("Без NVIDIA: Qwen3-TTS локально не тестируем, GigaAM и Whisper — на CPU, медленнее.")
    missing = [k for k, v in need.items() if not v]
    print("Готово к бесплатным тестам." if not missing else f"Не хватает: {', '.join(missing)} — см. references/install.md")


if __name__ == "__main__":
    main()
