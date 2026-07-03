/* ============================================================
   CULIVER GROUP — interactions & data-driven rendering
   Ported from the Claude Design component (state + renderVals).
   ============================================================ */
(function () {
  'use strict';

  /* ---------------------------------------------- data */
  var companies = [
    { href: 'culiver-aqua.html', no: '01', color: '#0E4E78', img: 'assets/img/biz-culiver.jpg', imgRight: false,
      overlay: 'linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.72))',
      chipBg: 'rgba(14,78,120,.08)', tagKo: '스마트 양식', tagEn: 'SMART AQUACULTURE',
      nameKo: '컬리버', nameEn: 'CULIVER',
      descKo: '미생물 기반 BFT 바이오플락 기술로 흰다리새우를 육상에서 연중 안정 생산합니다. 항생제 없는 양식, 데이터로 관리되는 수조.',
      descEn: 'Year-round, land-based whiteleg shrimp production powered by microbial BFT technology — antibiotic-free, data-managed.',
      chips: ['흰다리새우', 'BFT 바이오플락', 'Shrimp365'] },
    { href: 'amp.html', no: '02', color: '#1E7F96', img: 'assets/img/biz-amp.jpg', imgRight: true,
      overlay: 'linear-gradient(150deg,rgba(30,127,150,.46),rgba(15,74,92,.72))',
      chipBg: 'rgba(30,127,150,.09)', tagKo: '수처리 솔루션', tagEn: 'WATER TREATMENT',
      nameKo: '에이엠피', nameEn: 'AMP',
      descKo: '양식장과 산업 현장의 물을 다루는 수처리 엔지니어링. 미생물 제제와 순환여과 시스템으로 물의 순환을 완성합니다.',
      descEn: 'Water-treatment engineering for aquaculture and industry — microbial agents and recirculating filtration that close the water loop.',
      chips: ['수처리 설비', '미생물 제제', '순환여과'] },
    { href: 'cobaltive.html', no: '03', color: '#77653F', img: 'assets/img/biz-cobaltive.jpg', imgRight: false,
      overlay: 'linear-gradient(150deg,rgba(142,122,92,.46),rgba(94,79,58,.72))',
      chipBg: 'rgba(142,122,92,.12)', tagKo: '자원순환 소재', tagEn: 'UPCYCLED MATERIALS',
      nameKo: '코발티브', nameEn: 'COBALTIVE',
      descKo: '버려지는 굴 패각을 친환경 소재와 생활 제품으로 되살립니다. 폐기물이 아닌 자원으로 — 숨쉘, 셸픽.',
      descEn: 'Discarded oyster shells reborn as eco-materials and everyday products — waste turned back into a resource.',
      chips: ['굴패각 업사이클', '숨쉘', '셸픽'] },
    { href: 'susinje-farm.html', no: '04', color: '#3E7C4F', img: 'assets/img/biz-susinje.jpg', imgRight: true,
      overlay: 'linear-gradient(150deg,rgba(62,124,79,.46),rgba(36,82,50,.72))',
      chipBg: 'rgba(62,124,79,.1)', tagKo: '스마트팜 · 유통', tagEn: 'SMART FARM · DISTRIBUTION',
      nameKo: '수신제팜', nameEn: 'SUSINJE FARM',
      descKo: '데이터 기반 수경재배로 기르고, 산지에서 식탁까지 직접 잇습니다. 스마트팜 재배와 신선 유통을 한 흐름으로.',
      descEn: 'Data-driven hydroponic growing connected directly to the table — smart-farm cultivation and fresh distribution in one flow.',
      chips: ['수경재배', '스마트팜', '신선유통'] }
  ];

  var cycles = [
    { no: '01', nameKo: '컬리버', nameEn: 'CULIVER', role: '양식', color: '#0E4E78',
      dKo: '육상 BFT 양식장에서 나온 사육수를 에이엠피로 보내 정화합니다. 순환의 출발점입니다.',
      dEn: 'Rearing water from land-based BFT farms flows to AMP for treatment — the start of the loop.', top: '2%', left: '50%' },
    { no: '02', nameKo: '에이엠피', nameEn: 'AMP', role: '수처리', color: '#1E7F96',
      dKo: '정화·순환여과로 되살린 물을 다시 양식장과 스마트팜으로 돌려보냅니다.',
      dEn: 'Treated, recirculated water returns to the farms and smart-farm greenhouses.', top: '50%', left: '98%' },
    { no: '03', nameKo: '수신제팜', nameEn: 'SUSINJE', role: '재배·유통', color: '#3E7C4F',
      dKo: '순환수로 기른 작물을 데이터로 관리하고, 산지에서 식탁까지 직접 유통합니다.',
      dEn: 'Crops grown with recirculated water, data-managed and delivered farm-to-table.', top: '98%', left: '50%' },
    { no: '04', nameKo: '코발티브', nameEn: 'COBALTIVE', role: '자원순환', color: '#8E7A5C',
      dKo: '버려지는 굴 패각을 소재로 되살려 그룹의 순환 고리를 자원 영역까지 넓힙니다.',
      dEn: 'Discarded oyster shells reborn as materials, extending the loop into resources.', top: '50%', left: '2%' }
  ];

  var values = [
    { no: '01', color: '#0E4E78', titleKo: '순환 Circularity', titleEn: 'Circularity',
      dKo: '한 사업의 부산물이 다른 사업의 원료가 됩니다. 버려지는 것 없이 순환하는 생산 구조를 지향합니다.',
      dEn: "One business's byproduct becomes another's raw material — a production structure where nothing is wasted." },
    { no: '02', color: '#1E7F96', titleKo: '기술 Technology', titleEn: 'Technology',
      dKo: '미생물, 수처리, 데이터. 1차 산업을 과학의 언어로 다시 씁니다.',
      dEn: 'Microbes, water engineering, data — rewriting primary industry in the language of science.' },
    { no: '03', color: '#3E7C4F', titleKo: '상생 Coexistence', titleEn: 'Coexistence',
      dKo: '바다와 어촌, 산지와 지역사회. 생산의 현장과 함께 성장하는 방식을 선택합니다.',
      dEn: 'The sea and fishing villages, farms and their communities — we choose to grow together.' }
  ];

  var history = [
    { year: '2019', color: '#0E4E78', tKo: '컬리버 설립', tEn: 'CULIVER founded',
      dKo: '육상 흰다리새우 BFT 양식 연구로 그룹의 출발점을 세웠습니다.',
      dEn: 'The group began with R&D in land-based whiteleg shrimp BFT aquaculture.' },
    { year: '2021', color: '#1E7F96', tKo: '에이엠피 합류 · 수처리 내재화', tEn: 'AMP joins — water treatment',
      dKo: '수처리·미생물 기술을 그룹에 내재화하며 순환 구조의 두 번째 축을 마련했습니다.',
      dEn: 'Brought water-treatment and microbial technology in-house, forming the second axis of the loop.' },
    { year: '2023', color: '#8E7A5C', tKo: '코발티브 출범 · 자원순환', tEn: 'COBALTIVE launched',
      dKo: '굴 패각 업사이클 사업을 시작하며 자원순환 영역으로 확장했습니다.',
      dEn: 'Started oyster-shell upcycling, expanding into the circular-materials domain.' },
    { year: '2025', color: '#3E7C4F', tKo: '수신제팜 편입 · 스마트팜', tEn: 'SUSINJE FARM joins',
      dKo: '수경재배 스마트팜과 신선 유통을 더해 바다에서 농장까지 잇는 포트폴리오를 완성했습니다.',
      dEn: 'Added hydroponic smart-farming and fresh distribution, completing the ocean-to-farm portfolio.' },
    { year: '2026', color: '#0B2438', tKo: '컬리버 그룹 지주 체제 전환', tEn: 'Holding structure',
      dKo: '네 개 사업을 하나의 그룹 비전 아래 정렬하고 지주 체제로 전환했습니다.',
      dEn: 'Aligned four businesses under one group vision and transitioned to a holding structure.' }
  ];

  var esg = [
    { label: 'E — ENVIRONMENT', titleKo: '자원의 재순환', titleEn: 'Circular resources',
      dKo: '굴 패각 업사이클, 양식수 순환여과, 무항생제 생산으로 폐기물과 배출을 구조적으로 줄입니다.',
      dEn: 'Shell upcycling, recirculating aquaculture water, and antibiotic-free production structurally cut waste and emissions.' },
    { label: 'S — SOCIAL', titleKo: '어촌·산지와의 상생', titleEn: 'Coexisting communities',
      dKo: '생산의 현장인 바다와 산지, 지역사회와 함께 일자리와 가치를 나눕니다.',
      dEn: 'We share jobs and value with the seas, farmlands, and communities where we produce.' },
    { label: 'G — GOVERNANCE', titleKo: '투명한 순환 경영', titleEn: 'Transparent governance',
      dKo: '네 사업을 하나의 그룹 비전 아래 정렬하고, 데이터에 기반한 투명한 의사결정을 지향합니다.',
      dEn: 'Four businesses aligned under one vision, with transparent, data-driven decision-making.' }
  ];

  var news = [
    { tag: '보도자료', date: '2026.06', title: '컬리버, BFT 기반 흰다리새우 스마트 양식장 2호기 준공', overlay: 'linear-gradient(150deg,rgba(14,78,120,.32),rgba(10,44,70,.55))', photo: 'assets/img/news-1.jpg', color: '#0E4E78', chipBg: 'rgba(14,78,120,.08)' },
    { tag: '소식', date: '2026.05', title: '코발티브, 굴패각 업사이클 소재 친환경 인증 획득', overlay: 'linear-gradient(150deg,rgba(142,122,92,.3),rgba(94,79,58,.55))', photo: 'assets/img/news-2.jpg', color: '#77653F', chipBg: 'rgba(142,122,92,.12)' },
    { tag: '소식', date: '2026.04', title: '수신제팜, 데이터 기반 수경재배 채소 정기유통 시작', overlay: 'linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))', photo: 'assets/img/news-3.jpg', color: '#3E7C4F', chipBg: 'rgba(62,124,79,.1)' },
    { tag: '보도자료', date: '2026.03', title: '에이엠피, 산업용수 순환여과 플랜트 신규 수주', overlay: 'linear-gradient(150deg,rgba(30,127,150,.3),rgba(15,74,92,.55))', photo: 'assets/img/news-4.jpg', color: '#1E7F96', chipBg: 'rgba(30,127,150,.09)' },
    { tag: '채용', date: '2026.02', title: '컬리버 그룹 2026 상반기 신입·경력 공개채용 시작', overlay: 'linear-gradient(150deg,rgba(11,36,56,.34),rgba(8,24,38,.6))', photo: 'assets/img/news-5.jpg', color: '#0B2438', chipBg: 'rgba(11,36,56,.08)' },
    { tag: '소식', date: '2026.01', title: '수신제팜 수경재배 채소, 대형 유통사 입점 확정', overlay: 'linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))', photo: 'assets/img/news-6.jpg', color: '#3E7C4F', chipBg: 'rgba(62,124,79,.1)' }
  ];

  var roles = [
    { role: '양식 생산 매니저', team: '컬리버', color: '#0E4E78', loc: '충남 태안', type: '정규직' },
    { role: '수처리 공정 엔지니어', team: '에이엠피', color: '#1E7F96', loc: '경기 안산', type: '정규직' },
    { role: '소재 R&D 연구원', team: '코발티브', color: '#77653F', loc: '경남 통영', type: '정규직' },
    { role: '스마트팜 재배 담당', team: '수신제팜', color: '#3E7C4F', loc: '전북 김제', type: '정규직' }
  ];

  var filterDefs = [
    { key: 'all', ko: '전체', en: 'All' },
    { key: '보도자료', ko: '보도자료', en: 'Press' },
    { key: '소식', ko: '소식', en: 'Updates' },
    { key: '채용', ko: '채용', en: 'Hiring' }
  ];

  /* ---------------------------------------------- helpers */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  /* ---------------------------------------------- state */
  var state = { activeCycle: 0, activeYear: 4, newsFilter: 'all' };

  /* ---------------------------------------------- BUSINESS cards */
  function renderBusiness() {
    var list = $('#bizList');
    companies.forEach(function (c) {
      var a = el('a', 'biz-card');
      a.href = c.href;
      a.innerHTML =
        '<div class="biz-media' + (c.imgRight ? ' img-right' : '') + '" style="background-image:' + c.overlay + ",url('" + c.img + "')\">" +
          '<span class="biz-no">' + c.no + '</span>' +
        '</div>' +
        '<div class="biz-body">' +
          '<p class="biz-tag" style="color:' + c.color + '"><span class="t-ko">' + c.tagKo + '</span><span class="t-en">' + c.tagEn + '</span></p>' +
          '<h3 class="biz-name"><span class="t-ko">' + c.nameKo + '</span><span class="t-en">' + c.nameEn + '</span><span class="rom t-ko">' + c.nameEn + '</span></h3>' +
          '<p class="biz-desc t-ko">' + c.descKo + '</p>' +
          '<p class="biz-desc t-en">' + c.descEn + '</p>' +
          '<div class="chips">' + c.chips.map(function (ch) {
            return '<span class="chip" style="color:' + c.color + ';background:' + c.chipBg + '">' + ch + '</span>';
          }).join('') + '</div>' +
          '<span class="biz-more" style="color:' + c.color + '"><span class="t-ko">자세히 보기</span><span class="t-en">Learn more</span> →</span>' +
        '</div>';
      list.appendChild(a);
    });
  }

  /* ---------------------------------------------- VALUES */
  function renderValues() {
    var list = $('#valuesList');
    values.forEach(function (v) {
      var d = el('div', 'value');
      d.innerHTML =
        '<span class="value-no" style="color:' + v.color + '">' + v.no + '</span>' +
        '<div class="value-body">' +
          '<h3><span class="t-ko">' + v.titleKo + '</span><span class="t-en">' + v.titleEn + '</span></h3>' +
          '<p class="t-ko">' + v.dKo + '</p>' +
          '<p class="t-en">' + esc(v.dEn) + '</p>' +
        '</div>';
      list.appendChild(d);
    });
  }

  /* ---------------------------------------------- ESG */
  function renderEsg() {
    var list = $('#esgList');
    esg.forEach(function (e) {
      var d = el('div', 'esg-card');
      d.innerHTML =
        '<span class="label">' + e.label + '</span>' +
        '<h3><span class="t-ko">' + e.titleKo + '</span><span class="t-en">' + e.titleEn + '</span></h3>' +
        '<p class="t-ko">' + e.dKo + '</p>' +
        '<p class="t-en">' + e.dEn + '</p>';
      list.appendChild(d);
    });
  }

  /* ---------------------------------------------- ROLES */
  function renderRoles() {
    var list = $('#rolesList');
    roles.forEach(function (r) {
      var a = el('a', 'role');
      a.href = '#contact';
      a.innerHTML =
        '<span class="role-title">' + r.role + '</span>' +
        '<span class="role-team" style="color:' + r.color + '">' + r.team + '</span>' +
        '<span class="role-loc">' + r.loc + '</span>' +
        '<span class="role-type">' + r.type + ' →</span>';
      list.appendChild(a);
    });
  }

  /* ---------------------------------------------- CYCLE (interactive) */
  function renderCycleNodes() {
    var box = $('#ringNodes');
    box.innerHTML = '';
    cycles.forEach(function (c, i) {
      var b = el('button', 'node');
      b.style.top = c.top;
      b.style.left = c.left;
      b.innerHTML = '<span class="no">' + c.no + '</span><span class="nm">' + c.nameKo + '</span>';
      b.addEventListener('click', function () { setCycle(i); });
      b.addEventListener('mouseenter', function () { setCycle(i); });
      box.appendChild(b);
    });
    var dots = $('#cycleDots');
    dots.innerHTML = '';
    cycles.forEach(function () { dots.appendChild(el('span')); });
  }
  function setCycle(i) {
    state.activeCycle = i;
    var c = cycles[i];
    // core
    var role = $('#ringRole'); role.textContent = c.role; role.style.color = c.color;
    $('#ringKo').textContent = c.nameKo;
    $('#ringEn').textContent = c.nameEn;
    // nodes
    var nodes = $('#ringNodes').children;
    for (var k = 0; k < nodes.length; k++) {
      var on = k === i, cc = cycles[k];
      nodes[k].classList.toggle('active', on);
      nodes[k].style.background = on ? cc.color : '#FDFCFA';
      nodes[k].style.color = on ? '#F6F4EF' : '#0B1E2D';
      nodes[k].style.boxShadow = on ? '0 16px 34px -12px ' + cc.color : '0 8px 20px -12px rgba(11,30,45,.35)';
    }
    // detail
    var badge = $('#cycleBadge'); badge.textContent = c.no; badge.style.background = c.color;
    $('#cycleTitle').innerHTML = '<span class="t-ko">' + c.nameKo + '</span><span class="t-en">' + c.nameEn + '</span> · <span style="color:' + c.color + '">' + c.role + '</span>';
    $('#cycleDescKo').textContent = c.dKo;
    $('#cycleDescEn').textContent = c.dEn;
    // dots
    var dots = $('#cycleDots').children;
    for (var d = 0; d < dots.length; d++) {
      var active = d === i;
      dots[d].style.width = active ? '30px' : '8px';
      dots[d].style.background = active ? cycles[d].color : 'rgba(11,30,45,.18)';
    }
  }

  /* ---------------------------------------------- HISTORY (interactive) */
  function renderHistYears() {
    var box = $('#histYears');
    box.innerHTML = '';
    history.forEach(function (h, i) {
      var b = el('button', 'hist-year', h.year);
      b.addEventListener('click', function () { setYear(i); });
      box.appendChild(b);
    });
  }
  function setYear(i) {
    state.activeYear = i;
    var h = history[i];
    var btns = $('#histYears').children;
    for (var k = 0; k < btns.length; k++) {
      var on = k === i, hh = history[k];
      btns[k].classList.toggle('active', on);
      btns[k].style.background = on ? hh.color : 'transparent';
      btns[k].style.borderColor = on ? hh.color : 'rgba(11,30,45,.2)';
      btns[k].style.color = on ? '#F6F4EF' : 'rgba(11,30,45,.6)';
    }
    var big = $('#histBig'); big.textContent = h.year; big.style.color = h.color;
    $('#histTitle').innerHTML = '<span class="t-ko">' + h.tKo + '</span><span class="t-en">' + h.tEn + '</span>';
    $('#histDescKo').textContent = h.dKo;
    $('#histDescEn').textContent = h.dEn;
  }

  /* ---------------------------------------------- NEWSROOM (filter) */
  function renderNews() {
    var list = $('#newsList');
    news.forEach(function (n, i) {
      var a = el('a', 'news-card');
      a.href = '#news';
      a.setAttribute('data-tag', n.tag);
      a.style.order = i;
      a.innerHTML =
        '<div class="news-photo" style="background-image:' + n.overlay + ",url('" + n.photo + "')\"></div>" +
        '<div class="news-body">' +
          '<div class="news-meta">' +
            '<span class="news-tag" style="color:' + n.color + ';background:' + n.chipBg + '">' + n.tag + '</span>' +
            '<span class="news-date">' + n.date + '</span>' +
          '</div>' +
          '<h3>' + n.title + '</h3>' +
          '<span class="news-arrow">→</span>' +
        '</div>';
      list.appendChild(a);
    });
    var fbox = $('#newsFilters');
    filterDefs.forEach(function (f) {
      var b = el('button', 'news-filter');
      b.setAttribute('data-key', f.key);
      b.innerHTML = '<span class="t-ko">' + f.ko + '</span><span class="t-en">' + f.en + '</span>';
      b.addEventListener('click', function () { setFilter(f.key); });
      fbox.appendChild(b);
    });
  }
  function setFilter(key) {
    state.newsFilter = key;
    var cards = $('#newsList').children;
    for (var i = 0; i < cards.length; i++) {
      var show = key === 'all' || cards[i].getAttribute('data-tag') === key;
      cards[i].classList.toggle('hidden', !show);
    }
    var btns = $('#newsFilters').children;
    for (var k = 0; k < btns.length; k++) {
      btns[k].classList.toggle('active', btns[k].getAttribute('data-key') === key);
    }
  }

  /* ---------------------------------------------- LANGUAGE */
  function setupLang() {
    var btn = $('#langToggle');
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
    function toggle() {
      var open = menu.classList.toggle('open');
      ham.textContent = open ? '✕' : '☰';
      gnb.classList.toggle('menu-open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    }
    function close() {
      menu.classList.remove('open');
      ham.textContent = '☰';
      gnb.classList.remove('menu-open');
      document.body.style.overflow = '';
    }
    ham.addEventListener('click', toggle);
    menu.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', close);
    });
    window.matchMedia('(max-width: 900px)').addEventListener('change', function (e) {
      if (!e.matches) close();
    });
  }

  /* ---------------------------------------------- SCROLL: progress, nav, back-to-top */
  function setupScroll() {
    var progress = $('#progress'), gnb = $('#gnb'), toTop = $('#toTop');
    var secIds = ['top', 'business', 'cycle', 'about', 'history', 'esg', 'news', 'careers', 'contact'];
    var navLinks = document.querySelectorAll('.nav-links a');
    function onScroll() {
      var sc = window.scrollY;
      var doc = document.documentElement;
      var max = (doc.scrollHeight - window.innerHeight) || 1;
      progress.style.width = Math.min(100, Math.max(0, (sc / max) * 100)) + '%';
      gnb.classList.toggle('scrolled', sc > 40 && !$('#mobileMenu').classList.contains('open'));
      toTop.classList.toggle('show', sc > 600);
      var active = 'top';
      secIds.forEach(function (id) {
        var e = document.getElementById(id);
        if (e && e.offsetTop - 140 <= sc) active = id;
      });
      navLinks.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('data-sec') === active);
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------------------------------------------- REVEAL on scroll */
  function setupReveal() {
    var reveals = document.querySelectorAll('.reveal');
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
    var counters = document.querySelectorAll('[data-count]');
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
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { run(); co.disconnect(); } });
    }, { threshold: 0.4 });
    co.observe(counters[0]);
  }

  /* ---------------------------------------------- CONTACT form */
  function setupForm() {
    var wrap = $('#formWrap'), form = $('#contactForm'), sent = $('#formSent'), reset = $('#formReset');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      wrap.classList.add('sent');
      sent.classList.add('show');
    });
    reset.addEventListener('click', function () {
      wrap.classList.remove('sent');
      sent.classList.remove('show');
      form.reset();
    });
  }

  /* ---------------------------------------------- init */
  function init() {
    renderBusiness();
    renderValues();
    renderEsg();
    renderRoles();
    renderCycleNodes();
    setCycle(state.activeCycle);
    renderHistYears();
    setYear(state.activeYear);
    renderNews();
    setFilter(state.newsFilter);
    setupLang();
    setupMenu();
    setupScroll();
    setupReveal();
    setupCounters();
    setupForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
