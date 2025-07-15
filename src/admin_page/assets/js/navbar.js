document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navToggle');
  const nav    = document.getElementById('navLinks');

  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    nav.classList.toggle('open');
  });

  /* optional: close menu on link click (mobile) */
  nav.addEventListener('click', e => {
    if (e.target.tagName === 'A' && nav.classList.contains('open')) {
      toggle.click();
    }
  });
});
