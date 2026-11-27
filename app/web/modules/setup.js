/* Раздел «Установка»: компоненты из app/setup/components.json, доставка выключенных при установке. */
(() => {
  "use strict";
  const { h, api, run, toast, confirmBox } = KP;
  const ST = { ok: "установлено", already: "уже было", error: "ошибка", cancelled: "отменено", skipped: "пропущено" };

  async function render(main) {
    const listBox = h("div", {}, h("p", { class: "muted" }, "Проверяю, что установлено…"));
    const box = h("div", { "aria-live": "polite" });
    main.append(
      h("h1", {}, "Установка"),
      h("p", {}, "Компоненты ставятся в папку программы" + (KP.meta.installed ? " (data\\venv). " : " (окружения .venv-*). "),
        "Нужен интернет. Модели скачиваются позже, при первом запуске теста."),
      h("section", { class: "card", "aria-labelledby": "h-comp" }, h("h2", { id: "h-comp" }, "Компоненты"), listBox, box));
    await load(listBox, box);
  }

  async function install(ids, names, size, listBox, box) {
    const ok = await confirmBox("Установить?", [`Будет установлено: ${names}.`, size ? `Объём скачивания ${size} (примерно).` : "",
      "Это может занять от минуты до получаса. Отменить можно кнопкой «Остановить»."].filter(Boolean));
    if (!ok) return;
    const j = await run("setup.install", { components: ids }, box);
    if (j && j.state === "done") toast("Установлено");
    await load(listBox, box);
  }

  async function load(listBox, box) {
    let d;
    try { d = await api("/api/setup/components"); } catch (e) { listBox.replaceChildren(h("div", { class: "errbox" }, e.message)); return; }
    const rows = d.components.map(c => h("tr", {},
      h("td", {}, h("b", {}, c.name), h("div", { class: "muted small" }, c.description)),
      h("td", { class: "small" }, c.size || ""),
      h("td", {}, c.installed ? h("span", { class: "badge ok" }, "установлено")
        : !c.available ? h("span", { class: "reason" }, c.reason)
        : KP.h("button", { class: "btn small", type: "button", onclick: () => install([c.id], c.name, c.size, listBox, box) }, "Доставить"))));
    const pending = (d.pending || []).filter(id => d.components.some(c => c.id === id && !c.installed && c.available));
    const pendBox = pending.length ? h("div", { class: "card" },
      h("p", {}, "При установке программы выбраны, но ещё не поставлены: ",
        h("b", {}, pending.map(id => d.components.find(c => c.id === id).name).join(", "))),
      h("button", { class: "btn primary", type: "button", onclick: () => install(pending, "выбранные компоненты", "", listBox, box) }, "Установить выбранные")) : null;
    const last = d.last && d.last.results ? h("details", {}, h("summary", {}, `Последняя установка: ${d.last.date}`),
      h("ul", {}, d.last.results.map(r => h("li", {}, `${r.name} — ${ST[r.status] || r.status}${r.error ? ": " + r.error : ""}`)))) : null;
    listBox.replaceChildren(...[pendBox,
      h("div", { class: "scroll" }, h("table", { class: "t" },
        h("thead", {}, h("tr", {}, h("th", {}, "Компонент"), h("th", {}, "Объём"), h("th", {}, ""))), h("tbody", {}, rows))),
      last].filter(Boolean));
  }

  KP.section("setup", { render });
})();
