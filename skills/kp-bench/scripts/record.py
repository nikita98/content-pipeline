"""Запись результата одного прогона: тест × вариант × тестировщик.

Пример:
  python skills/kp-bench/scripts/record.py --test asr --variant gigaam --tester nikita \
      --metric wer=0.071 --metric run_s=42 --metric word_timestamps=1 \
      --setup-min 25 --verdict ok --note "на CPU, longform не понадобился"

  python skills/kp-bench/scripts/record.py --list      # какие тесты, варианты и метрики есть

Пишет bench/results/<test>/<дата>_<tester>_<variant>.json. Тяжёлые файлы (аудио, видео) не
коммитятся: кладите их в bench/runs/ и указывайте путь через --file.
"""
from __future__ import annotations

import argparse
import json
from datetime import date

from _common import load_catalog, repo_root, slug, write_json

VERDICTS = {"ok": "годится", "partial": "с оговорками", "no": "не годится", "fail": "не запустилось"}


def num(v: str):
    v = v.strip().replace(",", ".")
    try:
        return int(v) if v.lstrip("-").isdigit() else float(v)
    except ValueError:
        return v


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--test")
    ap.add_argument("--variant")
    ap.add_argument("--tester")
    ap.add_argument("--metric", action="append", default=[], help="имя=значение, можно несколько")
    ap.add_argument("--setup-min", type=float, help="сколько минут ушло на установку")
    ap.add_argument("--cost", type=float, default=0.0, help="потрачено на прогон")
    ap.add_argument("--currency", default="USD")
    ap.add_argument("--verdict", choices=VERDICTS, required=False)
    ap.add_argument("--note", default="")
    ap.add_argument("--file", action="append", default=[], help="путь к выходному файлу в bench/runs/")
    a = ap.parse_args()
    root = repo_root()
    cat = load_catalog(root)
    tests = {t["id"]: t for t in cat["tests"]}

    if a.list:
        for t in cat["tests"]:
            print(f"{t['id']}  [{'бесплатно' if t['group'] == 'free' else 'платно'}]  {t['title']}")
            print(f"    варианты: {', '.join(v['id'] for v in t['variants'])}")
            print(f"    метрики:  {', '.join(m['id'] for m in t['metrics'])}")
        return

    for need in ("test", "variant", "tester", "verdict"):
        if not getattr(a, need):
            ap.error(f"нужен --{need}")
    t = tests.get(a.test) or ap.error(f"нет теста {a.test}; см. --list")
    if a.variant not in {v["id"] for v in t["variants"]}:
        ap.error(f"у теста {a.test} нет варианта {a.variant}; есть: {', '.join(v['id'] for v in t['variants'])}")
    known = {m["id"] for m in t["metrics"]}
    metrics = {}
    for kv in a.metric:
        if "=" not in kv:
            ap.error(f"метрика без '=': {kv}")
        k, v = kv.split("=", 1)
        if k not in known:
            print(f"Внимание: метрики {k} нет в каталоге теста ({', '.join(sorted(known))}). Записываю как есть.")
        metrics[k] = num(v)

    env_path = root / "bench" / "env" / f"{slug(a.tester)}.json"
    env = json.loads(env_path.read_text(encoding="utf-8")) if env_path.is_file() else None
    rec = {
        "test": a.test, "variant": a.variant, "tester": slug(a.tester), "date": date.today().isoformat(),
        "metrics": metrics, "setup_min": a.setup_min,
        "cost": {"amount": a.cost, "currency": a.currency.upper()},
        "verdict": a.verdict, "note": a.note, "files": a.file,
        "env": {k: env.get(k) for k in ("os", "gpu")} if env else None,
    }
    base = root / "bench" / "results" / a.test / f"{rec['date']}_{rec['tester']}_{slug(a.variant)}"
    path, n = base.with_suffix(".json"), 2
    while path.exists():
        path = base.parent / f"{base.name}-{n}.json"; n += 1
    write_json(path, rec)
    print(f"Записано: {path.relative_to(root)}  ({VERDICTS[a.verdict]})")
    if not env:
        print("Нет описания среды: запустите check_env.py --tester " + rec["tester"])


if __name__ == "__main__":
    main()
