// base_columns.js
(() => {
  if (window.extraColumnsSetup) return;      // ✅ already initialised
  window.extraColumnsSetup = true;           // 🔒 set guard
  const template   = document.getElementById("baseColumnTemplate");
  const container  = document.getElementById("baseColumnsContainer");
  const addBtn     = document.getElementById("addBaseColumnBtn");

  if (!template || !container) return;

  /* ---------- helpers ---------- */
  function onDrop(e, targetRow = null) {
    e.preventDefault();
    if (!dragSrc) return;

    const refRow =
      targetRow ||
      document.elementFromPoint(e.clientX, e.clientY)
              ?.closest(".base-columns-group");

    if (!refRow || refRow === dragSrc) return;

    const rows = [...container.children];
    const from = rows.indexOf(dragSrc);
    const to   = rows.indexOf(refRow);

    container.insertBefore(
      dragSrc,
      from < to ? refRow.nextSibling : refRow
    );
    renumberRows();
  }
  
  function renumberRows() {
    [...container.children].forEach((row, idx) => {
      /* ----------- order (hidden) ----------- */
      const orderInput =
        row.querySelector('[name$="-order"]') ||
        row.querySelector('[name="order"]');          // template default
      if (orderInput) {
        const v = idx + 1;
        orderInput.value = v;                         // property
        orderInput.setAttribute("value", v);          // attribute (for hidden)
        orderInput.name  = `columns-${idx}-order`;
      }

      /* helper: find element by suffixed OR plain name  */
      const sel = (plain) =>
        row.querySelector(`[name$="-${plain}"]`) ||
        row.querySelector(`[name="${plain}"]`);

      /* rename every field -------------------- */
      sel("key")     ?.setAttribute("name", `columns-${idx}-key`);
      sel("name")    ?.setAttribute("name", `columns-${idx}-name`);
      sel("dtype")   ?.setAttribute("name", `columns-${idx}-dtype`);
      sel("length")  ?.setAttribute("name", `columns-${idx}-length`);
      sel("decimals")?.setAttribute("name", `columns-${idx}-decimals`);
    });
  }


  function attachRowBehaviour(row) {
    row.querySelector('.removeColumnBtn')
      .addEventListener('click', () => { row.remove(); renumberRows(); });
    /* dtype toggle */
    const dtypeSel = row.querySelector('[name$="-dtype"], [name="dtype"]');
    const lenGrp   = row.querySelector(".length-group");
    const decGrp   = row.querySelector(".decimals-group");
    const lenInput = lenGrp?.querySelector("input");
    const decInput = decGrp?.querySelector("input");
    if (dtypeSel) {
      const toggle = () => {
        const val = dtypeSel.value;
        // show / hide groups
        if (lenGrp) lenGrp.style.visibility = val === "string" ? "visible" : "hidden";
        if (decGrp) decGrp.style.visibility = val === "float"  ? "visible" : "hidden";

        // add / remove required attribute
        lenInput?.toggleAttribute("required",  val === "string");
        decInput?.toggleAttribute("required",  val === "float");
      };
      dtypeSel.addEventListener("change", toggle);
      toggle();          // initial state
    }
    /* drag-and-drop */
    const handle = row.querySelector(".drag-handle");
    if (handle) {
      handle.addEventListener("mousedown", () => { row.draggable = true; });

      row.addEventListener("dragstart", e => {
        dragSrc = row;                               // ② set global
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", "");    // Firefox / Edge need some data
        row.classList.add("dragging");
      });

      row.addEventListener("dragover",  e => e.preventDefault());
      row.addEventListener("drop",      e => onDrop(e, row));  // ③ local drop
      row.addEventListener("dragend",   () => {
        row.classList.remove("dragging");
        row.draggable = false;
        dragSrc = null;                                // ④ reset
      });
    }
  }

  /* ───────── container-level drop (between rows) ─────────────────────── */
  container.addEventListener("dragover", e => e.preventDefault());
  container.addEventListener("drop",     onDrop);     // call shared helper

  function addRow() {
    const frag = template.content.cloneNode(true);
    const row  = frag.querySelector(".base-columns-group");

    // ensure hidden order input exists
    if (!row.querySelector('[name="order"]')) {
      const hidden = document.createElement("input");
      hidden.type  = "hidden";
      hidden.name  = "order";
      hidden.value = "";  // default value
      row.prepend(hidden);
    }

    container.appendChild(frag);   // 1️⃣ add to DOM first
    renumberRows();                // 2️⃣ give it its final names
    attachRowBehaviour(row);       // 3️⃣ now selectors will match
  }

  /* ---------- initial setup ---------- */
  container.querySelectorAll(".base-columns-group").forEach(attachRowBehaviour);
  renumberRows();
  addBtn?.addEventListener("click", addRow);
})();
