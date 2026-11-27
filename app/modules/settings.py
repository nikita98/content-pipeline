"""Модуль «Настройки»: тестировщик, выбор ИИ-агента, внешние программы. API — в ядре (/api/settings, /api/agents, /api/tools)."""
from __future__ import annotations


def register(app) -> None:
    app.section("settings", "Настройки", js="modules/settings.js", order=900, hint="Тестировщик, агент, программы")
