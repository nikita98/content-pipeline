"""Git и экспорт архивом: общие функции для модулей.

Проверка (git_info) — быстрые команды git только для чтения. Отправка — шаги задачи:
add → commit → pull --rebase → push; при сбое pull выполняется rebase --abort, чтобы не оставить репозиторий
посреди перебазирования. Архив — zip в bench/runs/export/.
"""
from __future__ import annotations

import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from .agents import find_exe
from .jobs import Cmd, Py, child_env
from .paths import ROOT, RUNS, rel

EXPORT_DIR = RUNS / "export"


def _git(args: list[str], timeout: int = 20) -> tuple[int, str]:
    g = find_exe("git")
    if not g:
        return 127, "git не найден"
    try:
        r = subprocess.run([g, *args], cwd=str(ROOT), capture_output=True, timeout=timeout, env=child_env(),
                           stdin=subprocess.DEVNULL)
        return r.returncode, (r.stdout or r.stderr).decode("utf-8", "replace").rstrip()
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def git_info(paths: list[str]) -> dict:
    """Можно ли отправить в git и какие файлы изменены в paths."""
    info = {"git": bool(find_exe("git")), "repo": False, "remote": "", "user": "", "branch": "", "files": [], "problems": []}
    if not info["git"]:
        info["problems"].append("git не установлен.")
        return info
    code, _ = _git(["rev-parse", "--is-inside-work-tree"])
    info["repo"] = code == 0
    if not info["repo"]:
        info["problems"].append("Папка не является репозиторием git (скачана архивом?).")
        return info
    _, info["branch"] = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    code, remote = _git(["remote", "get-url", "origin"])
    info["remote"] = remote if code == 0 else ""
    if code != 0:
        info["problems"].append("Нет удалённого репозитория origin.")
    _, name = _git(["config", "user.name"])
    _, email = _git(["config", "user.email"])
    info["user"] = f"{name} <{email}>" if name and email else ""
    if not info["user"]:
        info["problems"].append("Не заданы имя и почта для коммитов (git config user.name / user.email).")
    code, st = _git(["-c", "core.quotepath=false", "status", "--porcelain", "--untracked-files=all", "--", *paths])
    if code == 0:
        info["files"] = [ln[3:].strip().strip('"').split(" -> ")[-1] for ln in st.splitlines() if ln.strip()]
    return info


def push_steps(paths: list[str], message: str) -> list:
    g = find_exe("git") or "git"
    state = {"pulled": False}

    def pull(job) -> int:
        code = job._run_cmd(Cmd([g, "pull", "--rebase"]))
        if code != 0:
            job.log("Не удалось подтянуть изменения (конфликт или нет доступа). Отменяю перебазирование.")
            job._run_cmd(Cmd([g, "rebase", "--abort"], ok_codes=(0, 1, 128)))
            job.error = "git pull --rebase не прошёл. Коммит остался у вас локально. Скачайте результаты архивом и отправьте владельцу."
            return code
        state["pulled"] = True
        return 0

    return [
        Cmd([g, "add", "--", *paths], label="git add"),
        Cmd([g, "commit", "-m", message, "--", *paths], label=f"git commit «{message}»"),
        Py(pull, label="git pull --rebase"),
        Cmd([g, "push"], label="git push"),
    ]


def make_zip(files: list[Path], name: str) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = EXPORT_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{name}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.is_file():
                z.write(f, rel(f))
    return out
