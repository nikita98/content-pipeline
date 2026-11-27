"""Слова с таймкодами (из asr_run.py) → субтитры для монтажа.

Пишет рядом:
  <name>.captions.json  формат Caption для @remotion/captions: text, startMs, endMs, timestampMs, confidence
  <name>.srt            для HyperFrames, ffmpeg и любого редактора (по 3–4 слова в строке)

Пример:
  python skills/kp-bench/scripts/captions.py bench/runs/asr/nikita/gigaam.words.json --words-per-line 3
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import _common  # noqa: F401


def ts(sec: float) -> str:
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3_600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", type=Path)
    ap.add_argument("--words-per-line", type=int, default=3)
    a = ap.parse_args()
    words = json.loads(a.words.read_text(encoding="utf-8"))
    base = a.words.with_suffix("").with_suffix("")
    caps = [{"text": (" " if i else "") + w["text"], "startMs": int(w["start"] * 1000), "endMs": int(w["end"] * 1000),
             "timestampMs": int((w["start"] + w["end"]) * 500), "confidence": None} for i, w in enumerate(words)]
    Path(f"{base}.captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=0), encoding="utf-8")
    lines = []
    for n, i in enumerate(range(0, len(words), a.words_per_line), 1):
        grp = words[i:i + a.words_per_line]
        lines.append(f"{n}\n{ts(grp[0]['start'])} --> {ts(grp[-1]['end'])}\n{' '.join(w['text'] for w in grp)}\n")
    Path(f"{base}.srt").write_text("\n".join(lines), encoding="utf-8")
    print(f"Готово: {base}.captions.json и {base}.srt ({len(words)} слов)")


if __name__ == "__main__":
    main()
