"""Замер громкости через ffmpeg loudnorm и, по желанию, двухпроходная нормализация.

Пример:
  python skills/kp-bench/scripts/loudness.py in.wav                      # замер: I (LUFS), TP (dBTP), LRA
  python skills/kp-bench/scripts/loudness.py in.mp4 --normalize out.mp4  # −14 LUFS / −1 dBTP / LRA 11
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

import _common  # noqa: F401


def measure(path: str, i: float, tp: float, lra: float) -> dict:
    ff = shutil.which("ffmpeg") or sys.exit("ffmpeg не найден")
    out = subprocess.run([ff, "-hide_banner", "-nostats", "-i", path, "-af",
                          f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", out.stderr, re.S)
    if not m:
        sys.exit("Не удалось прочитать вывод loudnorm:\n" + out.stderr[-800:])
    return json.loads(m.group(0))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--normalize", metavar="OUT")
    ap.add_argument("--i", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--lra", type=float, default=11.0)
    a = ap.parse_args()
    m = measure(a.input, a.i, a.tp, a.lra)
    print(f"{a.input}: I {m['input_i']} LUFS, TP {m['input_tp']} dBTP, LRA {m['input_lra']} LU")
    if not a.normalize:
        return
    flt = (f"loudnorm=I={a.i}:TP={a.tp}:LRA={a.lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
           f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    ff = shutil.which("ffmpeg")
    cmd = [ff, "-hide_banner", "-y", "-i", a.input, "-af", flt, "-ar", "48000"]
    if a.normalize.lower().endswith((".mp4", ".mov", ".mkv")):
        cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"]
    subprocess.run(cmd + [a.normalize], check=True)
    m2 = measure(a.normalize, a.i, a.tp, a.lra)
    print(f"{a.normalize}: I {m2['input_i']} LUFS, TP {m2['input_tp']} dBTP, LRA {m2['input_lra']} LU")


if __name__ == "__main__":
    main()
