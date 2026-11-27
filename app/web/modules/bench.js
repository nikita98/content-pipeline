/* Раздел «Тесты»: стенд этапа 3 (skills/kp-bench). Данные — /api/bench/catalog и /api/bench/state. */
(() => {
  "use strict";
  const { h, api, run, toast, step, resultForm, player, md, copyBtn, codeBlock, fileUrl, confirmBox } = KP;
  let C = null;          // каталог bench.json + разделы tests.md
  let S = null;          // состояние тестировщика
  let T = "";            // тестировщик
  const updaters = [];   // функции перерисовки динамических частей после обновления состояния
  const VERD = { ok: "годится", partial: "с оговорками", no: "не годится", fail: "не запустилось" };

  const test = id => C.catalog.tests.find(t => t.id === id);
  const sec = id => (C.sections[id] || "").replace(/^## .*\n/, "");
  const lsKey = k => `kp-bench:${T}:${k}`;
  const lsGet = (k, d) => { try { return JSON.parse(localStorage.getItem(lsKey(k))) ?? d; } catch (e) { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(lsKey(k), JSON.stringify(v)); } catch (e) { /* приватный режим */ } };
  const pct = v => (typeof v === "number" ? (v * 100).toFixed(1).replace(".", ",") + " %" : "—");

  async function refresh() {
    S = await api(`/api/bench/state?tester=${encodeURIComponent(T)}`);
    updaters.forEach(f => { try { f(); } catch (e) { console.error(e); } });
  }
  function onUpdate(f) { updaters.push(f); f(); }
  const recorded = (testId, v) => {
    const r = S.results.filter(x => x.test === testId && x.variant === v);
    return r.length ? r.map(x => `${x.date}, ${VERD[x.verdict] || x.verdict}`).join("; ") : null;
  };

  /* Форма результата для теста: метрики из каталога, запись через record.py, затем summary.py. */
  function recordForm(testId, prefill, files, variants) {
    const t = test(testId);
    return resultForm({
      title: `Записать результат: ${t.title}`,
      variants: variants || t.variants,
      metrics: t.metrics,
      prefill, files,
      recorded: v => recorded(testId, v),
      onSubmit: async (vals, box) => {
        const j = await run("bench.record", { tester: T, test: testId, ...vals }, box);
        if (j && j.state === "done") { toast("Результат записан"); await refresh(); }
      },
    });
  }
  function pane(title, ...kids) { return h("div", { class: "pane stack" }, h("h3", {}, title), ...kids); }
  const agentOk = () => S.agent.selected && S.agent.found;

  // ---------- шапка ----------
  function header() {
    const envBox = h("div");
    const doneBox = h("div");
    const sumBox = h("div");
    onUpdate(() => {
      const e = S.env;
      envBox.replaceChildren(e ? h("dl", { class: "kv small" },
        h("dt", {}, "Проверено"), h("dd", {}, e.date),
        h("dt", {}, "ОС"), h("dd", {}, `${e.os} ${e.machine || ""}`),
        h("dt", {}, "Python / Node"), h("dd", {}, `${e.python} / ${e.node || "нет"}`),
        h("dt", {}, "ffmpeg / git"), h("dd", {}, `${e.ffmpeg ? "есть" : "нет"} / ${e.git ? "есть" : "нет"}`),
        h("dt", {}, "Видеокарта"), h("dd", {}, e.gpu && e.gpu.nvidia ? `${e.gpu.name || "NVIDIA"} ${e.gpu.vram || ""}` : "NVIDIA нет — Qwen3-TTS пропускаем"),
        h("dt", {}, "Свободно"), h("dd", {}, `${e.disk_free_gb} ГБ`))
        : h("p", { class: "muted" }, "Среда ещё не проверена: нажмите «Проверить среду»."));
      doneBox.replaceChildren(S.results.length
        ? h("div", { class: "scroll" }, h("table", { class: "t" }, h("thead", {}, h("tr", {}, ["Тест", "Вариант", "Дата", "Вердикт"].map(x => h("th", {}, x)))),
          h("tbody", {}, S.results.map(r => h("tr", {}, h("td", {}, r.test), h("td", {}, r.variant), h("td", {}, r.date), h("td", { class: "v-" + r.verdict }, VERD[r.verdict] || r.verdict))))))
        : h("p", { class: "muted" }, "Пока ничего не записано."));
    });
    const loadSummary = async () => {
      const R = await api("/api/bench/results");
      sumBox.replaceChildren(R.results.length
        ? h("div", { class: "scroll" }, h("table", { class: "t" }, h("thead", {}, h("tr", {}, ["Тест", "Вариант", "Прогонов", "Метрики", "Вердикты"].map(x => h("th", {}, x)))),
          h("tbody", {}, R.results.map(r => h("tr", {}, h("td", {}, r.test), h("td", {}, r.variant), h("td", {}, r.runs),
            h("td", { class: "small" }, Object.entries(r.metrics).map(([k, v]) => `${k}=${v}`).join(", ")),
            h("td", { class: "small" }, Object.entries(r.verdicts).map(([k, n]) => `${VERD[k] || k}: ${n}`).join(", ")))))))
        : h("p", { class: "muted" }, `Свод пуст (обновлён ${R.updated || "—"}).`));
    };
    loadSummary();
    const box = h("div", { "aria-live": "polite" });
    return h("section", { class: "card", "aria-labelledby": "h-head" },
      h("h2", { id: "h-head" }, `Тестировщик: ${T}`, h("a", { href: "#settings", class: "small" }, "сменить")),
      h("div", { class: "grid2" },
        h("div", { class: "stack" }, h("h3", {}, "Среда"), envBox,
          h("div", { class: "row" }, KP.actionButton({ label: "Проверить среду", action: "bench.check_env", params: () => ({ tester: T }), primary: !S.env, onDone: refresh }, box))),
        h("div", { class: "stack" }, h("h3", {}, "Записано у вас"), doneBox)),
      box,
      h("details", {}, h("summary", {}, "Свод всех тестировщиков (summary.py)"), sumBox,
        h("div", { class: "row" }, KP.actionButton({ label: "Пересобрать свод", action: "bench.summary", params: {}, onDone: () => { loadSummary(); refresh(); } }, box))),
      delivery());
  }

  // ---------- отправка результатов ----------
  function delivery() {
    const box = h("div", { "aria-live": "polite" });
    const gitBtn = h("button", { class: "btn primary", type: "button" }, "Отправить в git");
    const zipBtn = h("button", { class: "btn", type: "button" }, "Скачать результаты архивом");
    const exportZip = async () => {
      const j = await run("bench.export", { tester: T }, box);
      if (j && j.state === "done" && j.result.file) {
        const a = h("a", { class: "btn", href: fileUrl(j.result.file, true), download: "" }, "Скачать " + j.result.file.split("/").pop());
        box.append(h("div", { class: "row" }, a, h("span", { class: "muted small" }, "Отправьте архив владельцу проекта.")));
        a.click();
      }
    };
    zipBtn.addEventListener("click", exportZip);
    gitBtn.addEventListener("click", async () => {
      let g;
      try { g = await api(`/api/bench/git?tester=${encodeURIComponent(T)}`); } catch (e) { toast(e.message, true); return; }
      if (g.problems.length) {
        box.replaceChildren(h("div", { class: "errbox", role: "alert" }, "Отправить в git нельзя: " + g.problems.join(" ") + " Скачайте результаты архивом.", " ", h("span", {}, zipFallback())));
        return;
      }
      if (!g.files.length) { toast("Нет новых результатов для отправки"); return; }
      const ok = await confirmBox("Отправить в git", [
        h("p", {}, `Ветка ${g.branch}, автор ${g.user}. Файлы:`),
        h("ul", {}, g.files.map(f => h("li", {}, h("code", {}, f)))),
        h("p", {}, "Коммит: ", h("b", {}, g.message)),
        h("p", { class: "muted small" }, "Будет выполнено: git add → git commit → git pull --rebase → git push."),
      ]);
      if (!ok) return;
      const j = await run("bench.git_push", { tester: T }, box);
      if (j && j.state !== "done") box.append(h("div", { class: "errbox" }, "Не получилось отправить. Скачайте результаты архивом и передайте владельцу. ", zipFallback()));
      if (j && j.state === "done") toast("Отправлено в git");
    });
    const zipFallback = () => { const b = h("button", { class: "btn small", type: "button" }, "Скачать архивом"); b.addEventListener("click", exportZip); return b; };
    if (!KP.meta.git_repo) {
      // установленная копия или архив — не git-клон: основной путь — архив (решение 22)
      zipBtn.className = "btn primary";
      return h("div", { class: "stack" }, h("hr", { class: "sep" }), h("h3", {}, "Отправить результаты"),
        h("p", { class: "muted small" }, "Скачайте архив с результатами и перешлите его владельцу проекта (почтой или в мессенджере)."),
        h("div", { class: "row" }, zipBtn), box);
    }
    return h("div", { class: "stack" }, h("hr", { class: "sep" }), h("h3", {}, "Отправить результаты"),
      h("p", { class: "muted small" }, "Если git настроен и есть права — «Отправить в git». Если нет — архив: его можно переслать владельцу."),
      h("div", { class: "row" }, gitBtn, zipBtn), box);
  }

  // ---------- 0. Подготовка ----------
  function prep() {
    const toolsBox = h("div");
    KP.toolsTable(toolsBox);
    const packsBox = h("div", { class: "stack" });
    const box = h("div", { "aria-live": "polite" });
    onUpdate(() => {
      packsBox.replaceChildren(h("div", { class: "scroll" }, h("table", { class: "t" },
        h("thead", {}, h("tr", {}, ["Пакет", "Для чего", "Окружение", ""].map(x => h("th", {}, x)))),
        h("tbody", {}, S.packs.map(p => h("tr", {},
          h("td", {}, h("b", {}, p.label), " ", p.installed ? h("span", { class: "badge ok" }, "установлен") : null),
          h("td", { class: "small" }, p.for),
          h("td", { class: "small" }, h("code", {}, p.venv_label || ".venv-" + p.venv)),
          h("td", {}, p.disabled ? h("span", { class: "reason" }, p.disabled) : KP.actionButton({
            label: p.installed ? "Переустановить" : "Установить", action: "bench.install", params: { pack: p.id, tester: T },
            warn: [h("p", {}, `Будет скачано: ${p.downloads}`), p.requires ? h("p", {}, `Сначала должен быть установлен пакет «${S.packs.find(x => x.id === p.requires).label}».`) : null,
              h("p", { class: "muted small" }, `Установка в окружение ${p.venv_label || ".venv-" + p.venv} в папке проекта (в git не попадает). Отменить можно кнопкой «Остановить».`)],
            onDone: refresh }, box))))))));
    });
    const recBox = h("div", { class: "grid2" });
    onUpdate(() => recBox.replaceChildren(uploader("script", "Запись текста script_ru.txt (45–60 с)"), uploader("voice_sample", "Свободная речь 15 с (образец для клона)")));
    return step({
      num: 0, id: "prep", title: "Подготовка",
      why: "Программы, окружения Python и запись голоса нужны для тестов asr, voice-clean, tts-local и edit. text-check и stress запись не требуют.",
      body: [
        h("h3", {}, "Среда: программы"), toolsBox,
        h("hr", { class: "sep" }),
        h("h3", {}, "Установка пакетов Python"),
        h("p", { class: "muted small" }, "Ставится только то, что нажмёте. Модели скачиваются при первом запуске теста. Для моделей нужно от 20 ГБ свободного места (check_env.py)."),
        packsBox,
        h("details", {}, h("summary", {}, "Как ставить вручную (install.md)"), h("p", { class: "small" }, "Полная инструкция — skills/kp-bench/references/install.md.")),
        h("hr", { class: "sep" }),
        h("h3", {}, "Запись голоса"),
        h("details", { open: true }, h("summary", {}, "Как записать"), md(sec("prep"))),
        h("details", {}, h("summary", {}, "Текст для чтения (script_ru.txt)"), ...C.script_text.split(/\n\s*\n/).map(p => h("p", {}, p))),
        recBox,
      ],
      box,
    });
  }
  function uploader(kind, label) {
    const id = "up-" + kind;
    const inp = h("input", { type: "file", id, accept: "audio/*,video/*,.m4a,.wav,.mp3,.ogg,.flac,.aac,.opus,.webm,.mp4,.mov" });
    const prog = h("progress", { max: "100", value: "0", hidden: true, "aria-label": "Загрузка" });
    const msg = h("p", { class: "small muted", "aria-live": "polite" });
    inp.addEventListener("change", () => {
      const f = inp.files[0];
      if (!f) return;
      if (f.size > 500 * 1024 * 1024) { msg.textContent = "Файл больше 500 МБ."; return; }
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `/api/upload?tester=${encodeURIComponent(T)}&kind=${kind}`);
      xhr.setRequestHeader("X-Bench-Token", document.querySelector('meta[name="kp-token"]').content);
      xhr.setRequestHeader("X-File-Name", encodeURIComponent(f.name));
      prog.hidden = false;
      xhr.upload.onprogress = e => { if (e.lengthComputable) prog.value = Math.round(e.loaded / e.total * 100); };
      xhr.onload = async () => {
        prog.hidden = true;
        let d = {}; try { d = JSON.parse(xhr.responseText); } catch (e) { /* пусто */ }
        if (xhr.status === 200) { toast("Загружено: " + d.path); await refresh(); }
        else { msg.textContent = d.error || "Ошибка загрузки " + xhr.status; toast(msg.textContent, true); }
      };
      xhr.onerror = () => { prog.hidden = true; msg.textContent = "Нет связи с интерфейсом."; };
      xhr.send(f);
    });
    const cur = S.rec[kind];
    return h("div", { class: "pane stack" }, h("label", { class: "field", for: id }, h("span", {}, label), inp), prog, msg,
      cur ? h("p", { class: "small" }, "Сейчас: ", h("code", {}, cur)) : h("p", { class: "small muted" }, "Файл ещё не загружен."),
      player(cur));
  }

  // ---------- 1. text-check ----------
  function textCheck() {
    const t = test("text-check");
    const panes = h("div", { class: "stack" });
    let form;
    const state = v => lsGet("tc-" + v, { found: [], fp: "" });
    const prefill = v => { const s = state(v); const m = S.text_check[v] && S.text_check[v].meta; return { found: s.found.length || null, false_pos: s.fp === "" ? null : Number(s.fp), run_s: m ? m.run_s : null }; };
    const box = h("div", { "aria-live": "polite" });
    onUpdate(() => {
      panes.replaceChildren(...t.variants.map(v => {
        const out = S.text_check[v.id];
        const st = state(v.id);
        const counter = h("span", { class: "badge ok" });
        const setCount = () => { counter.textContent = `найдено ${st.found.length} из ${S.key.length}`; };
        const checks = h("div", { class: "issue-list" }, S.key.map(k => {
          const c = h("input", { type: "checkbox", checked: st.found.includes(k.id) });
          c.addEventListener("change", () => {
            st.found = c.checked ? [...new Set([...st.found, k.id])] : st.found.filter(x => x !== k.id);
            lsSet("tc-" + v.id, st); setCount(); if (form) form.querySelector("form").refill();
          });
          return h("label", { class: "check" }, c, h("span", {}, h("b", {}, k.id), ` ${k.type}: «${k.text}»`));
        }));
        setCount();
        const fpId = "fp-" + v.id;
        const fp = h("input", { type: "number", min: "0", id: fpId, value: st.fp });
        fp.addEventListener("input", () => { st.fp = fp.value; lsSet("tc-" + v.id, st); if (form) form.querySelector("form").refill(); });
        let actions;
        if (v.id === "ru-text") {
          actions = agentOk()
            ? [KP.actionButton({ label: "Запустить в агенте", action: "bench.textcheck_agent", params: () => ({ tester: T }), primary: true, onDone: refresh,
                warn: "Агент прочитает post_ru.md и ответит списком проблем. Нужен установленный скилл ru-text (npx skills add talkstream/ru-text). Агент тратит лимиты своей подписки." }, box)]
            : [h("div", { class: "stack" }, h("p", { class: "reason" }, "Агент не выбран или не найден (Настройки). Скопируйте задачу в агента вручную и вставьте ответ ниже."), codeBlock(S.ru_text_prompt))];
        } else if (v.id === "ru-lint") {
          actions = [KP.actionButton({ label: S.rulint ? "Скачать ru-editor заново" : "Скачать ru-editor", action: "bench.clone_rulint", params: {}, onDone: refresh,
            warn: "Будет скачан репозиторий github.com/miolamio/agent-skills в bench/tools/agent-skills (git clone, без моделей)." }, box),
            KP.actionButton({ label: "Запустить ru_lint.py", action: "bench.textcheck", params: () => ({ tester: T, variant: v.id }), primary: true, disabled: !S.rulint, reason: S.rulint ? "" : "сначала «Скачать ru-editor»", onDone: refresh }, box)];
        } else {
          actions = [KP.actionButton({ label: "Запустить humanizer-ru", action: "bench.textcheck", params: () => ({ tester: T, variant: v.id }), primary: true, onDone: refresh }, box)];
        }
        const outEl = out && out.output ? h("pre", {}, out.output)
          : v.id === "ru-text" && !agentOk() ? h("textarea", { "aria-label": "Ответ агента (только для сверки, не сохраняется)", placeholder: "Вставьте сюда ответ агента для сверки" })
          : h("p", { class: "muted" }, "Ещё не запускали.");
        return pane(`${v.name}${out && out.meta ? ` · ${out.meta.run_s} с` : ""}`,
          h("div", { class: "row" }, actions),
          h("div", { class: "grid2" }, h("div", {}, h("b", {}, "Вывод"), outEl),
            h("div", { class: "stack" }, h("b", {}, "Что нашёл (по ключу)"), counter, checks,
              h("label", { class: "field", for: fpId }, h("span", {}, "Ложных срабатываний (замечания к нормальному тексту)"), fp))));
      }));
    });
    form = recordForm("text-check", prefill, v => { const o = S.text_check[v]; return o && o.output ? [`bench/runs/text-check/${T}/${v}.txt`] : []; });
    return step({ num: 1, id: "text-check", title: t.title, why: t.goal, needs: [t.input, "ключ проверщикам не показывать"], howto: sec("text-check"),
      body: [panes], box, result: form });
  }

  // ---------- 2. stress ----------
  function stress() {
    const t = test("stress");
    const panes = h("div", { class: "grid2" });
    const box = h("div", { "aria-live": "polite" });
    let form;
    const errs = v => lsGet("st-" + v, []);
    onUpdate(() => {
      panes.replaceChildren(...t.variants.map(v => {
        const r = S.stress[v.id];
        const marked = errs(v.id);
        const rows = r && r.rows.length ? r.rows.map((row, i) => {
          const c = h("input", { type: "checkbox", checked: marked.includes(i), "aria-label": `Строка ${i + 1}: ошибка` });
          c.addEventListener("change", () => {
            const m = errs(v.id).filter(x => x !== i); if (c.checked) m.push(i); lsSet("st-" + v.id, m); if (form) form.querySelector("form").refill();
          });
          return h("div", { class: "stress-row" }, h("b", {}, i + 1), h("span", { class: "small muted" }, row.src), h("span", {}, row.res), h("label", { class: "check small" }, c, "ошибка"));
        }) : [h("p", { class: "muted" }, "Ещё не запускали. Исходные строки:"), h("ol", { class: "small" }, S.stress_lines.map(l => h("li", {}, l)))];
        return pane(`${v.name}${r && r.run_s != null ? ` · ${r.run_s} с` : ""}`,
          h("div", { class: "row" }, KP.actionButton({ label: "Запустить", action: "bench.stress", params: () => ({ tester: T, variant: v.id }), primary: true, onDone: refresh }, box)),
          ...rows);
      }));
    });
    form = recordForm("stress", v => ({ errors: S.stress[v] && S.stress[v].rows.length ? errs(v).length : null, run_s: S.stress[v] ? S.stress[v].run_s : null }),
      v => S.stress[v] && S.stress[v].rows.length ? [`bench/runs/stress/${T}/${v}.txt`] : []);
    return step({ num: 2, id: "stress", title: t.title, why: t.goal, needs: [t.input, "пакет «rutextnorm, silero-stress, RUAccent»"], howto: sec("stress"),
      body: [h("p", { class: "small muted" }, "Отметьте строки с ошибкой: ударение по смыслу, всё/все, падеж числа, «₽» и «%» не словами, латиница не прочитана."), panes], box, result: form });
  }

  // ---------- 3. asr ----------
  function asr() {
    const t = test("asr");
    const panes = h("div", { class: "grid3" });
    const box = h("div", { "aria-live": "polite" });
    onUpdate(() => {
      panes.replaceChildren(...t.variants.map(v => {
        const r = S.asr[v.id];
        return pane(v.name,
          h("p", { class: "small muted" }, v.needs),
          KP.actionButton({ label: "Распознать", action: "bench.asr", params: () => ({ tester: T, engine: v.id }), primary: true, disabled: !S.rec.script, reason: S.rec.script ? "" : "нет записи (Подготовка)", onDone: refresh,
            warn: "При первом запуске скачается модель распознавания (размер — проверить). На процессоре распознавание идёт медленнее записи." }, box),
          r.wer ? h("dl", { class: "kv small" }, h("dt", {}, "WER"), h("dd", {}, pct(r.wer.wer)), h("dt", {}, "CER"), h("dd", {}, pct(r.wer.cer)),
            h("dt", {}, "Время"), h("dd", {}, r.run ? `${r.run.run_s} с на ${r.run.audio_s} с (RTF ${r.run.rtf})` : "—"),
            h("dt", {}, "Таймкоды слов"), h("dd", {}, r.run ? (r.run.word_timestamps ? "есть" : "нет") : "—")) : h("p", { class: "muted small" }, "Нет результата."),
          r.text ? h("details", {}, h("summary", {}, "Текст"), h("p", { class: "small" }, r.text)) : null);
      }));
    });
    const form = recordForm("asr", v => { const r = S.asr[v]; return { wer: r.wer ? r.wer.wer : null, cer: r.wer ? r.wer.cer : null, run_s: r.run ? r.run.run_s : null, word_timestamps: r.run ? r.run.word_timestamps : null }; },
      v => S.asr[v].run ? [`bench/runs/asr/${T}/${v}.txt`, `bench/runs/asr/${T}/${v}.words.json`] : []);
    return step({ num: 3, id: "asr", title: t.title, why: t.goal, needs: [t.input, "пакеты GigaAM, faster-whisper или WhisperX"], howto: sec("asr"),
      body: [h("p", { class: "small muted" }, "Глазами проверьте: «Reels», «CRM», «Telegram», «ЗАМОК», числа. Если читали с оговорками — укажите в заметке."), panes], box, result: form });
  }

  // ---------- 4. voice-clean ----------
  function clean() {
    const t = test("voice-clean");
    const panes = h("div", { class: "grid2" });
    const box = h("div", { "aria-live": "polite" });
    onUpdate(() => {
      panes.replaceChildren(
        ...t.variants.map(v => {
          const r = S.clean[v.id];
          return pane(v.name,
            KP.actionButton({ label: "Очистить", action: "bench.clean", params: () => ({ tester: T, variant: v.id }), primary: true, disabled: !S.rec.script, reason: S.rec.script ? "" : "нет записи (Подготовка)", onDone: refresh,
              warn: v.id === "dfn-chain" ? "Нужны пакет DeepFilterNet и программа auto-editor. Модель DeepFilterNet3 скачается при первом запуске." : null }, box),
            r ? h("dl", { class: "kv small" }, h("dt", {}, "Громкость"), h("dd", {}, `${r.lufs} LUFS (цель −14)`), h("dt", {}, "Пик"), h("dd", {}, `${r.true_peak} dBTP`),
              h("dt", {}, "Длительность"), h("dd", {}, `${r.dur_before} → ${r.dur_after} с, вырезано ${r.cut_s} с`)) : h("p", { class: "muted small" }, "Нет результата."),
            r ? player(r.file) : null);
        }),
        S.clean_src ? pane("До очистки (WAV 48 кГц)", player(S.clean_src)) : null);
    });
    const form = recordForm("voice-clean", v => { const r = S.clean[v]; return r ? { lufs: r.lufs, true_peak: r.true_peak, cut_s: r.cut_s } : {}; },
      v => S.clean[v] ? [S.clean[v].file] : []);
    return step({ num: 4, id: "voice-clean", title: t.title, why: t.goal, needs: [t.input, "ffmpeg; для цепочки DeepFilterNet — пакет DeepFilterNet и auto-editor"], howto: sec("voice-clean"),
      body: [h("p", { class: "small muted" }, "Оценку «на слух» ставьте сами: нет ли «металла», не съедены ли концы слов."), panes], box, result: form });
  }

  // ---------- 5. tts-local ----------
  function tts() {
    const t = test("tts-local");
    const panes = h("div", { class: "grid3" });
    const blindBox = h("div", { class: "stack" });
    const box = h("div", { "aria-live": "polite" });
    const voiceSel = h("select", { id: "edge-voice", "aria-label": "Голос Edge TTS" });
    let form;
    onUpdate(() => {
      const keep = voiceSel.value || lsGet("voice", "");
      voiceSel.replaceChildren(...(S.voices.length ? S.voices : ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"]).map(n => h("option", { value: n, selected: n === keep }, n)));
      panes.replaceChildren(...t.variants.map(v => {
        const r = S.tts[v.id];
        const gpuOnly = v.id.startsWith("qwen");
        const blocked = gpuOnly && !S.nvidia;
        const acts = [];
        if (blocked) {
          acts.push(h("p", { class: "reason" }, "Нет видеокарты NVIDIA — вариант не запускается."),
            KP.actionButton({ label: "Записать: не запустилось", action: "bench.record", params: () => ({ tester: T, test: "tts-local", variant: v.id, verdict: "fail", note: "нет GPU", metrics: {} }), onDone: refresh }, box));
        } else {
          if (v.id === "edge-tts") acts.push(h("div", { class: "row" }, h("label", { class: "field", for: "edge-voice" }, h("span", {}, "Голос"), voiceSel),
            KP.actionButton({ label: "Список голосов", action: "bench.tts_voices", params: {}, onDone: refresh }, box)));
          acts.push(h("div", { class: "row" },
            KP.actionButton({ label: "Синтезировать", action: "bench.tts", primary: true, onDone: refresh,
              params: () => { if (v.id === "edge-tts") lsSet("voice", voiceSel.value); return { tester: T, variant: v.id, voice: v.id === "edge-tts" ? voiceSel.value : undefined }; },
              disabled: gpuOnly && !S.rec.voice_sample, reason: gpuOnly && !S.rec.voice_sample ? "нет образца голоса (Подготовка)" : "",
              warn: gpuOnly ? "Скачаются веса Qwen3-TTS 1.7B (размер — проверить). Клон голоса — только с письменного согласия владельца голоса." : "Текст уйдёт в облако Microsoft (Edge TTS, неофициальный доступ)." }, box),
            KP.actionButton({ label: "Обратное распознавание", action: "bench.tts_back", params: () => ({ tester: T, variant: v.id }), disabled: !r.file, reason: r.file ? "" : "сначала синтез", onDone: refresh }, box)));
        }
        return h("div", { class: "pane stack" + (blocked ? " disabled-block" : "") }, h("h3", {}, v.name), h("p", { class: "small muted" }, v.needs), ...acts,
          r.file ? h("dl", { class: "kv small" }, h("dt", {}, "Время"), h("dd", {}, r.meta ? `${r.meta.run_s} с` : "—"), h("dt", {}, "WER обратно"), h("dd", {}, r.back ? pct(r.back.wer) : "—")) : null,
          h("p", { class: "small muted" }, "Плеер — в слепой оценке ниже, чтобы не знать заранее, где какой вариант."));
      }));
      blindBox.replaceChildren(...blindView());
    });
    function blindView() {
      const b = S.blind;
      const make = KP.actionButton({ label: b.items.length ? "Перемешать заново" : "Перемешать файлы", action: "bench.blind_make", params: () => ({ tester: T }), onDone: refresh,
        disabled: !Object.values(S.tts).some(x => x.file), reason: Object.values(S.tts).some(x => x.file) ? "" : "сначала синтез" }, box);
      if (!b.items.length) return [h("p", { class: "muted small" }, "Файлы копируются под именами A, B, C. Оценивает лучше тот, кто не запускал синтез."), make];
      if (b.reveal) {
        return [h("table", { class: "t" }, h("thead", {}, h("tr", {}, ["Файл", "Оценка", "Вариант"].map(x => h("th", {}, x)))),
          h("tbody", {}, Object.entries(b.reveal).map(([lab, r]) => h("tr", {}, h("td", {}, lab), h("td", {}, r.score), h("td", {}, h("b", {}, r.variant)))))),
          h("p", { class: "small muted" }, "Оценки подставлены в форму как mos."), make];
      }
      const sc = {};
      const items = b.items.map(it => {
        const name = "blind-" + it.label;
        return h("div", { class: "pane stack" }, h("h3", {}, "Файл " + it.label), player(it.file),
          h("fieldset", {}, h("legend", {}, "Естественность 1–5"), h("div", { class: "verdicts" }, [1, 2, 3, 4, 5].map(n => {
            const r = h("input", { type: "radio", name, value: n });
            r.addEventListener("change", () => (sc[it.label] = n));
            return h("label", {}, r, n);
          }))));
      });
      const save = h("button", { class: "btn primary", type: "button" }, "Сохранить оценки и раскрыть");
      save.addEventListener("click", async () => {
        try { await api("/api/bench/blind_scores", { body: { tester: T, scores: sc } }); await refresh(); toast("Ключ раскрыт"); }
        catch (e) { toast(e.message, true); }
      });
      return [h("p", { class: "small" }, "1 — непригодно; 2 — заметные дефекты; 3 — годится с правками; 4 — можно публиковать; 5 — не отличить от живого голоса."),
        h("div", { class: "grid3" }, items), h("div", { class: "row" }, save, make)];
    }
    const mos = v => { const r = S.blind.reveal; if (!r) return null; const x = Object.values(r).find(y => y.variant === v); return x ? x.score : null; };
    form = recordForm("tts-local", v => { const r = S.tts[v]; return { mos: mos(v), back_wer: r.back ? r.back.wer : null, run_s: r.meta ? r.meta.run_s : null }; },
      v => S.tts[v].file ? [S.tts[v].file] : []);
    return step({ num: 5, id: "tts-local", title: t.title, why: t.goal, needs: [t.input, "пакеты Edge TTS и GigaAM; Qwen3-TTS — только NVIDIA"], howto: sec("tts-local"),
      body: [panes, h("h3", {}, "Слепая оценка (blind.py)"), blindBox], box, result: form });
  }

  // ---------- 6. edit ----------
  function edit() {
    const t = test("edit");
    const top = h("div", { class: "stack" });
    const panes = h("div", { class: "grid2" });
    const box = h("div", { "aria-live": "polite" });
    onUpdate(() => {
      const e = S.edit;
      top.replaceChildren(h("dl", { class: "kv small" },
        h("dt", {}, "Звук"), h("dd", {}, e.audio ? h("code", {}, e.audio) : "нет (Подготовка, voice-clean)"),
        h("dt", {}, "Слова"), h("dd", {}, e.words ? h("code", {}, e.words) : "нет (тест asr)"),
        h("dt", {}, "Субтитры"), h("dd", {}, e.captions ? [h("code", {}, e.captions), " ", h("code", {}, e.srt)] : "ещё не подготовлены")),
        h("div", { class: "row" }, KP.actionButton({ label: "Подготовить субтитры", action: "bench.captions", params: () => ({ tester: T }), primary: !e.captions, disabled: !e.words, reason: e.words ? "" : "сначала тест asr", onDone: refresh }, box)));
      panes.replaceChildren(...t.variants.map(v => {
        const r = e.runs[v.id];
        const acts = agentOk()
          ? KP.actionButton({ label: "Смонтировать через агента", action: "bench.edit_agent", params: () => ({ tester: T, variant: v.id }), primary: true, disabled: !r.prompt, reason: r.prompt ? "" : e.missing, onDone: refresh,
              warn: [h("p", {}, `Агент в фоне поставит ${v.name} в bench/tools/${v.id}-test (npm скачает пакеты, Remotion или HyperFrames — размер проверить) и отрендерит ролик.`),
                h("p", {}, "Агент получает право запускать команды в папке проекта. Агент тратит лимиты своей подписки. Время установки засеките отдельно.")] }, box)
          : h("div", { class: "stack" }, h("p", { class: "reason" }, "Агент не выбран или не найден (Настройки). Скопируйте задачу в агента вручную."), r.prompt ? codeBlock(r.prompt) : h("p", { class: "muted small" }, e.missing || ""));
        return pane(v.name, h("p", { class: "small muted" }, `${v.price}; ${v.needs}`), acts,
          r.video ? player(r.video) : h("p", { class: "muted small" }, `Ролик появится в bench/runs/edit/${T}/${v.id}.mp4`),
          r.meta && r.meta.render_s != null ? h("p", { class: "small" }, `Рендер: ${r.meta.render_s} с`) : null,
          r.agent ? h("details", {}, h("summary", {}, "Ответ агента"), h("pre", {}, r.agent)) : null);
      }));
    });
    const form = recordForm("edit", v => { const r = S.edit.runs[v]; return { render_s: r.meta ? r.meta.render_s : null }; },
      v => S.edit.runs[v].video ? [S.edit.runs[v].video] : []);
    return step({ num: 6, id: "edit", title: t.title, why: t.goal, needs: [t.input, "Node 22+, ffmpeg, ИИ-агент"], howto: sec("edit"),
      body: [h("p", { class: "small muted" }, "Безопасная зона: сверху 14 %, снизу 25 %, по бокам 10 %. Кириллица — без квадратиков и обрезанных букв."), top, panes], box, result: form });
  }

  // ---------- платные ----------
  function paid() {
    const tests = C.catalog.tests.filter(t => t.group === "paid");
    return h("section", { class: "card muted-card", id: "step-paid", "aria-labelledby": "h-paid" },
      h("h2", { id: "h-paid" }, "Позже: платные тесты"),
      h("p", {}, "Запуск — только после явного «да» с суммой от того, кто платит. В интерфейсе кнопок запуска нет. Ключи API — в своё окружение, не в файлы проекта."),
      ...tests.map(t => h("div", { class: "stack" }, h("h3", {}, `${t.title} (${t.id})`), h("p", { class: "small" }, t.goal),
        h("div", { class: "scroll" }, h("table", { class: "t" }, h("thead", {}, h("tr", {}, ["Вариант", "Цена", "Стоимость теста", "Нужно"].map(x => h("th", {}, x)))),
          h("tbody", {}, t.variants.map(v => h("tr", {}, h("td", {}, v.name), h("td", { class: "small" }, v.price), h("td", {}, h("b", {}, v.test_cost)), h("td", { class: "small" }, v.needs)))))))),
      h("p", { class: "small muted" }, C.catalog.prices_checked || ""));
  }

  // ---------- сборка ----------
  async function render(main) {
    updaters.length = 0;
    T = KP.settings.tester || "";
    main.append(h("h1", {}, "Тесты стенда"));
    if (!T) {
      main.append(h("div", { class: "card" }, h("p", {}, "Сначала укажите имя тестировщика латиницей."), h("a", { class: "btn primary", href: "#settings" }, "Открыть настройки")));
      return;
    }
    try {
      C = C || await api("/api/bench/catalog");
      S = await api(`/api/bench/state?tester=${encodeURIComponent(T)}`);
    } catch (e) { main.append(h("div", { class: "errbox", role: "alert" }, e.message)); return; }
    const order = [["prep", "Подготовка"], ["text-check", "text-check"], ["stress", "stress"], ["asr", "asr"], ["voice-clean", "voice-clean"], ["tts-local", "tts-local"], ["edit", "edit"], ["paid", "Платные"]];
    main.append(
      h("p", { class: "muted" }, "Порядок: подготовка → text-check → stress → asr → voice-clean → tts-local → edit. Каждый вариант — отдельный результат; если не запустился, тоже запишите."),
      h("nav", { "aria-label": "Шаги стенда", class: "row" }, order.map(([id, l]) => h("a", { class: "btn small", href: "#bench", onclick: e => { e.preventDefault(); document.getElementById("step-" + id).scrollIntoView({ behavior: "smooth" }); } }, l))),
      header(), prep(), textCheck(), stress(), asr(), clean(), tts(), edit(), paid());
  }

  KP.section("bench", { render });
})();
