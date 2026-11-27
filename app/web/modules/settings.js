/* Раздел «Настройки»: тестировщик, ИИ-агент для шагов, где думает ИИ, внешние программы. */
(() => {
  "use strict";
  const { h, api, toast } = KP;

  async function render(main) {
    const s = await KP.reloadSettings();
    const tester = h("input", { type: "text", id: "set-tester", value: s.tester || "", pattern: "[a-z0-9\\-]{1,32}", autocomplete: "off", spellcheck: "false", "aria-describedby": "set-tester-hint" });
    const saveT = h("button", { class: "btn primary", type: "submit" }, "Сохранить");
    const tform = h("form", { class: "stack" },
      h("label", { class: "field", for: "set-tester" }, h("span", {}, "Имя тестировщика латиницей"), tester),
      h("p", { id: "set-tester-hint", class: "muted small" }, "Строчные латинские буквы, цифры и дефис, до 32 знаков: nikita, anna. Это имя попадает в имена файлов результатов."),
      h("div", { class: "row" }, saveT));
    tform.addEventListener("submit", async e => {
      e.preventDefault();
      const v = tester.value.trim().toLowerCase();
      if (!/^[a-z0-9-]{1,32}$/.test(v)) { toast("Имя: латиница, цифры, дефис — до 32 знаков", true); tester.focus(); return; }
      try { await api("/api/settings", { body: { tester: v } }); await KP.reloadSettings(); toast("Сохранено: " + v); }
      catch (err) { toast(err.message, true); }
    });

    const agentsBox = h("div", {}, h("p", { class: "muted" }, "Ищу агентов…"));
    const toolsBox = h("div");
    main.append(
      h("h1", {}, "Настройки"),
      h("section", { class: "card", "aria-labelledby": "h-tester" }, h("h2", { id: "h-tester" }, "Тестировщик"), tform),
      h("section", { class: "card", "aria-labelledby": "h-agent" }, h("h2", { id: "h-agent" }, "ИИ-агент"),
        h("p", {}, "Шаги, где думает ИИ (оценка текста по ru-text, монтаж), запускаются в фоне через выбранного агента. Агент работает в папке проекта и может менять файлы и выполнять команды в режиме монтажа."),
        agentsBox),
      h("section", { class: "card", "aria-labelledby": "h-tools" }, h("h2", { id: "h-tools" }, "Программы на компьютере"), toolsBox));
    loadAgents(agentsBox, false);
    KP.toolsTable(toolsBox);
  }

  async function loadAgents(box, refresh) {
    let d;
    try { d = await api("/api/agents" + (refresh ? "?refresh=1" : "")); } catch (e) { box.replaceChildren(h("div", { class: "errbox" }, e.message)); return; }
    const found = d.agents.filter(a => a.found);
    const again = h("button", { class: "btn", type: "button" }, "Проверить снова");
    again.addEventListener("click", () => loadAgents(box, true));
    const list = h("fieldset", {}, h("legend", {}, "Агент для фоновых шагов"),
      ...d.agents.map(a => h("label", { class: "check" },
        h("input", { type: "radio", name: "agent", value: a.id, checked: d.selected === a.id, disabled: !a.found }),
        h("span", {}, h("b", {}, a.name), " ", a.found ? h("span", { class: "badge ok" }, "найден") : h("span", { class: "badge" }, "не установлен"),
          a.found && a.version ? h("span", { class: "muted small" }, " " + a.version) : null,
          a.checked ? null : h("span", { class: "badge warn", title: "Флаги запуска в фоне не подтверждены документацией" }, " проверить"),
          " ", h("a", { href: a.docs, target: "_blank", rel: "noopener noreferrer" }, "документация")))));
    list.addEventListener("change", async e => {
      try { await api("/api/settings", { body: { agent: e.target.value } }); await KP.reloadSettings(); toast("Агент: " + e.target.value); }
      catch (err) { toast(err.message, true); }
    });
    box.replaceChildren(
      found.length ? null : h("div", { class: "errbox" }, "Ни одного агента не найдено. Можно работать без агента: для шагов с ИИ интерфейс покажет текст задачи с кнопкой «Скопировать» — вставьте его в агента вручную."),
      list, again);
  }

  KP.section("settings", { render });
})();
