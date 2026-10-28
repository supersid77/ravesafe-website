// Audio players: play/pause button, progress bar and time
(function () {
  function fmt(s) {
    if (!isFinite(s)) return '0:00';
    var m = Math.floor(s / 60), r = Math.floor(s % 60);
    return m + ':' + (r < 10 ? '0' : '') + r;
  }
  document.querySelectorAll('[data-audio]').forEach(function (box) {
    var audio = box.querySelector('audio');
    var btn = box.querySelector('.audio__play');
    var fill = box.querySelector('.audio__fill');
    var time = box.querySelector('.audio__time');
    var iconPlay = box.querySelector('.audio__icon-play');
    var iconPause = box.querySelector('.audio__icon-pause');
    function sync() {
      var playing = !audio.paused;
      iconPlay.hidden = playing;
      iconPause.hidden = !playing;
      btn.setAttribute('aria-label', playing ? btn.dataset.labelPause : btn.dataset.labelPlay);
    }
    btn.addEventListener('click', function () {
      if (audio.paused) {
        var p = audio.play();
        if (p && p.catch) p.catch(function () { time.textContent = 'Could not play. Try again.'; });
      } else {
        audio.pause();
      }
    });
    audio.addEventListener('play', sync);
    audio.addEventListener('pause', sync);
    audio.addEventListener('ended', function () { audio.currentTime = 0; sync(); });
    audio.addEventListener('timeupdate', function () {
      var d = audio.duration || 0;
      fill.style.width = d ? (audio.currentTime / d * 100) + '%' : '0';
      time.textContent = fmt(audio.currentTime) + ' / ' + fmt(d);
    });
  });
})();

// Festival Prep checklist progress
(function () {
  var box = document.querySelector('[data-checklist]');
  if (!box) return;
  var boxes = box.querySelectorAll('input[type="checkbox"]');
  var bar = box.querySelector('.progress__bar');
  var fill = box.querySelector('.progress__fill');
  var text = box.querySelector('.progress__text');
  function sync() {
    var done = 0;
    boxes.forEach(function (b) { if (b.checked) done++; });
    fill.style.width = (done / boxes.length * 100) + '%';
    bar.setAttribute('aria-valuenow', String(done));
    text.textContent = done === boxes.length ? 'All done. You are festival ready.' : done + ' of ' + boxes.length + ' done';
  }
  boxes.forEach(function (b) { b.addEventListener('change', sync); });
  sync();
})();

// RaveSafe ID lock screen maker (draws on a canvas, nothing leaves the phone)
(function () {
  var form = document.getElementById('id-form');
  var canvas = document.getElementById('id-canvas');
  if (!form || !canvas) return;
  var ctx = canvas.getContext('2d');
  var status = document.getElementById('id-status');
  var W = 1080, H = 1920, PAD = 96;
  var logo = new Image();
  var brand = document.querySelector('.brand__logo');
  if (brand) { logo.src = brand.currentSrc || brand.src; }
  var fields = ['festival', 'date', 'meet', 'backup', 'contact', 'medical'];

  function val(id) { return (document.getElementById('id-' + id).value || '').trim(); }

  function wrap(text, x, y, maxW, lineH, maxLines) {
    var words = text.split(/\s+/), line = '', lines = [];
    words.forEach(function (w) {
      var test = line ? line + ' ' + w : w;
      if (ctx.measureText(test).width > maxW && line) { lines.push(line); line = w; } else { line = test; }
    });
    if (line) lines.push(line);
    lines = lines.slice(0, maxLines);
    lines.forEach(function (l, i) { ctx.fillText(l, x, y + i * lineH); });
    return y + lines.length * lineH;
  }

  function draw() {
    var bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, '#0C141E'); bg.addColorStop(1, '#070B12');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    var glow = ctx.createRadialGradient(W / 2, 640, 40, W / 2, 640, 560);
    glow.addColorStop(0, 'rgba(184,245,50,0.22)'); glow.addColorStop(1, 'rgba(184,245,50,0)');
    ctx.fillStyle = glow; ctx.fillRect(0, 0, W, 1200);

    // Logo, kept below the lock screen clock
    var y = 760;
    if (logo.complete && logo.naturalWidth) {
      ctx.save(); ctx.beginPath(); ctx.arc(W / 2, y - 100, 90, 0, Math.PI * 2); ctx.clip();
      ctx.drawImage(logo, W / 2 - 90, y - 190, 180, 180); ctx.restore();
    }
    ctx.textAlign = 'center'; ctx.fillStyle = '#B8F532';
    ctx.font = '700 30px Inter, system-ui, sans-serif';
    ctx.fillText('R A V E S A F E   I D', W / 2, y + 40);

    ctx.textAlign = 'left';
    y += 160;
    ctx.fillStyle = '#F4F7FB'; ctx.font = '86px Anton, Impact, sans-serif';
    y = wrap((val('festival') || 'Festival weekend').toUpperCase(), PAD, y, W - PAD * 2, 92, 2);
    if (val('date')) { ctx.fillStyle = '#A9B4C2'; ctx.font = '500 36px Inter, system-ui, sans-serif'; y = wrap(val('date'), PAD, y + 4, W - PAD * 2, 46, 1); }

    var rows = [['MEETING POINT', val('meet'), 48], ['BACKUP POINT', val('backup'), 42], ['EMERGENCY CONTACT', val('contact'), 44], ['MEDICAL INFO', val('medical'), 36]];
    y += 36;
    rows.forEach(function (r) {
      ctx.fillStyle = '#B8F532'; ctx.font = '800 26px Inter, system-ui, sans-serif';
      ctx.fillText(r[0], PAD, y); y += r[2] + 6;
      ctx.fillStyle = '#F4F7FB'; ctx.font = '700 ' + r[2] + 'px Inter, system-ui, sans-serif';
      y = wrap(r[1] || '-', PAD, y, W - PAD * 2, r[2] * 1.25, r[0] === 'MEDICAL INFO' ? 3 : 2) + 26;
    });

    // Footer box
    var fy = H - 300;
    ctx.fillStyle = '#E0157A';
    ctx.beginPath(); if (ctx.roundRect) { ctx.roundRect(PAD - 24, fy, W - (PAD - 24) * 2, 210, 28); } else { ctx.rect(PAD - 24, fy, W - (PAD - 24) * 2, 210); } ctx.fill();
    ctx.fillStyle = '#FFFFFF'; ctx.font = '700 34px Inter, system-ui, sans-serif';
    wrap('If this phone is found, please call my emergency contact. If I seem unwell, take me to welfare or medical straight away.', PAD, fy + 62, W - PAD * 2, 46, 3);
  }

  fields.forEach(function (f) { document.getElementById('id-' + f).addEventListener('input', draw); });
  logo.addEventListener('load', draw);
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(draw); }
  draw();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    draw();
    try {
      canvas.toBlob(function (blob) {
        if (!blob) { status.textContent = 'Could not make the image. Try again.'; return; }
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url; a.download = 'ravesafe-id-lockscreen.png';
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
        status.textContent = 'Saved. Now set it as your lock screen.';
      }, 'image/png');
    } catch (err) {
      status.textContent = 'Could not make the image. Try again.';
    }
  });
})();

// Open a closed section when someone jumps to it (substance chips, shared links)
(function () {
  function openTarget() {
    if (!location.hash) return;
    var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el && el.tagName === 'DETAILS') el.open = true;
  }
  window.addEventListener('hashchange', openTarget);
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if (el && el.tagName === 'DETAILS') el.open = true;
  });
  openTarget();
})();

// Video: only loads YouTube (privacy-enhanced mode) when someone taps play
(function () {
  document.querySelectorAll('[data-youtube]').forEach(function (box) {
    var btn = box.querySelector('.video__start');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + box.dataset.youtube + '?autoplay=1&rel=0&playsinline=1';
      f.title = box.dataset.title || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      box.innerHTML = '';
      box.appendChild(f);
      f.focus();
    });
  });
})();

// Heads Up: hide testing-service headlines if they haven't updated for 48 hours (SOP 9a point 7)
(function () {
  var box = document.querySelector('[data-feed-checked]');
  if (!box) return;
  var checked = Date.parse(box.dataset.feedChecked);
  var maxMs = (parseFloat(box.dataset.feedMaxHours) || 48) * 3600000;
  if (isNaN(checked) || Date.now() - checked > maxMs) {
    box.querySelector('.hu-feed').hidden = true;
    box.querySelector('.hu-feed__stale').hidden = false;
  }
})();

// Share button: phone share sheet, or copy the link
(function () {
  document.querySelectorAll('[data-share]').forEach(function (btn) {
    var label = btn.textContent;
    btn.addEventListener('click', function () {
      var url = location.href.split('#')[0];
      if (navigator.share) {
        navigator.share({ title: document.title, url: url }).catch(function () {});
        return;
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          btn.textContent = 'Link copied';
          setTimeout(function () { btn.textContent = label; }, 1500);
        }).catch(function () { btn.textContent = url; });
      }
    });
  });
})();

// Mobile menu toggle
(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (!btn || !nav) return;
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
      btn.focus();
    }
  });
})();

/* ---------- Forms: send to Web3Forms, then show our thank-you page ---------- */
document.querySelectorAll('form[data-web3form]').forEach(function (form) {
  var status = form.querySelector('.form__status');
  var btn = form.querySelector('button[type="submit"]');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var label = btn.textContent;
    btn.disabled = true; btn.textContent = 'Sending...';
    if (status) status.textContent = '';
    fetch(form.action, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data && data.success) { window.location.href = '/thank-you/'; return; }
        throw new Error((data && data.message) || 'failed');
      })
      .catch(function () {
        btn.disabled = false; btn.textContent = label;
        if (status) status.innerHTML = 'Sorry, that didn\'t send. Please try again, or email <a href="mailto:miss.k@ravesafecommunity.com">miss.k@ravesafecommunity.com</a>.';
      });
  });
});
