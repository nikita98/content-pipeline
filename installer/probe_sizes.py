"""Примерный объём скачивания компонентов (app/setup/components.json) для Windows x64 и Python 3.12.

  python installer/probe_sizes.py              # таблица и предложение для size_mb
  python installer/probe_sizes.py --write      # записать size_mb в components.json

Как считает: для каждого шага pip — `pip install --dry-run --ignore-installed --report` (ничего не ставит),
затем HEAD по адресам колёс из отчёта и сумма Content-Length. Пакеты, общие для шагов одного компонента,
считаются один раз. Это объём СКАЧИВАНИЯ без моделей; на диске после распаковки занимает больше.
Запускать на Windows x64 с Python 3.12 (так делает workflow build-installer, задача probe).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "app" / "setup" / "components.json"


def head_size(url: str) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "content-pipeline-probe"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception as e:  # noqa: BLE001
        print(f"    HEAD {url}: {e}")
        return 0


def resolve(pkgs: list[str], index_url: str | None) -> list[dict]:
    with tempfile.TemporaryDirectory() as td:
        rep = Path(td) / "r.json"
        cmd = [sys.executable, "-m", "pip", "install", "--dry-run", "--ignore-installed", "--quiet", "--report", str(rep),
               "--disable-pip-version-check", *pkgs]
        if index_url:
            cmd += ["--index-url", index_url]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print("    pip: " + (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "    pip: ошибка")
            return []
        return json.loads(rep.read_text(encoding="utf-8")).get("install", [])


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    result = {}
    for c in data["components"]:
        if not c.get("steps"):
            continue
        seen: dict[str, tuple[str, int]] = {}
        clone = None
        for s in c["steps"]:
            if "git_clone" in s:
                clone = s["git_clone"]
                continue
            pkgs = [p for p in s["pip"] if p not in ("-U",)]
            if pkgs and pkgs[0] == "-e":
                # редактируемая установка из склонированного репозитория — считаем по git+URL
                extra = pkgs[1].split("[", 1)[1].rstrip("]") if "[" in pkgs[1] else ""
                pkgs = [f"gigaam[{extra}] @ git+{clone}" if extra else f"gigaam @ git+{clone}"]
            print(f"== {c['id']}: pip {' '.join(pkgs)}" + (f" ({s['index_url']})" if s.get("index_url") else ""), flush=True)
            for item in resolve(pkgs, s.get("index_url")):
                name = item["metadata"]["name"].lower()
                if name in seen:
                    continue
                url = item.get("download_info", {}).get("url", "")
                size = head_size(url) if url.startswith("http") else 0
                seen[name] = (item["metadata"]["version"], size)
        total = sum(sz for _, sz in seen.values()) / (1024 * 1024)
        top = sorted(seen.items(), key=lambda kv: -kv[1][1])[:6]
        print(f"   {c['id']}: {len(seen)} пакетов, ≈ {total:.0f} МБ; крупные: "
              + ", ".join(f"{n}=={v} {sz / 1048576:.0f} МБ" for n, (v, sz) in top), flush=True)
        result[c["id"]] = round(total)
    print("\nsize_mb:", json.dumps(result, ensure_ascii=False))
    if a.write:
        for c in data["components"]:
            if c["id"] in result and result[c["id"]]:
                c["size_mb"] = result[c["id"]]
        CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
