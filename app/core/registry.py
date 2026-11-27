"""Реестр: разделы, действия белого списка и маршруты API, которые регистрируют модули app/modules/<id>.py.

Модуль экспортирует функцию register(app). В ней:
  app.section(id=..., title=..., js="modules/<id>.js", order=..., skill=...)  — раздел в навигации;
  app.action(id, label, build, heavy=False)  — действие: build(params, app) -> list[Cmd|Py];
  app.route("GET"|"POST", "/api/<id>/...", handler)  — handler(req) -> (код, объект JSON) или Response.
Клиент не передаёт команды: только id действия и параметры. build проверяет параметры и строит argv
сам; при ошибке бросает ValueError с понятным текстом (ответ 400).
"""
from __future__ import annotations

import importlib
import json
import pkgutil
from dataclasses import dataclass, field
from typing import Callable

from .paths import APP_DIR, ROOT


@dataclass
class Action:
    id: str
    label: str
    build: Callable
    heavy: bool = False
    describe: str = ""               # человеческое описание: что выполняет (для README и отчёта)
    on_done: Callable | None = None


@dataclass
class Section:
    id: str
    title: str
    js: str = ""
    order: int = 100
    skill: str = ""                  # если раздел закрывает шаг конвейера из steps.json
    hint: str = ""


@dataclass
class Registry:
    actions: dict = field(default_factory=dict)
    routes: dict = field(default_factory=dict)
    sections: dict = field(default_factory=dict)

    def action(self, id: str, label: str, build: Callable, heavy: bool = False, describe: str = "", on_done=None) -> None:
        if id in self.actions:
            raise RuntimeError(f"действие {id} уже зарегистрировано")
        self.actions[id] = Action(id, label, build, heavy, describe, on_done)

    def route(self, method: str, path: str, handler: Callable) -> None:
        self.routes[(method.upper(), path)] = handler

    def section(self, id: str, title: str, js: str = "", order: int = 100, skill: str = "", hint: str = "") -> None:
        self.sections[id] = Section(id, title, js, order, skill, hint)


def load_modules(app) -> list[str]:
    """Импортирует все app/modules/*.py и вызывает register(app)."""
    import modules  # type: ignore  # app/ в sys.path
    loaded = []
    for m in sorted(pkgutil.iter_modules([str(APP_DIR / "modules")]), key=lambda x: x.name):
        if m.name.startswith("_"):
            continue
        mod = importlib.import_module(f"modules.{m.name}")
        if hasattr(mod, "register"):
            mod.register(app)
            loaded.append(m.name)
    return loaded


def pipeline_steps() -> list[dict]:
    """Шаги конвейера из site/data/steps.json: для навигации «скоро»."""
    p = ROOT / "site" / "data" / "steps.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    items = data if isinstance(data, list) else data.get("steps", [])
    return [{"n": s.get("n", ""), "short": s.get("short", ""), "name": s.get("name", ""), "skill": s.get("skill", "")}
            for s in items]
