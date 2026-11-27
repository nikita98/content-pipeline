"""Синтез Qwen3-TTS с клоном голоса (тест tts-local). Только NVIDIA GPU. Код — по install.md, раздел 5.

Пример:
  python skills/kp-bench/scripts/tts_qwen.py --text-file skills/kp-bench/assets/inputs/script_ru.txt \
      --ref-audio bench/runs/tts-ref/nikita/ref.wav --ref-text-file bench/runs/tts-ref/nikita/gigaam.txt \
      --out bench/runs/tts/nikita/qwen3-tts.wav
  ... --stress --model siriusfreak/qwen3-tts-12hz-1.7b-ru-stress-cf --out bench/runs/tts/nikita/qwen3-tts-stress.wav

--stress: rutextnorm + RUAccent, «+» перед гласной переводится в знак U+0301 после неё.
Не запускался на GPU при написании — проверить.
"""
from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

import _common  # noqa: F401

BASE = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"


def stressed(text: str) -> str:
    from rutextnorm import normalize_russian  # type: ignore
    from ruaccent import RUAccent  # type: ignore
    r = RUAccent(); r.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
    out = r.process_all(normalize_russian(text))
    return re.sub(r"\+(\w)", "\\1\u0301", out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-file", required=True, type=Path)
    ap.add_argument("--ref-audio", required=True, type=Path)
    ap.add_argument("--ref-text-file", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--model", default=BASE)
    ap.add_argument("--stress", action="store_true")
    a = ap.parse_args()
    import soundfile as sf  # type: ignore
    import torch  # type: ignore
    from qwen_tts import Qwen3TTSModel  # type: ignore

    text = a.text_file.read_text(encoding="utf-8").strip()
    if a.stress:
        text = stressed(text)
    ref_text = a.ref_text_file.read_text(encoding="utf-8").strip()
    t0 = time.perf_counter()
    m = Qwen3TTSModel.from_pretrained(a.model, device_map="cuda:0", dtype=torch.bfloat16)
    wavs, sr = m.generate_voice_clone(text=text, language="Russian", ref_audio=str(a.ref_audio), ref_text=ref_text)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(a.out), wavs[0], sr)
    print(f"Готово: {a.out} за {time.perf_counter() - t0:.1f} с (с загрузкой модели)")


if __name__ == "__main__":
    main()
