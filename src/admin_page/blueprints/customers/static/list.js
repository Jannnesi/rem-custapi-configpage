document.addEventListener("DOMContentLoaded", () => {
  /* ─── 1. “Create customer” button ─────────────────────────────── */
  const createCustomerBtn = document.getElementById("createCustomerBtn");
  createCustomerBtn?.addEventListener("click", e => {
    e.preventDefault();
    window.location.href = "/customers/create";
  });

  /* ─── 2. Enabled/disabled slider ──────────────────────────────── */
  const CSRF = document.querySelector('input[name="csrf_token"]')?.value || "";
    if (!CSRF) {
        console.warn("CSRF token not found! Cannot toggle enabled state.");
        return;
    }
  document.querySelectorAll(".enabled-switch").forEach(cb => {
    cb.addEventListener("change", async ev => {
      const el      = ev.currentTarget;
      const id      = el.dataset.name;          // set with data-name="{{ cust.id }}"
      const enabled = el.checked;
      try {
        const res = await fetch(`/customers/${id}/enabled`, {
          method : "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken" : CSRF               // ok if CSRFProtect is enabled
          },
          body   : JSON.stringify({ enabled })
        });
        if (!res.ok) throw new Error(await res.text());
        console.log("Toggle successful:", res.ok);
      } catch (err) {
        console.error("Toggle failed:", err);
        el.checked = !enabled;                 // rollback UI state
        alert("Päivitys epäonnistui – yritä uudelleen.");
      }
    });
  });
});