"""Свод результатов всех тестировщиков в site/data/bench_results.json (его показывает страница стенда).

Пример:
  python skills/kp-bench/scripts/summary.py           # пересобрать свод и напечатать таблицу
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from statistics import mean

from _common import load_catalog, repo_root, write_json

VERDICTS = {"ok": "годится", "partial": "с оговорками", "no": "не годится", "fail": "не запустилось"}


def main() -> None:
    root = repo_root()
    cat = load_catalog(root)
    runs = defaultdict(list)
    for p in sorted((root / "bench" / "results").glob("*/*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        runs[(r["test"], r["variant"])].append(r)

    out = {"updated": date.today().isoformat(), "results": []}
    for t in cat["tests"]:
        for v in t["variants"]:
            rs = runs.get((t["id"], v["id"]), [])
            if not rs:
                continue
            metrics = {}
            for m in t["metrics"]:
                vals = [r["metrics"][m["id"]] for r in rs if isinstance(r["metrics"].get(m["id"]), (int, float))]
                if vals:
                    metrics[m["id"]] = round(mean(vals), 4)
            verdicts = defaultdict(int)
            for r in rs:
                verdicts[r["verdict"]] += 1
            cost = defaultdict(float)
            for r in rs:
                cost[r["cost"]["currency"]] += r["cost"]["amount"]
            out["results"].append({
                "test": t["id"], "variant": v["id"], "runs": len(rs),
                "testers": sorted({r["tester"] for r in rs}),
                "last_date": max(r["date"] for r in rs),
                "metrics": metrics, "verdicts": dict(verdicts),
                "cost": {k: round(x, 2) for k, x in cost.items() if x},
                "setup_min": round(mean([r["setup_min"] for r in rs if r.get("setup_min") is not None]), 1)
                if any(r.get("setup_min") is not None for r in rs) else None,
                "notes": [f"{r['tester']}: {r['note']}" for r in rs if r.get("note")][-3:],
            })
    write_json(root / "site" / "data" / "bench_results.json", out)

    if not out["results"]:
        print("Результатов пока нет.")
        return
    for r in out["results"]:
        ms = ", ".join(f"{k}={v}" for k, v in r["metrics"].items())
        vs = ", ".join(f"{VERDICTS.get(k, k)}: {n}" for k, n in r["verdicts"].items())
        print(f"{r['test']:12} {r['variant']:18} прогонов {r['runs']}  {ms}  [{vs}]")
    print("Свод: site/data/bench_results.json")


if __name__ == "__main__":
    main()
