#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static page generator for the CULIVER GROUP site.

Emits the homepage, the corporate sub-pages, and the detail pages
(affiliate companies, news articles, job postings) — all sharing one
header, footer, and mobile menu so the chrome stays consistent. Output
is plain static HTML; the site needs no build step to run. This script
is only a dev convenience for keeping shared markup DRY.

    python3 tools/build_pages.py

Color note: each affiliate has a canonical brand hue (BIZ[...]['color'],
used for the About-page CI swatch and decorative borders) and, where that
hue is too light to hit WCAG AA 4.5:1 as text or as a white-text-on-fill
badge, a darker 'ink' variant used everywhere the color renders as text
or a solid fill (business/news tags, chips, cycle/history nodes, metrics).
CULIVER (#0E4E78) and SUSINJE (#3E7C4F) already clear 4.5:1, so their ink
equals their canonical color; AMP/teal (#1E7F96, ~4.2:1) and COBALTIVE
(#8E7A5C, ~3.75:1) do not, so their ink is darkened (#166578 / #6E5D38).
"""
import html
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = (
    '  <link rel="preconnect" href="https://cdn.jsdelivr.net">\n'
    '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">\n'
    # Archivo at expanded width (wdth=125) — the Latin display face. Korean
    # display glyphs fall through to Gothic A1 (a solid, confident gothic that
    # pairs with Archivo's industrial grotesque); body Korean stays Pretendard.
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,500;125,600;125,700;125,800&family=Gothic+A1:wght@500;600;700;800;900&display=swap">\n'
)

# tiny inline script placed immediately after <body> opens (before any
# visible markup is parsed) so a returning English-preferring visitor's
# language choice applies before first paint, with no flash of Korean.
LANG_RESTORE_SCRIPT = (
    "<script>(function(){try{var l=localStorage.getItem('cg_lang');"
    "if(l==='en'){document.body.setAttribute('data-lang','en');"
    "document.documentElement.setAttribute('lang','en');}}catch(e){}})();</script>\n"
)

NAV = [
    ("about.html", "회사소개", "About"),
    ("business.html", "사업영역", "Business"),
    ("sustainability.html", "지속가능경영", "Sustainability"),
    ("ir.html", "실적·인증", "Record"),
    ("newsroom.html", "뉴스룸", "Newsroom"),
    ("careers.html", "채용", "Careers"),
]

# Contact is deliberately NOT in NAV — it renders as a distinct primary
# CTA button (the site's main conversion path: partnership/investment/
# purchase inquiries), not a peer text link.
CONTACT_CTA = ("contact.html", "문의", "Contact")

FAMILY = [
    ("amp.html", "에이엠피", "AMP"),
    ("culiver-aqua.html", "컬리버", "CULIVER"),
    ("cobaltive.html", "코발티브", "COBALTIVE"),
    ("susinje-farm.html", "수신제팜", "SUSINJE FARM"),
]

# jump-links into the (long, single-page) About page's sections
ABOUT_SECTIONS = [
    ("about.html", "회사 개요", "Overview"),
    ("about.html#history", "연혁", "History"),
    ("about.html#org", "조직", "Organization"),
    ("about.html#ci", "브랜드 컬러", "Brand color"),
]

# top-level items that open a dropdown panel. Each panel gets a labelled
# heading so the relationship is explicit: under 사업영역 the four items
# are the group's 계열사(legal entities); under 그룹소개 they are section
# jump-links. label = (ko, en) heading; items = [(href, ko, en)]; all =
# optional (href, ko, en) "see all" link shown at the panel foot.
DROPDOWNS = {
    "about.html": dict(label=("회사", "COMPANY"), items=ABOUT_SECTIONS, all=None),
    "business.html": dict(label=("계열사", "AFFILIATES"), items=FAMILY,
                          all=("business.html", "사업영역 전체 보기", "All businesses")),
}


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


def _drop_panel(drop):
    """Render a labelled dropdown panel (heading + items + optional 'see all')."""
    lko, len_ = drop["label"]
    out = (
        f'            <span class="nav-drop-head"><span class="t-ko">{lko}</span>'
        f'<span class="t-en">{len_}</span></span>\n'
    )
    for ih, iko, ien in drop["items"]:
        out += (
            f'            <a href="{ih}"><span class="nm t-ko">{iko}</span>'
            f'<span class="en t-en">{ien}</span></a>\n'
        )
    if drop.get("all"):
        ah, ako, aen = drop["all"]
        out += (
            f'            <a href="{ah}" class="nav-drop-all"><span class="t-ko">{ako}</span>'
            f'<span class="t-en">{aen}</span> →</a>\n'
        )
    return out


def header(active):
    links = ""
    for href, ko, en in NAV:
        cur = "current" if href == active else ""
        if href in DROPDOWNS:
            links += (
                '        <div class="nav-item-drop">\n'
                f'          <a href="{href}" class="nav-drop-toggle {cur}" aria-haspopup="true" aria-expanded="false">'
                f'<span class="t-ko">{ko}</span><span class="t-en">{en}</span><span class="car" aria-hidden="true">▾</span></a>\n'
                '          <div class="nav-drop-panel">\n'
                + _drop_panel(DROPDOWNS[href]) +
                "          </div>\n"
                "        </div>\n"
            )
        else:
            links += (
                f'        <a href="{href}" class="{cur}">'
                f'<span class="t-ko">{ko}</span><span class="t-en">{en}</span></a>\n'
            )
    ch, cko, cen = CONTACT_CTA
    cta_cur = " current" if ch == active else ""
    return (
        '  <div class="progress" id="progress"></div>\n\n'
        '  <header class="gnb" id="gnb">\n'
        '    <a href="index.html" class="brand">\n'
        '      <span class="brand-mark">AMP</span>\n'
        '      <span class="brand-sub">에이엠피</span>\n'
        "    </a>\n"
        "    <nav>\n"
        '      <div class="nav-links" id="navLinks">\n'
        + links +
        "      </div>\n"
        f'      <a href="{ch}" class="nav-cta{cta_cur}"><span class="t-ko">{cko}</span><span class="t-en">{cen}</span></a>\n'
        '      <button class="lang-toggle" id="langToggle">EN</button>\n'
        '      <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">☰</button>\n'
        "    </nav>\n"
        "  </header>\n"
    )


def mobile_menu():
    # Contact rides along at the end of the mobile list (it's the CTA on
    # desktop; on mobile it stays a first-class row so the path is still
    # one tap away).
    mob = NAV + [CONTACT_CTA]
    items = ""
    for i, (href, ko, en) in enumerate(mob, 1):
        cta = " mm-cta" if href == CONTACT_CTA[0] else ""
        items += (
            f'      <a href="{href}" class="mm-link{cta}"><span class="mm-no">{i:02d}</span>'
            f'<span class="mm-label"><span class="t-ko">{ko}</span><span class="t-en">{en}</span></span></a>\n'
        )
    fam = "".join(
        f'        <a href="{fh}"><span class="t-ko">{fko}</span><span class="t-en">{fen}</span></a>\n'
        for fh, fko, fen in FAMILY
    )
    return (
        '  <div class="mobile-menu" id="mobileMenu">\n'
        "    <nav>\n" + items + "    </nav>\n"
        '    <div class="mm-family">\n'
        '      <span class="mm-family-label">FAMILY</span>\n'
        '      <div class="mm-family-row">\n'
        + fam +
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
    )


FOOTER = """  <footer class="footer">
    <div class="wrap">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="mark"><span class="m">AMP</span><span class="s">에이엠피</span></div>
          <p class="t-ko">현장에 맞춘 설비, 데이터로 관리하는 물.</p>
          <p class="t-en">Water systems built for the site, managed by data.</p>
        </div>
        <div class="footer-cols">
          <div class="footer-col">
            <span class="head">FAMILY</span>
            <a href="amp.html">에이엠피 <span class="rom">AMP</span></a>
            <a href="culiver-aqua.html">컬리버 <span class="rom">CULIVER</span></a>
            <a href="cobaltive.html">코발티브 <span class="rom">COBALTIVE</span></a>
            <a href="susinje-farm.html">수신제팜 <span class="rom">SUSINJE FARM</span></a>
          </div>
          <div class="footer-col">
            <span class="head">COMPANY</span>
            <a href="about.html"><span class="t-ko">회사소개</span><span class="t-en">About</span></a>
            <a href="about.html#history"><span class="t-ko">연혁</span><span class="t-en">History</span></a>
            <a href="sustainability.html"><span class="t-ko">지속가능경영</span><span class="t-en">Sustainability</span></a>
            <a href="ir.html"><span class="t-ko">실적·인증</span><span class="t-en">Record</span></a>
            <a href="careers.html"><span class="t-ko">채용</span><span class="t-en">Careers</span></a>
          </div>
          <div class="footer-col">
            <span class="head">CONTACT</span>
            <a href="contact.html"><span class="t-ko">문의하기</span><span class="t-en">Contact</span></a>
            <a href="https://amp0404.co.kr" target="_blank" rel="noopener">amp0404.co.kr</a>
            <span class="plain"><span class="t-ko">전남 광양시</span><span class="t-en">Gwangyang, Jeonnam</span></span>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 유한회사 에이엠피 (AMP Co., Ltd.) All rights reserved.</span>
        <span class="t-ko">사업자등록번호 171-81-03763 · 전남 광양시 광양읍 익신산단3길 40, 409호</span>
        <span class="t-en">Business Reg. 171-81-03763 · Gwangyang, Jeonnam, Korea</span>
      </div>
    </div>
  </footer>

  <button class="to-top" id="toTop" aria-label="top">↑</button>

  <script src="assets/js/main.js"></script>
</body>
</html>
"""


def page_hero(eyebrow, title_ko, title_en, sub_ko, sub_en, crumbs, bg=None, heading_level="h1", cta_html=""):
    """crumbs: list of (href_or_None, ko, en) between Home and current.
    The LAST crumb is always rendered as plain text with aria-current="page"
    (never a self-link to the current page), regardless of whether an href
    is supplied for it."""
    parts = ['<a href="index.html"><span class="t-ko">홈</span><span class="t-en">Home</span></a>']
    n = len(crumbs)
    for i, (href, ko, en) in enumerate(crumbs):
        parts.append('<span class="sep">/</span>')
        is_last = (i == n - 1)
        if href and not is_last:
            parts.append(f'<a href="{href}"><span class="t-ko">{ko}</span><span class="t-en">{en}</span></a>')
        else:
            parts.append(f'<span aria-current="page"><span class="t-ko">{ko}</span><span class="t-en">{en}</span></span>')
    style = f' style="background:{bg}"' if bg else ""
    return f"""  <section class="page-hero"{style}>
    <div class="inner">
      <nav class="breadcrumb" aria-label="Breadcrumb">{''.join(parts)}</nav>
      <p class="eyebrow">{eyebrow}</p>
      <{heading_level}><span class="t-ko">{title_ko}</span><span class="t-en">{title_en}</span></{heading_level}>
      <p class="sub"><span class="t-ko">{sub_ko}</span><span class="t-en">{sub_en}</span></p>
      {cta_html}
    </div>
  </section>
"""


def metric_value(v):
    """Wrap the literal placeholder-metric marker in t-ko/t-en; real values
    (numbers, "RAS", "Farm→Table", etc.) are already language-neutral."""
    if v == "예시":
        return '<span class="t-ko">예시</span><span class="t-en">example</span>'
    return v


def linkify_first(paragraphs, term, href):
    """Wrap the first occurrence of `term` (across the paragraph list) in a link.
    term/href are always build-time literals here, never external/user input,
    but the inserted markup is still escaped as defense in depth."""
    done = False
    out = []
    safe_term = html.escape(term)
    safe_href = html.escape(href, quote=True)
    for p in paragraphs:
        if not done and term in p:
            p = p.replace(term, f'<a href="{safe_href}">{safe_term}</a>', 1)
            done = True
        out.append(p)
    return out


# ------------------------------------------------------------------ data
BIZ = [
    dict(file="culiver-aqua.html", no="02", color="#0E4E78", ink="#0E4E78",
         deep="linear-gradient(160deg,#041821,#0A2C46 60%,#0E4E78 130%)",
         img="biz-culiver.jpg", right=True,
         overlay="linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.72))", chipbg="rgba(14,78,120,.08)",
         tko="스마트 양식 · AI", ten="SMART AQUACULTURE · AI", nko="컬리버", nen="CULIVER",
         dko="흰다리새우 육상 양식에 프리미엄 사료·복합 유용미생물·질병 조기진단·수질 데이터 관리를 하나로 묶은 통합 솔루션 기업입니다.",
         den="An integrated whiteleg-shrimp aquaculture solution — premium feed, complex probiotics, early disease diagnostics, and data-driven water management in one system.",
         chips=["흰다리새우", "복합 유용미생물", "Shrimp365"],
         leadko="컬리버는 흰다리새우 육상 양식의 5대 요소(사료·미생물·수질·질병·데이터)를 표준화한 통합 솔루션 기업이자 그룹의 지주회사입니다. 프리미엄 사료와 6종 복합 유용미생물, PCR 기반 질병 조기진단, Shrimp365 데이터 플랫폼으로 ‘감’에 의존하던 양식을 데이터 기반 표준 공정으로 바꿉니다.",
         leaden="CULIVER — the group's holding company — standardizes the five pillars of land-based whiteleg-shrimp farming: feed, microbes, water, disease, and data. Premium feed, a 6-strain probiotic blend, PCR-based early diagnostics, and the Shrimp365 platform turn guesswork farming into a data-driven standard process.",
         features=[("복합 유용미생물", "Complex probiotics", "바실러스·락토바실러스 등 6종을 조합한 유용미생물로 수질을 개선하고 유해균을 억제합니다. 조성물·배합 특허 출원을 진행 중입니다.", "A 6-strain blend (Bacillus, Lactobacillus and more) improves water quality and suppresses pathogens; composition & blend patents are pending."),
                   ("질병 조기진단", "Early diagnostics", "PCR 검사로 급성간췌장괴사병·흰반점바이러스 등을 주 1회 조기 진단해, 조기 대응 시 생존율을 크게 끌어올립니다.", "Weekly PCR screening for AHPND, white-spot virus and more enables early response that sharply raises survival."),
                   ("수질 · 데이터 관리", "Water & data", "수온·pH·용존산소 등 수질을 매일 3회 측정하고 주간 리포트로 문제를 조기에 파악하는 Shrimp365 플랫폼을 운영합니다.", "Water is measured 3×/day and surfaced in weekly reports via the Shrimp365 platform, catching problems early.")],
         products=[dict(nko="컬리버 1호", nen="Culiver No.1", dko="바실러스 등 유익균을 복합 조성한 새우양식용 미생물제제. 사육수 수질 개선·유해균 억제용.", den="A complex beneficial-microbe agent for shrimp farming that improves water quality and suppresses pathogens.", tko="미생물제품", ten="Microbial", status="양산중", statusen="In production"),
                   dict(nko="숨쉘 (SUMSHELL)", nen="SUMSHELL", dko="폐굴껍데기(굴패각 소성분말) 유래의 친환경 양식장 수질 pH 완충제. 시험성적서 보유.", den="An eco-friendly pH buffer for farm water made from calcined oyster-shell powder; test-report certified.", tko="미생물제품", ten="Microbial", status="양산중", statusen="In production"),
                   dict(nko="Shrimp365", nen="Shrimp365", dko="수질·생육 데이터 기반의 AI 새우양식 통합관리 플랫폼(SaaS). 웹·앱으로 운영.", den="An AI-driven, SaaS platform for integrated shrimp-farm management from water and growth data.", tko="AI · SW", ten="AI · SW", status="운영중", statusen="Live")],
         metrics=[("70%", "흰다리새우 생존율", "Survival rate"), ("7일", "수질 정상화 기간", "Water recovery"), ("6종", "복합 유용미생물", "Probiotic strains")]),
    dict(file="amp.html", no="01", color="#1B6E7D", ink="#14606E",
         deep="linear-gradient(160deg,#041821,#0C4A57 60%,#1B6E7D 130%)",
         img="biz-amp.jpg", right=False,
         overlay="linear-gradient(150deg,rgba(27,110,125,.5),rgba(12,58,71,.74))", chipbg="rgba(27,110,125,.1)",
         tko="수처리 · 물 매니지먼트", ten="WATER MANAGEMENT", nko="에이엠피", nen="AMP",
         dko="수처리 시스템 설비의 설계·제작·설치·시운전부터 실시간 수질 모니터링까지. 이차전지 공정 설비와 공조부품 제조 기술이 바탕입니다.",
         den="Water-treatment systems — designed, built, installed, commissioned and monitored in real time. Battery-process equipment and HVAC-parts manufacturing are the foundation.",
         chips=["수처리 시스템 설비", "실시간 수질 모니터링", "공조부품 제조"],
         leadko="에이엠피는 현장마다 다른 물의 성상에 맞춰 수처리 시스템 설비를 설계·제작·설치하는 기업입니다. 이차전지 폐수처리, 공정수 재순환, 육상양식 물관리, 제약·화학 폐수처리 네 분야를 다루며, 수질 센서와 실시간 모니터링 프로그램으로 물을 관리합니다. 자체 공장에서 구조물과 장치를 직접 제작하고, 공조용 Clad AL Header Pipe 제조로 쌓은 용접·가공 역량이 설비 제작의 바탕입니다.",
         leaden="AMP designs, builds and installs water-treatment systems tailored to each site's water. It covers four areas — battery wastewater, process-water reuse, aquaculture water, and pharma/chemical wastewater — and manages water with sensors and a live monitoring program. Everything is fabricated in-house, built on welding and machining experience from making clad-aluminum HVAC header pipe.",
         features=[("수처리 시스템 설비", "Water-treatment systems", "원수 성상을 분석해 현장에 맞춘 수처리 설비를 설계·제작·설치·시운전합니다. 이차전지·공정수·양식·제약화학 네 분야.", "Site-specific water-treatment systems designed, built, installed and commissioned across four fields."),
                   ("실시간 수질 모니터링", "Real-time monitoring", "pH·EC·온도·탁도·TDS·DO를 센서로 측정해 실시간 프로그램에서 확인하고, 이상이 생기면 알림으로 대응합니다.", "Sensors track pH, EC, temperature, turbidity, TDS and DO in a live program, with alerts on anomalies."),
                   ("제조 기반", "Manufacturing base", "공조용 Clad AL Header Pipe 제조와 이차전지 전구체 공침반응기 제작 역량이 수처리 설비 제작을 뒷받침합니다.", "Clad-aluminum HVAC header pipe and battery-precursor reactors — the fabrication base behind the water systems.")],
         products=[dict(nko="이차전지 망초폐수 처리 시스템", nen="Battery wastewater system", dko="전구체·양극재 생산 시 발생하는 망초폐수(Na₂SO₄)를 이온 제거 후 공정에 재투입하는 시스템.", den="Removes ions from sodium-sulfate battery wastewater and returns it to the process.", tko="소재·환경", ten="Materials", status="개발중", statusen="In development"),
                   dict(nko="공침반응기 (5L)", nen="Co-precipitation reactor (5L)", dko="pH·교반·온도를 제어해 NCM 삼원계 전구체를 생산하는 반응기. 조선대 납품 예정.", den="A reactor producing NCM ternary precursors under pH, agitation and temperature control.", tko="소재·환경", ten="Materials", status="시제품", statusen="Prototype"),
                   dict(nko="공정수 재순환 시스템", nen="Process-water recirculation", dko="전구체 세척 공정수를 공침반응기로 순환시켜 재활용하는 시스템.", den="Recirculates precursor-washing process water back to the reactor for reuse.", tko="소재·환경", ten="Materials", status="시제품", statusen="Prototype"),
                   dict(nko="전구체 입자선별·필터장치", nen="Precursor filtration", dko="사이클러 필터·필터프레스로 전구체와 망초폐수를 분리하는 장치.", den="Separates precursor from sodium-sulfate wastewater using cyclone filters and a filter press.", tko="소재·환경", ten="Materials", status="시제품", statusen="Prototype"),
                   dict(nko="미생물 배양수조", nen="Microbe culture tank", dko="육상양식 BFT 시스템용 미생물 자동 배양수조. 2단 구조로 순환·DO를 공급해 RAS에 투입.", den="An automated microbe culture tank for land-based BFT/RAS aquaculture systems.", tko="양식장비", ten="Aqua-equipment", status="개발중", statusen="In development"),
                   dict(nko="Header Pipe", nen="Header Pipe", dko="공조시스템(열교환기·콘덴서 등)에 적용되는 브레이징 가능 2종 알루미늄 Clad AL Pipe.", den="Brazable dual-alloy clad-aluminum pipe for HVAC heat exchangers and condensers.", tko="공조부품", ten="HVAC", status="양산중", statusen="In production")],
         metrics=[("4", "수처리 적용분야", "Applications"), ("7", "수행 프로세스", "Process steps"), ("ISO9001", "공조부품 인증", "Certification")]),
    dict(file="cobaltive.html", no="03", color="#A88F63", ink="#6E5D38",
         deep="linear-gradient(160deg,#041821,#5E4F3A 60%,#A88F63 130%)",
         img="biz-cobaltive.jpg", right=False,
         overlay="linear-gradient(150deg,rgba(168,143,99,.5),rgba(94,79,58,.74))", chipbg="rgba(168,143,99,.14)",
         tko="패각 업사이클 디자인", ten="UPCYCLED SHELL DESIGN", nko="코발티브", nen="COBALTIVE",
         dko="버려지는 굴 패각을 ‘패각콘크리트’ 소재로 되살려 가구·오브제·굿즈로 만드는 자원순환 디자인 브랜드입니다.",
         den="A circular-design brand that revives discarded oyster shells into ‘shell-concrete’ furniture, objects, and goods.",
         chips=["패각콘크리트", "업사이클 디자인", "굿즈 · 가구"],
         leadko="코발티브는 버려지는 굴 패각을 자체 ‘패각콘크리트’ 소재로 되살려 스툴·벤치·오브제·굿즈 등 디자인 제품으로 만드는 자원순환 브랜드입니다. 와디즈 펀딩, 오늘의집, 벤처나라 등에서 제품을 선보이며 녹색제품·저탄소제품 인증을 추진하고 있습니다.",
         leaden="COBALTIVE revives discarded oyster shells into its own ‘shell-concrete’ material, crafting stools, benches, objects, and goods. Its products are sold via Wadiz, Ohou, and Venture-Nara, with green- and low-carbon-product certifications in progress.",
         features=[("패각콘크리트 소재", "Shell-concrete material", "굴 패각을 원료로 한 자체 패각콘크리트로 가구·오브제를 성형합니다.", "An in-house shell-concrete made from oyster shells, cast into furniture and objects."),
                   ("업사이클 디자인 제품", "Upcycled design", "스툴·벤치부터 캔들홀더·거치대·굿즈까지 다양한 디자인 제품을 만듭니다.", "From stools and benches to candle holders, stands, and goods."),
                   ("친환경 인증 · 판로", "Certification & channels", "녹색제품·저탄소제품 인증을 추진하며 와디즈·오늘의집·벤처나라 등에서 판매합니다.", "Pursuing green/low-carbon certification, sold via Wadiz, Ohou, and Venture-Nara.")],
         products=[dict(nko="U 스툴", nen="U Stool", dko="패각콘크리트 1인용 스툴(U 타입). 벤처나라 입점.", den="A single-seat shell-concrete stool (U type); listed on Venture-Nara.", tko="가구", ten="Furniture", status="벤처나라 입점", statusen="Retail listed"),
                   dict(nko="큐브 스툴", nen="Cube Stool", dko="패각콘크리트 큐브형 1인용 스툴. 벤처나라 입점.", den="A cube-form shell-concrete stool; listed on Venture-Nara.", tko="가구", ten="Furniture", status="벤처나라 입점", statusen="Retail listed"),
                   dict(nko="U 벤치", nen="U Bench", dko="패각콘크리트 2인용 벤치(U 타입).", den="A two-seat shell-concrete bench (U type).", tko="가구", ten="Furniture", status="심사 진행중", statusen="Under review"),
                   dict(nko="부여석조여래좌상 홀더", nen="Buyeo Buddha Holder", dko="보물 329호 부여석조여래좌상 3D 데이터를 활용한 인센스·캔들홀더 굿즈. 와디즈 펀딩 완료.", den="An incense/candle holder based on 3D data of Treasure No.329; Wadiz funding completed.", tko="오브제", ten="Object", status="펀딩 완료", statusen="Funded"),
                   dict(nko="가족오브제", nen="Family Object", dko="아빠·엄마·아이로 구성된 3인 가족 오브제(구성 추가 가능). 오늘의집 판매.", den="A three-piece family object set; sold on Ohou.", tko="오브제", ten="Object", status="오늘의집 판매", statusen="On sale"),
                   dict(nko="소라홀더", nen="Conch Holder", dko="에어플랜트(이오난사)용 소라 모양 오브제 — 패각이 다시 소라로. 오늘의집 판매.", den="A conch-shaped holder for air plants — shell reborn as shell; sold on Ohou.", tko="오브제", ten="Object", status="오늘의집 판매", statusen="On sale")],
         metrics=[("패각콘크리트", "핵심 소재", "Core material"), ("10+", "제품 라인업", "Product lines"), ("녹색·저탄소", "인증 추진", "Eco-cert (WIP)")]),
    dict(file="susinje-farm.html", no="04", color="#3E7C4F", ink="#3E7C4F", coming_soon=True,
         deep="linear-gradient(160deg,#041821,#2A5A38 60%,#3E7C4F 130%)",
         img="biz-susinje.jpg", right=True,
         overlay="linear-gradient(150deg,rgba(62,124,79,.46),rgba(36,82,50,.72))", chipbg="rgba(62,124,79,.1)",
         tko="스마트팜 · 유통", ten="SMART FARM · DISTRIBUTION", nko="수신제팜", nen="SUSINJE FARM",
         dko="에이엠피와 함께하는 기업으로, 스마트팜·유통 분야에서 준비 중입니다.",
         den="A partner company of AMP in the smart-farm and distribution field — details in preparation.",
         chips=["스마트팜", "유통", "준비 중"],
         leadko="수신제팜은 에이엠피와 함께하는 기업입니다. 스마트팜·유통 분야의 상세 사업·제품 소개는 준비 중이며, 확정되는 대로 순차적으로 공개할 예정입니다.",
         leaden="SUSINJE FARM is a partner company of AMP. Its detailed business and product information in smart farming and distribution is in preparation and will be published as it is confirmed.",
         features=[],
         products=[],
         metrics=[]),
]
# AMP leads the family ordering (shown first across the site)
BIZ = [c for c in BIZ if c["file"] == "amp.html"] + [c for c in BIZ if c["file"] != "amp.html"]
BIZ_BY_FILE = {c["file"]: c for c in BIZ}

# maps affiliate file -> (1-based news index, careers slug) for cross-linking
AFFILIATE_LINKS = {
    "culiver-aqua.html": (1, "culiver"),
    "amp.html": (4, "amp"),
    "cobaltive.html": (2, "cobaltive"),
    "susinje-farm.html": (3, "susinje"),
}

NEWS = [
    dict(tagko="보도자료", tagen="Press", date="2025.05", title="컬리버, 복합 유용미생물제제 출시",
         titleen="CULIVER launches its complex probiotic agent",
         overlay="linear-gradient(150deg,rgba(14,78,120,.32),rgba(10,44,70,.55))", cover="linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.7))",
         photo="news-1.jpg", color="#0E4E78", chipbg="rgba(14,78,120,.08)", biz="culiver-aqua.html",
         body=["컬리버가 바실러스·락토바실러스 등 6종을 조합한 복합 유용미생물제제 ‘컬리버 1호’를 출시했습니다. 사육수 수질을 개선하고 유해균을 억제해 흰다리새우 양식의 안정성을 높입니다.",
               "회사는 복합 유용미생물 조성물 및 배합에 대한 특허 출원을 진행 중이며, 유용미생물 투입과 질병 조기진단을 결합해 생존율을 크게 끌어올리고 있습니다."]),
    dict(tagko="소식", tagen="Updates", date="2025.04", title="코발티브, 패각콘크리트 제품 와디즈 펀딩·오늘의집 입점",
         titleen="COBALTIVE: shell-concrete goods funded on Wadiz, listed on Ohou",
         overlay="linear-gradient(150deg,rgba(168,143,99,.3),rgba(94,79,58,.55))", cover="linear-gradient(150deg,rgba(168,143,99,.5),rgba(94,79,58,.7))",
         photo="news-2.jpg", color="#6E5D38", chipbg="rgba(168,143,99,.14)", biz="cobaltive.html",
         body=["코발티브가 버려지는 굴 패각을 되살린 ‘패각콘크리트’ 디자인 제품으로 와디즈 펀딩을 완료하고 오늘의집·벤처나라 등 판로를 넓히고 있습니다. 스툴·벤치·오브제·굿즈 등 다양한 라인업을 선보입니다.",
               "패각콘크리트 가구는 녹색제품·저탄소제품 인증을 추진 중이며, 버려지던 패각을 자원으로 되살려 순환의 고리를 완성합니다."]),
    dict(tagko="보도자료", tagen="Press", date="2026.03", title="에이엠피, 벤처기업 확인(혁신성장유형) 획득",
         titleen="AMP certified as a venture firm (innovation-growth type)",
         overlay="linear-gradient(150deg,rgba(27,110,125,.3),rgba(12,58,71,.55))", cover="linear-gradient(150deg,rgba(27,110,125,.5),rgba(12,58,71,.7))",
         photo="news-3.jpg", color="#14606E", chipbg="rgba(27,110,125,.1)", biz="amp.html",
         body=["유한회사 에이엠피가 벤처기업 확인(혁신성장유형)을 획득했습니다. 수처리 설비 설계·제작 역량과 이차전지 공정장비·공조부품 제조 기술의 혁신성을 인정받았습니다.",
               "에이엠피는 앞서 뿌리기업 확인(한국생산기술연구원)과 전라남도지사 표창도 받았습니다."]),
    dict(tagko="보도자료", tagen="Press", date="2025.02", title="에이엠피, 이차전지 전구체 공침반응기 시제품 완성",
         titleen="AMP completes a prototype co-precipitation reactor for battery precursors",
         overlay="linear-gradient(150deg,rgba(27,110,125,.3),rgba(12,58,71,.55))", cover="linear-gradient(150deg,rgba(27,110,125,.5),rgba(12,58,71,.7))",
         photo="news-4.jpg", color="#14606E", chipbg="rgba(27,110,125,.1)", biz="amp.html",
         body=["에이엠피가 NCM(니켈·코발트·망간) 삼원계 전구체 생산용 공침반응기(5L) 시제품을 완성했습니다. pH·교반·온도 조건을 정밀 제어해 전구체를 생산하며, 내부 테스트를 거쳐 대학 연구기관 납품을 앞두고 있습니다.",
               "에이엠피는 이차전지 생산 과정에서 발생하는 망초폐수(Na₂SO₄)를 처리해 공정수로 재순환하는 시스템도 함께 개발하고 있습니다."]),
    dict(tagko="채용", tagen="Hiring", date="2025.11", title="에이엠피, 수처리 설비 현장 인력 채용",
         titleen="AMP is hiring for water-treatment system projects",
         overlay="linear-gradient(150deg,rgba(11,36,56,.34),rgba(8,24,38,.6))", cover="linear-gradient(150deg,rgba(11,36,56,.55),rgba(8,24,38,.75))",
         photo="news-5.jpg", color="#06202B", chipbg="rgba(6,32,43,.08)", biz="amp.html",
         body=["유한회사 에이엠피가 수처리 설비 제작·설치 현장과 공조부품 제조 분야에서 함께할 인재를 모집합니다.",
               "자세한 직무 내용과 지원 방법은 채용 페이지에서 확인하실 수 있습니다."]),
    dict(tagko="소식", tagen="Updates", date="2024.12", title="컬리버, 기업부설연구소 설립·벤처기업 확인·TIPS 선정",
         titleen="CULIVER: R&D lab established, venture-firm certified, selected for TIPS",
         overlay="linear-gradient(150deg,rgba(14,78,120,.3),rgba(10,44,70,.55))", cover="linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.7))",
         photo="news-6.jpg", color="#0E4E78", chipbg="rgba(14,78,120,.08)", biz="culiver-aqua.html",
         body=["컬리버가 기업부설연구소를 설립하고 벤처기업 확인, 전남 청년기업 인증, 정부 TIPS 프로그램 선정 등 기술 기반과 성장 동력을 확보했습니다.",
               "Shrimp365 상표와 아쿠아포닉스 특허를 확보했으며, 데이터 기반 양식 관리 플랫폼 개발을 가속하고 있습니다."]),
]

# inline first-mention hyperlinks inside article bodies (terms guaranteed to
# appear in the corresponding body text above)
NEWS[0]["body"] = linkify_first(NEWS[0]["body"], "컬리버 1호", "culiver-aqua.html")
NEWS[1]["body"] = linkify_first(NEWS[1]["body"], "패각콘크리트", "cobaltive.html")
NEWS[3]["body"] = linkify_first(NEWS[3]["body"], "에이엠피", "amp.html")
NEWS[4]["body"] = linkify_first(NEWS[4]["body"], "채용 페이지", "careers.html")
NEWS[5]["body"] = linkify_first(NEWS[5]["body"], "Shrimp365", "culiver-aqua.html")

ROLES = [
    dict(slug="culiver", biz="culiver-aqua.html", color="#0E4E78",
         role_ko="양식 생산·관리 매니저", role_en="Aquaculture Production Manager",
         team_ko="컬리버", team_en="CULIVER",
         loc_ko="전남 순천", loc_en="Suncheon, Jeonnam",
         type_ko="정규직", type_en="Full-time",
         duties=[("복합 유용미생물 투입·사육수 수질 관리", "Manage probiotic dosing and rearing-water quality"),
                 ("생산 일정·입식·출하 관리", "Plan production, stocking, and harvest"),
                 ("Shrimp365 데이터 기반 사육 관리", "Run data-driven husbandry with Shrimp365")],
         quals=[("수산·생물 관련 전공 또는 양식 경력", "Degree in fisheries/biology or aquaculture experience"),
                ("데이터 기반 생산 관리에 대한 이해", "Understanding of data-driven production"),
                ("현장 근무 가능자", "Willing to work on-site")],
         plus=[("흰다리새우 양식 경험", "Whiteleg shrimp farming experience"),
               ("관련 자격증 보유", "Relevant certifications")]),
    dict(slug="amp", biz="amp.html", color="#14606E",
         role_ko="소재 · 환경 엔지니어", role_en="Materials & Environment Engineer",
         team_ko="에이엠피", team_en="AMP",
         loc_ko="전남 광양", loc_en="Gwangyang, Jeonnam",
         type_ko="정규직", type_en="Full-time",
         duties=[("이차전지 전구체 장비(공침반응기 등) 설계·운영", "Design and operate battery-precursor equipment"),
                 ("망초폐수·공정수 처리 및 재순환 시스템 개발", "Develop wastewater / process-water recirculation systems"),
                 ("공조 부품 등 소재·환경 프로젝트 지원", "Support HVAC-component and other materials projects")],
         quals=[("환경·화공·기계 관련 전공", "Degree in environmental/chemical/mechanical engineering"),
                ("공정·설비에 대한 이해", "Understanding of processes and equipment"),
                ("설비 현장 대응 가능자", "Able to respond on-site")],
         plus=[("이차전지 소재·수처리 경험", "Battery-materials or water-treatment experience"),
               ("관련 기사 자격증", "Relevant engineering license")]),
    dict(slug="cobaltive", biz="cobaltive.html", color="#6E5D38",
         role_ko="제품 디자이너", role_en="Product Designer",
         team_ko="코발티브", team_en="COBALTIVE",
         loc_ko="전남 순천 (협의)", loc_en="Suncheon (negotiable)",
         type_ko="정규직", type_en="Full-time",
         duties=[("패각콘크리트 기반 가구·오브제·굿즈 디자인", "Design shell-concrete furniture, objects, and goods"),
                 ("3D 데이터·성형·시제품 제작 협업", "Collaborate on 3D data, casting, and prototyping"),
                 ("펀딩·입점 등 상품화·판로 지원", "Support commercialization and retail channels")],
         quals=[("제품·산업·공예 디자인 전공 또는 경력", "Degree/experience in product, industrial, or craft design"),
                ("3D 모델링 등 제작 역량", "3D modeling and making skills"),
                ("협업 능력", "Collaboration skills")],
         plus=[("업사이클·친환경 제품 경험", "Upcycled / eco-product experience"),
               ("펀딩·커머스 경험", "Crowdfunding or commerce experience")]),
    dict(slug="susinje", biz="susinje-farm.html", color="#3E7C4F",
         role_ko="스마트팜 · 유통 직무 (준비 중)", role_en="Smart-farm & distribution (soon)",
         team_ko="수신제팜", team_en="SUSINJE FARM",
         loc_ko="전남 순천 (협의)", loc_en="Suncheon (negotiable)",
         type_ko="상시", type_en="Ongoing",
         duties=[("스마트팜·유통 분야 채용은 준비 중입니다", "Hiring for smart-farm & distribution is in preparation"),
                 ("관심 있는 분은 문의를 남겨 주세요", "Interested candidates are welcome to reach out")],
         quals=[("스마트팜·유통 분야에 대한 관심", "Interest in smart farming / distribution")],
         plus=[]),
]

VALUES = """      <div class="values reveal">
        <div class="value">
          <span class="value-no" style="color:#0E4E78">01</span>
          <div class="value-body">
            <h3><span class="t-ko">전문성 Professionalism</span><span class="t-en">Professionalism</span></h3>
            <p class="t-ko">현장 경험과 기술로 수처리 설비를 직접 설계·제작합니다. 자체 공장에서 구조물과 장치를 만듭니다.</p>
            <p class="t-en">We design and build water-treatment systems with real field experience, fabricating the structures and devices in our own shop.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#166578">02</span>
          <div class="value-body">
            <h3><span class="t-ko">신뢰 Trust</span><span class="t-en">Trust</span></h3>
            <p class="t-ko">작업표준서 기반 품질관리와 현장에 맞춘 사후관리로 신뢰받는 파트너가 됩니다.</p>
            <p class="t-en">Standardized quality control and site-specific aftercare make us a partner you can rely on.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#3E7C4F">03</span>
          <div class="value-body">
            <h3><span class="t-ko">도전 Challenge</span><span class="t-en">Challenge</span></h3>
            <p class="t-ko">수처리·소재·환경의 새로운 분야에 끊임없이 도전하며, 창조적 혁신으로 가치를 만듭니다.</p>
            <p class="t-en">We keep taking on new fields in water, materials and environment, creating value through innovation.</p>
          </div>
        </div>
      </div>
"""

# short homepage teaser version — avoids repeating about.html's full copy verbatim
VALUES_TEASER = """      <div class="values reveal">
        <div class="value">
          <span class="value-no" style="color:#0E4E78">01</span>
          <div class="value-body">
            <h3><span class="t-ko">순환 Circularity</span><span class="t-en">Circularity</span></h3>
            <p class="t-ko">부산물이 다음 사업의 원료가 됩니다.</p>
            <p class="t-en">One business's byproduct becomes the next one's raw material.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#166578">02</span>
          <div class="value-body">
            <h3><span class="t-ko">기술 Technology</span><span class="t-en">Technology</span></h3>
            <p class="t-ko">미생물과 데이터로 1차산업의 방식을 바꿉니다.</p>
            <p class="t-en">Changing how primary industry works, with microbes and data.</p>
          </div>
        </div>
        <div class="value">
          <span class="value-no" style="color:#3E7C4F">03</span>
          <div class="value-body">
            <h3><span class="t-ko">상생 Coexistence</span><span class="t-en">Coexistence</span></h3>
            <p class="t-ko">바다와 지역사회와 함께 성장합니다.</p>
            <p class="t-en">Growing together with the sea and local communities.</p>
          </div>
        </div>
      </div>
"""

ESG_CARDS = """      <div class="esg-grid reveal">
        <div class="esg-card">
          <span class="label">E — ENVIRONMENT</span>
          <h3><span class="t-ko">자원의 재순환</span><span class="t-en">Circular resources</span></h3>
          <p class="t-ko">굴 패각 업사이클, 복합 유용미생물 기반 양식, 이차전지 공정수 재순환으로 폐기물과 배출을 구조적으로 줄입니다.</p>
          <p class="t-en">Shell upcycling, probiotic-based aquaculture, and battery process-water recirculation structurally cut waste and emissions.</p>
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

# short homepage teaser version — avoids repeating sustainability.html's full copy verbatim
ESG_TEASER = """      <div class="esg-grid reveal">
        <div class="esg-card">
          <span class="label">E — ENVIRONMENT</span>
          <h3><span class="t-ko">자원의 재순환</span><span class="t-en">Circular resources</span></h3>
          <p class="t-ko">패각 업사이클과 공정수 재순환으로 폐기물을 줄입니다.</p>
          <p class="t-en">Shell upcycling and process-water recirculation cut waste.</p>
        </div>
        <div class="esg-card">
          <span class="label">S — SOCIAL</span>
          <h3><span class="t-ko">어촌·산지와의 상생</span><span class="t-en">Coexisting communities</span></h3>
          <p class="t-ko">생산 현장의 지역사회와 가치를 나눕니다.</p>
          <p class="t-en">We share value with the communities where we produce.</p>
        </div>
        <div class="esg-card">
          <span class="label">G — GOVERNANCE</span>
          <h3><span class="t-ko">투명한 순환 경영</span><span class="t-en">Transparent governance</span></h3>
          <p class="t-ko">데이터 기반의 투명한 의사결정을 지향합니다.</p>
          <p class="t-en">We pursue transparent, data-driven decisions.</p>
        </div>
      </div>
"""

CYCLE_BLOCK = """      <div class="cycle-grid reveal">
        <div class="ring" id="ring">
          <div class="ring-dash"></div>
          <div class="ring-core">
            <span class="role" id="ringRole" style="color:#0E4E78">스마트양식</span>
            <span class="ko" id="ringKo">컬리버</span>
            <span class="en" id="ringEn">CULIVER</span>
          </div>
          <button class="node active" data-i="0" data-no="01" data-name-ko="컬리버" data-name-en="CULIVER" data-role="스마트양식" data-color="#0E4E78"
            data-dko="프리미엄 사료·복합 유용미생물·질병 진단·데이터로 흰다리새우를 표준 공정으로 기릅니다. 순환의 출발점입니다."
            data-den="Whiteleg shrimp raised as a standard process — premium feed, probiotics, diagnostics, and data. The start of the loop."
            style="top:2%;left:50%;background:#0E4E78;box-shadow:0 16px 34px -12px #0E4E78">
            <span class="no">01</span><span class="nm">컬리버</span>
          </button>
          <button class="node" data-i="1" data-no="02" data-name-ko="에이엠피" data-name-en="AMP" data-role="소재·환경" data-color="#14606E"
            data-dko="이차전지 소재·장비와 폐수·공정수 처리 기술을 다루고, 육상양식용 미생물 배양수조로 양식 사업과 이어집니다."
            data-den="Battery materials/equipment and water treatment — linked back to aquaculture through microbe culture tanks."
            style="top:50%;left:98%">
            <span class="no">02</span><span class="nm">에이엠피</span>
          </button>
          <button class="node" data-i="2" data-no="03" data-name-ko="수신제팜" data-name-en="SUSINJE" data-role="스마트팜·유통" data-color="#3E7C4F"
            data-dko="스마트팜·유통 분야의 계열사입니다. 상세 사업 소개는 준비 중입니다."
            data-den="A smart-farm & distribution affiliate — details in preparation."
            style="top:98%;left:50%">
            <span class="no">03</span><span class="nm">수신제팜</span>
          </button>
          <button class="node" data-i="3" data-no="04" data-name-ko="코발티브" data-name-en="COBALTIVE" data-role="패각 업사이클" data-color="#6E5D38"
            data-dko="버려지는 굴 패각을 ‘패각콘크리트’로 되살려 가구·오브제로 만듭니다. 컬리버가 쓰는 패각 자원과 이어지는 순환의 고리입니다."
            data-den="Discarded oyster shells reborn as ‘shell-concrete’ furniture and objects — closing the shell-resource loop."
            style="top:50%;left:2%">
            <span class="no">04</span><span class="nm">코발티브</span>
          </button>
        </div>
        <div class="cycle-detail">
          <span class="cycle-badge" id="cycleBadge" style="background:#0E4E78">01</span>
          <h3 id="cycleTitle"><span class="t-ko">컬리버</span><span class="t-en">CULIVER</span> · <span style="color:#0E4E78">스마트양식</span></h3>
          <p class="t-ko" id="cycleDescKo">프리미엄 사료·복합 유용미생물·질병 진단·데이터로 흰다리새우를 표준 공정으로 기릅니다. 순환의 출발점입니다.</p>
          <p class="t-en" id="cycleDescEn">Whiteleg shrimp raised as a standard process — premium feed, probiotics, diagnostics, and data. The start of the loop.</p>
          <div class="cycle-dots" id="cycleDots">
            <span class="active" style="background:#0E4E78"></span><span></span><span></span><span></span>
          </div>
        </div>
      </div>
"""

HISTORY_BLOCK = """      <div class="hist-years reveal" id="histYears">
        <button class="hist-year active" data-i="0" data-color="#14606E" data-tko="중소벤처기업청장 상장" data-ten="SMBA commissioner award"
          data-dko="광주·전남지방중소벤처기업청장 상장을 수상했습니다(모범적인 기업경영)."
          data-den="Received a commendation from the Gwangju·Jeonnam SMBA commissioner for exemplary management."
          style="background:#14606E;border-color:#14606E">2024</button>
        <button class="hist-year" data-i="1" data-color="#1B6E7D" data-tko="사업 개시 · 뿌리기업·표창·지점" data-ten="Founded · certs · branch"
          data-dko="유한회사 에이엠피 사업을 개시(2025.01)하고, 뿌리기업 확인(한국생산기술연구원), 전라남도지사 표창, 여수 융합지구 지점 등록을 이어갔습니다."
          data-den="AMP began operations (Jan 2025), then earned Root-industry certification, a Jeonnam governor's commendation, and registered its Yeosu branch.">2025</button>
        <button class="hist-year" data-i="2" data-color="#4FA3A5" data-tko="벤처기업 확인 · 사업 확장" data-ten="Venture cert · growth"
          data-dko="벤처기업 확인(혁신성장유형, 2026.03)을 받고, 스마트제조 전환지원·AI솔루션 구축지원 사업을 수행했습니다."
          data-den="Certified as a venture firm (innovation-growth type, Mar 2026) and carried out smart-manufacturing and AI-solution support projects.">2026</button>
        <button class="hist-year" data-i="3" data-color="#06202B" data-tko="수처리 전문기업으로" data-ten="A water-treatment specialist"
          data-dko="현장 맞춤 수처리 설비와 데이터 기반 물관리로, 수처리·소재·환경을 아우르는 신뢰받는 파트너가 되겠습니다."
          data-den="With site-specific water systems and data-driven management, becoming a trusted partner across water, materials and environment."
          style="">비전</button>
      </div>
      <div class="hist-detail">
        <div class="hist-big" id="histBig" style="color:#14606E">2024</div>
        <div class="hist-text">
          <h3 id="histTitle"><span class="t-ko">중소벤처기업청장 상장</span><span class="t-en">SMBA commissioner award</span></h3>
          <p class="t-ko" id="histDescKo">광주·전남지방중소벤처기업청장 상장을 수상했습니다(모범적인 기업경영).</p>
          <p class="t-en" id="histDescEn">Received a commendation from the Gwangju·Jeonnam SMBA commissioner for exemplary management.</p>
        </div>
      </div>
"""

FORM_BLOCK = """      <div class="form-wrap reveal" id="formWrap">
        <form class="form" id="contactForm">
          <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="form-row">
            <label>
              <span class="lbl"><span class="t-ko">이름</span><span class="t-en">Name</span></span>
              <input name="name" placeholder="홍길동" data-ph-ko="홍길동" data-ph-en="e.g. John Doe" required autocomplete="name">
            </label>
            <label>
              <span class="lbl"><span class="t-ko">이메일</span><span class="t-en">Email</span></span>
              <input type="email" name="email" placeholder="you@example.com" required autocomplete="email">
            </label>
          </div>
          <div class="form-row">
            <label>
              <span class="lbl"><span class="t-ko">회사·소속</span><span class="t-en">Company</span></span>
              <input name="company" placeholder="회사명 / 소속" data-ph-ko="회사명 / 소속" data-ph-en="e.g. your company" autocomplete="organization">
            </label>
            <label>
              <span class="lbl"><span class="t-ko">문의 유형</span><span class="t-en">Inquiry type</span></span>
              <!-- native <option> can't hold t-ko/t-en spans; value stays the
                   fixed Korean string (matched elsewhere, e.g. prefillFromQuery),
                   main.js swaps the displayed label from data-ko/data-en -->
              <select name="type">
                <option value="사업 제휴" data-ko="사업 제휴" data-en="Business partnership">사업 제휴</option>
                <option value="설비·기술상담" data-ko="설비·기술상담" data-en="Systems · technical">설비·기술상담</option>
                <option value="제품 · 구매" data-ko="제품 · 구매" data-en="Product · Purchase">제품 · 구매</option>
                <option value="채용" data-ko="채용" data-en="Careers">채용</option>
                <option value="기타" data-ko="기타" data-en="Other">기타</option>
              </select>
            </label>
          </div>
          <label>
            <span class="lbl-row">
              <span class="lbl"><span class="t-ko">내용</span><span class="t-en">Message</span></span>
              <span class="counter" id="msgCounter">0 / 4000</span>
            </span>
            <textarea name="message" rows="4" maxlength="4000" placeholder="문의 내용을 입력하세요" data-ph-ko="문의 내용을 입력하세요" data-ph-en="Enter your message" required></textarea>
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
        <h2 class="h2 t-ko">함께 일하거나<br>협업하고 싶다면</h2>
        <h2 class="h2 t-en">Want to work or partner with us?</h2>
        <div class="contact-info">
          <div class="kv"><span class="kv-k"><span class="t-ko">회사</span><span class="t-en">COMPANY</span></span><span class="kv-v"><span class="t-ko">유한회사 에이엠피 · 대표이사 안명원</span><span class="t-en">AMP Co., Ltd. · CEO Ahn Myung-won</span></span></div>
          <div class="kv"><span class="kv-k">WEB</span><span class="kv-v">amp0404.co.kr</span></div>
          <div class="kv">
            <span class="kv-k"><span class="t-ko">주소</span><span class="t-en">ADDRESS</span></span>
            <span class="addr t-ko">전남 광양시 광양읍 익신산단3길 40, 409호</span>
            <span class="addr t-en">409, 40 Iksinsandan 3-gil, Gwangyang-eup, Gwangyang, Jeonnam, Korea</span>
          </div>
          <div class="kv"><span class="kv-k">EMAIL · TEL</span><span class="kv-v"><span class="t-ko">준비 중입니다. 아래 폼으로 남겨 주세요</span><span class="t-en">Coming soon — please use the form below</span></span></div>
        </div>
      </div>
"""


def biz_cards():
    out = ""
    for c in BIZ:
        rc = " img-right" if c["right"] else ""
        chip_html = "".join(f'<span class="chip" style="color:{c["ink"]};background:{c["chipbg"]}">{x}</span>' for x in c["chips"])
        out += f"""        <a href="{c['file']}" class="biz-card">
          <div class="biz-media{rc}" role="img" aria-label="{c['nko']} {c['tko']} 이미지" style="background-image:{c['overlay']},url('assets/img/{c['img']}')">
            <span class="biz-no">{c['no']}</span>
          </div>
          <div class="biz-body">
            <p class="biz-tag" style="color:{c['ink']}"><span class="t-ko">{c['tko']}</span><span class="t-en">{c['ten']}</span></p>
            <h3 class="biz-name"><span class="t-ko">{c['nko']}</span><span class="t-en">{c['nen']}</span><span class="rom t-ko">{c['nen']}</span></h3>
            <p class="biz-desc t-ko">{c['dko']}</p>
            <p class="biz-desc t-en">{c['den']}</p>
            <div class="chips">{chip_html}</div>
            <span class="link-arrow" style="color:{c['ink']}"><span class="t-ko">자세히 보기</span><span class="t-en">Learn more</span> →</span>
          </div>
        </a>
"""
    return out


def biz_bento():
    out = ""
    for i, c in enumerate(BIZ):
        large = " bento-lg" if i == 0 else ""
        # role="img" sits on a decorative inner layer, not the <a> itself,
        # so the tile keeps its native "link" role/name from its own
        # visible text (bento-tag/bento-name) instead of being replaced
        # by a single Korean-only aria-label.
        out += f"""        <a href="{c['file']}" class="bento-tile{large}">
          <span class="bento-bg" role="img" aria-label="{c['nko']} {c['tko']} 이미지" style="background-image:{c['overlay']},url('assets/img/{c['img']}')"></span>
          <span class="bento-no">{c['no']}</span>
          <p class="bento-tag"><span class="t-ko">{c['tko']}</span><span class="t-en">{c['ten']}</span></p>
          <h3 class="bento-name"><span class="t-ko">{c['nko']}</span><span class="t-en">{c['nen']}</span><span class="rom t-ko">{c['nen']}</span></h3>
        </a>
"""
    return out


def news_cards(limit=None):
    """Server-rendered seed snapshot used as (a) the no-JS fallback and
    (b) instant first paint before assets/js/main.js's setupNews() fetches
    /api/news and replaces this with the live, admin-managed list — so
    admin edits/deletes/new posts show up for JS users, while no-JS
    visitors still see a working (if static) newsroom."""
    out = ""
    for i, n in enumerate(NEWS[:limit]):
        out += f"""        <a href="news.html?id=news-{i+1}" class="news-card" data-tag="{n['tagko']}">
          <div class="news-photo" role="img" aria-label="{n['title']} 관련 이미지" style="background-image:{n['overlay']},url('assets/img/{n['photo']}')"></div>
          <div class="news-body">
            <div class="news-meta"><span class="news-tag" style="color:{n['color']};background:{n['chipbg']}"><span class="t-ko">{n['tagko']}</span><span class="t-en">{n['tagen']}</span></span><span class="news-date">{n['date']}</span></div>
            <h3><span class="t-ko">{n['title']}</span><span class="t-en">{n['titleen']}</span></h3>
            <span class="news-arrow">→</span>
          </div>
        </a>
"""
    return out


def roles_list():
    out = ""
    for r in ROLES:
        out += f"""        <a href="careers-{r['slug']}.html" class="role">
          <span class="role-title"><span class="t-ko">{r['role_ko']}</span><span class="t-en">{r['role_en']}</span></span>
          <span class="role-team" style="color:{r['color']}"><span class="t-ko">{r['team_ko']}</span><span class="t-en">{r['team_en']}</span></span>
          <span class="role-loc"><span class="t-ko">{r['loc_ko']}</span><span class="t-en">{r['loc_en']}</span></span>
          <span class="role-type"><span class="t-ko">{r['type_ko']}</span><span class="t-en">{r['type_en']}</span> →</span>
        </a>
"""
    return out


def write(name, body, active=None, subpage=True):
    cls = ' class="subpage"' if subpage else ""
    title, desc = TITLES.get(name, (name, ""))
    html = (
        head(title, desc)
        + f'<body data-lang="ko"{cls}>\n'
        + LANG_RESTORE_SCRIPT
        + "\n"
        + header(active if subpage else None)
        + mobile_menu()
        + body
        + FOOTER
    )
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name, f"({len(html)} bytes)")


TITLES = {
    "index.html": ("에이엠피 AMP — 현장에 맞춘 설비, 데이터로 관리하는 물",
                   "에이엠피(AMP)는 이차전지 폐수처리·공정수 재순환·육상양식·제약화학 수처리 시스템 설비를 설계·제작·설치하고, 실시간 수질 모니터링을 제공합니다."),
    "about.html": ("회사소개 About — 에이엠피 AMP", "수처리·물 매니지먼트 전문기업 에이엠피(AMP)의 인사말·연혁·조직·회사 개요를 소개합니다."),
    "business.html": ("사업영역 Business — 에이엠피 AMP", "이차전지 폐수처리·공정수 재순환·육상양식·제약화학 수처리 설비. 에이엠피(AMP)의 사업영역."),
    "sustainability.html": ("지속가능경영 Sustainability — 에이엠피 AMP", "폐수를 처리해 다시 쓰고, 자원을 순환시키는 일이 곧 에이엠피(AMP)의 사업입니다."),
    "ir.html": ("실적·인증 — 에이엠피 AMP", "에이엠피(AMP)의 시장 기회, 주요 지표, 인증·실적을 소개합니다."),
    "newsroom.html": ("뉴스룸 Newsroom — 에이엠피 AMP", "에이엠피(AMP)의 보도자료·소식·채용 소식을 전합니다."),
    "news.html": ("뉴스룸 Newsroom — 에이엠피 AMP", "에이엠피(AMP)의 보도자료·소식·채용 소식을 전합니다."),
    "careers.html": ("채용 Careers — 에이엠피 AMP", "수처리 설비 현장에서 함께 일할 사람을 찾습니다. 인재상·채용 절차·공고·복리후생 안내."),
    "contact.html": ("문의 Contact — 에이엠피 AMP", "수처리 설비·기술상담, 사업 제휴, 제품·구매, 채용 등 에이엠피(AMP)에 문의하세요."),
}
for _c in BIZ:
    TITLES[_c["file"]] = (f"{_c['nko']} {_c['nen']} — 에이엠피 AMP", _c["dko"])
for _r in ROLES:
    TITLES[f"careers-{_r['slug']}.html"] = (f"{_r['role_ko']} ({_r['team_ko']}) 채용 — 에이엠피 AMP", f"{_r['team_ko']} {_r['role_ko']} 채용 공고")

# ================================================================= HOME
home = f"""  <section id="top" class="hero">
    <div class="hero-glow"></div>
    <div class="hero-inner">
      <p class="hero-eyebrow">AMP · WATER MANAGEMENT</p>
      <h1 class="t-ko">현장에 맞춘 설비,<br>데이터로 관리하는 물</h1>
      <h1 class="t-en">Water systems built for the site,<br>managed by data</h1>
      <p class="hero-lead t-ko">에이엠피(AMP)는 수처리 시스템 설비의 설계·제작·설치·시운전부터 실시간 수질 모니터링까지 맡습니다. 이차전지 공정 설비와 공조부품 제조 기술이 그 바탕입니다.</p>
      <p class="hero-lead t-en">AMP designs, builds, installs and commissions water-treatment systems, and monitors water quality in real time. Battery-process equipment and HVAC-parts manufacturing are the foundation.</p>
      <div class="hero-cta">
        <a href="amp.html" class="btn btn-primary"><span class="t-ko">수처리 솔루션 보기</span><span class="t-en">Water solutions</span><span>→</span></a>
        <a href="contact.html" class="btn btn-ghost"><span class="t-ko">견적·기술상담</span><span class="t-en">Get a quote</span></a>
      </div>
    </div>
    <div class="scroll-hint"><span>SCROLL</span><span class="bar"></span></div>
  </section>

  <section class="stats">
    <div class="wrap stats-grid reveal">
      <div class="stat"><div class="stat-num"><span class="val" data-count="7">7</span><span class="suffix">단계</span></div><span class="stat-label"><span class="t-ko">수행 프로세스</span><span class="t-en">Process steps</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="4">4</span><span class="suffix">분야</span></div><span class="stat-label"><span class="t-ko">수처리 적용 분야</span><span class="t-en">Applications</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="6">6</span><span class="suffix">종</span></div><span class="stat-label"><span class="t-ko">수질 측정 항목</span><span class="t-en">Quality metrics</span></span></div>
      <div class="stat"><div class="stat-num"><span class="val" data-count="3">3</span><span class="suffix">개</span></div><span class="stat-label"><span class="t-ko">공신력 인증</span><span class="t-en">Certifications</span></span></div>
    </div>
  </section>

  <section class="section bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">APPLICATION</p>
          <h2 class="h2 t-ko">물이 다르면, 설비도 달라야 합니다</h2>
          <h2 class="h2 t-en">Different water needs different systems</h2>
        </div>
        <a class="more-link" href="amp.html"><span class="t-ko">수처리 전체 보기</span><span class="t-en">All water solutions</span> →</a>
      </div>
      <div class="amp-areas reveal-stagger">
        <article class="amp-area">
          <div class="amp-area-img" style="background-image:url('assets/img/amp/area-battery.jpg')" role="img" aria-label="이차전지 폐수처리 Pilot 설비"></div>
          <div class="amp-area-body">
            <span class="amp-area-no">01</span>
            <h3 class="t-ko">이차전지 폐수처리</h3><h3 class="t-en">Battery wastewater</h3>
            <p class="t-ko">전구체·양극재 공정에서 나오는 망초폐수(Na₂SO₄)를 전처리·농축·EDR(전기투석역전)로 처리해 공정수로 재이용합니다.</p>
            <p class="t-en">Sodium-sulfate wastewater from precursor/cathode processes is pre-treated, concentrated and run through EDR, then reused as process water.</p>
          </div>
        </article>
        <article class="amp-area">
          <div class="amp-area-img" style="background-image:url('assets/img/amp/area-recycle.jpg')" role="img" aria-label="공정수 재순환 시스템"></div>
          <div class="amp-area-body">
            <span class="amp-area-no">02</span>
            <h3 class="t-ko">공정수 재순환</h3><h3 class="t-en">Process-water reuse</h3>
            <p class="t-ko">입자 선별·필터 장치로 공정수를 재이용하는 현장 맞춤형 재순환 시스템을 설계·제작합니다.</p>
            <p class="t-en">Site-specific recirculation systems that screen particles and filter process water for reuse.</p>
          </div>
        </article>
        <article class="amp-area">
          <div class="amp-area-img" style="background-image:url('assets/img/amp/area-aqua.jpg')" role="img" aria-label="육상양식 물관리"></div>
          <div class="amp-area-body">
            <span class="amp-area-no">03</span>
            <h3 class="t-ko">육상양식 물관리</h3><h3 class="t-en">Aquaculture water</h3>
            <p class="t-ko">RAS·BFT 양식장의 수질을 센서와 모니터링 프로그램으로 관리하고, 미생물 배양수조를 제작합니다.</p>
            <p class="t-en">Sensor-based monitoring for RAS/BFT farms, plus microbe culture tanks we build in-house.</p>
          </div>
        </article>
        <article class="amp-area">
          <div class="amp-area-img" style="background-image:url('assets/img/amp/area-pharma.jpg')" role="img" aria-label="제약·화학 폐수처리"></div>
          <div class="amp-area-body">
            <span class="amp-area-no">04</span>
            <h3 class="t-ko">제약·화학 폐수처리</h3><h3 class="t-en">Pharma &amp; chemical</h3>
            <p class="t-ko">원수 성상을 분석해 현장마다 다른 폐수에 맞춘 수처리 시스템을 설계·제작·설치합니다.</p>
            <p class="t-en">We analyze each influent and build treatment systems matched to that site's wastewater.</p>
          </div>
        </article>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap amp-split reveal">
      <div class="amp-split-text">
        <p class="eyebrow">PROCESS · MONITORING</p>
        <h2 class="h2 t-ko">진단에서 유지관리까지,<br>데이터로 관리합니다</h2>
        <h2 class="h2 t-en">From diagnosis to upkeep,<br>managed by data</h2>
        <p class="t-ko">자체 공장에서 구조물과 장치를 직접 제작하기 때문에 설계 변경에도 빠르게 대응합니다. 수질 센서로 측정한 값을 실시간 프로그램에서 확인하고, 이상이 생기면 알림으로 대응합니다.</p>
        <p class="t-en">We fabricate the structures and devices in our own shop, so design changes are quick. Sensor readings show up in a live program, and anomalies trigger alerts.</p>
        <ol class="amp-steps">
          <li><span class="t-ko">현장·수질 진단</span><span class="t-en">Site &amp; water diagnosis</span></li>
          <li><span class="t-ko">처리목표 설정</span><span class="t-en">Set targets</span></li>
          <li><span class="t-ko">공정설계</span><span class="t-en">Process design</span></li>
          <li><span class="t-ko">Pilot·시제품 제작</span><span class="t-en">Pilot build</span></li>
          <li><span class="t-ko">설비 제작·설치</span><span class="t-en">Build &amp; install</span></li>
          <li><span class="t-ko">시운전</span><span class="t-en">Commissioning</span></li>
          <li><span class="t-ko">모니터링·유지관리</span><span class="t-en">Monitor &amp; maintain</span></li>
        </ol>
        <p class="amp-metrics-line"><span class="t-ko">실시간 측정 항목</span><span class="t-en">Live metrics</span> · pH · EC · 온도 · 탁도 · TDS · DO</p>
      </div>
      <div class="amp-split-img" style="background-image:url('assets/img/amp/monitoring.jpg')" role="img" aria-label="실시간 수질 모니터링 현장"></div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">GROUP</p>
          <h2 class="h2 t-ko">함께하는 기업</h2>
          <h2 class="h2 t-en">Companies we work with</h2>
        </div>
      </div>
      <p class="sub reveal" style="margin:0 0 28px;max-width:640px"><span class="t-ko">수처리를 중심으로, 스마트양식과 자원 업사이클까지 이어집니다.</span><span class="t-en">Water treatment at the center, reaching into smart aquaculture and resource upcycling.</span></p>
      <div class="rel-grid reveal-stagger">
        <article class="rel-card">
          <div class="rel-img" style="background-image:url('assets/img/amp/reactor.jpg')"></div>
          <div class="rel-body">
            <span class="rel-tag">수처리 · 소재·환경</span>
            <h3>에이엠피 <span class="rom">AMP</span></h3>
            <p class="t-ko">수처리 시스템 설비, 이차전지 공정 장비, 공조부품 제조.</p>
            <p class="t-en">Water-treatment systems, battery-process equipment, HVAC parts.</p>
            <a class="more-link" href="amp.html"><span class="t-ko">자세히</span><span class="t-en">More</span> →</a>
          </div>
        </article>
        <article class="rel-card">
          <div class="rel-img" style="background-image:url('assets/img/biz-culiver.jpg')"></div>
          <div class="rel-body">
            <span class="rel-tag">스마트양식 · AI</span>
            <h3>컬리버 <span class="rom">CULIVER</span></h3>
            <p class="t-ko">흰다리새우 스마트양식, 복합 유용미생물·데이터 기반 수질 관리.</p>
            <p class="t-en">Smart whiteleg-shrimp aquaculture with probiotics and data-driven water care.</p>
            <a class="more-link" href="culiver-aqua.html"><span class="t-ko">자세히</span><span class="t-en">More</span> →</a>
          </div>
        </article>
        <article class="rel-card">
          <div class="rel-img" style="background-image:url('assets/img/biz-cobaltive.jpg')"></div>
          <div class="rel-body">
            <span class="rel-tag">자원 업사이클 · 디자인</span>
            <h3>코발티브 <span class="rom">COBALTIVE</span></h3>
            <p class="t-ko">버려지는 굴 패각을 ‘패각콘크리트’ 소재로 되살려 가구·오브제·굿즈로 만듭니다.</p>
            <p class="t-en">Discarded oyster shells reborn as ‘shell-concrete’ furniture, objects and goods.</p>
            <a class="more-link" href="cobaltive.html"><span class="t-ko">자세히</span><span class="t-en">More</span> →</a>
          </div>
        </article>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">NEWSROOM</p>
          <h2 class="h2 t-ko">소식</h2>
          <h2 class="h2 t-en">News</h2>
        </div>
        <a class="more-link" href="newsroom.html"><span class="t-ko">뉴스룸 전체 보기</span><span class="t-en">All news</span> →</a>
      </div>
      <div class="news-grid reveal" id="newsPreview">
{news_cards(3)}      </div>
    </div>
  </section>


  <section class="section bg-card">
    <div class="wrap reveal">
      <div class="cta-band">
        <div>
          <h2><span class="t-ko">함께 성장할 사람을 찾습니다</span><span class="t-en">Grow with us</span></h2>
          <p><span class="t-ko">에이엠피와 계열사의 채용 공고를 확인하세요.</span><span class="t-en">See open roles at AMP and its affiliates.</span></p>
        </div>
        <a class="btn btn-primary" href="careers.html"><span class="t-ko">채용 보기</span><span class="t-en">Careers</span> →</a>
      </div>
    </div>
  </section>
"""
write("index.html", home, active=None, subpage=False)

# ================================================================= ABOUT
about = (
    page_hero("ABOUT AMP", "에이엠피를 소개합니다", "About AMP",
              "현장·수질 진단부터 설비 제작·설치, 모니터링까지 한 흐름으로 수행하는 수처리 전문기업입니다.",
              "A water-treatment company that does it all in one flow — from site and water diagnosis to building, installing and monitoring the systems.",
              [("about.html", "회사소개", "About")])
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div class="greeting reveal">
        <div class="portrait"><span>AMP</span></div>
        <div class="body">
          <p class="t-ko">홈페이지를 방문해 주신 여러분께 감사드립니다. 에이엠피는 수처리·물 매니지먼트 분야에서 현장·수질 진단부터 공정 설계, 설비 제작·설치, 시운전, 모니터링까지 한 흐름으로 수행합니다.</p>
          <p class="t-ko">이차전지 공정 폐수, 공정수 재순환, 육상양식, 제약·화학 폐수까지 현장마다 물의 성상이 다르다는 점에서 출발합니다. 이 사업의 바탕에는 공조부품 제조가 있습니다. Clad Aluminum Header Pipe를 주문 생산하며 쌓은 가공·품질관리 역량이 수처리 설비 제작의 기반입니다. 현장에 맞춘 설계·제작과 사후관리로 신뢰받는 파트너가 되겠습니다.</p>
          <p class="t-en">Thank you for visiting. AMP handles water management end to end — site and water diagnosis, process design, fabrication, installation, commissioning and monitoring. It begins from the fact that every site's water is different. Underneath it is our manufacturing base: the machining and quality control built while producing clad-aluminum header pipe to order now underpins how we build water-treatment systems.</p>
          <div class="sign"><b>유한회사 에이엠피 대표이사 안명원</b><span class="t-ko">안명원 · 대표이사</span><span class="t-en">Ahn Myung-won · CEO, AMP</span></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">OUR VALUES</p>
        <h2 class="h2 t-ko">일하는 방식</h2>
        <h2 class="h2 t-en">How we work</h2>
        <p class="lead"><span class="t-ko">전문성, 신뢰, 도전. 에이엠피가 일하는 방식입니다.</span><span class="t-en">Professionalism, trust, challenge — the way AMP works.</span></p>
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
        <h2 class="h2 t-ko">걸어온 길</h2>
        <h2 class="h2 t-en">How we got here</h2>
      </div>
"""
    + HISTORY_BLOCK
    + """    </div>
  </section>

  <section id="org" class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">ORGANIZATION</p>
        <h2 class="h2 t-ko">사업 구조</h2>
        <h2 class="h2 t-en">Business structure</h2>
        <p class="lead"><span class="t-ko">수처리 설비를 중심으로, 공조부품 제조와 이차전지 공정장비가 이를 뒷받침합니다.</span><span class="t-en">Water-treatment systems at the center, supported by HVAC-parts manufacturing and battery-process equipment.</span></p>
      </div>
      <div class="org reveal">
        <div class="org-top"><div class="t">유한회사 에이엠피</div><div class="s">AMP Co., Ltd.</div></div>
        <div class="org-stem"></div>
        <div class="org-row">
          <a class="org-node" href="amp.html"><div class="nm">수처리 설비</div><div class="en">WATER</div><div class="role">설계·제작·설치·모니터링</div></a>
          <a class="org-node" href="amp.html" style="border-top-color:#1B6E7D"><div class="nm">공조부품 제조</div><div class="en">HVAC</div><div class="role">Clad AL Header Pipe</div></a>
          <a class="org-node" href="amp.html" style="border-top-color:#4FA3A5"><div class="nm">이차전지 공정장비</div><div class="en">BATTERY</div><div class="role">공침반응기·폐수처리</div></a>
          <a class="org-node" href="ir.html" style="border-top-color:#3E7C4F"><div class="nm">연구전담부서</div><div class="en">R&amp;D</div><div class="role">공정·소재 연구</div></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">COMPANY OVERVIEW</p>
        <h2 class="h2 t-ko">회사 개요</h2>
        <h2 class="h2 t-en">At a glance</h2>
      </div>
      <dl class="overview reveal">
        <div class="row"><dt><span class="t-ko">회사명</span><span class="t-en">Company</span></dt><dd>유한회사 에이엠피 · AMP Co., Ltd.</dd></div>
        <div class="row"><dt><span class="t-ko">대표이사</span><span class="t-en">CEO</span></dt><dd><span class="t-ko">안명원</span><span class="t-en">Ahn Myung-won</span></dd></div>
        <div class="row"><dt><span class="t-ko">설립</span><span class="t-en">Founded</span></dt><dd><span class="t-ko">2025년 1월 (사업 개시)</span><span class="t-en">January 2025</span></dd></div>
        <div class="row"><dt><span class="t-ko">사업자등록번호</span><span class="t-en">Business Reg.</span></dt><dd>171-81-03763</dd></div>
        <div class="row"><dt><span class="t-ko">사업영역</span><span class="t-en">Businesses</span></dt><dd><span class="t-ko">수처리 시스템 설비 · 공조부품 제조 · 이차전지 공정장비</span><span class="t-en">Water-treatment systems · HVAC parts · battery-process equipment</span></dd></div>
        <div class="row"><dt><span class="t-ko">본사</span><span class="t-en">HQ</span></dt><dd><span class="t-ko">전남 광양시 광양읍 익신산단3길 40, 409호</span><span class="t-en">409, 40 Iksinsandan 3-gil, Gwangyang-eup, Gwangyang, Jeonnam</span></dd></div>
        <div class="row"><dt><span class="t-ko">사업장</span><span class="t-en">Sites</span></dt><dd><span class="t-ko">공장 — 광양 태인동 국가산업단지 · 지점·연구 — 여수 융합지구</span><span class="t-en">Plant — Taein-dong National Complex, Gwangyang · Branch/R&amp;D — Yeosu</span></dd></div>
        <div class="row"><dt><span class="t-ko">인증</span><span class="t-en">Certifications</span></dt><dd><span class="t-ko">벤처기업 · 뿌리기업 · ISO 9001</span><span class="t-en">Venture firm · Root industry · ISO 9001</span></dd></div>
        <div class="row"><dt><span class="t-ko">홈페이지</span><span class="t-en">Web</span></dt><dd>amp0404.co.kr</dd></div>
      </dl>
    </div>
  </section>

  <section id="ci" class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">BRAND IDENTITY</p>
        <h2 class="h2 t-ko">브랜드 컬러</h2>
        <h2 class="h2 t-en">Brand colors</h2>
        <p class="lead"><span class="t-ko">물과 설비, 데이터를 담은 에이엠피의 색입니다.</span><span class="t-en">AMP's palette — water, equipment, and data.</span></p>
      </div>
      <div class="ci-grid reveal-stagger">
        <div class="swatch"><div class="chip" style="background:#06202B"></div><div class="meta"><div class="nm">Abyss</div><div class="hex">#06202B</div></div></div>
        <div class="swatch"><div class="chip" style="background:#0E4E78"></div><div class="meta"><div class="nm">컬리버 Blue</div><div class="hex">#0E4E78</div></div></div>
        <div class="swatch"><div class="chip" style="background:#1B6E7D"></div><div class="meta"><div class="nm">에이엠피 Tide</div><div class="hex">#1B6E7D</div></div></div>
        <div class="swatch"><div class="chip" style="background:#A88F63"></div><div class="meta"><div class="nm">코발티브 Sand</div><div class="hex">#A88F63</div></div></div>
        <div class="swatch"><div class="chip" style="background:#3E7C4F"></div><div class="meta"><div class="nm">수신제팜 Green</div><div class="hex">#3E7C4F</div></div></div>
        <div class="swatch"><div class="chip" style="background:#4FA3A5"></div><div class="meta"><div class="nm">Current</div><div class="hex">#4FA3A5</div></div></div>
      </div>
    </div>
  </section>
"""
)
write("about.html", about, active="about.html")

# ================================================================= BUSINESS
business = (
    page_hero("OUR BUSINESS", "에이엠피와 함께하는 사업", "AMP and partner businesses",
              "수처리를 중심으로, 스마트양식과 자원 업사이클이 물과 자원으로 이어집니다.",
              "Water treatment at the center, connected through water and resources to smart aquaculture and resource upcycling.",
              [("business.html", "사업영역", "Business")])
    + """  <section id="cycle" class="section bg-paper">
    <div class="wrap">
      <div class="cycle-head reveal">
        <p class="eyebrow">THE LOOP</p>
        <h2 class="h2 t-ko">한 사업의 부산물이<br>다른 사업의 원료가 됩니다</h2>
        <h2 class="h2 t-en">One business's byproduct feeds another</h2>
        <p class="sub t-ko">각 사업을 눌러 어떤 역할을 하는지 확인해 보세요.</p>
        <p class="sub t-en">Tap a business to see the role it plays.</p>
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
        <p class="lead"><span class="t-ko">각 계열사를 눌러 사업·기술·제품을 자세히 확인하세요.</span><span class="t-en">Tap each affiliate for its business, technology, and products.</span></p>
      </div>
      <div class="biz-list reveal-stagger">
"""
    + biz_cards()
    + """      </div>
    </div>
  </section>

  <section class="section bg-paper">
    <div class="wrap reveal">
      <div class="cta-band">
        <div>
          <h2><span class="t-ko">이 사업에서 함께할 사람을 찾습니다</span><span class="t-en">We're hiring across these businesses</span></h2>
          <p><span class="t-ko">양식·수처리·소재·스마트팜, 네 계열사의 채용 공고를 확인하세요.</span><span class="t-en">See open roles across aquaculture, water treatment, materials, and smart farming.</span></p>
        </div>
        <a class="btn btn-primary" href="careers.html"><span class="t-ko">채용 공고 보기</span><span class="t-en">View openings</span> →</a>
      </div>
    </div>
  </section>
"""
)
write("business.html", business, active="business.html")

# ================================================================= SUSTAINABILITY
sustain = (
    page_hero("SUSTAINABILITY", "지속가능성은 저희 사업의 기본입니다", "Sustainability is built into what we do",
              "폐수를 처리해 다시 쓰고 자원을 순환시키는 일이 곧 에이엠피가 하는 사업입니다.",
              "Treating and reusing water, and circulating resources, is AMP's actual business.",
              [("sustainability.html", "지속가능경영", "Sustainability")])
    + """  <section class="section esg">
    <div class="esg-glow"></div>
    <div class="wrap esg-inner">
      <div class="reveal">
        <p class="eyebrow on-dark">E · S · G</p>
        <div class="esg-head">
          <h2 class="h2 t-ko">사업 안에 담긴 지속가능성</h2>
          <h2 class="h2 t-en">Sustainability built into the business</h2>
          <p class="sub t-ko">환경·사회·지배구조를 각 사업을 만드는 기준으로 삼습니다.</p>
          <p class="sub t-en">We treat environment, society, and governance as the basis for how each business is run.</p>
        </div>
      </div>
"""
    + ESG_CARDS
    + """    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">IMPACT</p>
        <h2 class="h2 t-ko">성과 지표</h2>
        <h2 class="h2 t-en">Our impact</h2>
        <p class="lead"><span class="t-ko">기술로 만든 실측 성과입니다. 데이터 기반 표준 공정이 자원 효율과 생산성을 동시에 끌어올립니다.</span><span class="t-en">Measured results from technology — a data-driven standard process that raises both resource efficiency and productivity.</span></p>
      </div>
      <div class="metrics bento-metrics reveal-stagger">
        <div class="metric"><span class="v" style="color:#0E4E78"><span data-count="70">0</span>%</span><span class="l"><span class="t-ko">흰다리새우 생존율</span><span class="t-en">Shrimp survival</span></span></div>
        <div class="metric"><span class="v" style="color:#14606E"><span data-count="65">0</span>%</span><span class="l"><span class="t-ko">미생물 비용 절감</span><span class="t-en">Microbe cost cut</span></span></div>
        <div class="metric"><span class="v" style="color:#6E5D38">패각콘크리트</span><span class="l"><span class="t-ko">굴패각 자원화</span><span class="t-en">Shell upcycling</span></span></div>
        <div class="metric"><span class="v" style="color:#1B6E7D"><span data-count="7">0</span>일</span><span class="l"><span class="t-ko">수질 정상화 기간</span><span class="t-en">Water recovery</span></span></div>
      </div>
    </div>
  </section>

  <section class="section tall contact">
    <div class="wrap">
      <div class="section-intro on-dark reveal">
        <p class="eyebrow on-dark">OUR COMMITMENTS</p>
        <h2 class="h2 t-ko">지속가능을 위한 약속</h2>
        <h2 class="h2 t-en">What we commit to</h2>
      </div>
      <div class="commitments reveal-stagger">
        <div class="commitment"><span class="no">01</span><div><h3><span class="t-ko">유용미생물 기반 저투입 생산</span><span class="t-en">Probiotic-based, low-input production</span></h3><p><span class="t-ko">복합 유용미생물과 데이터 관리로 약품 의존과 폐사를 낮추고 사료·투입 비용을 줄입니다.</span><span class="t-en">Complex probiotics and data management reduce chemical dependence, mortality, and feed/input costs.</span></p></div></div>
        <div class="commitment"><span class="no">02</span><div><h3><span class="t-ko">자원 순환의 확대</span><span class="t-en">Expanding resource circulation</span></h3><p><span class="t-ko">굴 패각 업사이클을 넘어 부산물을 원료로 되돌리는 순환 범위를 넓혀 갑니다.</span><span class="t-en">Beyond shell upcycling, we keep widening the loop that returns byproducts to raw materials.</span></p></div></div>
        <div class="commitment"><span class="no">03</span><div><h3><span class="t-ko">지역사회와의 상생</span><span class="t-en">Coexistence with communities</span></h3><p><span class="t-ko">생산의 현장인 어촌·산지와 일자리·가치를 나누며 함께 성장합니다.</span><span class="t-en">We grow together with the fishing villages and farmlands where we produce.</span></p></div></div>
        <div class="commitment"><span class="no">04</span><div><h3><span class="t-ko">투명한 지배구조</span><span class="t-en">Transparent governance</span></h3><p><span class="t-ko">데이터에 기반한 의사결정과 투명한 정보 공개를 지향합니다.</span><span class="t-en">We pursue data-driven decisions and transparent disclosure.</span></p></div></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">REPORTS</p>
        <h2 class="h2 t-ko">지속가능경영 자료</h2>
        <h2 class="h2 t-en">Reports &amp; resources</h2>
        <p class="lead"><span class="t-ko">지속가능경영 보고서를 준비 중입니다. 실제 파일로 링크를 교체하세요.</span><span class="t-en">A sustainability report is in preparation — replace with a real file.</span></p>
      </div>
      <div class="report-row reveal">
        <span class="btn-outline is-disabled" aria-disabled="true"><span class="t-ko">📄 지속가능경영 보고서 (준비 중)</span><span class="t-en">📄 Sustainability report (soon)</span></span>
        <a class="btn-outline" href="contact.html"><span class="t-ko">문의하기</span><span class="t-en">Contact us</span> →</a>
      </div>
    </div>
  </section>
"""
)
write("sustainability.html", sustain, active="sustainability.html")

# ================================================================= IR / INVESTOR RELATIONS
# Structure is real; figures/filings are placeholders clearly marked
# "준비 중 / soon" since there is no actual financial data yet.
ir_contact = "contact.html?" + urllib.parse.urlencode({"type": "설비·기술상담"})
ir = (
    page_hero("RECORD · CERTIFICATIONS", "실적·인증", "Record & Certifications",
              "자체 제작 역량과 데이터 기반 물관리로 쌓아온 에이엠피의 강점과 공신력입니다.",
              "AMP's strengths and credentials — built on in-house fabrication and data-driven water management.",
              [("ir.html", "실적·인증", "Record")])
    + """  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">STRENGTHS</p>
        <h2 class="h2 t-ko">에이엠피의 강점</h2>
        <h2 class="h2 t-en">What sets AMP apart</h2>
        <p class="lead"><span class="t-ko">설계부터 제작·설치·사후관리까지 한 흐름으로 수행하는 수처리 전문기업입니다.</span><span class="t-en">A water-treatment specialist that handles design, fabrication, installation and aftercare in one flow.</span></p>
      </div>
      <div class="commitments reveal-stagger">
        <div class="commitment"><span class="no">01</span><div><h3><span class="t-ko">자체 제작 역량</span><span class="t-en">In-house fabrication</span></h3><p><span class="t-ko">자체 공장에서 구조물과 장치를 직접 제작해 설계 변경에도 빠르게 대응합니다.</span><span class="t-en">We fabricate structures and devices in our own shop, so design changes are quick.</span></p></div></div>
        <div class="commitment"><span class="no">02</span><div><h3><span class="t-ko">데이터 기반 물관리</span><span class="t-en">Data-driven water</span></h3><p><span class="t-ko">수질 센서와 실시간 모니터링 프로그램으로 물 상태를 확인하고 이상에 대응합니다.</span><span class="t-en">Sensors and a live monitoring program track water and respond to anomalies.</span></p></div></div>
        <div class="commitment"><span class="no">03</span><div><h3><span class="t-ko">제조 품질관리</span><span class="t-en">Manufacturing quality</span></h3><p><span class="t-ko">공조부품 제조로 쌓은 작업표준서 기반 품질관리가 수처리 설비 제작의 바탕입니다.</span><span class="t-en">Standardized quality control from HVAC-parts manufacturing underpins our water systems.</span></p></div></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">KEY FIGURES</p>
        <h2 class="h2 t-ko">핵심 지표</h2>
        <h2 class="h2 t-en">Key figures</h2>
      </div>
      <div class="metrics bento-metrics reveal-stagger">
        <div class="metric"><span class="v" style="color:#14606E"><span data-count="4">0</span></span><span class="l"><span class="t-ko">수처리 적용 분야</span><span class="t-en">Applications</span></span></div>
        <div class="metric"><span class="v" style="color:#1B6E7D"><span data-count="7">0</span></span><span class="l"><span class="t-ko">수행 프로세스 단계</span><span class="t-en">Process steps</span></span></div>
        <div class="metric"><span class="v" style="color:#4FA3A5"><span data-count="6">0</span>종</span><span class="l"><span class="t-ko">실시간 수질 측정</span><span class="t-en">Live metrics</span></span></div>
        <div class="metric"><span class="v" style="color:#06202B">ISO 9001</span><span class="l"><span class="t-ko">품질경영 인증</span><span class="t-en">Quality cert</span></span></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">CREDENTIALS</p>
        <h2 class="h2 t-ko">인증 · 수상</h2>
        <h2 class="h2 t-en">Certifications &amp; awards</h2>
      </div>
      <div class="chips reveal-stagger" style="gap:10px">
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">벤처기업 확인</span>
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">뿌리기업 확인</span>
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">ISO 9001</span>
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">연구전담부서</span>
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">전라남도지사 표창</span>
        <span class="chip" style="background:rgba(20,96,110,.08);color:#14606E">중소벤처기업청장 상장</span>
      </div>
      <div class="report-row reveal" style="margin-top:32px">
        <span class="btn-outline is-disabled" aria-disabled="true"><span class="t-ko">📄 회사소개서 (준비 중)</span><span class="t-en">📄 Company profile (soon)</span></span>
        <span class="btn-outline is-disabled" aria-disabled="true"><span class="t-ko">📄 시공 실적 자료 (준비 중)</span><span class="t-en">📄 Project record (soon)</span></span>
      </div>
    </div>
  </section>

  <section class="section bg-card">
    <div class="wrap reveal">
      <div class="cta-band" style="background:linear-gradient(160deg,#041821,#0C3A47 60%,#1B6E7D 130%)">
        <div>
          <h2><span class="t-ko">사업·기술 문의</span><span class="t-en">Business inquiries</span></h2>
          <p><span class="t-ko">수처리 설비·기술상담, 사업 제휴 문의를 환영합니다.</span><span class="t-en">We welcome water-system, technical and partnership inquiries.</span></p>
        </div>
        <a class="btn btn-primary" href=\"""" + ir_contact + """"><span class="t-ko">문의하기</span><span class="t-en">Contact</span> →</a>
      </div>
    </div>
  </section>
"""
)
write("ir.html", ir, active="ir.html")

# ================================================================= NEWSROOM
newsroom = (
    page_hero("NEWSROOM", "소식", "News",
              "에이엠피의 보도자료·소식·채용 소식을 전합니다.",
              "Press releases, updates and hiring news from AMP.",
              [("newsroom.html", "뉴스룸", "Newsroom")])
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
    page_hero("CAREERS", "함께 일할 사람을 찾습니다", "Join the team",
              "바다와 농장, 실험실과 현장에서 일할 사람을 찾고 있습니다.",
              "We're looking for people to work across the sea and the farm, the lab and the field.",
              [("careers.html", "채용", "Careers")],
              cta_html='<a class="careers-hero-cta" href="#roles"><span class="t-ko">채용 공고 보기</span><span class="t-en">View openings</span> ↓</a>')
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">TALENT</p>
        <h2 class="h2 t-ko">이런 분을 찾습니다</h2>
        <h2 class="h2 t-en">Who we look for</h2>
      </div>
      <div class="values reveal">
        <div class="value"><span class="value-no" style="color:#0E4E78">01</span><div class="value-body"><h3><span class="t-ko">현장을 아는 사람</span><span class="t-en">Grounded in the field</span></h3><p class="t-ko">데이터와 현장을 함께 읽고, 실제 생산의 문제를 해결하는 사람.</p><p class="t-en">Someone who reads both data and the field to solve real production problems.</p></div></div>
        <div class="value"><span class="value-no" style="color:#166578">02</span><div class="value-body"><h3><span class="t-ko">순환을 설계하는 사람</span><span class="t-en">A systems thinker</span></h3><p class="t-ko">한 사업의 부산물을 다음 사업의 원료로 잇는 시야를 가진 사람.</p><p class="t-en">Someone who connects one business's byproduct to the next as raw material.</p></div></div>
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
        <div class="step"><div class="n">4</div><h3><span class="t-ko">입사</span><span class="t-en">Onboarding</span></h3><p><span class="t-ko">온보딩과 함께 에이엠피의 일원이 됩니다.</span><span class="t-en">Join AMP with a full onboarding.</span></p></div>
      </div>
    </div>
  </section>

  <section id="roles" class="section tall bg-paper">
    <div class="wrap">
      <div class="section-head-row reveal">
        <div>
          <p class="eyebrow">OPEN ROLES</p>
          <h2 class="h2 t-ko">채용 공고</h2>
          <h2 class="h2 t-en">Open positions</h2>
        </div>
      </div>
      <div class="roles reveal-stagger">
"""
    + roles_list()
    + """      </div>
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

  <section class="section bg-paper">
    <div class="wrap reveal">
      <div class="cta-band">
        <div>
          <h2><span class="t-ko">지금 지원하세요</span><span class="t-en">Apply now</span></h2>
          <p><span class="t-ko">관심 있는 포지션이 있다면 언제든 문의해 주세요.</span><span class="t-en">Interested in a role? Reach out any time.</span></p>
        </div>
        <a class="btn btn-primary" href="contact.html"><span class="t-ko">지원 · 문의</span><span class="t-en">Apply / Contact</span> →</a>
      </div>
    </div>
  </section>
"""
)
write("careers.html", careers, active="careers.html")

# ================================================================= CONTACT
contact = (
    page_hero("CONTACT", "에이엠피에 문의하기", "Contact AMP",
              "수처리 설비·기술상담, 사업 제휴, 제품·구매, 채용 등 무엇이든 문의해 주세요.",
              "Water-treatment systems, technical consulting, partnerships, products, hiring — reach out about anything.",
              [("contact.html", "문의", "Contact")])
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

# ================================================================= AFFILIATE DETAIL PAGES
for c in BIZ:
    feats = "".join(
        f"""        <div class="feature">
          <span class="k">{i+1:02d}</span>
          <h3><span class="t-ko">{fko}</span><span class="t-en">{fen}</span></h3>
          <p><span class="t-ko">{dko}</span><span class="t-en">{den}</span></p>
        </div>
""" for i, (fko, fen, dko, den) in enumerate(c["features"]))
    prods = "".join(
        f"""        <div class="product">
          <div class="product-top">
            <span class="product-cat" style="color:{c['ink']}"><span class="t-ko">{p['tko']}</span><span class="t-en">{p['ten']}</span></span>
            <span class="product-status"><span class="t-ko">{p['status']}</span><span class="t-en">{p['statusen']}</span></span>
          </div>
          <h3><span class="t-ko">{p['nko']}</span><span class="t-en">{p['nen']}</span></h3>
          <p><span class="t-ko">{p['dko']}</span><span class="t-en">{p['den']}</span></p>
        </div>
""" for p in c["products"])
    mets = "".join(
        f"""        <div class="metric"><span class="v" style="color:{c['ink']}">{metric_value(v)}</span><span class="l"><span class="t-ko">{lko}</span><span class="t-en">{len_}</span></span></div>
""" for (v, lko, len_) in c["metrics"])

    news_idx, careers_slug = AFFILIATE_LINKS[c["file"]]
    related_news = NEWS[news_idx - 1]
    related_role = next(r for r in ROLES if r["slug"] == careers_slug)
    related = f"""  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">RELATED</p>
        <h2 class="h2 t-ko">함께 보면 좋은 콘텐츠</h2>
        <h2 class="h2 t-en">Related content</h2>
      </div>
      <div class="related-grid reveal-stagger">
        <a class="related-card" href="news.html?id=news-{news_idx}">
          <span class="ic">📰</span>
          <span class="body"><span class="kicker"><span class="t-ko">최근 소식</span><span class="t-en">LATEST NEWS</span></span><span class="title">{related_news['title']}</span></span>
        </a>
        <a class="related-card" href="careers-{careers_slug}.html">
          <span class="ic">💼</span>
          <span class="body"><span class="kicker"><span class="t-ko">채용 중</span><span class="t-en">OPEN ROLE</span></span><span class="title"><span class="t-ko">{related_role['role_ko']}</span><span class="t-en">{related_role['role_en']}</span></span></span>
        </a>
      </div>
    </div>
  </section>
"""

    if c.get("coming_soon"):
        mid = f"""  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">COMING SOON</p>
        <h2 class="h2 t-ko">상세 소개 준비 중</h2>
        <h2 class="h2 t-en">Details in preparation</h2>
        <p class="lead"><span class="t-ko">{c['nko']}의 사업·제품 상세는 준비 중입니다. 확정되는 대로 순차적으로 공개할 예정입니다.</span><span class="t-en">Detailed business and product information for {c['nen']} is in preparation and will be published as it is confirmed.</span></p>
      </div>
    </div>
  </section>
"""
    else:
        mid = f"""  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">TECHNOLOGY</p>
        <h2 class="h2 t-ko">핵심 기술</h2>
        <h2 class="h2 t-en">Core technology</h2>
      </div>
      <div class="feature-grid reveal-stagger">
{feats}      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">PRODUCTS</p>
        <h2 class="h2 t-ko">제품 · 서비스</h2>
        <h2 class="h2 t-en">Products &amp; services</h2>
      </div>
      <div class="product-grid reveal-stagger">
{prods}      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">BY THE NUMBERS</p>
        <h2 class="h2 t-ko">주요 지표</h2>
        <h2 class="h2 t-en">Key figures</h2>
      </div>
      <div class="metrics bento-metrics reveal-stagger">
{mets}      </div>
    </div>
  </section>
"""

    body = (
        page_hero(c["ten"], c["nko"], c["nen"], c["dko"], c["den"],
                  [("business.html", "사업영역", "Business"), (None, c["nko"], c["nen"])],
                  bg=c["deep"])
        + f"""  <section class="section bg-paper">
    <div class="wrap">
      <div class="section-intro reveal" style="text-align:left;max-width:820px;margin-left:0">
        <p class="eyebrow" style="color:{c['ink']}">{c['tko']} · {c['ten']}</p>
        <h2 class="h2 t-ko">{c['nko']} 소개</h2>
        <h2 class="h2 t-en">About {c['nen']}</h2>
        <p class="lead"><span class="t-ko">{c['leadko']}</span><span class="t-en">{c['leaden']}</span></p>
      </div>
    </div>
  </section>
"""
        + mid
        + related
        + f"""  <section class="section bg-paper">
    <div class="wrap reveal">
      <div class="cta-band" style="background:{c['deep']}">
        <div>
          <h2><span class="t-ko">{c['nko']}에 대해 더 알고 싶으신가요?</span><span class="t-en">Want to know more about {c['nen']}?</span></h2>
          <p><span class="t-ko">사업 제휴·제품·구매 문의를 환영합니다.</span><span class="t-en">We welcome partnership, product, and purchase inquiries.</span></p>
        </div>
        <a class="btn btn-primary" href="contact.html"><span class="t-ko">문의하기</span><span class="t-en">Contact</span> →</a>
      </div>
    </div>
  </section>
"""
    )
    write(c["file"], body, active="business.html")

# ================================================================= NEWS ARTICLE (dynamic)
# One template, not one file per article: content is admin-managed (see
# api/news, admin.html), so assets/js/main.js's setupArticle() fetches
# /api/news/<id> (read from the ?id= query string) and fills #articleRoot
# client-side. The 6 build-time seed articles get thin redirect stubs
# below so any old news-N.html links/bookmarks keep working.
news_detail = (
    page_hero("NEWSROOM", "소식", "News",
              "보도자료·소식·채용 소식을 전합니다.", "Press, updates, and hiring news.",
              [("newsroom.html", "뉴스룸", "Newsroom"), (None, "불러오는 중...", "Loading…")],
              heading_level="h2")
    + """  <section class="section bg-paper">
    <div class="wrap">
      <div id="articleRoot">
        <p><span class="t-ko">불러오는 중…</span><span class="t-en">Loading…</span></p>
      </div>
      <noscript>
        <p><span class="t-ko">이 페이지는 JavaScript가 필요합니다. 목록은 </span><span class="t-en">This page needs JavaScript. See the </span><a href="newsroom.html"><span class="t-ko">뉴스룸</span><span class="t-en">Newsroom</span></a><span class="t-ko">에서 확인하세요.</span><span class="t-en"> list instead.</span></p>
      </noscript>
    </div>
  </section>
"""
)
write("news.html", news_detail, active="newsroom.html")

for i, n in enumerate(NEWS):
    idx = i + 1
    stub_id = f"news-{idx}"
    stub_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=news.html?id={stub_id}">
<link rel="canonical" href="news.html?id={stub_id}">
<title>{n['title']}</title>
</head>
<body>
<p><a href="news.html?id={stub_id}">{n['title']}</a></p>
</body>
</html>
"""
    with open(os.path.join(ROOT, f"{stub_id}.html"), "w", encoding="utf-8") as f:
        f.write(stub_html)
    print("wrote", f"{stub_id}.html", f"({len(stub_html)} bytes, redirect stub)")

# ================================================================= ROLE DETAIL PAGES
for r in ROLES:
    duties = "".join(f'            <li><span class="t-ko">{ko}</span><span class="t-en">{en}</span></li>\n' for ko, en in r["duties"])
    quals = "".join(f'            <li><span class="t-ko">{ko}</span><span class="t-en">{en}</span></li>\n' for ko, en in r["quals"])
    plus = "".join(f'            <li><span class="t-ko">{ko}</span><span class="t-en">{en}</span></li>\n' for ko, en in r["plus"])
    # pass both languages; the static site can't know the visitor's current
    # language at build time, so main.js's prefillFromQuery() picks whichever
    # matches the persisted data-lang when contact.html actually loads.
    apply_href = "contact.html?" + urllib.parse.urlencode({
        "type": "채용",
        "role_ko": f"{r['team_ko']} {r['role_ko']}",
        "role_en": f"{r['team_en']} {r['role_en']}",
    })

    body = (
        page_hero("CAREERS", r["role_ko"], r["role_en"],
                  f"{r['team_ko']} · {r['loc_ko']} · {r['type_ko']}", f"{r['team_en']} · {r['loc_en']} · {r['type_en']}",
                  [("careers.html", "채용", "Careers"), (None, r["role_ko"], r["role_en"])])
        + f"""  <section class="section bg-paper">
    <div class="wrap">
      <div class="job-grid">
        <div class="reveal">
          <div class="job-block">
            <h2><span class="t-ko">담당 업무</span><span class="t-en">Responsibilities</span></h2>
            <ul class="ticks">
{duties}            </ul>
          </div>
          <div class="job-block">
            <h2><span class="t-ko">자격 요건</span><span class="t-en">Requirements</span></h2>
            <ul class="ticks">
{quals}            </ul>
          </div>
          <div class="job-block">
            <h2><span class="t-ko">우대 사항</span><span class="t-en">Nice to have</span></h2>
            <ul class="ticks">
{plus}            </ul>
          </div>
          <p class="note" style="font-size:13px;color:var(--text-3)"><span class="t-ko">※ 본 공고는 예시입니다. 실제 채용 내용으로 교체하세요.</span><span class="t-en">※ Example posting — replace with a real job description.</span></p>
        </div>
        <aside class="job-aside reveal">
          <div class="meta"><span class="k">TEAM</span><a class="v" href="{r['biz']}" style="color:{r['color']}"><span class="t-ko">{r['team_ko']}</span><span class="t-en">{r['team_en']}</span></a></div>
          <div class="meta"><span class="k">LOCATION</span><span class="v"><span class="t-ko">{r['loc_ko']}</span><span class="t-en">{r['loc_en']}</span></span></div>
          <div class="meta"><span class="k">TYPE</span><span class="v"><span class="t-ko">{r['type_ko']}</span><span class="t-en">{r['type_en']}</span></span></div>
          <a class="btn btn-primary" href="{apply_href}"><span class="t-ko">지원 · 문의</span><span class="t-en">Apply</span> →</a>
          <a class="more-link" href="careers.html" style="margin-top:0"><span class="t-ko">← 전체 공고</span><span class="t-en">← All roles</span></a>
        </aside>
      </div>
    </div>
  </section>
"""
    )
    write(f"careers-{r['slug']}.html", body, active="careers.html")

print("done.")
