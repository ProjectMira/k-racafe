// Phone navigation — the toggle shows the links under the sticky header.
(function () {
  const header = document.querySelector('.nav');
  const toggle = header && header.querySelector('.nav-toggle');
  if (!toggle) return;

  function setOpen(open) {
    header.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
  }

  toggle.addEventListener('click', () => setOpen(!header.classList.contains('open')));

  // Close after following a link, on Escape, or on a tap anywhere else.
  header.querySelector('nav').addEventListener('click', (e) => {
    if (e.target.closest('a')) setOpen(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || !header.classList.contains('open')) return;
    setOpen(false);
    toggle.focus();
  });
  document.addEventListener('click', (e) => {
    if (!header.contains(e.target)) setOpen(false);
  });
})();

// Menu category tabs — keyboard accessible per WAI-ARIA tabs pattern.
(function () {
  const tablist = document.querySelector('.tabs');
  if (!tablist) return;

  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));

  function select(tab) {
    tabs.forEach((t) => {
      const selected = t === tab;
      t.setAttribute('aria-selected', String(selected));
      document.getElementById(t.getAttribute('aria-controls')).hidden = !selected;
    });
    tab.focus({ preventScroll: true });
    // On phones the tabs scroll sideways; bring a half-hidden one fully in.
    tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }

  tablist.addEventListener('click', (e) => {
    const tab = e.target.closest('[role="tab"]');
    if (tab) select(tab);
  });

  tablist.addEventListener('keydown', (e) => {
    const i = tabs.indexOf(document.activeElement);
    if (i === -1) return;
    const keys = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 };
    if (!(e.key in keys)) return;
    e.preventDefault();
    select(tabs[(keys[e.key] + tabs.length) % tabs.length]);
  });
})();
