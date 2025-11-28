(function(){
  function getStored() { try { return localStorage.getItem('viewflow_theme'); } catch (e) { return null; } }
  function store(v) { try { localStorage.setItem('viewflow_theme', v); } catch(e){} }

  var btn = document.getElementById('theme-toggle');
  var body = document.body;

  function applyTheme(t) {
    if (t === 'light') { body.classList.remove('theme-dark'); body.classList.add('theme-light'); if (btn) btn.textContent = '☀️'; }
    else { body.classList.remove('theme-light'); body.classList.add('theme-dark'); if (btn) btn.textContent = '🌙'; }
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
