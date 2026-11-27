"""Доля ошибок распознавания (WER) и символов (CER) между эталоном и результатом.

Нормализация: нижний регистр, ё → е, без пунктуации, дефисы → пробел.
Эталон для записи эксперта — assets/inputs/script_ru_spoken.txt (числа словами).

Пример:
  python skills/kp-bench/scripts/wer.py --ref skills/kp-bench/assets/inputs/script_ru_spoken.txt --hyp out/gigaam.txt
  python skills/kp-bench/scripts/wer.py --ref ref.txt --hyp a.txt b.txt c.txt   # несколько вариантов сразу
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import _common  # noqa: F401  (кодировка вывода)


def norm(t: str) -> list[str]:
    t = t.lower().replace("ё", "е")
    t = re.sub(r"[-‐‑–—]", " ", t)
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    return t.split()


def edit_distance(a: list, b: list) -> tuple[int, int, int, int]:
    """Возвращает (расстояние, замены, удаления, вставки)."""
    n, m = len(a), len(b)
    d = [[(0, 0, 0, 0)] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        d[i][0] = (i, 0, i, 0)
    for j in range(1, m + 1):
        d[0][j] = (j, 0, 0, j)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                d[i][j] = d[i - 1][j - 1]
                continue
            s, de, ins = d[i - 1][j - 1], d[i - 1][j], d[i][j - 1]
            best = min((s[0], 0), (de[0], 1), (ins[0], 2))
            if best[1] == 0:
                d[i][j] = (s[0] + 1, s[1] + 1, s[2], s[3])
            elif best[1] == 1:
                d[i][j] = (de[0] + 1, de[1], de[2] + 1, de[3])
            else:
                d[i][j] = (ins[0] + 1, ins[1], ins[2], ins[3] + 1)
    return d[n][m]


def score(ref: str, hyp: str) -> dict:
    rw, hw = norm(ref), norm(hyp)
    dist, sub, dele, ins = edit_distance(rw, hw)
    rc, hc = list("".join(rw)), list("".join(hw))
    cdist = edit_distance(rc, hc)[0] if len(rc) * len(hc) < 4_000_000 else None
    return {
        "wer": round(dist / max(len(rw), 1), 4),
        "cer": round(cdist / max(len(rc), 1), 4) if cdist is not None else None,
        "ref_words": len(rw), "substitutions": sub, "deletions": dele, "insertions": ins,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, type=Path)
    ap.add_argument("--hyp", required=True, nargs="+", type=Path)
    ap.add_argument("--json", action="store_true", help="вывести JSON")
    a = ap.parse_args()
    ref = a.ref.read_text(encoding="utf-8")
    res = {str(h): score(ref, h.read_text(encoding="utf-8")) for h in a.hyp}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    for h, r in res.items():
        cer = f"{r['cer']:.1%}" if r["cer"] is not None else "—"
        print(f"{h}: WER {r['wer']:.1%}  CER {cer}  (замен {r['substitutions']}, пропусков {r['deletions']}, вставок {r['insertions']}, слов в эталоне {r['ref_words']})")


if __name__ == "__main__":
    main()
