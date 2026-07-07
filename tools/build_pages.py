#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static page generator for the CULIVER GROUP site.

Emits index.html and the corporate sub-pages (about, business,
sustainability, newsroom, careers, contact) sharing one header, footer,
and mobile menu so the chrome stays consistent. Pure output — the site
needs no build step to run; this is only a dev convenience for keeping
the shared markup DRY. Run from the repo root:  python3 tools/build_pages.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = (
    '  <link rel="preconnect" href="https://cdn.jsdelivr.net">\n'
    '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">\n'
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600&display=swap">\n'
)

NAV = [
    ("about.html", "그룹소개", "About"),
    ("business.html", "사업영역", "Business"),
    ("sustainability.html", "지속가능경영", "Sustainability"),
    ("newsroom.html", "뉴스룸", "Newsroom"),
    ("careers.html", "채용", "Careers"),
    ("contact.html", "문의", "Contact"),
]


def head(title, desc):
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ko" class="no-js">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{title}</title>\n"
        f'  <meta name="description" content="{desc}">\n'
        "  <script>document.documentElement.className = 'js';</script>\n"
        + FONTS +
        '  <link rel="stylesheet" href="assets/css/style.css">\n'
        "</head>\n"
    )


def header(active):
    links = ""
    for href, ko, en in NAV:
        cur = " current" if href == active else ""
        links += (
            f'        <a href="{href}" class="{cur.strip()}">'
            f'<span class="t-ko">{ko}</span><span class="t-en">{en}</span></a>\n'
        )
    return (
        '  <div class="progress" id="progress"></div>\n\n'
        '  <header class="gnb" id="gnb">\n'
        '    <a href="index.html" class="brand">\n'
        '      <span class="brand-mark">CULIVER</span>\n'
        '      <span class="brand-sub">GROUP</span>\n'
        "    </a>\n"
        "    <nav>\n"
        '      <div class="nav-links" id="navLinks">\n'
        + links +
        "      </div>\n"
        '      <button class="lang-toggle" id="langToggle">EN</button>\n'
        '      <button class="hamburger" id="hamburger" aria-label="menu">☰</button>\n'
        "    </nav>\n"
        "  </header>\n"
    )


def mobile_menu():
    items = ""
    for i, (href, ko, en) in enumerate(NAV, 1):
        items += (
            f'      <a href="{href}"><span class="mm-no">{i:02d}</span>'
            f'<span class="mm-label"><span class="t-ko">{ko}</span><span class="t-en">{en}</span></span></a>\n'
        )
    return (
        '  <div class="mobile-menu" id="mobileMenu">\n'
        "    <nav>\n" + items + "    </nav>\n"
        '    <div class="mm-family">\n'
        '      <span class="mm-family-label">FAMILY</span>\n'
        '      <div class="mm-family-row">\n'
        '        <a href="culiver-aqua.html">컬리버</a>\n'
        '        <a href="amp.html">에이엠피</a>\n'
        '        <a href="cobaltive.html">코발티브</a>\n'
        '        <a href="susinje-farm.html">수신제팜</a>\n'
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
    )


FOOTER = """  <footer class="footer">
    <div class="wrap">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="mark"><span class="m">CULIVER</span><span class="s">GROUP</span></div>
          <p class="t-ko">바다에서 농장까지, 순환하는 내일을 기릅니다.</p>
          <p class="t-en">From ocean to farm, we cultivate a circular tomorrow.</p>
        </div>
        <div class="footer-cols">
          <div class="footer-col">
            <span class="head">FAMILY</span>
            <a href="culiver-aqua.html">컬리버 <span class="rom">CULIVER</span></a>
            <a href="amp.html">에이엠피 <span class="rom">AMP</span></a>
            <a href="cobaltive.html">코발티브 <span class="rom">COBALTIVE</span></a>
            <a href="susinje-farm.html">수신제팜 <span class="rom">SUSINJE FARM</span></a>
          </div>
          <div class="footer-col">
            <span class="head">GROUP</span>
            <a href="about.html"><span class="t-ko">그룹소개</span><span class="t-en">About</span></a>
            <a href="about.html#history"><span class="t-ko">연혁</span><span class="t-en">History</span></a>
            <a href="sustainability.html"><span class="t-ko">지속가능경영</span><span class="t-en">Sustainability</span></a>
            <a href="careers.html"><span class="t-ko">채용</span><span class="t-en">Careers</span></a>
          </div>
          <div class="footer-col">
            <span class="head">CONTACT</span>
            <a href="contact.html"><span class="t-ko">문의하기</span><span class="t-en">Contact</span></a>
            <span>contact@culiver.co.kr</span>
            <span>T. 000-0000-0000</span>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 CULIVER GROUP. All rights reserved.</span>
        <span class="t-ko">사업자 정보 · 주소는 실제 정보로 교체하세요</span>
        <span class="t-en">Replace with real business registration &amp; address</span>
      </div>
    </div>
  </footer>

  <button class="to-top" id="toTop" aria-label="top">↑</button>

  <script src="assets/js/main.js"></script>
</body>
</html>
"""


def page_hero(eyebrow, title_ko, title_en, sub_ko, sub_en, crumb_ko, crumb_en):
    return f"""  <section class="page-hero">
    <div class="inner">
      <nav class="breadcrumb"><a href="index.html"><span class="t-ko">홈</span><span class="t-en">Home</span></a><span class="sep">/</span><span class="t-ko">{crumb_ko}</span><span class="t-en">{crumb_en}</span></nav>
      <p class="eyebrow">{eyebrow}</p>
      <h1><span class="t-ko">{title_ko}</span><span class="t-en">{title_en}</span></h1>
      <p class="sub"><span class="t-ko">{sub_ko}</span><span class="t-en">{sub_en}</span></p>
    </div>
  </section>
"""


# ------------------------------------------------------------------ reusable blocks
BIZ = [
    ("culiver-aqua.html", "01", "#0E4E78", "biz-culiver.jpg", False,
     "linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.72))", "rgba(14,78,120,.08)",
     "스마트 양식", "SMART AQUACULTURE", "컬리버", "CULIVER",
     "미생물 기반 BFT 바이오플락 기술로 흰다리새우를 육상에서 연중 안정 생산합니다. 항생제 없는 양식, 데이터로 관리되는 수조.",
     "Year-round, land-based whiteleg shrimp production powered by microbial BFT technology — antibiotic-free, data-managed.",
     ["흰다리새우", "BFT 바이오플락", "Shrimp365"]),
    ("amp.html", "02", "#1E7F96", "biz-amp.jpg", True,
     "linear-gradient(150deg,rgba(30,127,150,.46),rgba(15,74,92,.72))", "rgba(30,127,150,.09)",
     "수처리 솔루션", "WATER TREATMENT", "에이엠피", "AMP",
     "양식장과 산업 현장의 물을 다루는 수처리 엔지니어링. 미생물 제제와 순환여과 시스템으로 물의 순환을 완성합니다.",
     "Water-treatment engineering for aquaculture and industry — microbial agents and recirculating filtration that close the water loop.",
     ["수처리 설비", "미생물 제제", "순환여과"]),
    ("cobaltive.html", "03", "#77653F", "biz-cobaltive.jpg", False,
     "linear-gradient(150deg,rgba(142,122,92,.46),rgba(94,79,58,.72))", "rgba(142,122,92,.12)",
     "자원순환 소재", "UPCYCLED MATERIALS", "코발티브", "COBALTIVE",
     "버려지는 굴 패각을 친환경 소재와 생활 제품으로 되살립니다. 폐기물이 아닌 자원으로 — 숨쉘, 셸픽.",
     "Discarded oyster shells reborn as eco-materials and everyday products — waste turned back into a resource.",
     ["굴패각 업사이클", "숨쉘", "셸픽"]),
    ("susinje-farm.html", "04", "#3E7C4F", "biz-susinje.jpg", True,
     "linear-gradient(150deg,rgba(62,124,79,.46),rgba(36,82,50,.72))", "rgba(62,124,79,.1)",
     "스마트팜 · 유통", "SMART FARM · DISTRIBUTION", "수신제팜", "SUSINJE FARM",
     "데이터 기반 수경재배로 기르고, 산지에서 식탁까지 직접 잇습니다. 스마트팜 재배와 신선 유통을 한 흐름으로.",
     "Data-driven hydroponic growing connected directly to the table — smart-farm cultivation and fresh distribution in one flow.",
     ["수경재배", "스마트팜", "신선유통"]),
]


def biz_cards():
    out = ""
    for href, no, color, img, right, overlay, chipbg, tko, ten, nko, nen, dko, den, chips in BIZ:
        rc = " img-right" if right else ""
        chip_html = "".join(
            f'<span class="chip" style="color:{color};background:{chipbg}">{c}</span>' for c in chips
        )
        out += f"""        <a href="{href}" class="biz-card">
          <div class="biz-media{rc}" style="background-image:{overlay},url('assets/img/{img}')">
            <span class="biz-no">{no}</span>
          </div>
          <div class="biz-body">
            <p class="biz-tag" style="color:{color}"><span class="t-ko">{tko}</span><span class="t-en">{ten}</span></p>
            <h3 class="biz-name"><span class="t-ko">{nko}</span><span class="t-en">{nen}</span><span class="rom t-ko">{nen}</span></h3>
            <p class="biz-desc t-ko">{dko}</p>
            <p class="biz-desc t-en">{den}</p>
            <div class="chips">{chip_html}</div>
            <span class="biz-more" style="color:{color}"><span class="t-ko">자세히 보기</span><span class="t-en">Learn more</span> →</span>
          </div>
        </a>
"""
    return out


VALUES = """      <div class="values reveal">
        <div class="value">
          <span class="value-no" style="color:#0E4E78">01</span>
          <div class="value-body">
            <h3><span class="t-ko">순환 Circularity</span><span class="t-en">Circularity</span></h3>
            <p class="t-ko">한 사업의 부산물이 다른 사업의 원료가 됩니다. 버려지는 것 없이 순환하는 생산 구조를 지향합니다.</p>
            <p class="t-en">One business's byproduct becomes another's raw material — a production structure where nothing is wasted.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#1E7F96">02</span>
          <div class="value-body">
            <h3><span class="t-ko">기술 Technology</span><span class="t-en">Technology</span></h3>
            <p class="t-ko">미생물, 수처리, 데이터. 1차 산업을 과학의 언어로 다시 씁니다.</p>
            <p class="t-en">Microbes, water engineering, data — rewriting primary industry in the language of science.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#3E7C4F">03</span>
          <div class="value-body">
            <h3><span class="t-ko">상생 Coexistence</span><span class="t-en">Coexistence</span></h3>
            <p class="t-ko">바다와 어촌, 산지와 지역사회. 생산의 현장과 함께 성장하는 방식을 선택합니다.</p>
            <p class="t-en">The sea and fishing villages, farms and their communities — we choose to grow together.</p>
          </div>
        </div>
      </div>
"""

ESG_CARDS = """      <div class="esg-grid reveal">
        <div class="esg-card">
          <span class="label">E — ENVIRONMENT</span>
          <h3><span class="t-ko">자원의 재순환</span><span class="t-en">Circular resources</span></h3>
          <p class="t-ko">굴 패각 업사이클, 양식수 순환여과, 무항생제 생산으로 폐기물과 배출을 구조적으로 줄입니다.</p>
          <p class="t-en">Shell upcycling, recirculating aquaculture water, and antibiotic-free production structurally cut waste and emissions.</p>
        </div>
        <div class="esg-card">
          <span class="label">S — SOCIAL</span>
          <h3><span class="t-ko">어촌·산지와의 상생</span><span class="t-en">Coexisting communities</span></h3>
          <p class="t-ko">생산의 현장인 바다와 산지, 지역사회와 함께 일자리와 가치를 나눕니다.</p>
          <p class="t-en">We share jobs and value with the seas, farmlands, and communities where we produce.</p>
        </div>
        <div class="esg-card">
          <span class="label">G — GOVERNANCE</span>
          <h3><span class="t-ko">투명한 순환 경영</span><span class="t-en">Transparent governance</span></h3>
          <p class="t-ko">네 사업을 하나의 그룹 비전 아래 정렬하고, 데이터에 기반한 투명한 의사결정을 지향합니다.</p>
          <p class="t-en">Four businesses aligned under one vision, with transparent, data-driven decision-making.</p>
        </div>
      </div>
"""

NEWS = [
    ("보도자료", "Press", "2026.06", "컬리버, BFT 기반 흰다리새우 스마트 양식장 2호기 준공",
     "linear-gradient(150deg,rgba(14,78,120,.32),rgba(10,44,70,.55))", "news-1.jpg", "#0E4E78", "rgba(14,78,120,.08)"),
    ("소식", "Updates", "2026.05", "코발티브, 굴패각 업사이클 소재 친환경 인증 획득",
     "linear-gradient(150deg,rgba(142,122,92,.3),rgba(94,79,58,.55))", "news-2.jpg", "#77653F", "rgba(142,122,92,.12)"),
    ("소식", "Updates", "2026.04", "수신제팜, 데이터 기반 수경재배 채소 정기유통 시작",
     "linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))", "news-3.jpg", "#3E7C4F", "rgba(62,124,79,.1)"),
    ("보도자료", "Press", "2026.03", "에이엠피, 산업용수 순환여과 플랜트 신규 수주",
     "linear-gradient(150deg,rgba(30,127,150,.3),rgba(15,74,92,.55))", "news-4.jpg", "#1E7F96", "rgba(30,127,150,.09)"),
    ("채용", "Hiring", "2026.02", "컬리버 그룹 2026 상반기 신입·경력 공개채용 시작",
     "linear-gradient(150deg,rgba(11,36,56,.34),rgba(8,24,38,.6))", "news-5.jpg", "#0B2438", "rgba(11,36,56,.08)"),
    ("소식", "Updates", "2026.01", "수신제팜 수경재배 채소, 대형 유통사 입점 확정",
     "linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))", "news-6.jpg", "#3E7C4F", "rgba(62,124,79,.1)"),
]


def news_cards(limit=None):
    out = ""
    for tagko, _tagen, date, title, overlay, photo, color, chipbg in NEWS[:limit]:
        out += f"""        <a href="newsroom.html" class="news-card" data-tag="{tagko}">
          <div class="news-photo" style="background-image:{overlay},url('assets/img/{photo}')"></div>
          <div class="news-body">
            <div class="news-meta"><span class="news-tag" style="color:{color};background:{chipbg}">{tagko}</span><span class="news-date">{date}</span></div>
            <h3>{title}</h3>
            <span class="news-arrow">→</span>
          </div>
        </a>
"""
    return out


CYCLE_BLOCK = """      <div class="cycle-grid reveal">
        <div class="ring" id="ring">
          <div class="ring-dash"></div>
          <div class="ring-core">
            <span class="role" id="ringRole" style="color:#0E4E78">양식</span>
            <span class="ko" id="ringKo">컬리버</span>
            <span class="en" id="ringEn">CULIVER</span>
          </div>
          <button class="node active" data-i="0" data-no="01" data-name-ko="컬리버" data-name-en="CULIVER" data-role="양식" data-color="#0E4E78"
            data-dko="육상 BFT 양식장에서 나온 사육수를 에이엠피로 보내 정화합니다. 순환의 출발점입니다."
            data-den="Rearing water from land-based BFT farms flows to AMP for treatment — the start of the loop."
            style="top:2%;left:50%;background:#0E4E78;color:#F6F4EF;box-shadow:0 16px 34px -12px #0E4E78">
            <span class="no">01</span><span class="nm">컬리버</span>
          </button>
          <button class="node" data-i="1" data-no="02" data-name-ko="에이엠피" data-name-en="AMP" data-role="수처리" data-color="#1E7F96"
            data-dko="정화·순환여과로 되살린 물을 다시 양식장과 스마트팜으로 돌려보냅니다."
            data-den="Treated, recirculated water returns to the farms and smart-farm greenhouses."
            style="top:50%;left:98%">
            <span class="no">02</span><span class="nm">에이엠피</span>
          </button>
          <button class="node" data-i="2" data-no="03" data-name-ko="수신제팜" data-name-en="SUSINJE" data-role="재배·유통" data-color="#3E7C4F"
            data-dko="순환수로 기른 작물을 데이터로 관리하고, 산지에서 식탁까지 직접 유통합니다."
            data-den="Crops grown with recirculated water, data-managed and delivered farm-to-table."
            style="top:98%;left:50%">
            <span class="no">03</span><span class="nm">수신제팜</span>
          </button>
          <button class="node" data-i="3" data-no="04" data-name-ko="코발티브" data-name-en="COBALTIVE" data-role="자원순환" data-color="#8E7A5C"
            data-dko="버려지는 굴 패각을 소재로 되살려 그룹의 순환 고리를 자원 영역까지 넓힙니다."
            data-den="Discarded oyster shells reborn as materials, extending the loop into resources."
            style="top:50%;left:2%">
            <span class="no">04</span><span class="nm">코발티브</span>
          </button>
        </div>
        <div class="cycle-detail">
          <span class="cycle-badge" id="cycleBadge" style="background:#0E4E78">01</span>
          <h3 id="cycleTitle"><span class="t-ko">컬리버</span><span class="t-en">CULIVER</span> · <span style="color:#0E4E78">양식</span></h3>
          <p class="t-ko" id="cycleDescKo">육상 BFT 양식장에서 나온 사육수를 에이엠피로 보내 정화합니다. 순환의 출발점입니다.</p>
          <p class="t-en" id="cycleDescEn">Rearing water from land-based BFT farms flows to AMP for treatment — the start of the loop.</p>
          <div class="cycle-dots" id="cycleDots">
            <span style="width:30px;background:#0E4E78"></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
"""

HISTORY_BLOCK = """      <div class="hist-years reveal" id="histYears">
        <button class="hist-year" data-i="0" data-color="#0E4E78" data-tko="컬리버 설립" data-ten="CULIVER founded"
          data-dko="육상 흰다리새우 BFT 양식 연구로 그룹의 출발점을 세웠습니다."
          data-den="The group began with R&amp;D in land-based whiteleg shrimp BFT aquaculture.">2019</button>
        <button class="hist-year" data-i="1" data-color="#1E7F96" data-tko="에이엠피 합류 · 수처리 내재화" data-ten="AMP joins — water treatment"
          data-dko="수처리·미생물 기술을 그룹에 내재화하며 순환 구조의 두 번째 축을 마련했습니다."
          data-den="Brought water-treatment and microbial technology in-house, forming the second axis of the loop.">2021</button>
        <button class="hist-year" data-i="2" data-color="#8E7A5C" data-tko="코발티브 출범 · 자원순환" data-ten="COBALTIVE launched"
          data-dko="굴 패각 업사이클 사업을 시작하며 자원순환 영역으로 확장했습니다."
          data-den="Started oyster-shell upcycling, expanding into the circular-materials domain.">2023</button>
        <button class="hist-year" data-i="3" data-color="#3E7C4F" data-tko="수신제팜 편입 · 스마트팜" data-ten="SUSINJE FARM joins"
          data-dko="수경재배 스마트팜과 신선 유통을 더해 바다에서 농장까지 잇는 포트폴리오를 완성했습니다."
          data-den="Added hydroponic smart-farming and fresh distribution, completing the ocean-to-farm portfolio.">2025</button>
        <button class="hist-year active" data-i="4" data-color="#0B2438" data-tko="컬리버 그룹 지주 체제 전환" data-ten="Holding structure"
          data-dko="네 개 사업을 하나의 그룹 비전 아래 정렬하고 지주 체제로 전환했습니다."
          data-den="Aligned four businesses under one group vision and transitioned to a holding structure."
          style="background:#0B2438;border-color:#0B2438;color:#F6F4EF">2026</button>
      </div>
      <div class="hist-detail">
        <div class="hist-big" id="histBig" style="color:#0B2438">2026</div>
        <div class="hist-text">
          <h3 id="histTitle"><span class="t-ko">컬리버 그룹 지주 체제 전환</span><span class="t-en">Holding structure</span></h3>
          <p class="t-ko" id="histDescKo">네 개 사업을 하나의 그룹 비전 아래 정렬하고 지주 체제로 전환했습니다.</p>
          <p class="t-en" id="histDescEn">Aligned four businesses under one group vision and transitioned to a holding structure.</p>
        </div>
      </div>
"""

FORM_BLOCK = """      <div class="form-wrap reveal" id="formWrap">
        <form class="form" id="contactForm">
          <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="form-row">
            <label>
              <span class="lbl"><span class="t-ko">이름</span><span class="t-en">Name</span></span>
              <input name="name" placeholder="홍길동">
            </label>
            <label>
              <span class="lbl"><span class="t-ko">회사·소속</span><span class="t-en">Company</span></span>
              <input name="company" placeholder="컬리버">
            </label>
          </div>
          <label>
            <span class="lbl"><span class="t-ko">문의 유형</span><span class="t-en">Inquiry type</span></span>
            <select name="type">
              <option>사업 제휴</option>
              <option>투자 · IR</option>
              <option>제품 · 구매</option>
              <option>채용</option>
              <option>기타</option>
            </select>
          </label>
          <label>
            <span class="lbl"><span class="t-ko">내용</span><span class="t-en">Message</span></span>
            <textarea name="message" rows="4" placeholder="문의 내용을 입력하세요"></textarea>
          </label>
          <button type="submit" class="form-submit"><span class="t-ko">문의 보내기</span><span class="t-en">Send inquiry</span></button>
          <p class="form-error" id="formError" role="alert" hidden></p>
        </form>
        <div class="form-sent" id="formSent">
          <span class="check">✓</span>
          <h3 class="t-ko">문의가 접수되었습니다</h3>
          <h3 class="t-en">Your inquiry has been received</h3>
          <p class="t-ko">빠른 시일 내에 담당자가 연락드리겠습니다.</p>
          <p class="t-en">Our team will get back to you shortly.</p>
          <button class="form-reset" id="formReset"><span class="t-ko">새 문의 작성</span><span class="t-en">New inquiry</span></button>
        </div>
      </div>
"""

CONTACT_INFO = """      <div class="reveal">
        <p class="eyebrow on-dark">CONTACT</p>
        <h2 class="h2 t-ko">함께 만들<br>순환을 제안하세요</h2>
        <h2 class="h2 t-en">Let's build a loop together</h2>
        <div class="contact-info">
          <div class="row"><span class="k">EMAIL</span><span class="v">contact@culiver.co.kr</span></div>
          <div class="row"><span class="k">TEL</span><span class="v">000-0000-0000</span></div>
          <div class="row">
            <span class="k"><span class="t-ko">주소</span><span class="t-en">ADDRESS</span></span>
            <span class="addr t-ko">본사 주소를 입력하세요 (실제 정보로 교체)</span>
            <span class="addr t-en">Replace with headquarters address</span>
          </div>
        </div>
      </div>
"""


def write(name, body, active=None, subpage=True):
    cls = ' class="subpage"' if subpage else ""
    dp = f' data-page="{active}"' if active else ""
    html = (
        head(TITLES[name][0], TITLES[name][1])
        + f'<body data-lang="ko"{cls}{dp}>\n\n'
        + header(active if subpage else None)
        + mobile_menu()
        + body
        + FOOTER
    )
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name, f"({len(html)} bytes)")


TITLES = {
    "index.html": ("컬리버 그룹 CULIVER GROUP — 바다에서 농장까지, 순환하는 내일을 기릅니다",
                   "컬리버 그룹은 스마트 양식, 수처리, 자원순환 소재, 스마트팜을 잇는 지속가능한 생산 생태계를 만들어 갑니다."),
    "about.html": ("그룹소개 About — 컬리버 그룹 CULIVER GROUP",
                   "‘기른다’는 하나의 동사에서 출발한 컬리버 그룹의 비전과 연혁, 그룹 개요를 소개합니다."),
    "business.html": ("사업영역 Business — 컬리버 그룹 CULIVER GROUP",
                      "스마트 양식·수처리·자원순환 소재·스마트팜, 하나의 순환으로 연결된 컬리버 그룹의 네 개 사업."),
    "sustainability.html": ("지속가능경영 Sustainability — 컬리버 그룹 CULIVER GROUP",
                            "ESG는 별도 활동이 아니라 컬리버 그룹 네 사업이 존재하는 이유입니다."),
    "newsroom.html": ("뉴스룸 Newsroom — 컬리버 그룹 CULIVER GROUP",
                      "컬리버 그룹과 계열사의 보도자료·소식·채용 소식을 전합니다."),
    "careers.html": ("채용 Careers — 컬리버 그룹 CULIVER GROUP",
                     "바다와 농장, 실험실과 현장을 잇는 사람들을 찾습니다. 인재상·채용 절차·공고·복리후생 안내."),
    "contact.html": ("문의 Contact — 컬리버 그룹 CULIVER GROUP",
                     "사업 제휴, 투자, 제품·구매, 채용 등 컬리버 그룹에 문의하세요."),
}

# ================================================================= HOME
home = f"""  <section id="top" class="hero">
    <div class="hero-glow"></div>
    <div class="hero-inner">
      <p class="hero-eyebrow">CULIVER GROUP</p>
      <h1 class="t-ko">바다에서 농장까지,<br>순환하는 내일을 기릅니다</h1>
      <h1 class="t-en">From ocean to farm,<br>we cultivate a circular tomorrow</h1>
      <p class="hero-lead t-ko">컬리버 그룹은 스마트 양식, 수처리, 자원순환 소재, 스마트팜을 잇는<br>지속가능한 생산 생태계를 만들어 갑니다.</p>
      <p class="hero-lead t-en">CULIVER Group builds a sustainable production ecosystem spanning smart aquaculture, water treatment, upcycled materials, and smart farming.</p>
      <div class="hero-cta">
        <a href="business.html" class="btn btn-primary"><span class="t-ko">사업영역 보기</span><span class="t-en">Our Business</span><span>→</span></a>
        <a href="contact.html" class="btn btn-ghost"><span class="t-ko">문의하기</span><span class="t-en">Contact</span></a>
      </div>
    </div>
    <div class="scroll-hint"><span>SCROLL</span><span class="bar"></span></div>
  </section>

  <section class="stats">
    <div class="wrap stats-grid reveal">
      <div class="stat"><div class="stat-num"><span class="val" data-count="4">4</span><span class="suffix"></span></div><span class="stat-label"><span class="t-ko">계열사</span><span class="t-en">Affiliates</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="100">100</span><span class="suffix">%</span></div><span class="stat-label"><span class="t-ko">무항생제 양식</span><span class="t-en">Antibiotic-free</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="365">365</span><span class="suffix"></span></div><span class="stat-label"><span class="t-ko">연중 생산</span><span class="t-en">Days a year</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="2019">2019</span><span class="suffix"></span></div><span class="stat-label"><span class="t-ko">그룹 시작</span><span class="t-en">Since</span></span></div>
    </div>
  </section>

  <section class="section bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">OUR BUSINESS</p>
          <h2 class="h2 t-ko">하나의 순환, 네 개의 사업</h2>
          <h2 class="h2 t-en">One cycle, four businesses</h2>
        </div>
        <a class="more-link" href="business.html"><span class="t-ko">사업영역 전체 보기</span><span class="t-en">All businesses</span> →</a>
      </div>
      <div class="biz-list reveal">
{biz_cards()}      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap about-grid">
      <div class="about-intro reveal">
        <p class="eyebrow">ABOUT CULIVER GROUP</p>
        <h2 class="h2 t-ko">기르는 일의<br>순환을 설계합니다</h2>
        <h2 class="h2 t-en">We design the cycle<br>of cultivation</h2>
        <p class="t-ko">컬리버 그룹은 ‘기른다’는 하나의 동사에서 출발했습니다. 새우를 기르고, 물을 되살리고, 껍데기를 소재로 기르고, 작물을 길러 식탁에 올립니다. 각 사업은 서로의 출발점이 됩니다.</p>
        <p class="t-en">CULIVER Group began with a single verb: to cultivate. We raise shrimp, restore water, grow materials from shells, and bring crops to the table — each business feeding the next.</p>
        <a class="more-link" href="about.html"><span class="t-ko">그룹소개 자세히</span><span class="t-en">More about us</span> →</a>
      </div>
{VALUES}    </div>
  </section>

  <section class="section tall esg">
    <div class="esg-glow"></div>
    <div class="wrap esg-inner">
      <div class="reveal">
        <p class="eyebrow on-dark">SUSTAINABILITY</p>
        <div class="esg-head">
          <h2 class="h2 t-ko">지속가능성은 사업 그 자체입니다</h2>
          <h2 class="h2 t-en">Sustainability is the business itself</h2>
          <p class="sub t-ko">ESG는 컬리버 그룹의 별도 활동이 아니라, 네 사업이 존재하는 이유입니다.</p>
          <p class="sub t-en">ESG is not a side program — it is why our four businesses exist.</p>
        </div>
      </div>
{ESG_CARDS}      <a class="more-link" href="sustainability.html" style="color:#7FC4C9"><span class="t-ko">지속가능경영 자세히</span><span class="t-en">More on sustainability</span> →</a>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">NEWSROOM</p>
          <h2 class="h2 t-ko">컬리버 그룹 소식</h2>
          <h2 class="h2 t-en">News from the group</h2>
        </div>
        <a class="more-link" href="newsroom.html"><span class="t-ko">뉴스룸 전체 보기</span><span class="t-en">All news</span> →</a>
      </div>
      <div class="news-grid reveal">
{news_cards(3)}      </div>
    </div>
  </section>

  <section class="section bg-card">
    <div class="wrap reveal">
      <div class="cta-band">
        <div>
          <h2><span class="t-ko">함께 성장할 사람을 찾습니다</span><span class="t-en">Grow with us</span></h2>
          <p><span class="t-ko">바다와 농장, 실험실과 현장을 잇는 컬리버 그룹의 채용을 확인하세요.</span><span class="t-en">See open roles across the CULIVER Group affiliates.</span></p>
        </div>
        <a class="btn btn-primary" href="careers.html"><span class="t-ko">채용 보기</span><span class="t-en">Careers</span> →</a>
      </div>
    </div>
  </section>
"""
write("index.html", home, active=None, subpage=False)

# ================================================================= ABOUT
about = (
    page_hero("ABOUT CULIVER GROUP", "기르는 일의 순환을 설계합니다", "We design the cycle of cultivation",
              "‘기른다’는 하나의 동사에서 출발한 네 개의 사업이 하나의 순환으로 연결됩니다.",
              "Four businesses born from a single verb — to cultivate — connected as one loop.",
              "그룹소개", "About")
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div class="greeting reveal">
        <div class="portrait"><span>CULIVER GROUP</span></div>
        <div class="body">
          <p class="t-ko">컬리버 그룹은 ‘기른다’는 하나의 동사에서 시작했습니다. 새우를 기르고, 그 물을 되살리고, 버려지던 껍데기를 소재로 되살리며, 데이터로 작물을 길러 식탁까지 잇습니다.</p>
          <p class="t-ko">우리는 1차 산업을 과학과 데이터의 언어로 다시 씁니다. 한 사업의 부산물이 다른 사업의 원료가 되는 순환 구조 속에서, 버려지는 것 없이 지속가능한 생산 생태계를 만들어 가겠습니다. 바다와 어촌, 산지와 지역사회와 함께 성장하겠습니다.</p>
          <p class="t-en">CULIVER Group began with a single verb — to cultivate. We raise shrimp, restore their water, revive discarded shells into materials, and grow crops with data all the way to the table. We are rewriting primary industry in the language of science, building a circular, sustainable production ecosystem where nothing is wasted.</p>
          <div class="sign"><b>컬리버 그룹</b><span class="t-ko">대표이사</span><span class="t-en">CEO, CULIVER GROUP</span></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">OUR VALUES</p>
        <h2 class="h2 t-ko">세 가지 약속</h2>
        <h2 class="h2 t-en">Three commitments</h2>
        <p class="lead"><span class="t-ko">순환·기술·상생 — 컬리버 그룹이 일하는 방식입니다.</span><span class="t-en">Circularity, technology, coexistence — the way CULIVER Group works.</span></p>
      </div>
      <div class="about-grid">
        <div></div>
"""
    + VALUES
    + """      </div>
    </div>
  </section>

  <section id="history" class="section tall bg-paper">
    <div class="wrap">
      <div class="hist-head reveal">
        <p class="eyebrow">HISTORY</p>
        <h2 class="h2 t-ko">순환을 만들어온 길</h2>
        <h2 class="h2 t-en">The path to the loop</h2>
      </div>
"""
    + HISTORY_BLOCK
    + """    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">GROUP OVERVIEW</p>
        <h2 class="h2 t-ko">그룹 개요</h2>
        <h2 class="h2 t-en">At a glance</h2>
      </div>
      <dl class="overview reveal">
        <div class="row"><dt><span class="t-ko">그룹명</span><span class="t-en">Group</span></dt><dd>컬리버 그룹 · CULIVER GROUP</dd></div>
        <div class="row"><dt><span class="t-ko">설립</span><span class="t-en">Founded</span></dt><dd><span class="t-ko">2019년 (2026년 지주 체제 전환)</span><span class="t-en">2019 (holding structure since 2026)</span></dd></div>
        <div class="row"><dt><span class="t-ko">계열사</span><span class="t-en">Affiliates</span></dt><dd><span class="t-ko">컬리버 · 에이엠피 · 코발티브 · 수신제팜 (4개사)</span><span class="t-en">CULIVER · AMP · COBALTIVE · SUSINJE FARM (4)</span></dd></div>
        <div class="row"><dt><span class="t-ko">사업영역</span><span class="t-en">Businesses</span></dt><dd><span class="t-ko">스마트 양식 · 수처리 · 자원순환 소재 · 스마트팜/유통</span><span class="t-en">Smart aquaculture · water treatment · upcycled materials · smart farming</span></dd></div>
        <div class="row"><dt><span class="t-ko">본사</span><span class="t-en">HQ</span></dt><dd><span class="t-ko">본사 주소를 입력하세요 (실제 정보로 교체)</span><span class="t-en">Replace with headquarters address</span></dd></div>
      </dl>
    </div>
  </section>
"""
)
write("about.html", about, active="about.html")

# ================================================================= BUSINESS
business = (
    page_hero("OUR BUSINESS", "하나의 순환, 네 개의 사업", "One cycle, four businesses",
              "양식에서 나온 물은 정화되고, 껍데기는 소재가 되며, 데이터는 농장으로 이어집니다.",
              "Water is treated and returned, shells become materials, data flows to the farm.",
              "사업영역", "Business")
    + """  <section id="cycle" class="section bg-paper">
    <div class="wrap">
      <div class="cycle-head reveal">
        <p class="eyebrow">THE LOOP</p>
        <h2 class="h2 t-ko">버려지는 것 없이, 순환합니다</h2>
        <h2 class="h2 t-en">Nothing wasted — everything circulates</h2>
        <p class="sub t-ko">노드를 눌러 각 사업이 순환 구조에서 맡는 역할을 확인하세요.</p>
        <p class="sub t-en">Tap a node to see the role each business plays in the loop.</p>
      </div>
"""
    + CYCLE_BLOCK
    + """    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">AFFILIATES</p>
        <h2 class="h2 t-ko">네 개의 계열사</h2>
        <h2 class="h2 t-en">Four affiliates</h2>
      </div>
      <div class="biz-list reveal">
"""
    + biz_cards()
    + """      </div>
    </div>
  </section>
"""
)
write("business.html", business, active="business.html")

# ================================================================= SUSTAINABILITY
sustain = (
    page_hero("SUSTAINABILITY", "지속가능성은 사업 그 자체입니다", "Sustainability is the business itself",
              "ESG는 컬리버 그룹의 별도 활동이 아니라, 네 사업이 존재하는 이유입니다.",
              "ESG is not a side program — it is why our four businesses exist.",
              "지속가능경영", "Sustainability")
    + """  <section class="section esg">
    <div class="esg-glow"></div>
    <div class="wrap esg-inner">
      <div class="reveal">
        <p class="eyebrow on-dark">E · S · G</p>
        <div class="esg-head">
          <h2 class="h2 t-ko">사업 안에 담긴 지속가능성</h2>
          <h2 class="h2 t-en">Sustainability built into the business</h2>
          <p class="sub t-ko">환경·사회·지배구조는 각 사업의 설계 원리입니다.</p>
          <p class="sub t-en">Environment, society, and governance are design principles of every business.</p>
        </div>
      </div>
"""
    + ESG_CARDS
    + """    </div>
  </section>

  <section class="section tall contact">
    <div class="wrap">
      <div class="section-intro on-dark reveal">
        <p class="eyebrow on-dark">OUR COMMITMENTS</p>
        <h2 class="h2 t-ko">지속가능을 위한 약속</h2>
        <h2 class="h2 t-en">What we commit to</h2>
      </div>
      <div class="commitments reveal">
        <div class="commitment"><span class="no">01</span><div><h3><span class="t-ko">무항생제·저배출 생산</span><span class="t-en">Antibiotic-free, low-emission production</span></h3><p><span class="t-ko">BFT 양식과 순환여과로 항생제 사용과 오염 배출을 구조적으로 낮춥니다.</span><span class="t-en">BFT aquaculture and recirculating filtration structurally reduce antibiotics and discharge.</span></p></div></div>
        <div class="commitment"><span class="no">02</span><div><h3><span class="t-ko">자원 순환의 확대</span><span class="t-en">Expanding resource circulation</span></h3><p><span class="t-ko">굴 패각 업사이클을 넘어 부산물을 원료로 되돌리는 순환 범위를 넓혀 갑니다.</span><span class="t-en">Beyond shell upcycling, we keep widening the loop that returns byproducts to raw materials.</span></p></div></div>
        <div class="commitment"><span class="no">03</span><div><h3><span class="t-ko">지역사회와의 상생</span><span class="t-en">Coexistence with communities</span></h3><p><span class="t-ko">생산의 현장인 어촌·산지와 일자리·가치를 나누며 함께 성장합니다.</span><span class="t-en">We grow together with the fishing villages and farmlands where we produce.</span></p></div></div>
        <div class="commitment"><span class="no">04</span><div><h3><span class="t-ko">투명한 지배구조</span><span class="t-en">Transparent governance</span></h3><p><span class="t-ko">데이터에 기반한 의사결정과 투명한 정보 공개를 지향합니다.</span><span class="t-en">We pursue data-driven decisions and transparent disclosure.</span></p></div></div>
      </div>
    </div>
  </section>
"""
)
write("sustainability.html", sustain, active="sustainability.html")

# ================================================================= NEWSROOM
newsroom = (
    page_hero("NEWSROOM", "컬리버 그룹 소식", "News from the group",
              "컬리버 그룹과 계열사의 보도자료·소식·채용 소식을 전합니다.",
              "Press releases, updates, and hiring news from CULIVER Group and its affiliates.",
              "뉴스룸", "Newsroom")
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div class="news-head reveal">
        <div>
          <p class="eyebrow">LATEST</p>
          <h2 class="h2 t-ko">전체 소식</h2>
          <h2 class="h2 t-en">All updates</h2>
        </div>
        <div class="news-filters" id="newsFilters">
          <button class="news-filter active" data-key="all"><span class="t-ko">전체</span><span class="t-en">All</span></button>
          <button class="news-filter" data-key="보도자료"><span class="t-ko">보도자료</span><span class="t-en">Press</span></button>
          <button class="news-filter" data-key="소식"><span class="t-ko">소식</span><span class="t-en">Updates</span></button>
          <button class="news-filter" data-key="채용"><span class="t-ko">채용</span><span class="t-en">Hiring</span></button>
        </div>
      </div>
      <div class="news-grid reveal" id="newsList">
"""
    + news_cards()
    + """      </div>
    </div>
  </section>
"""
)
write("newsroom.html", newsroom, active="newsroom.html")

# ================================================================= CAREERS
careers = (
    page_hero("CAREERS", "기르는 사람들과 함께 자랍니다", "Grow with the growers",
              "바다와 농장, 실험실과 현장을 잇는 사람들을 찾습니다.",
              "We look for people who connect the sea and the farm, the lab and the field.",
              "채용", "Careers")
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">TALENT</p>
        <h2 class="h2 t-ko">이런 분을 찾습니다</h2>
        <h2 class="h2 t-en">Who we look for</h2>
      </div>
      <div class="values reveal">
        <div class="value"><span class="value-no" style="color:#0E4E78">01</span><div class="value-body"><h3><span class="t-ko">현장을 아는 사람</span><span class="t-en">Grounded in the field</span></h3><p class="t-ko">데이터와 현장을 함께 읽고, 실제 생산의 문제를 해결하는 사람.</p><p class="t-en">Someone who reads both data and the field to solve real production problems.</p></div></div>
        <div class="value"><span class="value-no" style="color:#1E7F96">02</span><div class="value-body"><h3><span class="t-ko">순환을 설계하는 사람</span><span class="t-en">A systems thinker</span></h3><p class="t-ko">한 사업의 부산물을 다음 사업의 원료로 잇는 시야를 가진 사람.</p><p class="t-en">Someone who connects one business's byproduct to the next as raw material.</p></div></div>
        <div class="value"><span class="value-no" style="color:#3E7C4F">03</span><div class="value-body"><h3><span class="t-ko">함께 자라는 사람</span><span class="t-en">A grower of others</span></h3><p class="t-ko">바다와 지역사회, 동료와 함께 성장하는 것을 즐기는 사람.</p><p class="t-en">Someone who enjoys growing together with communities and colleagues.</p></div></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">HOW WE HIRE</p>
        <h2 class="h2 t-ko">채용 절차</h2>
        <h2 class="h2 t-en">Hiring process</h2>
      </div>
      <div class="steps reveal">
        <div class="step"><div class="n">1</div><h3><span class="t-ko">서류 전형</span><span class="t-en">Application</span></h3><p><span class="t-ko">이력서와 자기소개서로 지원해 주세요.</span><span class="t-en">Apply with your resume and cover letter.</span></p></div>
        <div class="step"><div class="n">2</div><h3><span class="t-ko">실무 면접</span><span class="t-en">Team interview</span></h3><p><span class="t-ko">함께 일할 팀과 직무 역량을 확인합니다.</span><span class="t-en">Meet the team you'll work with.</span></p></div>
        <div class="step"><div class="n">3</div><h3><span class="t-ko">최종 면접</span><span class="t-en">Final interview</span></h3><p><span class="t-ko">가치관과 성장 방향을 함께 이야기합니다.</span><span class="t-en">We talk values and growth together.</span></p></div>
        <div class="step"><div class="n">4</div><h3><span class="t-ko">입사</span><span class="t-en">Onboarding</span></h3><p><span class="t-ko">온보딩과 함께 컬리버 그룹의 일원이 됩니다.</span><span class="t-en">Join CULIVER Group with a full onboarding.</span></p></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">OPEN ROLES</p>
          <h2 class="h2 t-ko">채용 공고</h2>
          <h2 class="h2 t-en">Open positions</h2>
        </div>
      </div>
      <div class="roles reveal">
        <a href="contact.html" class="role"><span class="role-title">양식 생산 매니저</span><span class="role-team" style="color:#0E4E78">컬리버</span><span class="role-loc">충남 태안</span><span class="role-type">정규직 →</span></a>
        <a href="contact.html" class="role"><span class="role-title">수처리 공정 엔지니어</span><span class="role-team" style="color:#1E7F96">에이엠피</span><span class="role-loc">경기 안산</span><span class="role-type">정규직 →</span></a>
        <a href="contact.html" class="role"><span class="role-title">소재 R&D 연구원</span><span class="role-team" style="color:#77653F">코발티브</span><span class="role-loc">경남 통영</span><span class="role-type">정규직 →</span></a>
        <a href="contact.html" class="role"><span class="role-title">스마트팜 재배 담당</span><span class="role-team" style="color:#3E7C4F">수신제팜</span><span class="role-loc">전북 김제</span><span class="role-type">정규직 →</span></a>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">BENEFITS</p>
        <h2 class="h2 t-ko">복리후생</h2>
        <h2 class="h2 t-en">Benefits</h2>
      </div>
      <div class="benefits reveal">
        <div class="benefit"><div class="ic">🌱</div><h3><span class="t-ko">성장 지원</span><span class="t-en">Growth support</span></h3><p><span class="t-ko">교육·자격·컨퍼런스 비용을 지원합니다.</span><span class="t-en">Learning, certifications, and conferences covered.</span></p></div>
        <div class="benefit"><div class="ic">🏖️</div><h3><span class="t-ko">유연한 휴식</span><span class="t-en">Flexible time off</span></h3><p><span class="t-ko">자유로운 연차와 리프레시 휴가.</span><span class="t-en">Generous PTO and refresh leave.</span></p></div>
        <div class="benefit"><div class="ic">🍤</div><h3><span class="t-ko">제품 지원</span><span class="t-en">Product perks</span></h3><p><span class="t-ko">그룹 제품과 신선 먹거리를 임직원가로.</span><span class="t-en">Group products and fresh food at staff prices.</span></p></div>
        <div class="benefit"><div class="ic">🏥</div><h3><span class="t-ko">건강 관리</span><span class="t-en">Health care</span></h3><p><span class="t-ko">건강검진과 단체 보험을 지원합니다.</span><span class="t-en">Health checkups and group insurance.</span></p></div>
      </div>
    </div>
  </section>
"""
)
write("careers.html", careers, active="careers.html")

# ================================================================= CONTACT
contact = (
    page_hero("CONTACT", "함께 만들 순환을 제안하세요", "Let's build a loop together",
              "사업 제휴, 투자, 제품·구매, 채용 등 무엇이든 문의해 주세요.",
              "Partnerships, investment, products, hiring — reach out about anything.",
              "문의", "Contact")
    + """  <section class="section contact">
    <div class="wrap contact-grid">
"""
    + CONTACT_INFO
    + FORM_BLOCK
    + """    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">DIRECTIONS</p>
        <h2 class="h2 t-ko">오시는 길</h2>
        <h2 class="h2 t-en">How to find us</h2>
      </div>
      <div class="map reveal"><span class="t-ko">지도 영역 — 실제 주소·지도(Kakao/Google Map)로 교체하세요</span><span class="t-en">Map area — replace with your real address &amp; embedded map</span></div>
    </div>
  </section>
"""
)
write("contact.html", contact, active="contact.html")

print("done.")
