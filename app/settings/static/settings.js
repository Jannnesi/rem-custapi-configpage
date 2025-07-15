
(() => {
  if (window.extraColumnsSetup) return;      // ✅ already initialised
  window.extraColumnsSetup = true;           // 🔒 set guard
  const container = document.getElementById("emailContainer");
  const tmpl      = document.getElementById("emailTemplate").innerHTML;
  const addBtn    = document.getElementById("addEmailBtn");
  if (!container || !tmpl || !addBtn) return;

  // start at the number of rows WTForms rendered
  let index = container.querySelectorAll(".email-group").length;

  function wire(group) {
    group.querySelector(".removeEmailBtn")
         .addEventListener("click", () => group.remove());
  }

  function addRow() {
    const html   = tmpl.replace(/__index__/g, index);
    const holder = document.createElement("div");
    holder.innerHTML = html;
    const group  = holder.firstElementChild;
    wire(group);
    container.appendChild(group);
    index += 1;
  }

  // wire existing rows
  container.querySelectorAll(".email-group").forEach(wire);
  addBtn.addEventListener("click", addRow);
})();
