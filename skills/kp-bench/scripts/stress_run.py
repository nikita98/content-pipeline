"""Нормализация текста и ударения для теста stress: rutextnorm + silero-stress или RUAccent.

Пример:
  python skills/kp-bench/scripts/stress_run.py --variant rutextnorm-silero --out bench/runs/stress/nikita
  python skills/kp-bench/scripts/stress_run.py --variant rutextnorm-ruaccent --out bench/runs/stress/nikita
По умолчанию берёт assets/inputs/stress_ru.txt. Пишет <variant>.txt построчно: исходник → результат,
и печатает время. Ошибки (неверное ударение, омограф, число не тем падежом) считает человек.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import _common  # noqa: F401

HERE = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", required=True, choices=["rutextnorm-silero", "rutextnorm-ruaccent", "rutextnorm-only"])
    ap.add_argument("--input", type=Path, default=HERE / "assets" / "inputs" / "stress_ru.txt")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    from rutextnorm import normalize_russian  # type: ignore

    t0 = time.perf_counter()
    if a.variant == "rutextnorm-silero":
        from silero_stress import load_accentor  # type: ignore
        acc = load_accentor()
    elif a.variant == "rutextnorm-ruaccent":
        from ruaccent import RUAccent  # type: ignore
        r = RUAccent(); r.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
        acc = r.process_all
    else:
        acc = lambda s: s  # noqa: E731
    load_s = time.perf_counter() - t0

    lines = [l for l in a.input.read_text(encoding="utf-8").splitlines() if l.strip()]
    t1 = time.perf_counter()
    rows = [(l, acc(normalize_russian(l))) for l in lines]
    run_s = round(time.perf_counter() - t1, 2)
    a.out.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"{i}. {src}\n   → {res}" for i, (src, res) in enumerate(rows, 1))
    (a.out / f"{a.variant}.txt").write_text(body + "\n", encoding="utf-8")
    print(body)
    print(f"\nЗагрузка моделей {load_s:.1f} с, обработка {run_s} с. Файл: {a.out / (a.variant + '.txt')}")
    print("Посчитайте строки с ошибкой (ударение, омограф, падеж числа) и запишите --metric errors=N.")


if __name__ == "__main__":
    main()
