"""Адаптеры ИИ-агентов для запуска в фоне (headless).

Длинная задача пишется в файл bench/runs/_agent/<время>_<имя>.md, агенту уходит короткий промпт
«Прочитай задачу в файле <путь от корня> и выполни её». Так промпт не ломается на Windows, где .cmd-обёртки
npm плохо переносят переводы строк и кавычки в аргументах.

Режимы:
  read  — агент читает файлы и отвечает текстом (оценка текста);
  write — агент меняет файлы и запускает команды (монтаж). Это даёт агенту право на команды в папке репозитория.

Синтаксис сверен 27.11.2026:
  Claude Code — https://code.claude.com/docs/en/headless : `claude -p "<промпт>"`, `--permission-mode acceptEdits`,
                `--allowedTools "Bash,Read,Edit"`; без режима `-p` идёт в Manual и отклоняет то, что требует одобрения.
  Codex      — https://learn.chatgpt.com/codex/non-interactive-mode : `codex exec "<промпт>"`, по умолчанию
                read-only песочница, `--sandbox workspace-write` для правок, `--skip-git-repo-check`; `--full-auto` удалён.
  OpenCode   — https://opencode.ai/docs/cli.md : подтверждён только `opencode run "<промпт>"`.
  Kimi Code  — https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html : `kimi -p "<промпт>"`,
                print-режим работает с правами auto по умолчанию, `--yolo` с ним не сочетается; рабочая папка — текущая.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from .jobs import Cmd, child_env
from .paths import IS_WIN, ROOT, RUNS, rel

AGENT_DIR = RUNS / "_agent"


def _claude(prompt: str, mode: str) -> list[str]:
    if mode == "write":
        return ["-p", prompt, "--permission-mode", "acceptEdits", "--allowedTools", "Bash,Read,Edit,Write"]
    return ["-p", prompt, "--allowedTools", "Read"]


def _codex(prompt: str, mode: str) -> list[str]:
    # проверить: в workspace-write по умолчанию может быть закрыта сеть — npm install для монтажа тогда упадёт
    return ["exec", "--skip-git-repo-check", "--sandbox", "workspace-write" if mode == "write" else "read-only", prompt]


def _opencode(prompt: str, mode: str) -> list[str]:
    # проверить: флаги прав и автоподтверждения для opencode run в документации не нашли
    return ["run", prompt]


def _kimi(prompt: str, mode: str) -> list[str]:
    # по документации print-режим (-p) сам работает с правами auto; рабочая папка — cwd процесса
    return ["-p", prompt]


AGENTS = {
    "claude": {"name": "Claude Code", "exe": "claude", "argv": _claude,
               "docs": "https://code.claude.com/docs/en/headless", "checked": True},
    "codex": {"name": "Codex", "exe": "codex", "argv": _codex,
              "docs": "https://learn.chatgpt.com/codex/non-interactive-mode", "checked": True},
    "opencode": {"name": "OpenCode", "exe": "opencode", "argv": _opencode,
                 "docs": "https://opencode.ai/docs/cli/", "checked": False},
    "kimi": {"name": "Kimi Code", "exe": "kimi", "argv": _kimi,
             "docs": "https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html", "checked": True},
}

_cache: dict = {"t": 0.0, "data": None}
_lock = threading.Lock()


def _extra_dirs() -> list[Path]:
    home = Path.home()
    dirs = [home / ".local" / "bin", home / ".opencode" / "bin", home / ".kimi" / "bin"]
    if IS_WIN:
        appdata = os.environ.get("APPDATA")
        if appdata:
            dirs.append(Path(appdata) / "npm")
        dirs.append(home / "AppData" / "Local" / "Programs")
    else:
        dirs += [Path("/opt/homebrew/bin"), Path("/usr/local/bin")]
    return dirs


def find_exe(exe: str) -> str | None:
    """shutil.which учитывает PATHEXT на Windows (.exe, .cmd); дополнительно — типичные папки установки."""
    found = shutil.which(exe)
    if found:
        return found
    for d in _extra_dirs():
        for ext in ([".exe", ".cmd", ".bat", ""] if IS_WIN else [""]):
            p = d / f"{exe}{ext}"
            if p.is_file():
                return str(p)
    return None


def detect(refresh: bool = False) -> list[dict]:
    with _lock:
        if _cache["data"] is not None and not refresh and time.time() - _cache["t"] < 60:
            return _cache["data"]
        out = []
        for aid, a in AGENTS.items():
            path = find_exe(a["exe"])
            ver = None
            if path:
                try:
                    r = subprocess.run([path, "--version"], capture_output=True, timeout=15, env=child_env(),
                                       stdin=subprocess.DEVNULL)
                    ver = (r.stdout or r.stderr).decode("utf-8", "replace").strip().splitlines()[0][:80] if (r.stdout or r.stderr) else ""
                except Exception as e:  # noqa: BLE001
                    ver = f"не отвечает: {e.__class__.__name__}"
            out.append({"id": aid, "name": a["name"], "found": bool(path), "path": path, "version": ver,
                        "docs": a["docs"], "checked": a["checked"]})
        _cache.update(t=time.time(), data=out)
        return out


def task_file(name: str, text: str) -> Path:
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    p = AGENT_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{name}.md"
    p.write_text(text, encoding="utf-8")
    return p


def short_prompt(task: Path) -> str:
    return f"Прочитай задачу в файле {rel(task)} (путь от текущей папки) и выполни её. Отвечай по-русски."


def command(agent_id: str, task: Path, mode: str, tee: Path | None = None) -> Cmd:
    """Шаг Cmd для запуска агента в корне репозитория. ValueError, если агент не выбран или не найден."""
    a = AGENTS.get(agent_id)
    if not a:
        raise ValueError("Агент не выбран. Откройте «Настройки» и выберите агента.")
    path = find_exe(a["exe"])
    if not path:
        raise ValueError(f"{a['name']} не найден на этом компьютере. Установите его или выберите другого агента в «Настройках».")
    return Cmd([path, *a["argv"](short_prompt(task), mode)], label=f"{a['name']} в фоне: {rel(task)}", cwd=ROOT, tee=tee)
