"""Локальные настройки (app/settings.local.json, в git не идёт): тестировщик, выбранный агент."""
from __future__ import annotations

import json
import threading

from .paths import SETTINGS_FILE, TESTER_RE

_lock = threading.Lock()
DEFAULTS = {"tester": "", "agent": ""}


def load() -> dict:
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    return {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}


def save(update: dict, agent_ids: set[str]) -> dict:
    with _lock:
        cur = load()
        if "tester" in update:
            t = update["tester"]
            if t and (not isinstance(t, str) or not TESTER_RE.match(t)):
                raise ValueError("Имя тестировщика: латиница в нижнем регистре, цифры и дефис, до 32 знаков.")
            cur["tester"] = t or ""
        if "agent" in update:
            a = update["agent"]
            if a and a not in agent_ids:
                raise ValueError("Неизвестный агент.")
            cur["agent"] = a or ""
        SETTINGS_FILE.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return cur
