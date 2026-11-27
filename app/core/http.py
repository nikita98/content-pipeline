"""HTTP-сервер: статика, API ядра, маршруты модулей, токен и проверка Host.

Правила:
- слушаем только 127.0.0.1;
- Host — 127.0.0.1:<порт> или localhost:<порт>, иначе 403 (защита от DNS rebinding);
- каждый POST — заголовок X-Bench-Token с токеном этого запуска, иначе 403;
- файлы отдаются только из bench/runs/ с токеном в параметре t (для <audio>, <video>, ссылок «Скачать»);
- команды не принимаются: только id действия из реестра и параметры.
"""
from __future__ import annotations

import hmac
import json
import mimetypes
import re
import secrets
import shutil
import traceback
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from . import agents, settings, tools
from .jobs import JobBusy, JobManager
from .paths import IS_WIN, RUNS, WEB_DIR, PathError, check_tester, rel, safe_path
from .registry import Registry, pipeline_steps

MAX_JSON = 2 * 1024 * 1024
MAX_UPLOAD = 500 * 1024 * 1024


@dataclass
class Response:
    status: int
    body: bytes
    ctype: str = "application/json; charset=utf-8"
    headers: dict | None = None


class Request:
    def __init__(self, handler: "Handler", query: dict, body: dict | None):
        self.h = handler
        self.query = query
        self.body = body or {}
        self.app: App = handler.server.app  # type: ignore[attr-defined]

    def q(self, key: str, default: str = "") -> str:
        return self.query.get(key, [default])[0]

    @property
    def raw(self):
        return self.h


class App(Registry):
    def __init__(self) -> None:
        super().__init__()
        self.token = secrets.token_urlsafe(32)
        self.jobs = JobManager()
        self.port = 0
        self.modules: list[str] = []

    # удобные функции для модулей
    def settings(self) -> dict:
        return settings.load()


def jdump(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "kp-app"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # тише в консоли: только ошибки
        if args and str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            super().log_message(fmt, *args)

    # --- ответы ---
    def send(self, r: Response) -> None:
        self.send_response(r.status)
        self.send_header("Content-Type", r.ctype)
        self.send_header("Content-Length", str(len(r.body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (r.headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(r.body)

    def json(self, status: int, obj) -> None:
        self.send(Response(status, jdump(obj)))

    def err(self, status: int, msg: str) -> None:
        self.json(status, {"error": msg})

    # --- проверки ---
    @property
    def app(self) -> App:
        return self.server.app  # type: ignore[attr-defined]

    def host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").lower()
        return host in (f"127.0.0.1:{self.app.port}", f"localhost:{self.app.port}")

    def token_ok(self, value: str | None) -> bool:
        return bool(value) and hmac.compare_digest(value, self.app.token)

    def origin_ok(self) -> bool:
        o = self.headers.get("Origin")
        return not o or o in (f"http://127.0.0.1:{self.app.port}", f"http://localhost:{self.app.port}")

    def read_json(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_JSON:
            raise ValueError("слишком большой запрос")
        raw = self.rfile.read(n) if n else b"{}"
        data = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("ожидается объект JSON")
        return data

    # --- маршрутизация ---
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self.host_ok():
            return self.err(403, "Неверный Host")
        u = urlparse(self.path)
        q = parse_qs(u.query)
        path = u.path
        try:
            if path in ("/", "/index.html"):
                return self.index()
            if path.startswith("/web/"):
                return self.static(path[len("/web/"):])
            if path == "/api/file":
                return self.file(q)
            if path == "/api/meta":
                return self.json(200, self.meta())
            if path.startswith("/api/job/"):
                j = self.app.jobs.get(path.rsplit("/", 1)[-1])
                return self.json(200, j.public()) if j else self.err(404, "задача не найдена")
            if path == "/api/jobs":
                return self.json(200, {"jobs": [j.public(tail=0) for j in self.app.jobs.jobs.values()][-30:]})
            if path == "/api/agents":
                return self.json(200, {"agents": agents.detect(refresh=q.get("refresh", ["0"])[0] == "1"),
                                       "selected": settings.load().get("agent", "")})
            if path == "/api/tools":
                return self.json(200, {"tools": tools.detect_external(), "os": tools.OS_ID})
            if path == "/api/settings":
                return self.json(200, settings.load())
            h = self.app.routes.get(("GET", path))
            if h:
                return self.module_reply(h(Request(self, q, None)))
            return self.err(404, "нет такого адреса")
        except PathError as e:
            return self.err(403, f"Доступ запрещён: {e}")
        except ValueError as e:
            return self.err(400, str(e))
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self.err(500, f"Ошибка интерфейса: {e}")

    def do_POST(self):
        # тело могло остаться непрочитанным (отказ, ошибка загрузки) — соединение не переиспользуем
        self.close_connection = True
        if not self.host_ok() or not self.origin_ok():
            return self.err(403, "Неверный Host или Origin")
        if not self.token_ok(self.headers.get("X-Bench-Token")):
            return self.err(403, "Нет токена. Обновите страницу.")
        u = urlparse(self.path)
        q = parse_qs(u.query)
        path = u.path
        try:
            if path == "/api/upload":
                return self.upload(q)
            body = self.read_json()
            if path == "/api/run":
                return self.run_action(body)
            m = re.fullmatch(r"/api/job/([0-9a-f]{12})/stop", path)
            if m:
                j = self.app.jobs.get(m.group(1))
                if not j:
                    return self.err(404, "задача не найдена")
                j.stop()
                return self.json(200, {"ok": True})
            if path == "/api/settings":
                ids = set(agents.AGENTS)
                return self.json(200, settings.save(body, ids))
            h = self.app.routes.get(("POST", path))
            if h:
                return self.module_reply(h(Request(self, q, body)))
            return self.err(404, "нет такого адреса")
        except PathError as e:
            return self.err(403, f"Доступ запрещён: {e}")
        except (ValueError, json.JSONDecodeError) as e:
            return self.err(400, str(e))
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self.err(500, f"Ошибка интерфейса: {e}")

    def module_reply(self, res) -> None:
        if isinstance(res, Response):
            return self.send(res)
        status, obj = res
        return self.json(status, obj)

    # --- обработчики ядра ---
    def meta(self) -> dict:
        a = self.app
        secs = sorted(a.sections.values(), key=lambda s: s.order)
        return {
            "sections": [{"id": s.id, "title": s.title, "js": s.js, "skill": s.skill, "hint": s.hint} for s in secs],
            "steps": pipeline_steps(),
            "settings": settings.load(),
            "os": tools.OS_ID,
            "modules": a.modules,
        }

    def index(self) -> None:
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        html = html.replace("__KP_TOKEN__", self.app.token)
        self.send(Response(200, html.encode("utf-8"), "text/html; charset=utf-8",
                           {"Content-Security-Policy": "default-src 'self'; img-src 'self' data:; media-src 'self'; "
                                                       "style-src 'self'; script-src 'self'; connect-src 'self'; "
                                                       "frame-ancestors 'none'"}))

    def static(self, sub: str) -> None:
        parts = [p for p in sub.split("/") if p]
        if not parts or any(p in ("..", ".") or p.startswith(".") for p in parts):
            return self.err(403, "Доступ запрещён")
        p = WEB_DIR.joinpath(*parts)
        try:
            p.resolve().relative_to(WEB_DIR.resolve())
        except ValueError:
            return self.err(403, "Доступ запрещён")
        if p.is_symlink() or not p.is_file():
            return self.err(404, "нет файла")
        ctype = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
                 ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml"}.get(p.suffix, "application/octet-stream")
        self.send(Response(200, p.read_bytes(), ctype))

    def file(self, q: dict) -> None:
        if not self.token_ok(q.get("t", [""])[0]):
            return self.err(403, "Нет токена")
        p = safe_path(q.get("path", [""])[0], [RUNS], must_exist=True)
        if not p.is_file():
            return self.err(404, "нет файла")
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        if p.suffix.lower() in (".txt", ".log", ".md", ".json", ".srt"):
            ctype = ("application/json" if p.suffix.lower() == ".json" else "text/plain") + "; charset=utf-8"
        size = p.stat().st_size
        headers = {"Accept-Ranges": "bytes"}
        if q.get("download", ["0"])[0] == "1":
            headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(p.name)}"
        rng = self.headers.get("Range")
        start, end, status = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", rng or "")
        if m and size:
            if m.group(1):
                start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
            elif m.group(2):
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416); self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0"); self.end_headers(); return
            status = 206
            headers["Content-Range"] = f"bytes {start}-{end}/{size}"
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end - start + 1 if size else 0))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command == "HEAD" or not size:
            return
        with p.open("rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def run_action(self, body: dict) -> None:
        aid = body.get("action")
        act = self.app.actions.get(aid) if isinstance(aid, str) else None
        if not act:
            return self.err(400, f"Неизвестное действие: {aid!r}")
        params = body.get("params") or {}
        if not isinstance(params, dict):
            return self.err(400, "params — объект")
        try:
            steps = act.build(params, self.app)
        except PathError as e:
            return self.err(403, f"Доступ запрещён: {e}")
        except ValueError as e:
            return self.err(400, str(e))
        label = act.label
        if isinstance(steps, tuple):
            steps, label = steps
        try:
            job = self.app.jobs.start(aid, label, steps, act.heavy, on_done=act.on_done)
        except JobBusy as e:
            return self.err(409, str(e))
        return self.json(200, {"job": job.id, "label": label})

    def upload(self, q: dict) -> None:
        """Загрузка аудио/видео: тело запроса — сам файл. Куда класть — решает маршрут модуля upload_target."""
        target_fn = getattr(self.app, "upload_target", None)
        if not target_fn:
            return self.err(404, "загрузка не настроена")
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return self.err(400, "пустой файл")
        if n > MAX_UPLOAD:
            return self.err(413, "Файл больше 500 МБ. Сожмите запись или обрежьте её.")
        dst = target_fn({k: v[0] for k, v in q.items()}, self.headers.get("X-File-Name", ""))
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".part")
        left = n
        with tmp.open("wb") as f:
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        if left:
            tmp.unlink(missing_ok=True)
            return self.err(400, "Загрузка прервалась. Попробуйте ещё раз.")
        for old in dst.parent.glob(dst.stem + ".*"):
            if old != tmp and old.suffix != ".part":
                old.unlink()
        shutil.move(str(tmp), str(dst))
        return self.json(200, {"ok": True, "path": rel(dst), "bytes": n})


class Server(ThreadingHTTPServer):
    daemon_threads = True
    # на Windows SO_REUSEADDR позволяет двум процессам слушать один порт — там выключено
    allow_reuse_address = not IS_WIN

    def __init__(self, port: int, app: App):
        super().__init__(("127.0.0.1", port), Handler)
        self.app = app


def bind(app: App, start: int = 8765, tries: int = 40) -> Server:
    last = None
    for port in range(start, start + tries):
        try:
            srv = Server(port, app)
            app.port = port
            return srv
        except OSError as e:
            last = e
    raise SystemExit(f"Нет свободного порта {start}–{start + tries - 1}: {last}")


__all__ = ["App", "Request", "Response", "bind", "check_tester", "jdump"]
