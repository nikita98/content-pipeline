"""Слепое прослушивание: копирует файлы вариантов под случайными именами и хранит ключ отдельно.

Пример:
  python skills/kp-bench/scripts/blind.py make bench/runs/tts-free/nikita blind/tts
     -> blind/tts/A.wav, B.wav ... и blind/tts/_key.json (не открывать до оценки)
  python skills/kp-bench/scripts/blind.py reveal blind/tts --scores "A=4,B=3,C=5"
     -> печатает, какому варианту какая оценка
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import string
from pathlib import Path

import _common  # noqa: F401

AUDIO_VIDEO = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".mp4", ".mov", ".webm"}


def make(src: Path, dst: Path) -> None:
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in AUDIO_VIDEO)
    if not files:
        raise SystemExit(f"В {src} нет аудио или видео")
    labels = list(string.ascii_uppercase[: len(files)])
    random.shuffle(files)
    dst.mkdir(parents=True, exist_ok=True)
    key = {}
    for lab, f in zip(labels, files):
        shutil.copy2(f, dst / f"{lab}{f.suffix.lower()}")
        key[lab] = f.name
    (dst / "_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Готово: {len(files)} файлов в {dst}. Оцените A..{labels[-1]} по шкале 1–5, ключ — _key.json, не открывайте его до оценки.")


def reveal(dst: Path, scores: str) -> None:
    key = json.loads((dst / "_key.json").read_text(encoding="utf-8"))
    for part in scores.split(","):
        lab, val = part.split("=")
        print(f"{lab.strip()} = {val.strip()}  ->  {key[lab.strip()]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("src", type=Path); m.add_argument("dst", type=Path)
    r = sub.add_parser("reveal"); r.add_argument("dst", type=Path); r.add_argument("--scores", required=True)
    a = ap.parse_args()
    make(a.src, a.dst) if a.cmd == "make" else reveal(a.dst, a.scores)


if __name__ == "__main__":
    main()
