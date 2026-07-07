/* ============================================================
   CULIVER GROUP — interactions (progressive enhancement)
   All content lives in the generated HTML; this script only wires
   up behavior: language toggle (persisted), mobile menu + desktop
   dropdown, scroll progress / back-to-top, number counters, scroll
   reveal, the interactive loop diagram, history timeline, news
   filter, and the contact form (incl. query-param prefill).
   ============================================================ */
(function () {
  'use strict';

  var LANG_KEY = 'cg_lang';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ---------------------------------------------- LANGUAGE (persisted) */
  function setupLang() {
    var btn = $('#langToggle');
    var current = document.body.getAttribute('data-lang') === 'en' ? 'en' : 'ko';
    if (btn) btn.textContent = current === 'ko' ? 'EN' : 'KR';
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.body.getAttribute('data-lang') === 'ko' ? 'en' : 'ko';
      document.body.setAttribute('data-lang', next);
      document.documentElement.setAttribute('lang', next);
      btn.textContent = next === 'ko' ? 'EN' : 'KR';
      try { localStorage.setItem(LANG_KEY, next); } catch (e) { /* storage unavailable */ }
    });
  }

  /* ---------------------------------------------- MOBILE MENU + desktop dropdown */
  function setupMenu() {
    var menu = $('#mobileMenu'), ham = $('#hamburger'), gnb = $('#gnb');
    if (menu && ham) {
      function close() {
        menu.classList.remove('open');
        ham.textContent = '☰';
        ham.setAttribute('aria-expanded', 'false');
        ham.setAttribute('aria-label', 'Open menu');
        if (gnb) gnb.classList.remove('menu-open');
        document.body.style.overflow = '';
      }
      ham.addEventListener('click', function () {
        var open = menu.classList.toggle('open');
        ham.textContent = open ? '✕' : '☰';
        ham.setAttribute('aria-expanded', open ? 'true' : 'false');
        ham.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        if (gnb) gnb.classList.toggle('menu-open', open);
        document.body.style.overflow = open ? 'hidden' : '';
      });
      $all('a[href^="#"], a[href$=".html"]', menu).forEach(function (a) { a.addEventListener('click', close); });
      window.matchMedia('(max-width: 900px)').addEventListener('change', function (e) {
        if (!e.matches) close();
      });
    }

    // desktop "Business" dropdown: close on Escape / outside click for keyboard + mouse users
    var drop = $('.nav-item-drop');
    var toggle = drop && $('.nav-drop-toggle', drop);
    if (drop && toggle) {
      document.addEventListener('click', function (e) {
        if (!drop.contains(e.target)) toggle.setAttribute('aria-expanded', 'false');
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') toggle.setAttribute('aria-expanded', 'false');
      });
      drop.addEventListener('focusin', function () { toggle.setAttribute('aria-expanded', 'true'); });
      drop.addEventListener('mouseenter', function () { toggle.setAttribute('aria-expanded', 'true'); });
      drop.addEventListener('mouseleave', function () { toggle.setAttribute('aria-expanded', 'false'); });
    }
  }

  /* ---------------------------------------------- SCROLL: progress + back-to-top */
  function setupScroll() {
    var progress = $('#progress'), gnb = $('#gnb'), toTop = $('#toTop'), menu = $('#mobileMenu');
    var doc = document.documentElement;

    function onScroll() {
      var sc = window.scrollY;
      var max = (doc.scrollHeight - window.innerHeight) || 1;
      if (progress) progress.style.width = Math.min(100, Math.max(0, (sc / max) * 100)) + '%';
      if (gnb) gnb.classList.toggle('scrolled', sc > 40 && !(menu && menu.classList.contains('open')));
      if (toTop) toTop.classList.toggle('show', sc > 600);
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

  /* ---------------------------------------------- CYCLE (interactive)
     Base/inactive appearance (background: var(--card), color: var(--ink),
     box-shadow) is already supplied by the .node CSS rule, and the
     active look (color: var(--paper), scale) by .node.active — so this
     only needs to set the per-node DYNAMIC accent color inline, and
     clear it (empty string) when inactive so the CSS default re-applies.
     No hex literals duplicated here. */
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
        n.style.background = on ? color : '';
        n.style.boxShadow = on ? '0 16px 34px -12px ' + color : '';
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
        dot.classList.toggle('active', on);
        dot.style.background = on ? nodes[k].getAttribute('data-color') : '';
      });
    }
    nodes.forEach(function (n, i) {
      n.addEventListener('click', function () { select(i); });
      n.addEventListener('mouseenter', function () { select(i); });
    });
  }

  /* ---------------------------------------------- HISTORY (interactive)
     Same pattern as setupCycle(): base/active TEXT color comes from the
     .hist-year / .hist-year.active CSS rules; only the per-year dynamic
     background/border accent is set inline, cleared on deselect. */
  function setupHistory() {
    var btns = $all('#histYears .hist-year');
    if (!btns.length) return;
    var big = $('#histBig'), title = $('#histTitle'), dKo = $('#histDescKo'), dEn = $('#histDescEn');
    function select(idx) {
      btns.forEach(function (b, k) {
        var on = k === idx, color = b.getAttribute('data-color');
        b.classList.toggle('active', on);
        b.style.background = on ? color : '';
        b.style.borderColor = on ? color : '';
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
  var MESSAGE_MAX = 4000;

  function prefillFromQuery(form) {
    var params;
    try { params = new URLSearchParams(window.location.search); } catch (e) { return; }
    var type = params.get('type');
    var role = params.get('role');
    if (type && form.type) {
      var opts = Array.prototype.slice.call(form.type.options).map(function (o) { return o.value; });
      if (opts.indexOf(type) !== -1) form.type.value = type;
    }
    if (role && form.message && !form.message.value) {
      form.message.value = '[지원 직무 / Role: ' + role + ']\n\n';
    }
  }

  function setupForm() {
    var wrap = $('#formWrap'), form = $('#contactForm'), sent = $('#formSent'),
        reset = $('#formReset'), submit = $('.form-submit', form), errBox = $('#formError'),
        counter = $('#msgCounter');
    if (!form) return;

    prefillFromQuery(form);

    if (counter && form.message) {
      var updateCounter = function () {
        counter.textContent = form.message.value.length + ' / ' + MESSAGE_MAX;
      };
      form.message.addEventListener('input', updateCounter);
      updateCounter();
    }

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
        email: form.email ? form.email.value : '',
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
      if (counter) counter.textContent = '0 / ' + MESSAGE_MAX;
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
