// Script for updating exclude column count in the customer form
document.addEventListener('DOMContentLoaded', () => {
  const list     = document.getElementById('excludeList');
  const countEl  = document.getElementById('excludeCount');
  const checkboxes = list.querySelectorAll('input[id="exclude_columns"]');

  function updateCount() {
    const n = list.querySelectorAll('input[id="exclude_columns"]:checked').length;
    countEl.textContent = `${n} selected`;
  }
  window.updateExcludeCount = updateCount;

  // listen for every check/uncheck
  checkboxes.forEach(cb => cb.addEventListener('change', updateCount));

  // set initial value (in case some are pre‑checked)
  updateCount();
});

(() => {
  if (window.extraColumnsSetup) return;      // ✅ already initialised
  window.extraColumnsSetup = true;           // 🔒 set guard
  /* ---------- DOM handles ---------- */
  const templateEl     = document.getElementById("extraColumnTemplate");
  const extraContainer = document.getElementById("extraColumnsContainer");
  const addBtn         = document.getElementById("addExtraColumnBtn");

  if (!templateEl || !extraContainer) return;   // nothing to do on pages
                                                // that don’t have the form

  /* ---------- helper: build & append one extra-column row ---------- */
  function makeExtraRow(key = "", info = { name: "", dtype: "" }) {
    const index = extraContainer.children.length;    // 0, 1, 2 …

    // 1. clone the <template> fragment
    const frag  = templateEl.content.cloneNode(true);
    const group = frag.querySelector(".extra-columns-group");

    // 2. rename the inputs so WTForms can bind them
    group.querySelector('[name="extra_key"]').name   = `extra_columns-${index}-key`;
    group.querySelector('[name="extra_name"]').name  = `extra_columns-${index}-name`;
    group.querySelector('[name="extra_dtype"]').name = `extra_columns-${index}-dtype`;

    // 3. set initial values (for Edit mode)
    group.querySelector(`[name="extra_columns-${index}-key"]`).value   = key;
    group.querySelector(`[name="extra_columns-${index}-name"]`).value  = info.name;
    group.querySelector(`[name="extra_columns-${index}-dtype"]`).value = info.dtype || "string";

    // 4. wire up the remove button
    group.querySelector(".removeColumnBtn")
         .addEventListener("click", () => group.remove());

    // 5. append into the DOM
    extraContainer.appendChild(frag);
  }

  /* ---------- click handler for “+ Lisää lisäsarake” ---------- */
  if (addBtn) {
    addBtn.addEventListener("click", () => makeExtraRow());
  }

})();

(() => {
  /* ---------- grab DOM ---------- */
  const action      = document.getElementById("actionInput")?.value;  // "Edit" | "Create"
  const customerEl  = document.getElementById("customerData");        // <script type=application/json>

  const form        = document.getElementById("configForm");
  if (!form) return;                        // no form on this page

  const fields = {
    id:   form.querySelector("#pk"),
    name: form.querySelector("#name"),
    konserni: form.querySelector("#konserni"),
    src_container: form.querySelector("#source_container"),
    dest_container: form.querySelector("#destination_container"),
    file_format: form.querySelector("#file_format"),
    file_encoding: form.querySelector("#file_encoding"),
    enabledSel: form.querySelector("#enabled"),
    extraContainer: document.getElementById("extraColumnsContainer"),
  };

  const templateEl   = document.getElementById("extraColumnTemplate");
  const makeExtraRow = (key = "", info = { name: "", dtype: "" }) => {
    const clone  = templateEl.content.cloneNode(true);
    const group  = clone.querySelector(".extra-columns-group");
    group.querySelector(".removeColumnBtn").addEventListener("click", () => group.remove());
    group.querySelector('input[name="extra_key"]').value    = key;
    group.querySelector('input[name="extra_name"]').value   = info.name;
    group.querySelector('select[name="extra_dtype"]').value = info.dtype || "string";
    return group;
  };

  /* ---------- helper: push customer data into the form ---------- */
  function fillForm(cust) {
    if (!cust) return console.error("Customer not found");

    document.getElementById("formTitle").textContent = `Muokkaa: ${cust.name.toUpperCase()}`;
    fields.id.value               = cust.id ?? "";
    fields.name.value             = cust.name ?? "";
    fields.konserni.value         = cust.konserni_csv ?? "";
    fields.src_container.value    = (cust.source_container ?? "").replace("/", "");
    fields.dest_container.value   = (cust.destination_container ?? "").replace("/", "");
    fields.file_format.value      = cust.file_format ?? "";
    fields.file_encoding.value    = cust.file_encoding ?? "";
    if (fields.enabledSel) fields.enabledSel.value = String(cust.enabled);

    // extra columns
    fields.extraContainer.innerHTML = "";
    if (cust.extra_columns) {
      for (const [k, info] of Object.entries(cust.extra_columns)) {
        fields.extraContainer.appendChild(makeExtraRow(k, info));
      }
    }
    console.log("Exclude columns:", cust.exclude_columns);
    // checkboxes for exclude columns
    document.querySelectorAll('input[id="exclude_columns"]').forEach(cb => {
      cb.checked = cust.exclude_columns?.includes(cb.value) ?? false;
    });

    window.updateExcludeCount?.();
  }

  /* ---------- 2. auto-fill when page loads in Edit mode ---------- */
  if (action === "Edit" && customerEl) {
    const cust = JSON.parse(customerEl.textContent);
    fillForm(cust);

    // Hook the delete button in edit mode
    if (!window.deleteBtnSetup) {
      window.deleteBtnSetup = true;

      const btn  = document.getElementById("deleteBtn");
      const pk   = document.getElementById("pk")?.value;
      const form = document.getElementById("deleteCustomerForm");
      if (btn && pk && form) {
        btn.addEventListener("click", () => {
          if (!confirm("Haluatko varmasti poistaa tämän asiakkaan?")) return;
          form.action = `/customers/${encodeURIComponent(pk)}/delete`;
          form.submit();
        });
      }
    }
  }
})();
