/* Ядро интерфейса: API, навигация, общие компоненты. Модули разделов — web/modules/<id>.js, регистрируются через KP.section(). */
(() => {
  "use strict";
  const token = document.querySelector('meta[name="kp-token"]').content;

  // ---------- DOM ----------
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
      else if (k === "dataset") Object.assign(el.dataset, v);
      else if (v === true) el.setAttribute(k, "");
      else el.setAttribute(k, v);
    }
    for (const c of kids.flat(Infinity)) {
      if (c === null || c === undefined || c === false) continue;
      el.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------- API ----------
  async function api(path, opts = {}) {
    const init = { method: opts.method || (opts.body !== undefined ? "POST" : "GET"), headers: {} };
    if (init.method === "POST") {
      init.headers["X-Bench-Token"] = token;
      if (opts.raw) { init.body = opts.raw; Object.assign(init.headers, opts.headers || {}); }
      else { init.headers["Content-Type"] = "application/json"; init.body = JSON.stringify(opts.body ?? {}); }
    }
    let r;
    try { r = await fetch(path, init); }
    catch (e) { throw new Error("Нет связи с интерфейсом. Проверьте, что окно с сервером не закрыто."); }
    let data = null;
    try { data = await r.json(); } catch (e) { /* не JSON */ }
    if (!r.ok) throw new Error((data && data.error) || `Ошибка ${r.status}`);
    return data;
  }
  const fileUrl = (path, download) => `/api/file?path=${encodeURIComponent(path)}&t=${encodeURIComponent(token)}${download ? "&download=1" : ""}`;

  // ---------- уведомления и подтверждение ----------
  function toast(msg, err) {
    const el = h("div", { class: "toast" + (err ? " err" : ""), role: err ? "alert" : "status" }, msg);
    document.getElementById("toasts").append(el);
    setTimeout(() => el.remove(), err ? 9000 : 4500);
  }
  function confirmBox(title, body) {
    const d = document.getElementById("confirm");
    document.getElementById("confirm-title").textContent = title;
    const b = document.getElementById("confirm-body");
    b.replaceChildren(...(Array.isArray(body) ? body : [body]).map(x => x instanceof Node ? x : h("p", {}, x)));
    return new Promise(res => {
      d.addEventListener("close", () => res(d.returnValue === "ok"), { once: true });
      d.returnValue = "";
      d.showModal();
      document.getElementById("confirm-ok").focus();
    });
  }

  // ---------- задачи ----------
  const STATE = { running: "идёт", done: "готово", failed: "ошибка", stopped: "остановлено", queued: "в очереди" };
  const active = new Set();
  function indicator() {
    const el = document.getElementById("job-indicator");
    el.hidden = active.size === 0;
    el.className = "chip busy";
    el.textContent = active.size ? `Идёт задача: ${[...active][0]}` : "";
  }

  /* Запуск действия с живым логом. box — элемент, куда выводится лог; возвращает Promise с итогом задачи. */
  async function run(action, params, box, opts = {}) {
    let res;
    try { res = await api("/api/run", { body: { action, params } }); }
    catch (e) { toast(e.message, true); if (box) box.replaceChildren(h("div", { class: "errbox", role: "alert" }, e.message)); return null; }
    return watch(res.job, res.label, box, opts);
  }
  function watch(jobId, label, box, opts = {}) {
    const status = h("span", { class: "status running" }, "идёт");
    const secs = h("span", { class: "muted small" });
    const stop = h("button", { class: "btn small danger", type: "button" }, "Остановить");
    const pre = h("pre", { class: "log", tabindex: "0", "aria-label": "Лог задачи" });
    const err = h("div", { class: "errbox", role: "alert", hidden: true });
    const logLink = h("span", { class: "muted small" });
    stop.addEventListener("click", () => api(`/api/job/${jobId}/stop`, { body: {} }).catch(e => toast(e.message, true)));
    if (box) box.replaceChildren(h("div", { class: "jobbar" }, h("b", {}, label), status, secs, stop, logLink), err, pre);
    active.add(label); indicator();
    return new Promise(resolve => {
      const tick = async () => {
        let j;
        try { j = await api(`/api/job/${jobId}`); }
        catch (e) { setTimeout(tick, 2000); return; }
        const atBottom = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 30;
        pre.textContent = j.tail.join("\n");
        if (atBottom) pre.scrollTop = pre.scrollHeight;
        secs.textContent = `${j.seconds} с`;
        status.textContent = STATE[j.state] || j.state;
        status.className = "status " + j.state;
        if (j.state === "running" || j.state === "queued") { setTimeout(tick, 900); return; }
        stop.hidden = true;
        logLink.textContent = "Полный лог: " + j.log;
        if (j.state !== "done") { err.hidden = false; err.textContent = (j.error ? j.error + ". " : "") + "Подробности — в логе ниже."; }
        active.delete(label); indicator();
        if (opts.onDone) opts.onDone(j);
        resolve(j);
      };
      tick();
    });
  }

  // ---------- компоненты ----------
  function copyBtn(text, label = "Скопировать") {
    const b = h("button", { class: "btn small", type: "button" }, label);
    b.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(text); b.textContent = "Скопировано"; }
      catch (e) {
        const ta = h("textarea", {}); ta.value = text; document.body.append(ta); ta.select();
        try { document.execCommand("copy"); b.textContent = "Скопировано"; } catch (e2) { b.textContent = "Выделите и скопируйте вручную"; }
        ta.remove();
      }
      setTimeout(() => (b.textContent = label), 2500);
    });
    return b;
  }
  function codeBlock(text) {
    return h("div", { class: "codewrap" }, h("pre", {}, h("code", {}, text)), copyBtn(text));
  }

  /* Мини-разбор markdown из references/*.md: заголовки, списки, код, цитаты, `код`, **жирный**. */
  function md(src) {
    const out = [];
    const lines = String(src || "").split("\n");
    let i = 0, list = null;
    const inline = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };
    while (i < lines.length) {
      const ln = lines[i];
      if (ln.startsWith("```")) {
        closeList();
        const buf = []; i++;
        while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
        i++;
        out.push({ code: buf.join("\n") });
        continue;
      }
      let m;
      if ((m = ln.match(/^(#{2,4})\s+(.*)/))) { closeList(); out.push(`<h3>${inline(m[2])}</h3>`); }
      else if ((m = ln.match(/^\s*[-*]\s+(.*)/))) { if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if ((m = ln.match(/^\s*\d+\.\s+(.*)/))) { if (list !== "ol") { closeList(); out.push("<ol>"); list = "ol"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if (ln.startsWith("> ")) { closeList(); out.push(`<blockquote>${inline(ln.slice(2))}</blockquote>`); }
      else if (!ln.trim()) closeList();
      else { closeList(); out.push(`<p>${inline(ln)}</p>`); }
      i++;
    }
    closeList();
    const wrap = h("div", { class: "md" });
    let html = "";
    const flush = () => { if (html) { const d = h("div"); d.innerHTML = html; wrap.append(...d.childNodes); html = ""; } };
    for (const part of out) { if (typeof part === "string") html += part; else { flush(); wrap.append(codeBlock(part.code)); } }
    flush();
    return wrap;
  }

  /* Кнопка действия: предупреждение о скачивании, подтверждение, запуск, лог в box. */
  function actionButton(a, box) {
    const b = h("button", { class: "btn" + (a.primary ? " primary" : ""), type: "button", disabled: !!a.disabled,
      title: a.disabled && a.reason ? a.reason : null }, a.label);
    b.addEventListener("click", async () => {
      if (a.warn && !(await confirmBox(a.label, [a.warn, "Продолжить?"]))) return;
      const params = typeof a.params === "function" ? a.params() : (a.params || {});
      if (params === null) return;
      b.disabled = true;
      const j = await run(a.action, params, box, { onDone: a.onDone });
      b.disabled = false;
      if (!j && a.onFail) a.onFail();
    });
    return b;
  }

  /* Общий компонент «шаг». opts: num, id, title, why, needs[], howto (markdown или Node), actions[], body (Node[]), result (Node), muted */
  function step(opts) {
    const box = h("div", { class: "jobbox", "aria-live": "polite" });
    const acts = (opts.actions || []).map(a => {
      const btn = actionButton(a, opts.box || box);
      return a.disabled && a.reason ? h("span", { class: "row" }, btn, h("span", { class: "reason" }, a.reason)) : btn;
    });
    const card = h("section", { class: "card" + (opts.muted ? " muted-card" : ""), id: opts.id ? "step-" + opts.id : null, "aria-labelledby": opts.id ? "h-" + opts.id : null },
      h("h2", { id: opts.id ? "h-" + opts.id : null }, opts.num !== undefined ? h("span", { class: "step-num" }, opts.num) : null, opts.title, opts.badge || null),
      opts.why ? h("p", {}, h("b", {}, "Зачем. "), opts.why) : null,
      opts.needs && opts.needs.length ? h("p", {}, h("b", {}, "Что нужно. "), opts.needs.join("; ")) : null,
      opts.howto ? h("details", {}, h("summary", {}, "Инструкция"), typeof opts.howto === "string" ? md(opts.howto) : opts.howto) : null,
      opts.body || null,
      acts.length ? h("div", { class: "row" }, acts) : null,
      opts.box || box,
      opts.result || null);
    card.jobBox = box;
    return card;
  }

  const VERDICTS = [["ok", "годится"], ["partial", "с оговорками"], ["no", "не годится"], ["fail", "не запустилось"]];

  /* Форма результата: метрики (с предзаполнением), вердикт, заметка, «Записать результат».
     opts: title, variants [{id,name}], metrics [{id,label,unit}], prefill(variantId) -> {metric: value}, files(variantId) -> [path],
           onSubmit(values) -> Promise, recorded(variantId) -> строка или null */
  function resultForm(opts) {
    const uid = "rf" + Math.random().toString(36).slice(2, 8);
    const sel = h("select", { id: uid + "-v" }, opts.variants.map(v => h("option", { value: v.id }, v.name)));
    const metricsBox = h("div", { class: "grid3" });
    const inputs = {};
    const status = h("p", { class: "muted small" });
    const fill = () => {
      const pre = opts.prefill ? opts.prefill(sel.value) || {} : {};
      metricsBox.replaceChildren(...opts.metrics.map(m => {
        const inp = h("input", { type: "number", step: "any", id: `${uid}-${m.id}`, inputmode: "decimal" });
        if (pre[m.id] !== undefined && pre[m.id] !== null) inp.value = pre[m.id];
        inputs[m.id] = inp;
        return h("label", { class: "field", for: `${uid}-${m.id}` }, h("span", {}, `${m.label}${m.unit && !["балл", "0/1", "шт"].includes(m.unit) && !m.label.includes(m.unit) && !m.label.endsWith(", с") ? ", " + m.unit : ""}${pre[m.id] !== undefined && pre[m.id] !== null ? " · из прогона" : ""}`), inp);
      }));
      const rec = opts.recorded ? opts.recorded(sel.value) : null;
      status.textContent = rec ? "Уже записано: " + rec : "";
    };
    sel.addEventListener("change", fill);
    const vname = uid + "-verdict";
    const verdicts = h("fieldset", {}, h("legend", {}, "Вердикт"), h("div", { class: "verdicts" },
      VERDICTS.map(([id, label]) => h("label", {}, h("input", { type: "radio", name: vname, value: id }), label))));
    const setup = h("input", { type: "number", step: "any", min: "0", id: uid + "-setup" });
    const note = h("textarea", { id: uid + "-note", maxlength: "2000", placeholder: "Что сломалось, что пришлось обойти, на каком железе" });
    const btn = h("button", { class: "btn primary", type: "submit" }, "Записать результат");
    const box = h("div", { "aria-live": "polite" });
    const form = h("form", { class: "stack" },
      h("h3", {}, opts.title || "Записать результат"),
      h("div", { class: "row" }, h("label", { class: "field", for: uid + "-v" }, h("span", {}, "Вариант"), sel)),
      metricsBox, verdicts,
      h("div", { class: "grid2" },
        h("label", { class: "field", for: uid + "-setup" }, h("span", {}, "Минут на установку"), setup),
        h("label", { class: "field", for: uid + "-note" }, h("span", {}, "Заметка"), note)),
      h("div", { class: "row" }, btn), status, box);
    form.addEventListener("submit", async ev => {
      ev.preventDefault();
      const verdict = form.querySelector(`input[name="${vname}"]:checked`);
      if (!verdict) { toast("Выберите вердикт", true); return; }
      const metrics = {};
      for (const [k, inp] of Object.entries(inputs)) {
        if (inp.value.trim() === "") continue;
        const n = Number(inp.value.replace(",", "."));
        if (!Number.isFinite(n)) { toast(`Метрика ${k}: нужно число`, true); inp.focus(); return; }
        metrics[k] = n;
      }
      const values = { variant: sel.value, metrics, verdict: verdict.value, note: note.value,
        setup_min: setup.value.trim() === "" ? null : Number(setup.value.replace(",", ".")),
        files: opts.files ? opts.files(sel.value) || [] : [] };
      btn.disabled = true;
      await opts.onSubmit(values, box);
      btn.disabled = false;
    });
    form.setVariant = id => { sel.value = id; fill(); };
    form.setMetric = (id, v) => { if (inputs[id]) inputs[id].value = v; };
    form.refill = fill;
    fill();
    return h("div", { class: "card" }, form);
  }

  function player(path) {
    if (!path) return null;
    const ext = path.split(".").pop().toLowerCase();
    const isVideo = ["mp4", "mov", "webm"].includes(ext);
    return h("div", { class: "player" }, h(isVideo ? "video" : "audio", { controls: true, preload: "metadata", src: fileUrl(path) }));
  }

  /* Таблица внешних программ — общий компонент, его использует и раздел «Тесты». */
  async function toolsTable (box) {
    box.replaceChildren(h("p", { class: "muted" }, "Проверяю программы…"));
    let d;
    try { d = await api("/api/tools"); } catch (e) { box.replaceChildren(h("div", { class: "errbox" }, e.message)); return; }
    const rows = d.tools.map(t => h("tr", {},
      h("td", {}, h("b", {}, t.name)),
      h("td", {}, t.found ? h("span", { class: "badge ok" }, t.bundled ? "встроена" : "есть") : h("span", { class: "badge bad" }, "нет")),
      h("td", { class: "small" }, t.found ? (t.version || t.path) : h("div", { class: "stack" },
        h("div", { class: "row" }, h("code", {}, t.install), t.install && !/^Скачать/.test(t.install) ? copyBtn(t.install) : null),
        t.note ? h("span", { class: "muted" }, t.note) : null))));
    const again = h("button", { class: "btn", type: "button" }, "Проверить снова");
    again.addEventListener("click", () => toolsTable(box));
    box.replaceChildren(
      h("div", { class: "scroll" }, h("table", { class: "t" }, h("thead", {}, h("tr", {}, h("th", {}, "Программа"), h("th", {}, "Статус"), h("th", {}, "Версия или как поставить"))), h("tbody", {}, rows))),
      KP.meta && KP.meta.installed
        ? h("p", { class: "muted small" }, "Программы встроены в установку (папка tools). Пакеты Python и модели — раздел «Установка».")
        : h("p", { class: "muted small" }, `Интерфейс не ставит программы сам. Выполните команду в терминале (${d.os === "windows" ? "PowerShell" : "Терминал"}), затем «Проверить снова». После установки иногда нужно перезапустить интерфейс.`),
      again);
  }


  // ---------- разделы и навигация ----------
  const sections = {};
  const KP = window.KP = { h, esc, api, run, watch, toast, confirmBox, fileUrl, md, copyBtn, codeBlock, step, resultForm, player, actionButton, toolsTable, meta: null,
    section(id, def) { sections[id] = def; if (KP.meta && current() === id) route(); },
    get settings() { return KP.meta ? KP.meta.settings : {}; },
    async reloadSettings() { KP.meta.settings = await api("/api/settings"); chip(); return KP.meta.settings; } };

  const current = () => (location.hash.slice(1) || (KP.meta && KP.meta.sections[0] && KP.meta.sections[0].id) || "");
  function chip() {
    const t = KP.meta.settings.tester;
    const el = document.getElementById("tester-chip");
    el.textContent = t ? `Тестировщик: ${t}` : "Тестировщик не выбран";
  }
  function nav() {
    const ul = document.getElementById("nav");
    const cur = current();
    const bySkill = Object.fromEntries(KP.meta.sections.filter(s => s.skill).map(s => [s.skill, s]));
    const items = [];
    for (const s of KP.meta.sections.filter(s => !s.skill && (s.order || 0) < 800)) items.push(h("li", {}, h("a", { href: "#" + s.id, "aria-current": cur === s.id ? "page" : null }, s.title)));
    items.push(h("li", { class: "group", role: "presentation" }, "Шаги конвейера"));
    for (const st of KP.meta.steps) {
      const sec = bySkill[st.skill];
      const label = `${st.n} ${st.short}`;
      items.push(h("li", {}, sec ? h("a", { href: "#" + sec.id, "aria-current": cur === sec.id ? "page" : null }, label)
        : h("span", { class: "soon", "aria-disabled": "true", title: st.name }, label, h("span", { class: "tag" }, "скоро"))));
    }
    // служебные разделы: order >= 800 (Установка, Настройки)
    const service = KP.meta.sections.filter(s => !s.skill && (s.order || 0) >= 800);
    if (service.length) {
      items.push(h("li", { class: "group", role: "presentation" }, "Служебное"));
      for (const s of service) items.push(h("li", {}, h("a", { href: "#" + s.id, "aria-current": cur === s.id ? "page" : null }, s.title)));
    }
    ul.replaceChildren(...items);
  }
  const loaded = new Set();
  function loadJs(sec) {
    if (!sec.js || loaded.has(sec.js)) return;
    loaded.add(sec.js);
    document.head.append(h("script", { src: "/web/" + sec.js }));
  }
  function route() {
    nav();
    const id = current();
    const sec = KP.meta.sections.find(s => s.id === id);
    const main = document.getElementById("main");
    if (!sec) { main.replaceChildren(h("h1", {}, "Раздел не найден"), h("p", {}, h("a", { href: "#" + KP.meta.sections[0].id }, "На главную"))); return; }
    document.title = `${sec.title} — Конвейер контента`;
    if (!sections[id]) { main.replaceChildren(h("p", { class: "muted" }, "Загрузка раздела…")); loadJs(sec); return; }
    main.replaceChildren();
    sections[id].render(main);
    main.focus({ preventScroll: true });
  }
  window.addEventListener("hashchange", route);

  // ---------- выход и heartbeat ----------
  // Сервер останавливается сам, если браузер молчит 10 минут: вкладка раз в минуту сообщает, что открыта.
  let stopped = false;
  setInterval(() => { if (!stopped) api("/api/heartbeat", { body: {} }).catch(() => {}); }, 60000);
  function stoppedScreen() {
    stopped = true;
    document.getElementById("nav").replaceChildren();
    document.getElementById("main").replaceChildren(h("h1", {}, "Интерфейс остановлен"),
      h("p", {}, "Эту вкладку можно закрыть. Чтобы начать снова — ярлык «Конвейер контента» на рабочем столе."));
  }
  document.getElementById("exit-btn").addEventListener("click", async () => {
    const body = ["Интерфейс остановится на этом компьютере. Открыть снова — ярлыком «Конвейер контента»."];
    if (active.size) body.unshift(`Сейчас идёт задача: ${[...active][0]}. Она будет остановлена.`);
    if (!(await confirmBox("Выйти?", body))) return;
    try { await api("/api/shutdown", { body: {} }); } catch (e) { /* сервер мог уже остановиться */ }
    stoppedScreen();
  });
  window.addEventListener("error", e => toast("Ошибка страницы: " + e.message, true));

  api("/api/meta").then(m => { KP.meta = m; chip(); m.sections.forEach(loadJs); route(); })
    .catch(e => { document.getElementById("main").replaceChildren(h("div", { class: "errbox", role: "alert" }, e.message)); });
})();
