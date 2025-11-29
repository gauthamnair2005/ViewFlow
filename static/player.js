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
  var muteBtn = document.getElementById('vf-mute');
  var speedBtn = document.getElementById('vf-speed');
  var bigPlay = document.getElementById('vf-bigplay');
  var overlay = document.getElementById('suggestions-overlay');
  var playNextBtn = document.getElementById('vjs-play-next');

  var videoSrc = container.getAttribute('data-video-src') || '';
  var youtube = container.getAttribute('data-youtube') || '';

  var isYouTube = youtube && youtube.trim() !== '';
  var html5video = null;
  var ytPlayer = null;
  var ytReady = false;
  var progressTimer = null;

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds === undefined) return '0:00';
    var s = Math.floor(seconds % 60);
    var m = Math.floor((seconds / 60) % 60);
    return m + ':' + (s < 10 ? '0' + s : s);
  }

  function showOverlay() { if (overlay) overlay.style.display = 'flex'; }
  function hideOverlay() { if (overlay) overlay.style.display = 'none'; }
  function showBigPlay() { if (!bigPlay) return; bigPlay.classList.remove('hidden'); }
  function hideBigPlay() { if (!bigPlay) return; bigPlay.classList.add('hidden'); }
  function showReplayBtn() { if (!bigPlay) return; bigPlay.classList.remove('hidden'); bigPlay.innerHTML = '<span style="font-size: 48px;">🔄</span>'; }
  function hideReplayBtn() { if (!bigPlay) return; bigPlay.innerHTML = '<span style="font-size: 34px;">▶</span>'; }

  // HTML5 video flow
  function initHTML5(src) {
    html5video = document.createElement('video');
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
    });

    html5video.addEventListener('timeupdate', function () {
      var pct = (html5video.currentTime / html5video.duration) || 0;
      progressFilled.style.width = (pct * 100) + '%';
      updateTime();
    });

    html5video.addEventListener('play', function () { hideOverlay(); hideBigPlay(); playBtn.textContent = '❚❚'; hideReplayBtn(); startProgressTimer(); });
    html5video.addEventListener('pause', function () { playBtn.textContent = '▶'; stopProgressTimer(); });
    html5video.addEventListener('ended', function () { showOverlay(); showReplayBtn(); playBtn.textContent = '🔄'; stopProgressTimer(); });
    playBtn.addEventListener('click', function () { 
      if (html5video.ended) {
        html5video.currentTime = 0;
        html5video.play();
        playBtn.textContent = '❚❚';
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
            if (e.data === YT.PlayerState.PLAYING) { playBtn.textContent = '❚❚'; hideOverlay(); hideBigPlay(); hideReplayBtn(); startProgressTimer(); }
            else if (e.data === YT.PlayerState.PAUSED) { playBtn.textContent = '▶'; stopProgressTimer(); }
            else if (e.data === YT.PlayerState.ENDED) { playBtn.textContent = '🔄'; showOverlay(); showReplayBtn(); stopProgressTimer(); }
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
        playBtn.textContent = '❚❚';
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
    muteBtn.textContent = muted ? '🔇' : '🔊';
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
    if (e.key === 'f') { if (document.fullscreenElement) document.exitFullscreen(); else container.requestFullscreen(); }
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

  // fullscreen
  fullscreenBtn.addEventListener('click', function () {
    if (!container) return;
    if (document.fullscreenElement) document.exitFullscreen(); else container.requestFullscreen();
  });

  // suggestions overlay handling
  if (playNextBtn) {
    playNextBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var first = document.querySelector('.vjs-suggestion[data-src]');
      if (first) {
        var src = first.getAttribute('data-src');
        if (src) {
          // switch to the new source (HTML5 only)
          if (html5video) { 
            html5video.src = src; 
            html5video.play(); 
            hideOverlay(); 
            hideReplayBtn();
            playBtn.textContent = '❚❚';
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
    initHTML5(videoSrc);
  }

});
