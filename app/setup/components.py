"""Установка компонентов: пакеты Python в окружения data/venv (или .venv-* в копии из git).

Список — app/setup/components.json. Окно (tkinter из встроенного Python) показывает общий прогресс, текущий
пункт, прогресс скачивания pip, лог под «Подробнее», кнопку «Отмена» и итог по пунктам.

  pythonw app/setup/components.py --components text,stress     # окно (так запускает установщик)
  python  app/setup/components.py --headless --components text  # без окна: строки в консоль (CI, интерфейс)
  python  app/setup/components.py --headless --dry-run --components all --catalog fake.json   # только план
  pythonw app/setup/components.py --dry-run --close-when-done --components all                # окно без установки (CI)

Итог последнего запуска — data/setup/last.json. Код выхода в --headless: 0 — всё установлено или уже было,
1 — была ошибка или отмена, 2 — неверные аргументы.
Если tkinter недоступен, окно заменяет раздел «Установка» в браузере: выбранные пункты пишутся в
data/setup/pending.json, интерфейс открывается на #setup.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core import bundled, tools  # noqa: E402
from core.paths import DATA, IS_WIN, ROOT  # noqa: E402

CATALOG = Path(__file__).with_name("components.json")
STATE_DIR = DATA / "setup"
LAST = STATE_DIR / "last.json"
PENDING = STATE_DIR / "pending.json"
OPENED = STATE_DIR / "opened.flag"
LOG = DATA / "logs" / "components.log"

STATUS = {"ok": "установлено", "already": "уже было", "error": "ошибка", "cancelled": "отменено",
          "skipped": "пропущено", "planned": "будет установлено"}
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if IS_WIN else 0


# --- каталог и проверка ---------------------------------------------------------------------------

def load_catalog(path: Path | None = None) -> list[dict]:
    data = json.loads((path or CATALOG).read_text(encoding="utf-8"))
    comps = data["components"] if isinstance(data, dict) else data
    for c in comps:
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", c.get("id", "")):
            raise ValueError(f"components.json: неверный id {c.get('id')!r}")
    return comps


def has_nvidia() -> bool:
    if shutil.which("nvidia-smi"):
        return True
    if IS_WIN:
        sysroot = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        for p in (sysroot / "System32" / "nvidia-smi.exe",
                  Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "NVIDIA Corporation" / "NVSMI" / "nvidia-smi.exe"):
            if p.is_file():
                return True
    return False


def is_installed(c: dict) -> bool:
    if not c.get("steps"):
        return True
    venv = c.get("venv")
    if not venv or not tools.venv_exists(venv):
        return False
    return all(tools.installed(venv, d) for d in c.get("check", []))


def size_text(c: dict) -> str:
    mb = c.get("size_mb") or 0
    if not mb:
        return ""
    return f"≈ {mb / 1024:.1f} ГБ".replace(".", ",") if mb >= 1024 else f"≈ {round(mb)} МБ"


def status_all(catalog: list[dict] | None = None) -> dict:
    """Для раздела «Установка» в интерфейсе."""
    cat = catalog or load_catalog()
    nv = has_nvidia()
    items = []
    for c in cat:
        items.append({"id": c["id"], "name": c["name"], "description": c.get("description", ""), "size": size_text(c),
                      "fixed": bool(c.get("fixed")), "default": bool(c.get("default")), "venv": c.get("venv"),
                      "venv_label": tools.venv_label(c["venv"]) if c.get("venv") else "",
                      "installed": is_installed(c), "available": nv or not c.get("nvidia"),
                      "reason": "" if nv or not c.get("nvidia") else "нужна видеокарта NVIDIA (nvidia-smi не найден)"})
    return {"components": items, "nvidia": nv, "last": _read(LAST), "pending": (_read(PENDING) or {}).get("ids", [])}


def _read(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# --- план ----------------------------------------------------------------------------------------

@dataclass
class Step:
    argv: list
    say: str
    pip: bool = False


def plan(c: dict) -> list[Step]:
    steps: list[Step] = []
    venv = c.get("venv")
    if not c.get("steps"):
        return steps
    if not venv:
        raise ValueError(f"{c['id']}: не указано окружение venv")
    if not tools.venv_exists(venv):
        steps.append(Step([*tools.base_python(), "-m", "venv", str(tools.venv_dir(venv))], "Создаю окружение Python"))
    vpy = str(tools.venv_python(venv))
    for s in c["steps"]:
        say = s.get("say") or c["name"]
        if "pip" in s:
            argv = [vpy, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", *s["pip"]]
            if s.get("index_url"):
                argv += ["--index-url", s["index_url"]]
            steps.append(Step(argv, say, pip=True))
        elif "git_clone" in s:
            dest = ROOT / s["dest"]
            if (dest / ".git").exists():
                continue
            if dest.exists() and any(dest.iterdir()):
                raise ValueError(f"Папка {s['dest']} уже есть и не пустая — удалите её и повторите.")
            git = tools.exe("git") or "git"
            steps.append(Step([git, "clone", "--progress", "--depth", "1", s["git_clone"], str(dest)], say))
        else:
            raise ValueError(f"{c['id']}: неизвестный шаг {s}")
    return steps


# --- выполнение ----------------------------------------------------------------------------------

PROGRESS_RE = re.compile(r"^Progress (\d+) of (\d+)")
DOWNLOAD_RE = re.compile(r"Downloading (\S+?)(?:-\d[^ ]*)? \(([\d.,]+ [kMG]?B)\)")
GIT_RE = re.compile(r"(Receiving objects|Resolving deltas):\s+(\d+)%")


def child_env() -> dict:
    env = dict(os.environ)
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PIP_NO_INPUT": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"})
    return env


@dataclass
class Runner:
    ids: list
    catalog: list
    emit: object                               # emit(dict) — событие для окна или консоли
    dry_run: bool = False
    dry_delay: float = 0.0                     # пауза на шаг в --dry-run с окном: чтобы было видно полосы
    results: list = field(default_factory=list)
    _cancel: bool = False
    _proc: subprocess.Popen | None = None
    _raw: bool | None = None                   # поддерживает ли pip --progress-bar raw

    def cancel(self) -> None:
        self._cancel = True
        p = self._proc
        if p and p.poll() is None:
            try:
                p.kill()
            except OSError:
                pass

    def log(self, text: str) -> None:
        self.emit({"t": "log", "text": text})

    def run(self) -> list:
        known = {c["id"]: c for c in self.catalog}
        todo = [known[i] for i in self.ids if i in known]
        n = len(todo)
        nv = has_nvidia()
        for k, c in enumerate(todo, 1):
            self.emit({"t": "start", "i": k, "n": n, "id": c["id"], "name": c["name"], "size": size_text(c)})
            status, err = self._one(c, nv)
            self.results.append({"id": c["id"], "name": c["name"], "status": status, "error": err})
            self.emit({"t": "end", "i": k, "n": n, "id": c["id"], "name": c["name"], "status": status, "error": err})
        if not self.dry_run:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            LAST.write_text(json.dumps({"date": datetime.now().isoformat(timespec="seconds"), "results": self.results},
                                       ensure_ascii=False, indent=1), encoding="utf-8")
            if not any(r["status"] in ("error", "cancelled") for r in self.results):
                try:
                    PENDING.unlink()
                except OSError:
                    pass
        self.emit({"t": "done", "results": self.results})
        return self.results

    def _one(self, c: dict, nv: bool) -> tuple[str, str]:
        if self._cancel:
            return "cancelled", ""
        if c.get("nvidia") and not nv:
            return "skipped", "нет видеокарты NVIDIA"
        if is_installed(c):
            return "already", ""
        try:
            steps = plan(c)
        except ValueError as e:
            return "error", str(e)
        for st in steps:
            if self._cancel:
                return "cancelled", ""
            self.emit({"t": "say", "text": f"{st.say}{', ' + size_text(c) if size_text(c) and st.pip else ''}"})
            self.emit({"t": "frac", "value": None})
            self.log("$ " + " ".join(f'"{a}"' if " " in str(a) else str(a) for a in st.argv))
            if self.dry_run:
                time.sleep(self.dry_delay)
                continue
            code, tail = self._exec(st)
            if self._cancel:
                return "cancelled", ""
            if code != 0:
                return "error", _explain(tail, code)
        if self.dry_run:
            return "planned", ""
        return ("ok", "") if is_installed(c) else ("error", "после установки пакет не найден в окружении")

    def _exec(self, st: Step) -> tuple[int, list]:
        argv = [str(a) for a in st.argv]
        if st.pip and self._raw is not False:
            argv = argv[:4] + ["--progress-bar", "raw"] + argv[4:]
        code, tail = self._popen(argv)
        if st.pip and self._raw is None:
            if code == 2 and any("raw" in ln and ("invalid choice" in ln or "progress" in ln.lower()) for ln in tail):
                self._raw = False
                self.log("(pip без --progress-bar raw — прогресс скачивания не показывается)")
                return self._popen([str(a) for a in st.argv])
            self._raw = True if code == 0 else None
        return code, tail

    def _popen(self, argv: list) -> tuple[int, list]:
        tail: list = []
        try:
            p = subprocess.Popen(argv, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, env=child_env(), creationflags=NO_WINDOW)
        except OSError as e:
            self.log(f"Не удалось запустить {argv[0]}: {e}")
            return 127, [str(e)]
        self._proc = p
        buf = b""
        assert p.stdout is not None
        while True:
            chunk = p.stdout.read1(65536) if hasattr(p.stdout, "read1") else p.stdout.readline()
            if not chunk:
                break
            buf += chunk
            parts = re.split(rb"[\r\n]", buf)
            buf = parts.pop()
            for raw in parts:
                self._line(raw.decode("utf-8", "replace").rstrip(), tail)
        if buf:
            self._line(buf.decode("utf-8", "replace").rstrip(), tail)
        p.wait()
        self._proc = None
        return p.returncode, tail

    def _line(self, line: str, tail: list) -> None:
        if not line.strip():
            return
        m = PROGRESS_RE.match(line)
        if m:
            done, total = int(m.group(1)), int(m.group(2))
            self.emit({"t": "frac", "value": done / total if total else None})
            return
        m = GIT_RE.search(line)
        if m:
            self.emit({"t": "frac", "value": int(m.group(2)) / 100})
            if not line.endswith("done."):
                return
        m = DOWNLOAD_RE.search(line)
        if m:
            self.emit({"t": "sub", "text": f"Скачиваю {m.group(1).rsplit('/', 1)[-1]} ({m.group(2)})"})
        elif line.startswith("Installing collected packages"):
            self.emit({"t": "sub", "text": "Устанавливаю скачанные пакеты…"})
            self.emit({"t": "frac", "value": None})
        tail.append(line)
        del tail[:-40]
        self.log(line)


def _explain(tail: list, code: int) -> str:
    text = "\n".join(tail[-40:])
    if re.search(r"(?i)(connection|timed out|name resolution|getaddrinfo|ssl|proxy)", text):
        return "нет связи с интернетом или сайт недоступен — проверьте интернет и повторите"
    if re.search(r"(?i)no space left|not enough space|errno 28", text):
        return "не хватает места на диске"
    if re.search(r"(?i)could not find a version|no matching distribution", text):
        return "пакет для этой версии Python или Windows не найден"
    last = next((ln for ln in reversed(tail) if ln.strip().startswith(("ERROR", "error", "fatal"))), "")
    return (last[:200] or f"код выхода {code}")


# --- режим без окна ------------------------------------------------------------------------------

def headless(ids: list, catalog: list, dry_run: bool) -> int:
    if not dry_run:
        LOG.parent.mkdir(parents=True, exist_ok=True)
    logf = None if dry_run else open(LOG, "a", encoding="utf-8")  # noqa: SIM115
    last_pct = {"v": -1}

    def emit(ev: dict) -> None:
        t = ev["t"]
        line = None
        if t == "start":
            line = f"[{ev['i']}/{ev['n']}] {ev['name']} {ev['size']}".rstrip()
            last_pct["v"] = -1
        elif t == "say":
            line = "  " + ev["text"]
        elif t == "sub":
            line = "    " + ev["text"]
        elif t == "frac" and ev["value"] is not None:
            pct = int(ev["value"] * 100) // 10 * 10
            if pct != last_pct["v"]:
                last_pct["v"] = pct
                line = f"    {pct}%"
        elif t == "log":
            line = "    | " + ev["text"]
        elif t == "end":
            line = f"  → {STATUS[ev['status']]}" + (f": {ev['error']}" if ev["error"] else "")
        elif t == "done":
            line = "Итог: " + "; ".join(f"{r['name']} — {STATUS[r['status']]}" for r in ev["results"])
        if line is not None:
            print(line, flush=True)
            if logf:
                logf.write(line + "\n")
                logf.flush()

    if logf:
        logf.write(f"\n=== {datetime.now().isoformat(timespec='seconds')} {' '.join(ids)}\n")
    r = Runner(ids, catalog, emit, dry_run=dry_run)
    res = r.run()
    if logf:
        logf.close()
    return 1 if any(x["status"] in ("error", "cancelled") for x in res) else 0


# --- окно ----------------------------------------------------------------------------------------

def open_interface(section: str = "") -> None:
    """Запуск интерфейса без консоли. Повторный запуск сервер обрабатывает сам: откроет браузер на работающий."""
    py = bundled.bundled_python(windowless=True) or Path(sys.executable)
    argv = [str(py), str(APP_DIR / "server.py")] + (["--section", section] if section else [])
    flags = (getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)) if IS_WIN else 0
    subprocess.Popen(argv, cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=flags, close_fds=True, start_new_session=not IS_WIN)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        OPENED.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")
    except OSError:
        pass


def gui(ids: list, catalog: list, dry_run: bool = False, close_when_done: float = 0) -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext, ttk
        root = tk.Tk()
    except Exception:  # noqa: BLE001 — нет tkinter или нет экрана: раздел «Установка» в браузере
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        PENDING.write_text(json.dumps({"ids": ids}, ensure_ascii=False), encoding="utf-8")
        open_interface("setup")
        return 0

    root.title("Конвейер контента — установка компонентов")
    root.geometry("680x460")
    root.minsize(560, 380)
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except tk.TclError:
        pass
    ico = APP_DIR / "setup" / "icon.ico"
    if IS_WIN and ico.is_file():
        try:
            root.iconbitmap(str(ico))
        except tk.TclError:
            pass
    base_font = ("Segoe UI", 10) if IS_WIN else None
    big = ("Segoe UI", 14, "bold") if IS_WIN else ("TkDefaultFont", 14, "bold")

    q: queue.Queue = queue.Queue()
    runner = Runner(ids, catalog, q.put, dry_run=dry_run, dry_delay=1.0 if dry_run else 0.0)
    n = max(1, len([i for i in ids if i in {c["id"] for c in catalog}]))

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill="both", expand=True)
    ttk.Label(frm, text="Установка компонентов", font=big).pack(anchor="w")
    ttk.Label(frm, text="Нужен интернет. Ничего нажимать не надо: всё скачается и поставится само.",
              font=base_font, wraplength=620).pack(anchor="w", pady=(2, 10))
    overall_lbl = ttk.Label(frm, text="Подготовка…", font=base_font)
    overall_lbl.pack(anchor="w")
    overall = ttk.Progressbar(frm, maximum=n * 100, mode="determinate")
    overall.pack(fill="x", pady=(2, 10))
    cur_lbl = ttk.Label(frm, text="", font=base_font, wraplength=620)
    cur_lbl.pack(anchor="w")
    sub_lbl = ttk.Label(frm, text="", font=base_font, foreground="#5b6763", wraplength=620)
    sub_lbl.pack(anchor="w")
    cur = ttk.Progressbar(frm, maximum=100, mode="indeterminate")
    cur.pack(fill="x", pady=(2, 8))

    results_box = ttk.Frame(frm)
    results_box.pack(fill="x")

    det_btn = ttk.Button(frm, text="Подробнее ▸")
    det_btn.pack(anchor="w", pady=(6, 0))
    log = scrolledtext.ScrolledText(frm, height=8, wrap="word", state="disabled", font=("Consolas", 9) if IS_WIN else None)

    def toggle():
        if log.winfo_ismapped():
            log.pack_forget()
            det_btn.config(text="Подробнее ▸")
        else:
            log.pack(fill="both", expand=True, pady=(4, 0), before=btns)
            det_btn.config(text="Скрыть подробности ▾")
    det_btn.config(command=toggle)

    btns = ttk.Frame(frm)
    btns.pack(side="bottom", fill="x", pady=(10, 0))
    cancel_btn = ttk.Button(btns, text="Отмена")
    cancel_btn.pack(side="right")
    state = {"running": True, "index": 0, "indet": False}

    def set_indet(on: bool) -> None:
        if on and not state["indet"]:
            cur.config(mode="indeterminate")
            cur.start(12)
        elif not on and state["indet"]:
            cur.stop()
            cur.config(mode="determinate")
        state["indet"] = on

    def do_cancel():
        if state["running"] and messagebox.askyesno("Отменить установку?",
                                                    "Остановить установку компонентов? Уже поставленное останется. "
                                                    "Доставить остальное можно позже в интерфейсе: раздел «Установка».",
                                                    parent=root):
            cancel_btn.config(state="disabled", text="Останавливаю…")
            runner.cancel()
    cancel_btn.config(command=do_cancel)
    root.protocol("WM_DELETE_WINDOW", lambda: do_cancel() if state["running"] else root.destroy())

    def log_line(text: str) -> None:
        log.config(state="normal")
        log.insert("end", text + "\n")
        if int(log.index("end-1c").split(".")[0]) > 3000:
            log.delete("1.0", "500.0")
        log.see("end")
        log.config(state="disabled")

    def finish(results: list) -> None:
        state["running"] = False
        set_indet(False)
        cur["value"] = 100
        overall["value"] = n * 100
        bad = [r for r in results if r["status"] in ("error", "cancelled")]
        overall_lbl.config(text="Готово" if not bad else "Готово, но не всё установилось")
        cur_lbl.config(text="")
        sub_lbl.config(text="")
        icon = {"ok": "✓", "already": "✓", "error": "✗", "cancelled": "–", "skipped": "–"}
        for r in results:
            t = f"{icon.get(r['status'], '•')}  {r['name']} — {STATUS[r['status']]}" + (f": {r['error']}" if r["error"] else "")
            kw = {"foreground": "#b3261e"} if r["status"] == "error" else {}
            ttk.Label(results_box, text=t, font=base_font, wraplength=620, **kw).pack(anchor="w")
        if bad:
            ttk.Label(results_box, text="Повторить можно позже: интерфейс → «Установка». Подробности — «Подробнее».",
                      font=base_font, wraplength=620).pack(anchor="w", pady=(6, 0))
        cancel_btn.destroy()
        ttk.Button(btns, text="Закрыть", command=root.destroy).pack(side="right", padx=(8, 0))

        def go():
            open_interface()
            root.destroy()
        ob = ttk.Button(btns, text="Открыть интерфейс", command=go)
        ob.pack(side="right")
        ob.focus_set()
        if close_when_done:
            root.after(int(close_when_done * 1000), root.destroy)

    def poll():
        try:
            while True:
                ev = q.get_nowait()
                t = ev["t"]
                if t == "start":
                    state["index"] = ev["i"] - 1
                    overall["value"] = state["index"] * 100
                    overall_lbl.config(text=f"Компонент {ev['i']} из {ev['n']}: {ev['name']}")
                    cur_lbl.config(text="Проверяю…")
                    sub_lbl.config(text="")
                    log_line(f"── {ev['name']}")
                elif t == "say":
                    cur_lbl.config(text=ev["text"])
                    sub_lbl.config(text="")
                elif t == "sub":
                    sub_lbl.config(text=ev["text"])
                elif t == "frac":
                    if ev["value"] is None:
                        set_indet(True)
                    else:
                        set_indet(False)
                        cur["value"] = ev["value"] * 100
                elif t == "log":
                    log_line(ev["text"])
                elif t == "end":
                    overall["value"] = ev["i"] * 100
                    log_line(f"── {ev['name']}: {STATUS[ev['status']]}" + (f" ({ev['error']})" if ev["error"] else ""))
                elif t == "done":
                    finish(ev["results"])
        except queue.Empty:
            pass
        root.after(100, poll)

    # окно запускается из мастера установки — поднять его поверх мастера, потом вернуть обычный режим
    root.lift()
    root.attributes("-topmost", True)
    root.after(800, lambda: root.attributes("-topmost", False))
    root.focus_force()
    threading.Thread(target=runner.run, daemon=True, name="components").start()
    root.after(100, poll)
    root.mainloop()
    return 0


# --- CLI -----------------------------------------------------------------------------------------

def main(argv: list | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        if s is not None and hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--components", default="", help="id через запятую; all — все; пусто — выбранные по умолчанию")
    ap.add_argument("--headless", action="store_true", help="без окна, строки в консоль")
    ap.add_argument("--dry-run", action="store_true", help="только показать план, ничего не ставить")
    ap.add_argument("--catalog", type=Path, help="другой components.json (для проверки)")
    ap.add_argument("--list", action="store_true", help="показать компоненты и их состояние")
    ap.add_argument("--close-when-done", type=float, default=0, metavar="СЕК",
                    help="окно: закрыть через столько секунд после итога (для CI)")
    a = ap.parse_args(argv)
    bundled.apply_env()
    try:
        catalog = load_catalog(a.catalog)
    except (OSError, ValueError, KeyError) as e:
        print(f"Не прочитан список компонентов: {e}", file=sys.stderr)
        return 2
    known = [c["id"] for c in catalog]
    if a.list:
        st = status_all(catalog)
        for c in st["components"]:
            mark = "есть" if c["installed"] else ("недоступно" if not c["available"] else "нет")
            print(f"{c['id']:10} {mark:11} {c['size']:10} {c['name']}")
        return 0
    raw = a.components.strip()
    if raw == "all":
        ids = known
    elif raw:
        ids = [x.strip() for x in raw.replace(";", ",").split(",") if x.strip()]
        bad = [x for x in ids if x not in known]
        if bad:
            print(f"Неизвестные компоненты: {', '.join(bad)}. Есть: {', '.join(known)}", file=sys.stderr)
            return 2
    else:
        ids = [c["id"] for c in catalog if c.get("default")]
    ids = [i for i in ids if i != "base"] or ids     # «Основу» ставит сам установщик
    if a.headless:
        return headless(ids, catalog, a.dry_run)
    return gui(ids, catalog, a.dry_run, a.close_when_done)


if __name__ == "__main__":
    sys.exit(main())
