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
    tab.focus();
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
