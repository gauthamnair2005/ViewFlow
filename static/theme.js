(function(){
  function getStored() { try { return localStorage.getItem('viewflow_theme'); } catch (e) { return null; } }
  function store(v) { try { localStorage.setItem('viewflow_theme', v); } catch(e){} }

  var btn = document.getElementById('theme-toggle');
  var body = document.body;

  function applyTheme(t) {
    if (t === 'light') { body.classList.remove('theme-dark'); body.classList.add('theme-light'); if (btn) btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.79 1.42-1.41zM4 10.5H1v2h3v-2zm9-9.95h-2V3.5h2V.55zm7.45 3.91l-1.41-1.41-1.79 1.79 1.41 1.41 1.79-1.79zm-3.21 13.7l1.79 1.79 1.41-1.41-1.79-1.79-1.41 1.41zM20 10.5v2h3v-2h-3zm-8-5c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm-1 16.95h2V19.5h-2v2.95zm-7.45-3.91l1.41 1.41 1.79-1.8-1.41-1.41-1.79 1.8z"/></svg>'; }
    else { body.classList.remove('theme-light'); body.classList.add('theme-dark'); if (btn) btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/></svg>'; }
  }

  var stored = getStored();
  if (stored) applyTheme(stored);
  else {
    // respect system preference
    var prefers = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    applyTheme(prefers);
  }

  if (btn) btn.addEventListener('click', function(){
    var next = body.classList.contains('theme-light') ? 'dark' : 'light';
    applyTheme(next);
    store(next);
  });
})();
