"""Модуль «Установка»: компоненты из app/setup/components.json — что стоит, что можно доставить.

Доставка — тот же исполнитель, что у установщика: app/setup/components.py --headless --components <id>.
"""
from __future__ import annotations

from core import bundled
from core.jobs import Cmd
from core.paths import APP_DIR
from setup import components

SCRIPT = APP_DIR / "setup" / "components.py"


def state(req):
    return 200, components.status_all()


def build_install(params, app):
    ids = params.get("components")
    if isinstance(ids, str):
        ids = [ids]
    if not isinstance(ids, list) or not ids or len(ids) > 20:
        raise ValueError("components — список id")
    cat = {c["id"]: c for c in components.load_catalog()}
    bad = [i for i in ids if not isinstance(i, str) or i not in cat]
    if bad:
        raise ValueError(f"Неизвестный компонент: {bad[0]!r}")
    nv = components.has_nvidia()
    for i in ids:
        if cat[i].get("nvidia") and not nv:
            raise ValueError(f"«{cat[i]['name']}»: нужна видеокарта NVIDIA, nvidia-smi не найден.")
    names = ", ".join(cat[i]["name"] for i in ids)
    return [Cmd([bundled.console_python(), str(SCRIPT), "--headless", "--components", ",".join(ids)])], f"Установка: {names}"


def register(app) -> None:
    app.section("setup", "Установка", js="modules/setup.js", order=850, hint="Компоненты: распознавание, озвучка, проверка текстов")
    app.action("setup.install", "Установка компонентов", build_install, heavy=True,
               describe="python app/setup/components.py --headless --components <id,...>")
    app.route("GET", "/api/setup/components", state)
