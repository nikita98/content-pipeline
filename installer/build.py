"""Сборка Windows-установщика ContentPipeline-Setup-<версия>.exe.

  python installer/build.py --version 0.1.0                 # всё: файлы, программы, Inno Setup
  python installer/build.py --version 0.1.0 --no-compile    # без Inno Setup (проверка на Linux/macOS)

Шаги:
1. installer/build/stage — копия файлов репозитория (git ls-files) без installer/, .github/ и start-скриптов.
2. Программы по installer/deps.json (fetch_deps.py: скачать, сверить SHA256, распаковать в stage/tools).
3. stage/installed.json — признак установленной копии для app/ (версия, программы).
4. Значок app/setup/icon.ico, секция [Components] и код описаний из app/setup/components.json
   (installer/build/components.iss, installer/build/components_code.iss).
5. ISCC installer/ContentPipeline.iss → installer/build/out/ContentPipeline-Setup-<версия>.exe.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
BUILD = HERE / "build"
STAGE = BUILD / "stage"
EXCLUDE_PREFIXES = ("installer/", ".github/", ".claude/", ".agents/")
EXCLUDE_FILES = {"start.bat", "start-bench.bat", "start.command", "start-bench.command", ".gitignore", ".gitattributes"}


# --- 1. файлы репозитория ----------------------------------------------------------------------

def repo_files() -> list[str]:
    try:
        out = subprocess.run(["git", "-c", "core.quotepath=false", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True)
        files = [f for f in out.stdout.decode("utf-8").split("\0") if f]
    except (OSError, subprocess.CalledProcessError):
        files = []
        skip = {".git", "data", "__pycache__", "node_modules", "build", "cache"}
        for p in REPO.rglob("*"):
            rel = p.relative_to(REPO).as_posix()
            if p.is_file() and not (set(p.relative_to(REPO).parts) & skip) and not rel.startswith((".venv", "bench/runs", "bench/tools")):
                files.append(rel)
    return sorted(f for f in files if not f.startswith(EXCLUDE_PREFIXES) and f not in EXCLUDE_FILES)


def stage_repo() -> int:
    n = 0
    for rel in repo_files():
        src = REPO / rel
        if not src.is_file():
            continue
        dst = STAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    return n


# --- 4a. значок (без сторонних библиотек) ------------------------------------------------------

GREEN, LIME = (0x00, 0x46, 0x3C), (0xE6, 0xF5, 0xC8)


def _pixel(x: float, y: float) -> tuple[int, int, int, int]:
    """Скруглённый квадрат цвета бренда с треугольником «воспроизвести». x, y в [0, 1)."""
    r = 0.2
    cx, cy = min(max(x, r), 1 - r), min(max(y, r), 1 - r)
    inside = (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0.02 <= x <= 0.98 and 0.02 <= y <= 0.98
    if not inside:
        return (0, 0, 0, 0)
    # треугольник: вершины (0.36,0.27) (0.36,0.73) (0.76,0.5)
    in_tri = x >= 0.36 and abs(y - 0.5) <= (0.76 - x) * (0.23 / 0.40)
    return (*LIME, 255) if in_tri else (*GREEN, 255)


def _render(size: int, ss: int = 4) -> list[list[tuple[int, int, int, int]]]:
    rows = []
    for j in range(size):
        row = []
        for i in range(size):
            acc = [0, 0, 0, 0]
            for sj in range(ss):
                for si in range(ss):
                    p = _pixel((i + (si + 0.5) / ss) / size, (j + (sj + 0.5) / ss) / size)
                    a = p[3]
                    acc[0] += p[0] * a; acc[1] += p[1] * a; acc[2] += p[2] * a; acc[3] += a
            a = acc[3]
            row.append((acc[0] // a, acc[1] // a, acc[2] // a, a // (ss * ss)) if a else (0, 0, 0, 0))
        rows.append(row)
    return rows


def _png(rows) -> bytes:
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(c for px in r for c in px) for r in rows)

    def chunk(t: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _dib(rows) -> bytes:
    h, w = len(rows), len(rows[0])
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    xor = b"".join(bytes(c for (r, g, b, a) in row for c in (b, g, r, a)) for row in reversed(rows))
    mask_row = ((w + 31) // 32) * 4
    return hdr + xor + b"\x00" * (mask_row * h)


def make_icon(path: Path) -> None:
    images = []
    for s in (16, 24, 32, 48, 64, 256):
        rows = _render(s, 4 if s <= 64 else 2)
        images.append((s, _png(rows) if s == 256 else _dib(rows)))
    head = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, data = b"", b""
    for s, blob in images:
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(blob), offset + len(data))
        data += blob
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(head + entries + data)


# --- 4b. секция [Components] из components.json --------------------------------------------------

def pas(s: str) -> str:
    """Строка для Pascal Script / Inno: одинарные кавычки удваиваются, переводы строк — пробел."""
    return "'" + re.sub(r"\s+", " ", s).replace("'", "''") + "'"


def iss_str(s: str) -> str:
    """Значение параметра секции Inno в двойных кавычках."""
    return '"' + re.sub(r"\s+", " ", s).replace('"', '""') + '"'


def size_text(mb: float) -> str:
    if not mb:
        return ""
    return f"≈ {mb / 1024:.1f} ГБ".replace(".", ",") if mb >= 1024 else f"≈ {round(mb)} МБ"


def gen_components(base_mb: float) -> tuple[str, str]:
    data = json.loads((REPO / "app" / "setup" / "components.json").read_text(encoding="utf-8"))
    comps = data["components"]
    lines = ["; Сгенерировано installer/build.py из app/setup/components.json — не править вручную.", "[Components]"]
    code = ["// Сгенерировано installer/build.py из app/setup/components.json — не править вручную.",
            "function CompDescription(Index: Integer): String;", "begin", "  case Index of"]
    nvidia_idx, ids = [], []
    for i, c in enumerate(comps):
        mb = base_mb if c["id"] == "base" else (c.get("size_mb") or 0)
        size = size_text(mb)
        if size:
            caption = c["name"] + (f" — {size} на диске" if c["id"] == "base" else f" — скачать {size}")
        else:
            caption = c["name"]
        parts = [f"Name: \"{c['id']}\"", f"Description: {iss_str(caption)}"]
        if c.get("default") or c.get("fixed"):
            parts.append("Types: custom")
        flags = ["fixed"] if c.get("fixed") else []
        if flags:
            parts.append("Flags: " + " ".join(flags))
        if c["id"] != "base" and mb:
            parts.append(f"ExtraDiskSpaceRequired: {int(mb * 1024 * 1024)}")
        lines.append("; ".join(parts))
        desc = c.get("description", "")
        if size and c["id"] != "base":
            desc += f" Скачивание {size}, нужен интернет."
        code.append(f"    {i}: Result := {pas(desc)};")
        if c.get("nvidia"):
            nvidia_idx.append(i)
        ids.append(c["id"])
    code += ["  else", "    Result := '';", "  end;", "end;", "",
             "function CompIsNvidiaOnly(Index: Integer): Boolean;", "begin",
             "  Result := " + (" or ".join(f"(Index = {i})" for i in nvidia_idx) or "False") + ";", "end;", "",
             "function CompIdAt(Index: Integer): String;", "begin", "  case Index of"]
    code += [f"    {i}: Result := '{cid}';" for i, cid in enumerate(ids)]
    code += ["  else", "    Result := '';", "  end;", "end;", "",
             f"function CompCount: Integer;\nbegin\n  Result := {len(ids)};\nend;", ""]
    return "\n".join(lines) + "\n", "\n".join(code) + "\n"


def dir_mb(p: Path) -> float:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / (1024 * 1024)


# --- 5. Inno Setup ------------------------------------------------------------------------------

def find_iscc(given: str | None) -> str | None:
    if given:
        return given
    for c in (os.environ.get("ISCC"), shutil.which("iscc"), shutil.which("ISCC"),
              r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe", r"C:\Program Files\Inno Setup 6\ISCC.exe",
              str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe")):
        if c and Path(c).is_file():
            return c
    return None


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True, help="например 0.1.0")
    ap.add_argument("--no-fetch", action="store_true", help="без программ (только проверка файлов и генерации)")
    ap.add_argument("--no-compile", action="store_true", help="не запускать Inno Setup")
    ap.add_argument("--iscc", help="путь к ISCC.exe")
    ap.add_argument("--allow-unpinned", action="store_true", help="передать fetch_deps.py: не падать без sha256")
    a = ap.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+([.-][0-9A-Za-z.-]+)?", a.version):
        sys.exit("--version: вида 0.1.0")
    nums = [int(x) for x in re.findall(r"\d+", a.version)[:4]] + [0, 0, 0, 0]
    numver = ".".join(str(x) for x in nums[:4])

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    print(f"1. Файлы репозитория: {stage_repo()}")

    if not a.no_fetch:
        cmd = [sys.executable, str(HERE / "fetch_deps.py"), "--out", str(STAGE)] + (["--allow-unpinned", "--print-hashes"] if a.allow_unpinned else [])
        print("2. Программы:", " ".join(cmd), flush=True)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            return r.returncode
        if not (STAGE / "tools" / "python" / "python.exe").is_file() and sys.platform.startswith("win"):
            sys.exit("Нет tools/python/python.exe после распаковки")

    deps = json.loads((HERE / "deps.json").read_text(encoding="utf-8"))["deps"]
    info = {"version": a.version, "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tools": {d["id"]: d["version"] for d in deps}}
    (STAGE / "installed.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (STAGE / "licenses").mkdir(exist_ok=True)
    shutil.copy2(HERE / "licenses" / "README.txt", STAGE / "licenses" / "README.txt")
    print("3. installed.json:", info)

    make_icon(STAGE / "app" / "setup" / "icon.ico")
    base_mb = dir_mb(STAGE)
    comp, code = gen_components(base_mb)
    (BUILD / "components.iss").write_text(comp, encoding="utf-8-sig")
    (BUILD / "components_code.iss").write_text(code, encoding="utf-8-sig")
    print(f"4. Значок и компоненты; основа ≈ {base_mb:.0f} МБ")

    if a.no_compile:
        return 0
    iscc = find_iscc(a.iscc)
    if not iscc:
        sys.exit("Не найден ISCC.exe (Inno Setup 6). Установите: winget install JRSoftware.InnoSetup или choco install innosetup")
    out = BUILD / "out"
    out.mkdir(parents=True, exist_ok=True)
    cmd = [iscc, f"/DAppVersion={a.version}", f"/DNumVersion={numver}", f"/O{out}", str(HERE / "ContentPipeline.iss")]
    print("5.", " ".join(cmd), flush=True)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        return r.returncode
    exe = out / f"ContentPipeline-Setup-{a.version}.exe"
    print(f"Готово: {exe} ({exe.stat().st_size / 1e6:.1f} МБ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
