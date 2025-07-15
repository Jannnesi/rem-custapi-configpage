(function () {
  if (window.extraColumnsSetup) return;      // ✅ already initialised
  window.extraColumnsSetup = true;           // 🔒 set guard
  const form = document.getElementById('manualRunForm');
  const statusContainer = document.getElementById('statusContainer');
  if (!form || !statusContainer) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const selected = Array.from(form.querySelectorAll('input[name="customer"]:checked'))
      .map(cb => cb.value);
    if (!selected.length) return;
    statusContainer.innerHTML = '<p style="text-align:center;margin-top:10px;">Odota...</p>';
    if (btn) btn.disabled = true;
    try {
      // Make a post request to the server with the selected customer names
      const resp = await fetch(`http://localhost:7071/api/asiakasrajapinnat_manual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ names: selected })
      });
      const items = await resp.json();

      if (btn) btn.disabled = false;
      if (resp.status === 200) {
        const rows = items.map(item => {
          const cls = /ok|success/i.test(item.response) ? "status-ok" : "status-error";
          return `
            <tr>
              <td>${item.run}</td>
              <td>${item.customer}</td>
              <td class="${cls}">${item.response}</td>
            </tr>`;
        }).join("");

        const html =
          `<p></p>
          <table>
            <thead>
              <tr><th>Suoritus</th><th>Asiakas</th><th>Tila</th></tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>`;
        statusContainer.innerHTML = html;
      } else if (resp.status === 400) {
          statusContainer.innerHTML = '<p style="text-align:center;margin-top:10px;">' + items.error + '</p>';
      }
    } catch (err) {
      if (btn) btn.disabled = false;
      statusContainer.innerHTML = '<p style="text-align:center;margin-top:10px;">Virhe palveluun yhdistettäessä.</p>';
      console.error(err);
    }
  });
  const checkboxes = form.querySelectorAll("input[type=checkbox][name=customer]");
  const countLabel = document.getElementById("checkedCount");
  const toggleBtn  = document.getElementById("toggleAll");
  
  function updateCount() {
    const checked = [...checkboxes].filter(cb => cb.checked).length;
    countLabel.textContent = `${checked} / ${checkboxes.length}`;
    toggleBtn.textContent  = checked === checkboxes.length
                           ? "Poista valinnat"
                           : "Valitse kaikki";
  }
  
  checkboxes.forEach(cb => cb.addEventListener("change", updateCount));
  updateCount();
  
  toggleBtn.addEventListener("click", () => {
    // true  if we have at least one unchecked box
    const anyUnchecked = [...checkboxes].some(cb => !cb.checked);
    checkboxes.forEach(cb => {
      cb.checked = anyUnchecked;              // check-all or uncheck-all
      cb.dispatchEvent(new Event("change"));  // let other handlers react
    });
  
    updateCount();                            // refresh counter & button label
  });
})();

