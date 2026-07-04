/* ============================================================
   CULIVER GROUP — interactions (progressive enhancement)
   All content lives in index.html; this script only wires up
   behavior: language toggle, mobile menu, scroll progress /
   active-nav, number counters, scroll reveal, the interactive
   loop diagram, history timeline, news filter, and the form.
   ============================================================ */
(function () {
  'use strict';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ---------------------------------------------- LANGUAGE */
  function setupLang() {
    var btn = $('#langToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.body.getAttribute('data-lang') === 'ko' ? 'en' : 'ko';
      document.body.setAttribute('data-lang', next);
      document.documentElement.setAttribute('lang', next);
      btn.textContent = next === 'ko' ? 'EN' : 'KR';
    });
  }

  /* ---------------------------------------------- MOBILE MENU */
  function setupMenu() {
    var menu = $('#mobileMenu'), ham = $('#hamburger'), gnb = $('#gnb');
    if (!menu || !ham) return;
    function close() {
      menu.classList.remove('open');
      ham.textContent = '☰';
      if (gnb) gnb.classList.remove('menu-open');
      document.body.style.overflow = '';
    }
    ham.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      ham.textContent = open ? '✕' : '☰';
      if (gnb) gnb.classList.toggle('menu-open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    $all('a[href^="#"]', menu).forEach(function (a) { a.addEventListener('click', close); });
    window.matchMedia('(max-width: 900px)').addEventListener('change', function (e) {
      if (!e.matches) close();
    });
  }

  /* ---------------------------------------------- SCROLL: progress, nav, back-to-top */
  function setupScroll() {
    var progress = $('#progress'), gnb = $('#gnb'), toTop = $('#toTop'), menu = $('#mobileMenu');
    var secIds = ['top', 'business', 'cycle', 'about', 'history', 'esg', 'news', 'careers', 'contact'];
    var sections = secIds.map(function (id) { return document.getElementById(id); });
    var navLinks = $all('.nav-links a');
    var doc = document.documentElement;

    function onScroll() {
      var sc = window.scrollY;
      var max = (doc.scrollHeight - window.innerHeight) || 1;
      if (progress) progress.style.width = Math.min(100, Math.max(0, (sc / max) * 100)) + '%';
      if (gnb) gnb.classList.toggle('scrolled', sc > 40 && !(menu && menu.classList.contains('open')));
      if (toTop) toTop.classList.toggle('show', sc > 600);
      var active = 'top';
      for (var i = 0; i < sections.length; i++) {
        var e = sections[i];
        if (e && e.offsetTop - 140 <= sc) active = secIds[i];
      }
      navLinks.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('data-sec') === active);
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    if (toTop) toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------------------------------------------- REVEAL on scroll */
  function setupReveal() {
    var reveals = $all('.reveal');
    if (!('IntersectionObserver' in window)) {
      reveals.forEach(function (e) { e.classList.add('is-visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (e) { io.observe(e); });
  }

  /* ---------------------------------------------- NUMBER counters */
  function setupCounters() {
    var counters = $all('[data-count]');
    if (!counters.length) return;
    function run() {
      counters.forEach(function (elm) {
        var target = parseFloat(elm.getAttribute('data-count')) || 0;
        var raw = target >= 1000;
        var dur = 1400, t0 = null;
        function step(now) {
          if (t0 === null) t0 = now;
          var p = Math.min(1, (now - t0) / dur);
          var eased = 1 - Math.pow(1 - p, 3);
          var val = Math.round(target * eased);
          elm.textContent = raw ? String(val) : val.toLocaleString('en-US');
          if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }
    if (!('IntersectionObserver' in window)) { run(); return; }
    // reset to 0 only when JS will animate them into view
    counters.forEach(function (elm) { elm.textContent = '0'; });
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { run(); co.disconnect(); } });
    }, { threshold: 0.4 });
    co.observe(counters[0]);
  }

  /* ---------------------------------------------- CYCLE (interactive) */
  function setupCycle() {
    var nodes = $all('#ring .node');
    if (!nodes.length) return;
    var ringRole = $('#ringRole'), ringKo = $('#ringKo'), ringEn = $('#ringEn');
    var badge = $('#cycleBadge'), title = $('#cycleTitle'), dKo = $('#cycleDescKo'), dEn = $('#cycleDescEn');
    var dots = $all('#cycleDots span');

    function select(idx) {
      nodes.forEach(function (n, k) {
        var on = k === idx, color = n.getAttribute('data-color');
        n.classList.toggle('active', on);
        n.style.background = on ? color : '#FDFCFA';
        n.style.color = on ? '#F6F4EF' : '#0B1E2D';
        n.style.boxShadow = on ? '0 16px 34px -12px ' + color : '0 8px 20px -12px rgba(11,30,45,.35)';
      });
      var d = nodes[idx], c = d.getAttribute('data-color');
      if (ringRole) { ringRole.textContent = d.getAttribute('data-role'); ringRole.style.color = c; }
      if (ringKo) ringKo.textContent = d.getAttribute('data-name-ko');
      if (ringEn) ringEn.textContent = d.getAttribute('data-name-en');
      if (badge) { badge.textContent = d.getAttribute('data-no'); badge.style.background = c; }
      if (title) title.innerHTML = '<span class="t-ko">' + d.getAttribute('data-name-ko') + '</span><span class="t-en">' + d.getAttribute('data-name-en') + '</span> · <span style="color:' + c + '">' + d.getAttribute('data-role') + '</span>';
      if (dKo) dKo.textContent = d.getAttribute('data-dko');
      if (dEn) dEn.textContent = d.getAttribute('data-den');
      dots.forEach(function (dot, k) {
        var on = k === idx;
        dot.style.width = on ? '30px' : '8px';
        dot.style.background = on ? nodes[k].getAttribute('data-color') : 'rgba(11,30,45,.18)';
      });
    }
    nodes.forEach(function (n, i) {
      n.addEventListener('click', function () { select(i); });
      n.addEventListener('mouseenter', function () { select(i); });
    });
  }

  /* ---------------------------------------------- HISTORY (interactive) */
  function setupHistory() {
    var btns = $all('#histYears .hist-year');
    if (!btns.length) return;
    var big = $('#histBig'), title = $('#histTitle'), dKo = $('#histDescKo'), dEn = $('#histDescEn');
    function select(idx) {
      btns.forEach(function (b, k) {
        var on = k === idx, color = b.getAttribute('data-color');
        b.classList.toggle('active', on);
        b.style.background = on ? color : 'transparent';
        b.style.borderColor = on ? color : 'rgba(11,30,45,.2)';
        b.style.color = on ? '#F6F4EF' : 'rgba(11,30,45,.6)';
      });
      var y = btns[idx];
      if (big) { big.textContent = y.textContent; big.style.color = y.getAttribute('data-color'); }
      if (title) title.innerHTML = '<span class="t-ko">' + y.getAttribute('data-tko') + '</span><span class="t-en">' + y.getAttribute('data-ten') + '</span>';
      if (dKo) dKo.textContent = y.getAttribute('data-dko');
      if (dEn) dEn.textContent = y.getAttribute('data-den');
    }
    btns.forEach(function (b, i) { b.addEventListener('click', function () { select(i); }); });
  }

  /* ---------------------------------------------- NEWSROOM (filter) */
  function setupNews() {
    var cards = $all('#newsList .news-card');
    var btns = $all('#newsFilters .news-filter');
    if (!btns.length) return;
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-key');
        cards.forEach(function (c) {
          var show = key === 'all' || c.getAttribute('data-tag') === key;
          c.classList.toggle('hidden', !show);
        });
        btns.forEach(function (b) { b.classList.toggle('active', b === btn); });
      });
    });
  }

  /* ---------------------------------------------- CONTACT form */
  function setupForm() {
    var wrap = $('#formWrap'), form = $('#contactForm'), sent = $('#formSent'),
        reset = $('#formReset'), submit = $('.form-submit', form), errBox = $('#formError');
    if (!form) return;

    var submitHtml = submit ? submit.innerHTML : '';
    function setError(msg) {
      if (!errBox) return;
      if (msg) { errBox.textContent = msg; errBox.hidden = false; }
      else { errBox.textContent = ''; errBox.hidden = true; }
    }
    function setBusy(busy) {
      if (!submit) return;
      submit.disabled = busy;
      submit.innerHTML = busy
        ? '<span class="t-ko">보내는 중…</span><span class="t-en">Sending…</span>'
        : submitHtml;
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      setError('');
      var data = {
        name: form.name.value,
        company: form.company.value,
        type: form.type.value,
        message: form.message.value,
        _gotcha: form._gotcha ? form._gotcha.value : ''
      };
      var lang = document.body.getAttribute('data-lang');
      setBusy(true);
      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        return r.json().catch(function () { return { ok: r.ok }; });
      }).then(function (res) {
        if (res && res.ok) {
          if (wrap) wrap.classList.add('sent');
          if (sent) sent.classList.add('show');
        } else {
          setError((res && res.error) || (lang === 'en'
            ? 'Failed to send. Please try again.'
            : '전송에 실패했습니다. 다시 시도해 주세요.'));
        }
      }).catch(function () {
        setError(lang === 'en'
          ? 'Network error. Please try again.'
          : '네트워크 오류입니다. 다시 시도해 주세요.');
      }).then(function () {
        setBusy(false);
      });
    });

    if (reset) reset.addEventListener('click', function () {
      if (wrap) wrap.classList.remove('sent');
      if (sent) sent.classList.remove('show');
      setError('');
      form.reset();
    });
  }

  /* ---------------------------------------------- init */
  function init() {
    setupLang();
    setupMenu();
    setupScroll();
    setupReveal();
    setupCounters();
    setupCycle();
    setupHistory();
    setupNews();
    setupForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
