document.addEventListener('DOMContentLoaded', function(){
  function initShortsPlayer() {
    var sh = document.getElementById('vf-shorts-player');
    if (!sh) return;
    var vid = sh.querySelector('video');
    var src = sh.getAttribute('data-video-src');
    if (!vid || !src) return;
    vid.src = src;
    vid.muted = true;
    vid.autoplay = true;
    vid.loop = true;
    vid.preload = 'metadata';
    vid.style.objectFit = 'cover';
    vid.addEventListener('loadedmetadata', function(){
      var w = vid.videoWidth, h = vid.videoHeight, dur = vid.duration || 0;
      var ar = (w && h) ? (w/h) : 1;
      if (ar >= 1.6) { sh.style.width = '60%'; }
      else if (ar >= 1.0) { sh.style.width = '50%'; }
      else { sh.style.width = '40%'; }
      var d = document.createElement('div'); d.style.position='absolute'; d.style.top='10px'; d.style.right='10px'; d.style.color='white'; d.style.textShadow='0 1px 2px rgba(0,0,0,0.6)'; d.textContent = Math.round(dur) + 's'; sh.appendChild(d);
      try { vid.play(); } catch(e){}
    });
  }
  initShortsPlayer();
});