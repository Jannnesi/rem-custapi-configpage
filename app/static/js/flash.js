(() => {
  const AUTO_DISMISS_MS = 5_000;          // ⏱ 5 s timeout

  /* 1. Grab the container (if any) */
  const box = document.querySelector(".flash-container");
  if (!box) return;                       // no messages on this page

  /* 3. Activate each flash */
  box.querySelectorAll(".flash").forEach(flash => {
    /* a) add close button */
    const btn = document.createElement("button");
    btn.className = "close-btn";
    btn.setAttribute("aria-label", "Dismiss");
    btn.innerHTML = "&times;";
    btn.addEventListener("click", () => dismiss(flash));
    flash.appendChild(btn);

    /* b) slide-fade in on next frame */
    requestAnimationFrame(() => flash.classList.add("show"));

    /* c) auto-dismiss */
    const tid = setTimeout(() => dismiss(flash), AUTO_DISMISS_MS);
    /* stop countdown on hover */
    flash.addEventListener("mouseenter", () => clearTimeout(tid), {once:true});
  });

  /* 4. Dismiss helper */
  function dismiss(el) {
    el.classList.remove("show");                   // start fade-out
    el.addEventListener("transitionend", () => {
      el.remove();                                 // free up DOM
      /* optionally: collapse container when empty */
      if (!box.querySelector(".flash")) box.remove();
    }, {once:true});
  }
})();
