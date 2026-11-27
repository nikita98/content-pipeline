"""Фоновые задачи: последовательность шагов (команда или функция Python), лог в файл, остановка.

Шаг Cmd — argv-список, запускается без оболочки (shell=False). Шаг Py — функция ядра или модуля,
получает задачу и пишет в её лог. Одна тяжёлая задача за раз: вторую тяжёлую ядро отклоняет.
"""
from __future__ import annotations

import collections
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from .paths import IS_WIN, LOG_DIR, ROOT, rel


@dataclass
class Cmd:
    argv: list
    label: str = ""
    cwd: Path | None = None
    tee: Path | None = None          # копия вывода шага в файл + <stem>.meta.json со временем и кодом
    ok_codes: tuple = (0,)
    env: dict | None = None


@dataclass
class Py:
    fn: Callable                      # fn(job) -> int (0 — успех)
    label: str = ""


class JobBusy(Exception):
    pass


def child_env(extra: dict | None = None) -> dict:
    env = dict(os.environ)
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "KP_BENCH_ROOT": str(ROOT)})
    if extra:
        env.update(extra)
    return env


def show_argv(argv: list) -> str:
    out = []
    for a in argv:
        s = rel(Path(a)) if isinstance(a, Path) else str(a)
        out.append(f'"{s}"' if (" " in s or not s) else s)
    return " ".join(out)


@dataclass
class Job:
    id: str
    action: str
    label: str
    heavy: bool
    steps: list
    log_path: Path
    state: str = "queued"            # queued, running, done, failed, stopped
    code: int | None = None
    started: float = 0.0
    ended: float = 0.0
    error: str = ""
    result: dict = field(default_factory=dict)
    on_done: Callable | None = None
    _tail: collections.deque = field(default_factory=lambda: collections.deque(maxlen=400))
    _proc: subprocess.Popen | None = None
    _stop: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def log(self, line: str) -> None:
        line = line.rstrip("\r\n")
        with self._lock:
            self._tail.append(line)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def public(self, tail: int = 200) -> dict:
        with self._lock:
            lines = list(self._tail)[-tail:]
        return {"id": self.id, "action": self.action, "label": self.label, "state": self.state,
                "code": self.code, "error": self.error, "heavy": self.heavy,
                "started": self.started, "ended": self.ended,
                "seconds": round((self.ended or time.time()) - self.started, 1) if self.started else 0,
                "log": rel(self.log_path), "tail": lines, "result": self.result}

    # --- выполнение ---
    def run(self) -> None:
        self.state, self.started = "running", time.time()
        code = 0
        try:
            for i, st in enumerate(self.steps, 1):
                if self._stop:
                    break
                name = st.label or (show_argv(st.argv) if isinstance(st, Cmd) else getattr(st.fn, "__name__", "шаг"))
                self.log(f"── шаг {i}/{len(self.steps)}: {name}")
                code = self._run_cmd(st) if isinstance(st, Cmd) else self._run_py(st)
                if code != 0:
                    break
        except Exception as e:  # noqa: BLE001
            code, self.error = 1, str(e)
            self.log(f"Ошибка интерфейса: {e}")
        self.code = code
        self.state = "stopped" if self._stop else ("done" if code == 0 else "failed")
        self.ended = time.time()
        self.log(f"── итог: {'готово' if self.state == 'done' else ('остановлено' if self._stop else 'ошибка, код ' + str(code))}"
                 f", {self.ended - self.started:.1f} с")
        if self.on_done:
            try:
                self.on_done(self)
            except Exception as e:  # noqa: BLE001
                self.log(f"Ошибка после задачи: {e}")

    def _run_py(self, st: Py) -> int:
        try:
            return int(st.fn(self) or 0)
        except SystemExit as e:  # скрипты стенда завершаются через sys.exit("текст")
            self.log(f"Ошибка: {e}")
            self.error = str(e)
            return 1
        except Exception as e:  # noqa: BLE001
            self.log(f"Ошибка: {e}")
            self.error = str(e)
            return 1

    def _run_cmd(self, st: Cmd) -> int:
        argv = [str(a) for a in st.argv]
        self.log("$ " + show_argv(st.argv))
        kw: dict = {}
        if IS_WIN:
            kw["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            kw["start_new_session"] = True
        t0 = time.perf_counter()
        tee = None
        if st.tee:
            st.tee.parent.mkdir(parents=True, exist_ok=True)
            tee = st.tee.open("w", encoding="utf-8")
        try:
            try:
                p = subprocess.Popen(argv, cwd=str(st.cwd or ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, env=child_env(st.env), shell=False, **kw)
            except FileNotFoundError:
                self.log(f"Программа не найдена: {argv[0]}. Установите её (раздел «Подготовка» или «Настройки») и нажмите «Проверить снова».")
                self.error = f"не найдена программа {Path(argv[0]).name}"
                return 127
            except OSError as e:
                self.log(f"Не удалось запустить {argv[0]}: {e}")
                self.error = str(e)
                return 126
            self._proc = p
            assert p.stdout is not None
            for raw in iter(p.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace")
                self.log(line)
                if tee:
                    tee.write(line.rstrip("\r\n") + "\n")
            p.wait()
            code = p.returncode
        finally:
            self._proc = None
            if tee:
                tee.close()
        run_s = round(time.perf_counter() - t0, 1)
        if st.tee:
            meta = {"run_s": run_s, "code": code, "date": datetime.now().isoformat(timespec="seconds")}
            st.tee.with_name(st.tee.stem + ".meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        if code in st.ok_codes:
            if code != 0:
                self.log(f"(код {code} для этой программы — нормальный результат)")
            return 0
        if not self.error:
            self.error = f"{Path(argv[0]).name}: код выхода {code}"
        return code or 1

    def stop(self) -> None:
        self._stop = True
        p = self._proc
        if not p or p.poll() is not None:
            return
        self.log("── остановка по кнопке «Остановить»")
        try:
            if IS_WIN:
                # дерево процессов (npx, агенты запускают дочерние)
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True, timeout=20)
            else:
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
        except Exception:  # noqa: BLE001
            p.kill()


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()

    def running_heavy(self) -> Job | None:
        return next((j for j in self.jobs.values() if j.heavy and j.state in ("queued", "running")), None)

    def start(self, action: str, label: str, steps: list, heavy: bool, on_done=None) -> Job:
        with self.lock:
            busy = self.running_heavy()
            if heavy and busy:
                raise JobBusy(f"Уже идёт задача «{busy.label}». Дождитесь окончания или нажмите «Остановить».")
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            jid = uuid.uuid4().hex[:12]
            safe_action = "".join(c if c.isalnum() or c in "-_." else "_" for c in action)
            log_path = LOG_DIR / f"{stamp}_{safe_action}.txt"
            n = 2
            while log_path.exists():
                log_path = LOG_DIR / f"{stamp}_{safe_action}-{n}.txt"; n += 1
            job = Job(id=jid, action=action, label=label, heavy=heavy, steps=steps, log_path=log_path, on_done=on_done)
            job.log(f"Задача: {label}  [{action}]  {datetime.now().isoformat(timespec='seconds')}  Python {sys.version.split()[0]}")
            self.jobs[jid] = job
        threading.Thread(target=job.run, daemon=True, name=f"job-{jid}").start()
        return job

    def get(self, jid: str) -> Job | None:
        return self.jobs.get(jid)

    def stop_all(self) -> None:
        for j in self.jobs.values():
            if j.state == "running":
                j.stop()
