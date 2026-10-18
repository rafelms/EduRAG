// Checklist de passos reais: <ol class="checklist" data-key="..."> com <li>.
// Cada item ganha uma caixa; o progresso fica salvo neste navegador.
(function () {
  const css = `
  ol.checklist { list-style: none; counter-reset: passo; padding: 0; }
  ol.checklist > li { counter-increment: passo; position: relative; padding: .6rem 0 .6rem 2.4rem; border-bottom: 1px solid var(--rule); }
  ol.checklist > li > input { position: absolute; left: 0; top: .85rem; width: 1.1rem; height: 1.1rem; accent-color: var(--ok); }
  ol.checklist > li::before { content: counter(passo); position: absolute; left: 1.45rem; top: .6rem; font-size: .75rem; color: var(--muted); }
  ol.checklist > li.done { color: var(--muted); }
  ol.checklist > li.done > strong { text-decoration: line-through; }`;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch { return []; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* sem armazenamento: segue sem salvar */ }
  }

  document.querySelectorAll("ol.checklist").forEach((list) => {
    const key = "checklist:" + (list.dataset.key || location.pathname);
    const done = new Set(load(key));
    list.querySelectorAll(":scope > li").forEach((li, i) => {
      const box = document.createElement("input");
      box.type = "checkbox";
      box.checked = done.has(i);
      box.setAttribute("aria-label", "Passo " + (i + 1) + " feito");
      li.classList.toggle("done", box.checked);
      box.addEventListener("change", () => {
        box.checked ? done.add(i) : done.delete(i);
        li.classList.toggle("done", box.checked);
        save(key, [...done]);
      });
      li.prepend(box);
    });
  });
})();
