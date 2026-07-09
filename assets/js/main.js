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

  /* ---------------------------------------------- LANGUAGE (persisted)
     Everything else on the site toggles language via CSS ([data-lang]
     hiding .t-ko/.t-en spans), but native <input placeholder> and
     <option> text are plain attributes/strings a CSS rule can't reach
     into — this applies those from data-ph-ko/-en and data-ko/-en. */
  function applyFormI18n() {
    var lang = document.body.getAttribute('data-lang') === 'en' ? 'en' : 'ko';
    $all('[data-ph-ko]').forEach(function (el) {
      var ph = el.getAttribute(lang === 'en' ? 'data-ph-en' : 'data-ph-ko');
      if (ph) el.placeholder = ph;
    });
    $all('option[data-ko]').forEach(function (opt) {
      var label = opt.getAttribute(lang === 'en' ? 'data-en' : 'data-ko');
      if (label) opt.textContent = label;
    });
  }

  function setupLang() {
    var btn = $('#langToggle');
    var current = document.body.getAttribute('data-lang') === 'en' ? 'en' : 'ko';
    if (btn) btn.textContent = current === 'ko' ? 'EN' : 'KR';
    applyFormI18n();
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.body.getAttribute('data-lang') === 'ko' ? 'en' : 'ko';
      document.body.setAttribute('data-lang', next);
      document.documentElement.setAttribute('lang', next);
      btn.textContent = next === 'ko' ? 'EN' : 'KR';
      applyFormI18n();
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

    // desktop "Business" dropdown: the panel's visibility is CSS-driven
    // (:hover/:focus-within on .nav-item-drop); this only keeps the
    // aria-expanded state in sync, since a mismatched ARIA state is worse
    // than none for screen-reader users.
    var drop = $('.nav-item-drop');
    var toggle = drop && $('.nav-drop-toggle', drop);
    if (drop && toggle) {
      function closeDrop() { toggle.setAttribute('aria-expanded', 'false'); }
      document.addEventListener('click', function (e) {
        if (!drop.contains(e.target)) closeDrop();
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && drop.contains(document.activeElement)) {
          // focus the toggle first (its own focusin would otherwise re-open
          // the panel if this ran after closeDrop), then close last so the
          // final aria-expanded is false and the CSS force-close rule applies
          toggle.focus();
          closeDrop();
        }
      });
      drop.addEventListener('focusin', function () { toggle.setAttribute('aria-expanded', 'true'); });
      drop.addEventListener('focusout', function () {
        // let the newly-focused element settle before checking — on the
        // same tick, document.activeElement can still be the old one
        setTimeout(function () {
          if (!drop.contains(document.activeElement)) closeDrop();
        }, 0);
      });
      drop.addEventListener('mouseenter', function () { toggle.setAttribute('aria-expanded', 'true'); });
      drop.addEventListener('mouseleave', closeDrop);
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

  /* ---------------------------------------------- NEWSROOM (dynamic list + filter) */
  // article text now comes from the admin-managed /api/news store, not
  // build-time literals, so every field must be escaped before it goes
  // into innerHTML.
  function escHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var BIZ_INFO = {
    'culiver-aqua.html': { no: '01', nko: '컬리버', nen: 'CULIVER', tko: '스마트 양식', ten: 'SMART AQUACULTURE', ink: '#0E4E78' },
    'amp.html': { no: '02', nko: '에이엠피', nen: 'AMP', tko: '수처리 솔루션', ten: 'WATER TREATMENT', ink: '#166578' },
    'cobaltive.html': { no: '03', nko: '코발티브', nen: 'COBALTIVE', tko: '자원순환 소재', ten: 'UPCYCLED MATERIALS', ink: '#6E5D38' },
    'susinje-farm.html': { no: '04', nko: '수신제팜', nen: 'SUSINJE FARM', tko: '스마트팜 · 유통', ten: 'SMART FARM · DISTRIBUTION', ink: '#3E7C4F' }
  };

  function newsDateLabel(iso) {
    return iso && iso.length >= 7 ? iso.slice(0, 7).replace('-', '.') : (iso || '');
  }

  // color/chipbg/overlay/cover are always server-derived from a fixed
  // theme enum (see api/_lib/news-store.js THEMES) — never free text —
  // so they're safe to place directly into a style attribute.
  function newsCardHtml(n) {
    var bg = n.photo ? n.overlay + ",url('assets/img/" + escHtml(n.photo) + "')" : n.overlay;
    return '<a href="news.html?id=' + encodeURIComponent(n.id) + '" class="news-card" data-tag="' + escHtml(n.tagKo) + '">' +
      '<div class="news-photo" role="img" aria-label="' + escHtml(n.titleKo) + ' 관련 이미지" style="background-image:' + bg + '"></div>' +
      '<div class="news-body">' +
      '<div class="news-meta"><span class="news-tag" style="color:' + n.color + ';background:' + n.chipbg + '">' +
      '<span class="t-ko">' + escHtml(n.tagKo) + '</span><span class="t-en">' + escHtml(n.tagEn) + '</span></span>' +
      '<span class="news-date">' + escHtml(newsDateLabel(n.date)) + '</span></div>' +
      '<h3><span class="t-ko">' + escHtml(n.titleKo) + '</span><span class="t-en">' + escHtml(n.titleEn) + '</span></h3>' +
      '<span class="news-arrow">→</span>' +
      '</div></a>';
  }

  function loadNewsInto(container, opts) {
    if (!container) return;
    var qs = opts && opts.limit ? '?limit=' + opts.limit : '';
    fetch('/api/news' + qs).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data || !data.ok || !data.items) return; // keep the static seed fallback already in the DOM
      container.innerHTML = data.items.map(newsCardHtml).join('');
    }).catch(function () {
      // offline / KV not configured yet — static seed cards already rendered stay as-is
    });
  }

  function setupNews() {
    var list = $('#newsList');
    var preview = $('#newsPreview');
    var btns = $all('#newsFilters .news-filter');

    if (list) loadNewsInto(list);
    if (preview) loadNewsInto(preview, { limit: 3 });

    if (!btns.length) return;
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-key');
        $all('#newsList .news-card').forEach(function (c) {
          var show = key === 'all' || c.getAttribute('data-tag') === key;
          c.classList.toggle('hidden', !show);
        });
        btns.forEach(function (b) { b.classList.toggle('active', b === btn); });
      });
    });
  }

  /* ---------------------------------------------- NEWS ARTICLE (news.html) */
  function setupArticle() {
    var root = $('#articleRoot');
    if (!root) return;
    var params;
    try { params = new URLSearchParams(window.location.search); } catch (e) { params = null; }
    var id = params ? params.get('id') : null;
    if (!id) { renderArticleError(root); return; }

    fetch('/api/news/' + encodeURIComponent(id)).then(function (r) {
      if (!r.ok) throw new Error('not found');
      return r.json();
    }).then(function (data) {
      if (!data || !data.ok) throw new Error('bad response');
      renderArticle(root, data.article, data.prevId, data.nextId);
    }).catch(function () {
      renderArticleError(root);
    });
  }

  function renderArticleError(root) {
    root.innerHTML = '<div class="article reveal in-view">' +
      '<p><span class="t-ko">기사를 찾을 수 없습니다.</span><span class="t-en">Article not found.</span></p>' +
      '<p><a class="btn btn-primary" href="newsroom.html"><span class="t-ko">뉴스룸으로</span><span class="t-en">Back to Newsroom</span></a></p>' +
      '</div>';
  }

  // article title/body support 6 languages (ko/en written at build time
  // are always present; vi/th/ja/zh are filled in by hand in the admin
  // editor and may be partial or absent per article) — this in-article
  // picker is independent of the site-wide KO/EN chrome toggle, which
  // still only ever shows Korean or English nav/footer/labels.
  var ARTICLE_LANGS = ['ko', 'en', 'vi', 'th', 'ja', 'zh'];
  var ARTICLE_LANG_LABELS = { ko: '한국어', en: 'English', vi: 'Tiếng Việt', th: 'ภาษาไทย', ja: '日本語', zh: '中文' };

  function capLang(l) { return l.charAt(0).toUpperCase() + l.slice(1); }

  function availableArticleLangs(n) {
    return ARTICLE_LANGS.filter(function (l) {
      var t = n['title' + capLang(l)], b = n['body' + capLang(l)];
      return !!(t && String(t).trim()) && Array.isArray(b) && b.length > 0;
    });
  }

  function paintArticleLang(n, lang) {
    var titleEl = $('#artTitle'), bodyEl = $('#artBody'), coverEl = $('.art-cover');
    var title = n['title' + capLang(lang)] || n.titleKo;
    var paras = n['body' + capLang(lang)];
    if (!paras || !paras.length) paras = n.bodyKo || [];
    if (titleEl) titleEl.textContent = title;
    if (bodyEl) bodyEl.innerHTML = paras.map(function (p) { return '<p>' + escHtml(p) + '</p>'; }).join('');
    if (coverEl) coverEl.setAttribute('aria-label', title + ' 관련 이미지');
    document.title = title + ' — 컬리버 그룹 뉴스룸';
    var crumb = $('.page-hero .breadcrumb [aria-current="page"]');
    if (crumb) {
      var ko = crumb.querySelector('.t-ko'), en = crumb.querySelector('.t-en');
      if (ko) ko.textContent = n.titleKo;
      if (en) en.textContent = n.titleEn;
    }
    $all('.art-lang').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-lang') === lang); });
  }

  function aboutCardHtml(bizFile) {
    var b = bizFile && BIZ_INFO[bizFile];
    if (b) {
      return '<a class="about-card" href="' + bizFile + '">' +
        '<span class="badge" style="background:' + b.ink + '">' + b.no + '</span>' +
        '<span class="body"><h4><span class="t-ko">' + b.nko + '</span><span class="t-en">' + b.nen + '</span></h4>' +
        '<p><span class="t-ko">' + b.tko + '</span><span class="t-en">' + b.ten + '</span></p></span></a>';
    }
    return '<a class="about-card" href="careers.html">' +
      '<span class="badge" style="background:#0B2438">👥</span>' +
      '<span class="body"><h4><span class="t-ko">채용 공고 보기</span><span class="t-en">View open positions</span></h4>' +
      '<p><span class="t-ko">컬리버 그룹 채용</span><span class="t-en">CULIVER Group careers</span></p></span></a>';
  }

  function renderArticle(root, n, prevId, nextId) {
    var bg = n.photo ? n.cover + ",url('assets/img/" + escHtml(n.photo) + "')" : n.cover;
    var langs = availableArticleLangs(n);
    var siteLang = document.body.getAttribute('data-lang') === 'en' ? 'en' : 'ko';
    var initialLang = langs.indexOf(siteLang) !== -1 ? siteLang : (langs[0] || 'ko');
    var langButtons = langs.length > 1 ? langs.map(function (l) {
      return '<button type="button" class="art-lang' + (l === initialLang ? ' active' : '') + '" data-lang="' + l + '">' + ARTICLE_LANG_LABELS[l] + '</button>';
    }).join('') : '';
    var prevLink = prevId
      ? '<a href="news.html?id=' + encodeURIComponent(prevId) + '">← <span class="t-ko">이전 글</span><span class="t-en">Previous</span></a>'
      : '<span class="disabled">← <span class="t-ko">이전 글</span><span class="t-en">Previous</span></span>';
    var nextLink = nextId
      ? '<a href="news.html?id=' + encodeURIComponent(nextId) + '"><span class="t-ko">다음 글</span><span class="t-en">Next</span> →</a>'
      : '<span class="disabled"><span class="t-ko">다음 글</span><span class="t-en">Next</span> →</span>';

    root.innerHTML = '<article class="article reveal in-view">' +
      '<div class="art-meta">' +
      '<span class="art-tag" style="color:' + n.color + ';background:' + n.chipbg + '">' +
      '<span class="t-ko">' + escHtml(n.tagKo) + '</span><span class="t-en">' + escHtml(n.tagEn) + '</span></span>' +
      '<span class="art-date">' + escHtml(newsDateLabel(n.date)) + '</span></div>' +
      (langButtons ? '<div class="art-langs" id="artLangs">' + langButtons + '</div>' : '') +
      '<h1 id="artTitle"></h1>' +
      '<div class="art-cover" role="img" style="background-image:' + bg + '"></div>' +
      '<div id="artBody"></div>' +
      aboutCardHtml(n.biz) +
      '</article>' +
      '<div class="pager">' + prevLink +
      '<a href="newsroom.html"><span class="t-ko">목록</span><span class="t-en">List</span></a>' +
      nextLink + '</div>';

    var langsEl = $('#artLangs');
    if (langsEl) {
      langsEl.addEventListener('click', function (e) {
        var btn = e.target.closest && e.target.closest('.art-lang');
        if (!btn) return;
        paintArticleLang(n, btn.getAttribute('data-lang'));
      });
    }
    paintArticleLang(n, initialLang);
  }

  /* ---------------------------------------------- CONTACT form */
  var MESSAGE_MAX = 4000;

  function prefillFromQuery(form) {
    var params;
    try { params = new URLSearchParams(window.location.search); } catch (e) { return; }
    var type = params.get('type');
    // job postings pass both role_ko and role_en (the static site can't
    // know the visitor's language at build time); show whichever matches
    // the language currently active (persisted via localStorage, already
    // applied to <body> before this script runs).
    var lang = document.body.getAttribute('data-lang') === 'en' ? 'en' : 'ko';
    var role = params.get('role_' + lang) || params.get('role_ko') || params.get('role_en');
    if (type && form.type) {
      var opts = Array.prototype.slice.call(form.type.options).map(function (o) { return o.value; });
      if (opts.indexOf(type) !== -1) form.type.value = type;
    }
    if (role && form.message && !form.message.value) {
      var label = lang === 'en' ? 'Role: ' : '지원 직무: ';
      form.message.value = '[' + label + role + ']\n\n';
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
    setupArticle();
    setupForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
