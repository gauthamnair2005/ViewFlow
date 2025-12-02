// ViewFlow Custom Player: supports local HTML5 video and YouTube iframe via IFrame API.
document.addEventListener('DOMContentLoaded', function () {
  var container = document.getElementById('vf-player');
  if (!container) return;

  var mediaWrap = document.getElementById('vf-media');
  var playBtn = document.getElementById('vf-play');
  var progress = document.getElementById('vf-progress');
  var progressFilled = document.getElementById('vf-progress-filled');
  var progressTooltip = document.getElementById('vf-progress-tooltip');
  var timeDisplay = document.getElementById('vf-time');
  var volumeEl = document.getElementById('vf-volume');
  var fullscreenBtn = document.getElementById('vf-fullscreen');
  var theatreBtn = document.getElementById('vf-theatre');
  var muteBtn = document.getElementById('vf-mute');
  var speedBtn = document.getElementById('vf-speed');
  var bigPlay = document.getElementById('vf-bigplay');
  var overlay = document.getElementById('suggestions-overlay');
  var playNextBtn = document.getElementById('vjs-play-next');
  var ambientCanvas = document.getElementById('ambient-canvas');
  var ambientCtx = ambientCanvas ? ambientCanvas.getContext('2d') : null;
  var internalCanvas = document.getElementById('internal-ambient-canvas');
  var internalCtx = internalCanvas ? internalCanvas.getContext('2d') : null;

  var videoSrc = container.getAttribute('data-video-src') || '';
  var youtube = container.getAttribute('data-youtube') || '';

  /**
   * Check that the provided URL is a safe video URL.
   * Only allows https/http URLs, and optionally relative/local sources with safe file extensions.
   * Rejects javascript:, data:, file:, or other dangerous schemes.
   */
  var isYouTube = youtube && youtube.trim() !== '';
  var html5video = null;
  var ytPlayer = null;
  var ytReady = false;

  // Only allow safe video URLs (http, https, relative, with common video extensions)
  function isSafeVideoUrl(url) {
    if (!url) return false;
    // Allow only http(s) or relative URLs, ending in common video extensions
    try {
      var allowedExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.m4v', '.ogv', '.avi', '.mkv'];
      var urlObj = new URL(url, window.location.origin);
      if (
        (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') &&
        allowedExtensions.some(function(ext) { return urlObj.pathname.toLowerCase().endsWith(ext); })
      ) {
        return true;
      }
      // For strictly relative URLs (without protocol, begins with / or just filename)
      if (
        !/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(url) && // does not begin with protocol
        allowedExtensions.some(function(ext) { return url.toLowerCase().endsWith(ext); })
      ) {
        return true;
      }
    } catch (e) {}
    return false;
  }
  var progressTimer = null;
  var controlsHideTimer = null;

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds === undefined) return '0:00';
    var h = Math.floor(seconds / 3600);
    var m = Math.floor((seconds / 60) % 60);
    var s = Math.floor(seconds % 60);
    if (h > 0) {
      return h + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
    }
    return m + ':' + (s < 10 ? '0' + s : s);
  }

  function showOverlay() { if (overlay) overlay.style.display = 'flex'; }
  function hideOverlay() { if (overlay) overlay.style.display = 'none'; }
  function showBigPlay() { if (!bigPlay) return; bigPlay.classList.remove('hidden'); }
  function hideBigPlay() { if (!bigPlay) return; bigPlay.classList.add('hidden'); }
  function showReplayBtn() { 
    if (!bigPlay) return; 
    bigPlay.classList.remove('hidden'); 
    bigPlay.classList.add('replay-btn');
    bigPlay.innerHTML = '<svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>'; 
  }
  function hideReplayBtn() { 
    if (!bigPlay) return; 
    bigPlay.classList.remove('replay-btn');
    bigPlay.innerHTML = '<svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'; 
  }

  // HTML5 video flow
  function initHTML5(src) {
    if (!isSafeVideoUrl(src)) {
      console.error('Unsafe video URL blocked');
      return;
    }
    html5video = document.createElement('video');
    // src has been validated by isSafeVideoUrl before being passed here.
    html5video.src = src;
    html5video.setAttribute('playsinline', '');
    html5video.preload = 'metadata';
    html5video.style.width = '100%';
    html5video.style.maxHeight = '70vh';
    html5video.style.borderRadius = '12px';
    mediaWrap.innerHTML = '';
    mediaWrap.appendChild(html5video);

    html5video.addEventListener('loadedmetadata', function () {
      updateTime();
      // show big play if video hasn't started
      try { if (html5video.currentTime < 0.1 && html5video.paused) showBigPlay(); else hideBigPlay(); } catch(e){}
      // Initial ambient update
      if (ambientCtx) setTimeout(() => ambientCtx.drawImage(html5video, 0, 0, ambientCanvas.width, ambientCanvas.height), 500);
      if (internalCtx) setTimeout(() => internalCtx.drawImage(html5video, 0, 0, internalCanvas.width, internalCanvas.height), 500);
    });

    html5video.addEventListener('seeked', function() {
        if (ambientCtx) ambientCtx.drawImage(html5video, 0, 0, ambientCanvas.width, ambientCanvas.height);
        if (internalCtx) internalCtx.drawImage(html5video, 0, 0, internalCanvas.width, internalCanvas.height);
    });

    html5video.addEventListener('timeupdate', function () {
      var pct = (html5video.currentTime / html5video.duration) || 0;
      progressFilled.style.width = (pct * 100) + '%';
      updateTime();
    });

    html5video.addEventListener('play', function () { 
      hideOverlay(); 
      hideBigPlay(); 
      playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>'; 
      hideReplayBtn(); 
      startProgressTimer(); 
      container.classList.remove('paused');
      startAmbientLoop();
    });
    html5video.addEventListener('pause', function () { 
      playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'; 
      stopProgressTimer(); 
      container.classList.add('paused');
    });
    html5video.addEventListener('ended', function () { 
      showOverlay(); 
      showReplayBtn(); 
      playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>'; 
      stopProgressTimer(); 
      container.classList.add('paused');
    });
    playBtn.addEventListener('click', function () { 
      if (html5video.ended) {
        html5video.currentTime = 0;
        html5video.play();
        playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        hideReplayBtn();
        hideOverlay();
      } else {
        togglePlay();
      }
    });

    progress.addEventListener('click', function (e) {
      var rect = progress.getBoundingClientRect();
      var clickX = e.clientX - rect.left;
      var pct = clickX / rect.width;
      html5video.currentTime = pct * html5video.duration;
    });

    progress.addEventListener('mousemove', function (e) {
      if (!progressTooltip) return;
      var rect = progress.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var pct = Math.max(0, Math.min(1, x / rect.width));
      var t = (html5video.duration || 0) * pct;
      progressTooltip.style.display = 'block';
      progressTooltip.textContent = formatTime(t);
      progressTooltip.style.left = (pct * 100) + '%';
    });

    progress.addEventListener('mouseleave', function () { if (progressTooltip) progressTooltip.style.display = 'none'; });

    volumeEl.addEventListener('input', function () { html5video.volume = parseFloat(volumeEl.value); updateMuteIcon(); });
    if (muteBtn) muteBtn.addEventListener('click', function () { toggleMute(); });
    if (speedBtn) speedBtn.addEventListener('click', function () { cycleSpeed(); });
    if (bigPlay) bigPlay.addEventListener('click', function () { 
      if (html5video.ended) {
        html5video.currentTime = 0;
        html5video.play();
        hideReplayBtn();
      } else if (html5video.paused) { 
        html5video.play(); 
      } else { 
        html5video.pause(); 
      } 
    });

    // Initialize ambient light canvas size
    if (ambientCanvas) {
        ambientCanvas.width = 160;
        ambientCanvas.height = 90;
    }
    if (internalCanvas) {
        internalCanvas.width = 160;
        internalCanvas.height = 90;
    }

    function startAmbientLoop() {
        if ((!ambientCtx && !internalCtx) || !html5video) return;
        
        function loop() {
            if (html5video.paused || html5video.ended) return;
            if (ambientCtx) ambientCtx.drawImage(html5video, 0, 0, ambientCanvas.width, ambientCanvas.height);
            if (internalCtx) internalCtx.drawImage(html5video, 0, 0, internalCanvas.width, internalCanvas.height);
            requestAnimationFrame(loop);
        }
        loop();
    }
  }

  function updateTime() {
    var cur = 0, dur = 0;
    if (html5video) { cur = html5video.currentTime; dur = html5video.duration || 0; }
    else if (ytPlayer && ytReady) { cur = ytPlayer.getCurrentTime(); dur = ytPlayer.getDuration() || 0; }
    timeDisplay.textContent = formatTime(cur) + ' / ' + formatTime(dur);
  }

  function startProgressTimer() {
    if (progressTimer) return;
    progressTimer = setInterval(function () { updateTime(); updateYTProgress(); }, 250);
  }
  function stopProgressTimer() { if (progressTimer) { clearInterval(progressTimer); progressTimer = null; } }

  function updateYTProgress() {
    if (ytPlayer && ytReady) {
      try {
        var cur = ytPlayer.getCurrentTime();
        var dur = ytPlayer.getDuration() || 0;
        var pct = dur ? (cur / dur) : 0;
        progressFilled.style.width = (pct * 100) + '%';
      } catch (e) {}
    }
  }

  // YouTube flow
  function initYouTube(yurl) {
    // create iframe container
    mediaWrap.innerHTML = '<div id="vf-yt"></div>';

    function createPlayer() {
      ytPlayer = new YT.Player('vf-yt', {
        videoId: extractYouTubeID(yurl),
        playerVars: { rel: 0, modestbranding: 1 },
        events: {
          onReady: function (e) { ytReady = true; volumeEl.value = (e.target.getVolume() / 100) || 1; updateTime(); },
          onStateChange: function (e) {
            if (e.data === YT.PlayerState.PLAYING) { playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>'; hideOverlay(); hideBigPlay(); hideReplayBtn(); startProgressTimer(); }
            else if (e.data === YT.PlayerState.PAUSED) { playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'; stopProgressTimer(); }
            else if (e.data === YT.PlayerState.ENDED) { playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>'; showOverlay(); showReplayBtn(); stopProgressTimer(); }
          }
        }
      });
    }

    if (window.YT && window.YT.Player) { createPlayer(); }
    else {
      // load API
      var tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
      window.onYouTubeIframeAPIReady = function () { createPlayer(); };
    }

    playBtn.addEventListener('click', function () {
      if (!ytReady) return;
      var state = ytPlayer.getPlayerState();
      if (state === YT.PlayerState.ENDED) {
        ytPlayer.seekTo(0);
        ytPlayer.playVideo();
        playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        hideReplayBtn();
        hideOverlay();
      } else if (state === YT.PlayerState.PAUSED || state === YT.PlayerState.CUED) {
        ytPlayer.playVideo();
      } else if (state === YT.PlayerState.PLAYING) {
        ytPlayer.pauseVideo();
      }
    });

    // volume/mute handling for YT
    if (muteBtn) muteBtn.addEventListener('click', function () { toggleMute(); });
    if (speedBtn) speedBtn.addEventListener('click', function () { cycleSpeed(); });

    if (bigPlay) bigPlay.addEventListener('click', function () { 
      if (ytReady) { 
        var st = ytPlayer.getPlayerState(); 
        if (st === YT.PlayerState.ENDED) {
          ytPlayer.seekTo(0);
          ytPlayer.playVideo();
          hideReplayBtn();
        } else if (st !== YT.PlayerState.PLAYING) {
          ytPlayer.playVideo();
        } else {
          ytPlayer.pauseVideo();
        }
      } 
    });

    progress.addEventListener('click', function (e) {
      if (!ytReady) return;
      var rect = progress.getBoundingClientRect();
      var clickX = e.clientX - rect.left;
      var pct = clickX / rect.width;
      var dur = ytPlayer.getDuration() || 0;
      ytPlayer.seekTo(pct * dur, true);
    });

    volumeEl.addEventListener('input', function () { if (ytReady) ytPlayer.setVolume(Math.round(parseFloat(volumeEl.value) * 100)); });
  }

  function extractYouTubeID(url) {
    if (!url) return '';
    var id = url.split('v=')[1];
    if (!id) {
      var parts = url.split('/'); id = parts[parts.length - 1];
    }
    if (!id) return url;
    // strip params
    var amp = id.indexOf('&'); if (amp !== -1) id = id.substring(0, amp);
    return id;
  }

  function togglePlay() {
    if (html5video) {
      if (html5video.paused) html5video.play(); else html5video.pause();
    } else if (ytPlayer && ytReady) {
      var st = ytPlayer.getPlayerState(); if (st === YT.PlayerState.PLAYING) ytPlayer.pauseVideo(); else ytPlayer.playVideo();
    }
  }

  function toggleMute() {
    if (html5video) { html5video.muted = !html5video.muted; volumeEl.value = html5video.muted ? 0 : html5video.volume; updateMuteIcon(); }
    else if (ytPlayer && ytReady) { var muted = ytPlayer.isMuted(); if (muted) { ytPlayer.unMute(); } else { ytPlayer.mute(); } updateMuteIcon(); }
  }

  function updateMuteIcon() {
    if (!muteBtn) return;
    var muted = false;
    if (html5video) muted = html5video.muted || html5video.volume === 0;
    else if (ytPlayer && ytReady) muted = ytPlayer.isMuted();
    muteBtn.innerHTML = muted ? '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73 4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>' : '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
  }

  var playbackRates = [0.5,1,1.5,2];
  function cycleSpeed() {
    var current = 1;
    try { if (html5video) current = html5video.playbackRate || 1; else if (ytPlayer && ytReady) current = ytPlayer.getPlaybackRate() || 1; } catch (e) {}
    var idx = playbackRates.indexOf(current); idx = (idx + 1) % playbackRates.length; var next = playbackRates[idx];
    if (html5video) html5video.playbackRate = next; else if (ytPlayer && ytReady) try { ytPlayer.setPlaybackRate(next); } catch(e) {}
    if (speedBtn) speedBtn.textContent = next + 'x';
  }

  // keyboard shortcuts and interactions
  document.addEventListener('keydown', function (e) {
    // ignore when typing in inputs
    var tag = document.activeElement && document.activeElement.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;
    if (e.code === 'Space' || e.key === 'k') { e.preventDefault(); togglePlay(); }
    if (e.key === 'f') { 
      e.preventDefault();
      if (document.fullscreenElement) document.exitFullscreen(); 
      else container.requestFullscreen(); 
    }
    if (e.key === 't') { 
      e.preventDefault();
      if (theatreBtn) theatreBtn.click(); 
    }
    if (e.key === 'm') { toggleMute(); }
    if (e.key === 'ArrowRight') { if (html5video) html5video.currentTime += 5; else if (ytPlayer && ytReady) ytPlayer.seekTo(ytPlayer.getCurrentTime() + 5, true); }
    if (e.key === 'ArrowLeft') { if (html5video) html5video.currentTime -= 5; else if (ytPlayer && ytReady) ytPlayer.seekTo(ytPlayer.getCurrentTime() - 5, true); }
    if (e.key === 'ArrowUp') { if (html5video) { html5video.volume = Math.min(1, html5video.volume + 0.05); volumeEl.value = html5video.volume; updateMuteIcon(); } }
    if (e.key === 'ArrowDown') { if (html5video) { html5video.volume = Math.max(0, html5video.volume - 0.05); volumeEl.value = html5video.volume; updateMuteIcon(); } }
  });

  // double click toggles fullscreen
  container.addEventListener('dblclick', function () { if (document.fullscreenElement) document.exitFullscreen(); else container.requestFullscreen(); });

  // initial mute icon / speed label
  updateMuteIcon(); if (speedBtn) speedBtn.textContent = '1x';

  // theatre mode
  var isTheatreMode = false;
  if (theatreBtn) {
    theatreBtn.addEventListener('click', function () {
      isTheatreMode = !isTheatreMode;
      if (isTheatreMode) {
        document.body.classList.add('theatre-mode');
        theatreBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M19 5H5c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 12H5V7h14v10z"/></svg>';
        theatreBtn.title = 'Default mode';
      } else {
        document.body.classList.remove('theatre-mode');
        theatreBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M19 6H5c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 10H5V8h14v8z"/></svg>';
        theatreBtn.title = 'Theatre mode';
      }
    });
  }

  // fullscreen
  fullscreenBtn.addEventListener('click', function () {
    if (!container) return;
    if (document.fullscreenElement) document.exitFullscreen(); 
    else container.requestFullscreen().catch(function(err) {
      console.log('Fullscreen error:', err);
    });
  });

  // update fullscreen icon on change
  document.addEventListener('fullscreenchange', function() {
    showControls();
    if (document.fullscreenElement) {
      container.classList.add('is-fullscreen');
      fullscreenBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/></svg>';
      fullscreenBtn.title = 'Exit fullscreen';
    } else {
      container.classList.remove('is-fullscreen');
      container.style.cursor = 'default';
      fullscreenBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>';
      fullscreenBtn.title = 'Fullscreen';
    }
  });

  // suggestions overlay handling
  if (playNextBtn) {
    playNextBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var first = document.querySelector('.vjs-suggestion[data-src]');
      if (first) {
        var src = first.getAttribute('data-src');
        
        // Strict whitelist: Only allow http(s) URLs (same origin) or simple relative filenames ending in allowed extensions.
        var isValidSrc = false;
        var allowedExtensions = ['.mp4', '.webm', '.ogg'];
        function hasAllowedExtension(s) {
          return allowedExtensions.some(function(ext) {
            return typeof s === 'string' && s.toLowerCase().endsWith(ext);
          });
        }
        try {
          var srcUrl = new URL(src, window.location.origin);
          // Only allow http(s) to *this* origin, extension must be allowed
          if (
            (srcUrl.protocol === "http:" || srcUrl.protocol === "https:") &&
            (srcUrl.origin === window.location.origin) &&
            hasAllowedExtension(srcUrl.pathname)
          ) {
            isValidSrc = true;
          }
        } catch (e) {
          // fallback: Only allow plain relative file names with allowed extension
          if (
            typeof src === 'string' &&
            /^[a-zA-Z0-9_\-./%]+$/.test(src) && // simple safe chars, no directory traversal
            !/^(\/\/|\/|\\)/.test(src) &&       // does not start as absolute
            !/^(data:|javascript:|vbscript:)/i.test(src.trim()) && // not dangerous schemes
            hasAllowedExtension(src)
          ) {
            isValidSrc = true;
          }
        }

        if (src && isValidSrc) {
          // switch to the new source (HTML5 only), with extra sanitization to prevent interpretation as dangerous URL
          if (html5video) { 
            var sanitizedSrc = "";
            try {
              // Try to use URL API to create an absolute URL from the source, restricted to http(s) and same origin
              var parsedSrc = new URL(src.trim(), window.location.origin);
              var allowedProtocols = ['http:', 'https:'];
              if (
                allowedProtocols.indexOf(parsedSrc.protocol) !== -1 &&
                parsedSrc.origin === window.location.origin
              ) {
                sanitizedSrc = parsedSrc.href;
              }
            } catch (e) {
              // fallback: only allow safe relative file names with allowed extensions (dots, alphanum, _, -, /, %)
              if (
                typeof src === 'string' &&
                /^[a-zA-Z0-9_\-./%]+$/.test(src) && // simple safe chars
                !/^(\/\/|\/|\\)/.test(src) &&       // does not start as absolute
                !/^(data:|javascript:|vbscript:)/i.test(src.trim())
              ) {
                sanitizedSrc = src.trim();
              }
            }
            if (sanitizedSrc) {
              html5video.src = sanitizedSrc; // assign only fully sanitized src
              html5video.play(); 
              hideOverlay(); 
              hideReplayBtn();
              playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
            }
          }
          else if (ytPlayer) { /* can't change YouTube iframe source safely here */ }
        }
      }
    });
  }

  var suggestions = document.querySelectorAll('.vjs-suggestion');
  suggestions.forEach(function (s) { s.addEventListener('click', function () { try { if (overlay) overlay.style.display = 'none'; } catch (e) {} }); });

  // initialize appropriate player
  if (isYouTube) {
    initYouTube(youtube || videoSrc);
  } else {
    if (isSafeVideoUrl(videoSrc)) {
      initHTML5(videoSrc);
    } else {
      // If unsafe, do not load; optionally log error or show message.
      console.warn('Blocked potentially unsafe video src:', videoSrc);
    }
  }

  // Auto-hide controls functionality
  function showControls() {
    container.classList.add('show-controls');
    container.style.cursor = 'default';
    if (controlsHideTimer) clearTimeout(controlsHideTimer);
    controlsHideTimer = setTimeout(function() {
      // Don't hide if hovering the control bar itself
      var controls = document.getElementById('vf-controls');
      if (controls && controls.matches(':hover')) return;

      container.classList.remove('show-controls');
      // Hide cursor in fullscreen
      if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
        container.style.cursor = 'none';
      }
    }, 3000);
  }

  function hideControls() {
    if (controlsHideTimer) clearTimeout(controlsHideTimer);
    container.classList.remove('show-controls');
  }

  container.addEventListener('mousemove', function() {
    showControls();
  });

  container.addEventListener('mouseleave', function() {
    hideControls();
  });

  // Show controls when video is paused
  if (html5video) {
    html5video.addEventListener('pause', function() {
      showControls();
    });
    html5video.addEventListener('play', function() {
      showControls();
    });
  }

  // Initial show
  showControls();

});
