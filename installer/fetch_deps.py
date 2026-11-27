"""Скачивает переносные программы по installer/deps.json, проверяет SHA256 и раскладывает в папку tools/.

  python installer/fetch_deps.py --out installer/build/stage            # скачать, проверить, распаковать
  python installer/fetch_deps.py --print-hashes --allow-unpinned        # посчитать хэши для deps.json

Только стандартная библиотека Python 3.10+. Работает на Windows, macOS и Linux (распаковка — средствами Python).
Кэш скачанного — installer/cache/ (повторная сборка не качает заново, хэш проверяется каждый раз).
Если у программы есть опубликованный файл сумм (sums_url) — хэш дополнительно сверяется с ним.
Лицензии — в <out>/licenses/<id>/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tarfile
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
UA = {"User-Agent": "content-pipeline-installer-build"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dst: Path, tries: int = 3) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    for n in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r, tmp.open("wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                got, last = 0, 0.0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if time.time() - last > 5:
                        last = time.time()
                        print(f"    {got / 1e6:.0f} МБ" + (f" из {total / 1e6:.0f}" if total else ""), flush=True)
            tmp.replace(dst)
            return
        except Exception as e:  # noqa: BLE001
            print(f"    попытка {n}: {e}", flush=True)
            if n == tries:
                raise
            time.sleep(5 * n)


def published_sum(d: dict, cache: Path) -> str | None:
    """Хэш из опубликованного файла сумм (SHA256SUMS, SHASUMS256.txt), если он указан."""
    url = d.get("sums_url")
    if not url:
        return None
    name = urllib.parse.unquote(d["url"].rsplit("/", 1)[-1])
    sums = cache / f"{d['id']}-{d['version']}-sums.txt"
    if not sums.is_file():
        download(url, sums)
    for line in sums.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].lstrip("*").split("/")[-1] == name:
            return parts[0].lower()
    return None


def _strip(name: str, n: int) -> str | None:
    parts = [p for p in PurePosixPath(name.replace("\\", "/")).parts if p not in ("", ".")]
    if any(p == ".." for p in parts) or (parts and (parts[0].endswith(":") or name.startswith("/"))):
        raise ValueError(f"опасный путь в архиве: {name}")
    parts = parts[n:]
    return "/".join(parts) if parts else None


def extract(d: dict, archive: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    kind, strip = d["type"], int(d.get("strip", 0))
    if kind == "file":
        shutil.copy2(archive, dest / d.get("filename", archive.name))
        return
    if kind == "zip":
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                rel = _strip(info.filename, strip)
                if not rel:
                    continue
                out = dest / rel
                if info.is_dir():
                    out.mkdir(parents=True, exist_ok=True)
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, out.open("wb") as f:
                    shutil.copyfileobj(src, f)
        return
    if kind == "tar.gz":
        with tarfile.open(archive, "r:gz") as t:
            for m in t.getmembers():
                rel = _strip(m.name, strip)
                if not rel:
                    continue
                out = dest / rel
                if m.isdir():
                    out.mkdir(parents=True, exist_ok=True)
                elif m.isfile():
                    out.parent.mkdir(parents=True, exist_ok=True)
                    src = t.extractfile(m)
                    assert src is not None
                    with src, out.open("wb") as f:
                        shutil.copyfileobj(src, f)
                # ссылки и устройства пропускаем: в сборках для Windows их нет
        return
    raise ValueError(f"неизвестный тип архива {kind}")


def licenses(d: dict, dest: Path, out: Path) -> list[str]:
    ld = out / "licenses" / d["id"]
    ld.mkdir(parents=True, exist_ok=True)
    found = []
    for g in d.get("license_globs", []):
        for p in sorted(dest.glob(g)):
            if p.is_file():
                shutil.copy2(p, ld / p.name)
                found.append(p.name)
    for f in d.get("license_files", []):
        p = REPO / f
        shutil.copy2(p, ld / p.name)
        found.append(p.name)
    (ld / "SOURCE.txt").write_text(
        f"{d['name']}\nВерсия: {d['version']}\nЛицензия: {d['license']}\nСкачано: {d['url']}\nSHA256: {d.get('sha256', '')}\n"
        f"Исходный код: {d.get('source', '')}\n", encoding="utf-8")
    return found


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deps", type=Path, default=HERE / "deps.json")
    ap.add_argument("--cache", type=Path, default=HERE / "cache")
    ap.add_argument("--out", type=Path, help="корень сборки: программы — в <out>/tools, лицензии — в <out>/licenses")
    ap.add_argument("--only", default="", help="id через запятую")
    ap.add_argument("--print-hashes", action="store_true", help="напечатать SHA256 скачанного")
    ap.add_argument("--allow-unpinned", action="store_true", help="не падать, если в deps.json пустой sha256")
    a = ap.parse_args()
    deps = json.loads(a.deps.read_text(encoding="utf-8"))["deps"]
    only = {x for x in a.only.split(",") if x}
    errors = []
    for d in deps:
        if only and d["id"] not in only:
            continue
        name = urllib.parse.unquote(d["url"].rsplit("/", 1)[-1])
        arc = a.cache / f"{d['id']}-{d['version']}" / name
        print(f"== {d['id']} {d['version']}: {d['url']}", flush=True)
        if not arc.is_file():
            download(d["url"], arc)
        got = sha256(arc)
        pub = published_sum(d, a.cache)
        if a.print_hashes:
            print(f"   sha256 {got}  ({arc.stat().st_size / 1e6:.1f} МБ)")
        if pub is not None:
            print(f"   опубликованный хэш: {'совпадает' if pub == got else 'НЕ СОВПАДАЕТ ' + pub}")
            if pub != got:
                errors.append(f"{d['id']}: хэш не совпал с опубликованным {d['sums_url']}")
        elif d.get("sums_url"):
            errors.append(f"{d['id']}: в {d['sums_url']} нет строки для {name}")
        want = (d.get("sha256") or "").lower()
        if not want:
            msg = f"{d['id']}: в deps.json не закреплён sha256 (получено {got})"
            if a.allow_unpinned:
                print("   ВНИМАНИЕ: " + msg)
            else:
                errors.append(msg)
        elif want != got:
            errors.append(f"{d['id']}: SHA256 {got} не совпадает с deps.json {want}")
            arc.unlink()   # испорченный или подменённый файл — из кэша вон
            continue
        if a.out:
            dest = a.out / "tools" / d["dest"]
            extract(d, arc, dest)
            for r in d.get("remove", []):
                p = dest / r
                if p.is_dir():
                    shutil.rmtree(p)
                elif p.is_file():
                    p.unlink()
            lic = licenses(d, dest, a.out)
            print(f"   распаковано в {dest}; лицензии: {', '.join(lic) or 'НЕ НАЙДЕНЫ'}")
            if not lic:
                errors.append(f"{d['id']}: не найдены файлы лицензии ({d.get('license_globs')})")
    if errors:
        print("\nОшибки:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
