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
    # Archivo at expanded width (wdth=125) — the Latin display face; Korean
    # display glyphs fall back to Pretendard (loaded above) automatically.
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,500;125,600;125,700;125,800&display=swap">\n'
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
    ("about.html", "그룹소개", "About"),
    ("business.html", "사업영역", "Business"),
    ("sustainability.html", "지속가능경영", "Sustainability"),
    ("ir.html", "투자정보", "IR"),
    ("newsroom.html", "뉴스룸", "Newsroom"),
    ("careers.html", "채용", "Careers"),
]

# Contact is deliberately NOT in NAV — it renders as a distinct primary
# CTA button (the site's main conversion path: partnership/investment/
# purchase inquiries), not a peer text link.
CONTACT_CTA = ("contact.html", "문의", "Contact")

FAMILY = [
    ("culiver-aqua.html", "컬리버", "CULIVER"),
    ("amp.html", "에이엠피", "AMP"),
    ("cobaltive.html", "코발티브", "COBALTIVE"),
    ("susinje-farm.html", "수신제팜", "SUSINJE FARM"),
]

# jump-links into the (long, single-page) About page's sections
ABOUT_SECTIONS = [
    ("about.html", "그룹 개요", "Overview"),
    ("about.html#history", "연혁", "History"),
    ("about.html#org", "조직·지배구조", "Organization"),
    ("about.html#ci", "브랜드 컬러", "Brand color"),
]

# top-level items that open a dropdown panel. Each panel gets a labelled
# heading so the relationship is explicit: under 사업영역 the four items
# are the group's 계열사(legal entities); under 그룹소개 they are section
# jump-links. label = (ko, en) heading; items = [(href, ko, en)]; all =
# optional (href, ko, en) "see all" link shown at the panel foot.
DROPDOWNS = {
    "about.html": dict(label=("그룹", "GROUP"), items=ABOUT_SECTIONS, all=None),
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
        '      <span class="brand-mark">CULIVER</span>\n'
        '      <span class="brand-sub">GROUP</span>\n'
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
            <a href="ir.html"><span class="t-ko">투자정보</span><span class="t-en">IR</span></a>
            <a href="careers.html"><span class="t-ko">채용</span><span class="t-en">Careers</span></a>
          </div>
          <div class="footer-col">
            <span class="head">CONTACT</span>
            <a href="contact.html"><span class="t-ko">문의하기</span><span class="t-en">Contact</span></a>
            <span class="plain">contact@culiver.co.kr</span>
            <span class="plain">T. 000-0000-0000</span>
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
    dict(file="culiver-aqua.html", no="01", color="#0E4E78", ink="#0E4E78",
         deep="linear-gradient(160deg,#041821,#0A2C46 60%,#0E4E78 130%)",
         img="biz-culiver.jpg", right=False,
         overlay="linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.72))", chipbg="rgba(14,78,120,.08)",
         tko="스마트 양식", ten="SMART AQUACULTURE", nko="컬리버", nen="CULIVER",
         dko="미생물 기반 BFT 바이오플락 기술로 흰다리새우를 육상에서 연중 안정 생산합니다. 항생제 없는 양식, 데이터로 관리되는 수조.",
         den="Year-round, land-based whiteleg shrimp production powered by microbial BFT technology — antibiotic-free, data-managed.",
         chips=["흰다리새우", "BFT 바이오플락", "Shrimp365"],
         leadko="컬리버는 미생물 기반 BFT(바이오플락) 기술로 흰다리새우를 육상에서 연중 생산하는 스마트 양식 기업입니다. 항생제 없이, 데이터로 관리되는 수조에서 균일한 품질의 새우를 안정적으로 길러냅니다.",
         leaden="CULIVER is a smart-aquaculture company producing whiteleg shrimp year-round on land with microbial BFT technology — antibiotic-free, in data-managed tanks.",
         features=[("BFT 바이오플락", "BFT Bioflocs", "미생물이 사육수 속 유기물을 분해해 물을 되살리는 무환수·저환수 양식 기술입니다.", "Microbes break down organic matter in the water, enabling low- and zero-exchange farming."),
                   ("육상 순환 양식", "Land-based farming", "외부 환경에 영향받지 않는 실내 수조에서 연중 균일한 품질로 생산합니다.", "Indoor tanks produce a consistent harvest all year, shielded from the outside environment."),
                   ("Shrimp365 데이터 관제", "Shrimp365 monitoring", "수온·용존산소·수질을 실시간으로 모니터링하고 자동 제어합니다.", "Water temperature, oxygen, and quality are monitored and controlled in real time.")],
         products=[("무항생제 흰다리새우", "Antibiotic-free shrimp", "항생제 없이 길러낸 신선·냉장 새우를 식자재·유통 채널에 공급합니다.", "Fresh, chilled, antibiotic-free shrimp for food-service and retail."),
                   ("활새우 공급", "Live shrimp", "산지에서 직송하는 활새우를 공급합니다.", "Live shrimp shipped directly from the farm.")],
         metrics=[("365", "연중 생산일", "Days a year"), ("100%", "무항생제", "Antibiotic-free"), ("BFT", "핵심 양식 기술", "Core method")]),
    dict(file="amp.html", no="02", color="#1B6E7D", ink="#14606E",
         deep="linear-gradient(160deg,#041821,#0C4A57 60%,#1B6E7D 130%)",
         img="biz-amp.jpg", right=True,
         overlay="linear-gradient(150deg,rgba(27,110,125,.5),rgba(12,58,71,.74))", chipbg="rgba(27,110,125,.1)",
         tko="수처리 솔루션", ten="WATER TREATMENT", nko="에이엠피", nen="AMP",
         dko="양식장과 산업 현장의 물을 다루는 수처리 엔지니어링. 미생물 제제와 순환여과 시스템으로 물의 순환을 완성합니다.",
         den="Water-treatment engineering for aquaculture and industry — microbial agents and recirculating filtration that close the water loop.",
         chips=["수처리 설비", "미생물 제제", "순환여과"],
         leadko="에이엠피는 양식장과 산업 현장의 물을 다루는 수처리 엔지니어링 기업입니다. 미생물 제제와 순환여과 시스템으로 물을 정화하고 되돌려, 그룹 순환 구조의 ‘물’ 축을 담당합니다.",
         leaden="AMP is a water-treatment engineering company for aquaculture and industry. With microbial agents and recirculating systems, it purifies and returns water — the water axis of the group's loop.",
         features=[("순환여과 시스템(RAS)", "Recirculating systems", "사육수를 여과·정화해 재사용하는 폐쇄형 순환 설비를 설계·시공합니다.", "Closed-loop systems that filter and reuse rearing water."),
                   ("미생물 제제", "Microbial agents", "수질을 안정화하는 자체 미생물 제제를 개발·생산합니다.", "In-house microbial agents that stabilize water quality."),
                   ("산업용수 처리", "Industrial water", "산업 현장의 용수·폐수 처리 플랜트를 설계·시공합니다.", "Design and construction of industrial water and wastewater plants.")],
         products=[("양식 수처리 설비", "Aquaculture systems", "RAS 설계·시공·유지보수 서비스를 제공합니다.", "RAS design, construction, and maintenance."),
                   ("미생물 제제", "Microbial products", "양식·환경용 미생물 솔루션을 공급합니다.", "Microbial solutions for aquaculture and environment."),
                   ("산업용수 플랜트", "Industrial plants", "현장 맞춤형 수처리 플랜트를 구축합니다.", "Custom-built water-treatment plants.")],
         metrics=[("RAS", "핵심 설비", "Core system"), ("예시", "누적 수주 (교체)", "Projects (replace)"), ("예시", "재이용률 % (교체)", "Reuse % (replace)")]),
    dict(file="cobaltive.html", no="03", color="#8E7A5C", ink="#6E5D38",
         deep="linear-gradient(160deg,#041821,#5E4F3A 60%,#8E7A5C 130%)",
         img="biz-cobaltive.jpg", right=False,
         overlay="linear-gradient(150deg,rgba(142,122,92,.46),rgba(94,79,58,.72))", chipbg="rgba(142,122,92,.12)",
         tko="자원순환 소재", ten="UPCYCLED MATERIALS", nko="코발티브", nen="COBALTIVE",
         dko="버려지는 굴 패각을 친환경 소재와 생활 제품으로 되살립니다. 폐기물이 아닌 자원으로 — 숨쉘, 셸픽.",
         den="Discarded oyster shells reborn as eco-materials and everyday products — waste turned back into a resource.",
         chips=["굴패각 업사이클", "숨쉘", "셸픽"],
         leadko="코발티브는 버려지는 굴 패각을 친환경 소재와 생활 제품으로 되살리는 자원순환 소재 기업입니다. 폐기물을 자원으로 전환하여 그룹의 순환 고리를 자원 영역까지 넓힙니다.",
         leaden="COBALTIVE is a circular-materials company that revives discarded oyster shells into eco-materials and products, extending the group's loop into resources.",
         features=[("패각 정제·가공", "Shell processing", "수거한 굴 패각을 세척·분쇄·정제해 원료화합니다.", "Collected shells are washed, milled, and refined into raw material."),
                   ("친환경 소재화", "Eco-materials", "탄산칼슘 기반 기능성·건축 소재로 개발합니다.", "Developed into calcium-carbonate-based functional and building materials."),
                   ("제품화", "Productization", "소재를 생활 제품으로 상품화합니다.", "Materials commercialized into everyday products.")],
         products=[("숨쉘", "SUMSHELL", "패각 기반 기능성 소재입니다.", "A functional material made from oyster shells."),
                   ("셸픽", "SHELLPICK", "패각을 업사이클한 생활 제품입니다.", "Upcycled everyday products made from shells.")],
         metrics=[("Upcycle", "핵심 가치", "Core value"), ("예시", "재활용 패각량 (교체)", "Shells recycled (replace)"), ("예시", "친환경 인증 (교체)", "Eco-cert (replace)")]),
    dict(file="susinje-farm.html", no="04", color="#3E7C4F", ink="#3E7C4F",
         deep="linear-gradient(160deg,#041821,#2A5A38 60%,#3E7C4F 130%)",
         img="biz-susinje.jpg", right=True,
         overlay="linear-gradient(150deg,rgba(62,124,79,.46),rgba(36,82,50,.72))", chipbg="rgba(62,124,79,.1)",
         tko="스마트팜 · 유통", ten="SMART FARM · DISTRIBUTION", nko="수신제팜", nen="SUSINJE FARM",
         dko="데이터 기반 수경재배로 기르고, 산지에서 식탁까지 직접 잇습니다. 스마트팜 재배와 신선 유통을 한 흐름으로.",
         den="Data-driven hydroponic growing connected directly to the table — smart-farm cultivation and fresh distribution in one flow.",
         chips=["수경재배", "스마트팜", "신선유통"],
         leadko="수신제팜은 데이터 기반 수경재배 스마트팜과 신선 유통을 함께 운영합니다. 순환수로 기른 작물을 산지에서 식탁까지 직접 잇습니다.",
         leaden="SUSINJE FARM runs data-driven hydroponic smart farms together with fresh distribution, connecting crops grown in recirculated water straight to the table.",
         features=[("수경재배", "Hydroponics", "흙 없이 양액으로 작물을 균일하게 재배합니다.", "Crops grown uniformly in nutrient solution, without soil."),
                   ("스마트팜 환경제어", "Smart-farm control", "온도·습도·양액을 데이터로 자동 관리합니다.", "Temperature, humidity, and nutrients managed automatically by data."),
                   ("신선 유통", "Fresh distribution", "산지-식탁 직배송과 B2B 납품을 운영합니다.", "Farm-to-table delivery and B2B supply.")],
         products=[("수경재배 채소", "Hydroponic vegetables", "청정 환경에서 기른 신선 채소를 공급합니다.", "Fresh vegetables grown in a clean environment."),
                   ("정기배송", "Subscription", "가정·기업을 위한 정기 공급 서비스입니다.", "Recurring supply for homes and businesses.")],
         metrics=[("Farm→Table", "유통 구조", "Model"), ("예시", "재배 면적 (교체)", "Grow area (replace)"), ("예시", "연간 출하량 (교체)", "Annual output (replace)")]),
]
BIZ_BY_FILE = {c["file"]: c for c in BIZ}

# maps affiliate file -> (1-based news index, careers slug) for cross-linking
AFFILIATE_LINKS = {
    "culiver-aqua.html": (1, "culiver"),
    "amp.html": (4, "amp"),
    "cobaltive.html": (2, "cobaltive"),
    "susinje-farm.html": (3, "susinje"),
}

NEWS = [
    dict(tagko="보도자료", tagen="Press", date="2026.06", title="컬리버, BFT 기반 흰다리새우 스마트 양식장 2호기 준공",
         titleen="CULIVER completes second BFT-based smart shrimp farm",
         overlay="linear-gradient(150deg,rgba(14,78,120,.32),rgba(10,44,70,.55))", cover="linear-gradient(150deg,rgba(14,78,120,.5),rgba(10,44,70,.7))",
         photo="news-1.jpg", color="#0E4E78", chipbg="rgba(14,78,120,.08)", biz="culiver-aqua.html",
         body=["컬리버가 BFT(바이오플락) 기반 흰다리새우 스마트 양식장 2호기를 준공했습니다. 이번 2호기는 데이터 기반 사육 관제 시스템을 전면 적용해 연중 안정 생산 역량을 한층 강화했습니다.",
               "육상 순환 양식 방식으로 항생제 없이 균일한 품질의 새우를 생산하며, 사육수는 계열사 에이엠피의 수처리 공정과 연계해 순환·재사용됩니다.",
               "컬리버 그룹은 이번 증설을 계기로 스마트 양식 생산 규모를 지속 확대해 나갈 계획입니다."]),
    dict(tagko="소식", tagen="Updates", date="2026.05", title="코발티브, 굴패각 업사이클 소재 친환경 인증 획득",
         titleen="COBALTIVE earns eco-certification for upcycled oyster-shell materials",
         overlay="linear-gradient(150deg,rgba(142,122,92,.3),rgba(94,79,58,.55))", cover="linear-gradient(150deg,rgba(142,122,92,.5),rgba(94,79,58,.7))",
         photo="news-2.jpg", color="#6E5D38", chipbg="rgba(142,122,92,.12)", biz="cobaltive.html",
         body=["코발티브가 굴 패각을 업사이클한 친환경 소재로 인증을 획득했습니다. 버려지던 패각을 자원으로 되살려 폐기물과 배출을 구조적으로 줄이는 성과를 인정받았습니다.",
               "코발티브는 패각 정제·가공을 통해 탄산칼슘 기반 기능성 소재 ‘숨쉘’과 생활 제품 ‘셸픽’을 선보이고 있습니다.",
               "앞으로도 자원순환 소재 라인업을 확대해 나갈 예정입니다."]),
    dict(tagko="소식", tagen="Updates", date="2026.04", title="수신제팜, 데이터 기반 수경재배 채소 정기유통 시작",
         titleen="SUSINJE FARM launches subscription delivery for hydroponic vegetables",
         overlay="linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))", cover="linear-gradient(150deg,rgba(62,124,79,.5),rgba(36,82,50,.7))",
         photo="news-3.jpg", color="#3E7C4F", chipbg="rgba(62,124,79,.1)", biz="susinje-farm.html",
         body=["수신제팜이 데이터 기반 수경재배로 기른 채소의 정기유통을 시작했습니다. 스마트팜 환경제어로 균일한 품질을 유지하며, 산지에서 식탁까지 신선하게 배송합니다.",
               "순환수를 활용한 재배로 자원 효율을 높였으며, 가정과 기업 고객을 대상으로 정기배송 서비스를 운영합니다."]),
    dict(tagko="보도자료", tagen="Press", date="2026.03", title="에이엠피, 산업용수 순환여과 플랜트 신규 수주",
         titleen="AMP wins new industrial water recirculation plant contract",
         overlay="linear-gradient(150deg,rgba(30,127,150,.3),rgba(15,74,92,.55))", cover="linear-gradient(150deg,rgba(30,127,150,.5),rgba(15,74,92,.7))",
         photo="news-4.jpg", color="#166578", chipbg="rgba(30,127,150,.09)", biz="amp.html",
         body=["에이엠피가 산업용수 순환여과 플랜트를 신규 수주했습니다. 순환여과(RAS)와 미생물 제제 기술을 결합해 용수 재이용률을 높이는 맞춤형 설비를 공급합니다.",
               "에이엠피는 양식 수처리에서 축적한 기술을 산업 현장으로 확장하며 수처리 사업 영역을 넓혀가고 있습니다."]),
    dict(tagko="채용", tagen="Hiring", date="2026.02", title="컬리버 그룹 2026 상반기 신입·경력 공개채용 시작",
         titleen="CULIVER Group opens 2026 first-half hiring",
         overlay="linear-gradient(150deg,rgba(11,36,56,.34),rgba(8,24,38,.6))", cover="linear-gradient(150deg,rgba(11,36,56,.55),rgba(8,24,38,.75))",
         photo="news-5.jpg", color="#06202B", chipbg="rgba(6,32,43,.08)", biz=None,
         body=["컬리버 그룹이 2026년 상반기 신입·경력 공개채용을 시작합니다. 양식 생산, 수처리 엔지니어링, 소재 R&D, 스마트팜 재배 등 계열사 전 직무에서 인재를 모집합니다.",
               "자세한 직무 내용과 지원 방법은 채용 페이지에서 확인하실 수 있습니다."]),
    dict(tagko="소식", tagen="Updates", date="2026.01", title="수신제팜 수경재배 채소, 대형 유통사 입점 확정",
         titleen="SUSINJE FARM's hydroponic vegetables land major retail placement",
         overlay="linear-gradient(150deg,rgba(62,124,79,.3),rgba(36,82,50,.55))", cover="linear-gradient(150deg,rgba(62,124,79,.5),rgba(36,82,50,.7))",
         photo="news-6.jpg", color="#3E7C4F", chipbg="rgba(62,124,79,.1)", biz="susinje-farm.html",
         body=["수신제팜의 수경재배 채소가 대형 유통사 입점을 확정했습니다. 데이터 기반 재배로 균일한 품질을 확보한 점이 좋은 평가를 받았습니다.",
               "이번 입점을 통해 더 많은 소비자에게 신선한 채소를 선보일 수 있게 되었습니다."]),
]

# inline first-mention hyperlinks inside article bodies
NEWS[0]["body"] = linkify_first(NEWS[0]["body"], "컬리버", "culiver-aqua.html")
NEWS[1]["body"] = linkify_first(NEWS[1]["body"], "코발티브", "cobaltive.html")
NEWS[1]["body"] = linkify_first(NEWS[1]["body"], "숨쉘", "cobaltive.html")
NEWS[1]["body"] = linkify_first(NEWS[1]["body"], "셸픽", "cobaltive.html")
NEWS[2]["body"] = linkify_first(NEWS[2]["body"], "수신제팜", "susinje-farm.html")
NEWS[3]["body"] = linkify_first(NEWS[3]["body"], "에이엠피", "amp.html")
NEWS[4]["body"] = linkify_first(NEWS[4]["body"], "채용 페이지", "careers.html")
NEWS[5]["body"] = linkify_first(NEWS[5]["body"], "수신제팜", "susinje-farm.html")

ROLES = [
    dict(slug="culiver", biz="culiver-aqua.html", color="#0E4E78",
         role_ko="양식 생산 매니저", role_en="Aquaculture Production Manager",
         team_ko="컬리버", team_en="CULIVER",
         loc_ko="충남 태안", loc_en="Taean, Chungnam",
         type_ko="정규직", type_en="Full-time",
         duties=[("BFT 양식장 사육수 관리 및 수질 모니터링", "Manage rearing water and monitor quality at BFT farms"),
                 ("생산 일정·입식·출하 관리", "Plan production, stocking, and harvest"),
                 ("Shrimp365 데이터 기반 사육 관리", "Run data-driven husbandry with Shrimp365")],
         quals=[("수산·생물 관련 전공 또는 양식 경력", "Degree in fisheries/biology or aquaculture experience"),
                ("데이터 기반 생산 관리에 대한 이해", "Understanding of data-driven production"),
                ("현장 근무 가능자", "Willing to work on-site")],
         plus=[("흰다리새우·BFT 양식 경험", "Whiteleg shrimp / BFT experience"),
               ("관련 자격증 보유", "Relevant certifications")]),
    dict(slug="amp", biz="amp.html", color="#166578",
         role_ko="수처리 공정 엔지니어", role_en="Water Treatment Process Engineer",
         team_ko="에이엠피", team_en="AMP",
         loc_ko="경기 안산", loc_en="Ansan, Gyeonggi",
         type_ko="정규직", type_en="Full-time",
         duties=[("순환여과(RAS) 설비 설계·운영", "Design and operate recirculating (RAS) systems"),
                 ("미생물 제제 적용 및 수질 최적화", "Apply microbial agents and optimize water quality"),
                 ("산업용수 플랜트 유지보수", "Maintain industrial water plants")],
         quals=[("환경·화공·기계 관련 전공", "Degree in environmental/chemical/mechanical engineering"),
                ("수처리 공정에 대한 이해", "Understanding of water-treatment processes"),
                ("설비 현장 대응 가능자", "Able to respond on-site")],
         plus=[("RAS·폐수처리 경험", "RAS or wastewater experience"),
               ("수질환경기사 등 자격증", "Water-quality engineering license")]),
    dict(slug="cobaltive", biz="cobaltive.html", color="#6E5D38",
         role_ko="소재 R&D 연구원", role_en="Materials R&D Researcher",
         team_ko="코발티브", team_en="COBALTIVE",
         loc_ko="경남 통영", loc_en="Tongyeong, Gyeongnam",
         type_ko="정규직", type_en="Full-time",
         duties=[("굴 패각 기반 소재 연구·개발", "Research and develop shell-based materials"),
                 ("친환경 소재 물성 시험 및 분석", "Test and analyze eco-material properties"),
                 ("제품화 스케일업 지원", "Support scale-up to products")],
         quals=[("재료·화학 관련 전공", "Degree in materials/chemistry"),
                ("실험 설계·분석 역량", "Experiment design and analysis skills"),
                ("협업 능력", "Collaboration skills")],
         plus=[("탄산칼슘·친환경 소재 경험", "Calcium-carbonate / eco-material experience"),
               ("논문·특허 실적", "Publications or patents")]),
    dict(slug="susinje", biz="susinje-farm.html", color="#3E7C4F",
         role_ko="스마트팜 재배 담당", role_en="Smart Farm Cultivation Specialist",
         team_ko="수신제팜", team_en="SUSINJE FARM",
         loc_ko="전북 김제", loc_en="Gimje, Jeonbuk",
         type_ko="정규직", type_en="Full-time",
         duties=[("수경재배 작물 재배 및 양액 관리", "Grow hydroponic crops and manage nutrient solution"),
                 ("스마트팜 환경 데이터 운영", "Operate smart-farm environment data"),
                 ("출하 품질 관리", "Manage harvest quality")],
         quals=[("원예·농학 관련 전공 또는 재배 경력", "Degree in horticulture/agriculture or growing experience"),
                ("스마트팜 시스템에 대한 이해", "Understanding of smart-farm systems"),
                ("현장 근무 가능자", "Willing to work on-site")],
         plus=[("수경재배 경험", "Hydroponics experience"),
               ("스마트팜 운영 경험", "Smart-farm operations experience")]),
]

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
          <span class="value-no" style="color:#166578">02</span>
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
            <p class="t-ko">미생물과 데이터로 1차 산업을 다시 씁니다.</p>
            <p class="t-en">Rewriting primary industry with microbes and data.</p>
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

# short homepage teaser version — avoids repeating sustainability.html's full copy verbatim
ESG_TEASER = """      <div class="esg-grid reveal">
        <div class="esg-card">
          <span class="label">E — ENVIRONMENT</span>
          <h3><span class="t-ko">자원의 재순환</span><span class="t-en">Circular resources</span></h3>
          <p class="t-ko">패각 업사이클과 순환여과로 폐기물을 줄입니다.</p>
          <p class="t-en">Shell upcycling and recirculating water cut waste.</p>
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
            <span class="role" id="ringRole" style="color:#0E4E78">양식</span>
            <span class="ko" id="ringKo">컬리버</span>
            <span class="en" id="ringEn">CULIVER</span>
          </div>
          <button class="node active" data-i="0" data-no="01" data-name-ko="컬리버" data-name-en="CULIVER" data-role="양식" data-color="#0E4E78"
            data-dko="육상 BFT 양식장에서 나온 사육수를 에이엠피로 보내 정화합니다. 순환의 출발점입니다."
            data-den="Rearing water from land-based BFT farms flows to AMP for treatment — the start of the loop."
            style="top:2%;left:50%;background:#0E4E78;box-shadow:0 16px 34px -12px #0E4E78">
            <span class="no">01</span><span class="nm">컬리버</span>
          </button>
          <button class="node" data-i="1" data-no="02" data-name-ko="에이엠피" data-name-en="AMP" data-role="수처리" data-color="#166578"
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
          <button class="node" data-i="3" data-no="04" data-name-ko="코발티브" data-name-en="COBALTIVE" data-role="자원순환" data-color="#6E5D38"
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
            <span class="active" style="background:#0E4E78"></span><span></span><span></span><span></span>
          </div>
        </div>
      </div>
"""

HISTORY_BLOCK = """      <div class="hist-years reveal" id="histYears">
        <button class="hist-year" data-i="0" data-color="#0E4E78" data-tko="컬리버 설립" data-ten="CULIVER founded"
          data-dko="육상 흰다리새우 BFT 양식 연구로 그룹의 출발점을 세웠습니다."
          data-den="The group began with R&amp;D in land-based whiteleg shrimp BFT aquaculture.">2019</button>
        <button class="hist-year" data-i="1" data-color="#166578" data-tko="에이엠피 합류 · 수처리 내재화" data-ten="AMP joins — water treatment"
          data-dko="수처리·미생물 기술을 그룹에 내재화하며 순환 구조의 두 번째 축을 마련했습니다."
          data-den="Brought water-treatment and microbial technology in-house, forming the second axis of the loop.">2021</button>
        <button class="hist-year" data-i="2" data-color="#6E5D38" data-tko="코발티브 출범 · 자원순환" data-ten="COBALTIVE launched"
          data-dko="굴 패각 업사이클 사업을 시작하며 자원순환 영역으로 확장했습니다."
          data-den="Started oyster-shell upcycling, expanding into the circular-materials domain.">2023</button>
        <button class="hist-year" data-i="3" data-color="#3E7C4F" data-tko="수신제팜 편입 · 스마트팜" data-ten="SUSINJE FARM joins"
          data-dko="수경재배 스마트팜과 신선 유통을 더해 바다에서 농장까지 잇는 포트폴리오를 완성했습니다."
          data-den="Added hydroponic smart-farming and fresh distribution, completing the ocean-to-farm portfolio.">2025</button>
        <button class="hist-year active" data-i="4" data-color="#06202B" data-tko="컬리버 그룹 지주 체제 전환" data-ten="Holding structure"
          data-dko="네 개 사업을 하나의 그룹 비전 아래 정렬하고 지주 체제로 전환했습니다."
          data-den="Aligned four businesses under one group vision and transitioned to a holding structure."
          style="background:#06202B;border-color:#06202B">2026</button>
      </div>
      <div class="hist-detail">
        <div class="hist-big" id="histBig" style="color:#06202B">2026</div>
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
              <input name="company" placeholder="컬리버" data-ph-ko="컬리버" data-ph-en="e.g. CULIVER" autocomplete="organization">
            </label>
            <label>
              <span class="lbl"><span class="t-ko">문의 유형</span><span class="t-en">Inquiry type</span></span>
              <!-- native <option> can't hold t-ko/t-en spans; value stays the
                   fixed Korean string (matched elsewhere, e.g. prefillFromQuery),
                   main.js swaps the displayed label from data-ko/data-en -->
              <select name="type">
                <option value="사업 제휴" data-ko="사업 제휴" data-en="Business partnership">사업 제휴</option>
                <option value="투자 · IR" data-ko="투자 · IR" data-en="Investment · IR">투자 · IR</option>
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
        <h2 class="h2 t-ko">함께 만들<br>순환을 제안하세요</h2>
        <h2 class="h2 t-en">Let's build a loop together</h2>
        <div class="contact-info">
          <div class="kv"><span class="kv-k">EMAIL</span><span class="kv-v">contact@culiver.co.kr</span></div>
          <div class="kv"><span class="kv-k">TEL</span><span class="kv-v">000-0000-0000</span></div>
          <div class="kv">
            <span class="kv-k"><span class="t-ko">주소</span><span class="t-en">ADDRESS</span></span>
            <span class="addr t-ko">본사 주소를 입력하세요 (실제 정보로 교체)</span>
            <span class="addr t-en">Replace with headquarters address</span>
          </div>
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
    "index.html": ("컬리버 그룹 CULIVER GROUP — 바다에서 농장까지, 순환하는 내일을 기릅니다",
                   "컬리버 그룹은 스마트 양식, 수처리, 자원순환 소재, 스마트팜을 잇는 지속가능한 생산 생태계를 만들어 갑니다."),
    "about.html": ("그룹소개 About — 컬리버 그룹 CULIVER GROUP", "‘기른다’는 하나의 동사에서 출발한 컬리버 그룹의 비전과 연혁, 조직, 그룹 개요를 소개합니다."),
    "business.html": ("사업영역 Business — 컬리버 그룹 CULIVER GROUP", "스마트 양식·수처리·자원순환 소재·스마트팜, 하나의 순환으로 연결된 컬리버 그룹의 네 개 사업."),
    "sustainability.html": ("지속가능경영 Sustainability — 컬리버 그룹 CULIVER GROUP", "ESG는 별도 활동이 아니라 컬리버 그룹 네 사업이 존재하는 이유입니다."),
    "ir.html": ("투자정보 IR — 컬리버 그룹 CULIVER GROUP", "컬리버 그룹의 지배구조, 주요 지표, 공시·자료실과 IR 문의 안내."),
    "newsroom.html": ("뉴스룸 Newsroom — 컬리버 그룹 CULIVER GROUP", "컬리버 그룹과 계열사의 보도자료·소식·채용 소식을 전합니다."),
    "news.html": ("뉴스룸 Newsroom — 컬리버 그룹 CULIVER GROUP", "컬리버 그룹과 계열사의 보도자료·소식·채용 소식을 전합니다."),
    "careers.html": ("채용 Careers — 컬리버 그룹 CULIVER GROUP", "바다와 농장, 실험실과 현장을 잇는 사람들을 찾습니다. 인재상·채용 절차·공고·복리후생 안내."),
    "contact.html": ("문의 Contact — 컬리버 그룹 CULIVER GROUP", "사업 제휴, 투자, 제품·구매, 채용 등 컬리버 그룹에 문의하세요."),
}
for _c in BIZ:
    TITLES[_c["file"]] = (f"{_c['nko']} {_c['nen']} — 컬리버 그룹 CULIVER GROUP", _c["dko"])
for _r in ROLES:
    TITLES[f"careers-{_r['slug']}.html"] = (f"{_r['role_ko']} ({_r['team_ko']}) 채용 — 컬리버 그룹", f"{_r['team_ko']} {_r['role_ko']} 채용 공고")

# ================================================================= HOME
home = f"""  <section id="top" class="hero">
    <div class="hero-glow"></div>
    <div class="hero-inner">
      <p class="hero-eyebrow">CULIVER GROUP</p>
      <h1 class="t-ko">바다에서 농장까지,<br>순환하는 내일을 기릅니다</h1>
      <h1 class="t-en">From ocean to farm,<br>we cultivate a circular tomorrow</h1>
      <p class="hero-lead t-ko">스마트 양식·수처리·자원순환 소재·스마트팜, 4개 계열사를 둔 지주회사입니다.<br>한 사업의 부산물이 다음 사업의 원료가 되는 순환 생산 구조를 만듭니다.</p>
      <p class="hero-lead t-en">A holding company over four affiliates — smart aquaculture, water treatment, upcycled materials, and smart farming — where one business's byproduct becomes the next one's raw material.</p>
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
      <div class="bento-grid reveal">
{biz_bento()}      </div>
    </div>
  </section>

  <section id="cycle" class="section tall bg-paper">
    <div class="wrap">
      <div class="cycle-head reveal">
        <p class="eyebrow">THE LOOP</p>
        <h2 class="h2 t-ko">네 사업이 아니라, 하나의 순환입니다</h2>
        <h2 class="h2 t-en">Not four businesses — one loop</h2>
        <p class="sub t-ko">컬리버 그룹이 무엇을 하는 회사인지는 이 순환 하나로 설명됩니다. 노드를 눌러 각 사업이 맡는 역할을 확인하세요.</p>
        <p class="sub t-en">This loop is the simplest way to understand what CULIVER Group does. Tap a node to see each business's role.</p>
      </div>
{CYCLE_BLOCK}    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap about-grid">
      <div class="about-intro reveal">
        <p class="eyebrow">ABOUT CULIVER GROUP</p>
        <h2 class="h2 t-ko">기르는 일의<br>순환을 설계합니다</h2>
        <h2 class="h2 t-en">We design the cycle<br>of cultivation</h2>
        <p class="t-ko">컬리버 그룹은 ‘기른다’는 하나의 동사에서 출발했습니다. 각 사업은 서로의 출발점이 됩니다.</p>
        <p class="t-en">CULIVER Group began with a single verb: to cultivate. Each business feeds the next.</p>
        <a class="more-link" href="about.html"><span class="t-ko">그룹소개 자세히</span><span class="t-en">More about us</span> →</a>
      </div>
{VALUES_TEASER}    </div>
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
{ESG_TEASER}      <a class="more-link" href="sustainability.html" style="color:#4FA3A5"><span class="t-ko">지속가능경영 자세히</span><span class="t-en">More on sustainability</span> →</a>
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
      <div class="news-grid reveal" id="newsPreview">
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
              [("about.html", "그룹소개", "About")])
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

  <section id="org" class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">ORGANIZATION</p>
        <h2 class="h2 t-ko">그룹 구조</h2>
        <h2 class="h2 t-en">Group structure</h2>
        <p class="lead"><span class="t-ko">지주 체제 아래 네 개의 계열사가 하나의 순환으로 연결됩니다.</span><span class="t-en">Under a holding structure, four affiliates are connected as one loop.</span></p>
      </div>
      <div class="org reveal">
        <div class="org-top"><div class="t">컬리버 그룹</div><div class="s">CULIVER GROUP · HOLDINGS</div></div>
        <div class="org-stem"></div>
        <div class="org-row">
          <a class="org-node" href="culiver-aqua.html"><div class="nm">컬리버</div><div class="en">CULIVER</div><div class="role">스마트 양식</div></a>
          <a class="org-node" href="amp.html" style="border-top-color:#1B6E7D"><div class="nm">에이엠피</div><div class="en">AMP</div><div class="role">수처리</div></a>
          <a class="org-node" href="cobaltive.html" style="border-top-color:#8E7A5C"><div class="nm">코발티브</div><div class="en">COBALTIVE</div><div class="role">자원순환 소재</div></a>
          <a class="org-node" href="susinje-farm.html" style="border-top-color:#3E7C4F"><div class="nm">수신제팜</div><div class="en">SUSINJE FARM</div><div class="role">스마트팜·유통</div></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
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

  <section id="ci" class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">BRAND IDENTITY</p>
        <h2 class="h2 t-ko">그룹 컬러</h2>
        <h2 class="h2 t-en">Group colors</h2>
        <p class="lead"><span class="t-ko">바다에서 농장까지, 순환을 잇는 네 사업의 색을 담았습니다.</span><span class="t-en">From ocean to farm — a palette that links the four businesses of the loop.</span></p>
      </div>
      <div class="ci-grid reveal">
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
    page_hero("OUR BUSINESS", "하나의 순환, 네 개의 사업", "One cycle, four businesses",
              "양식에서 나온 물은 정화되고, 껍데기는 소재가 되며, 데이터는 농장으로 이어집니다.",
              "Water is treated and returned, shells become materials, data flows to the farm.",
              [("business.html", "사업영역", "Business")])
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
        <p class="lead"><span class="t-ko">각 계열사를 눌러 사업·기술·제품을 자세히 확인하세요.</span><span class="t-en">Tap each affiliate for its business, technology, and products.</span></p>
      </div>
      <div class="biz-list reveal">
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
    page_hero("SUSTAINABILITY", "지속가능성은 사업 그 자체입니다", "Sustainability is the business itself",
              "ESG는 컬리버 그룹의 별도 활동이 아니라, 네 사업이 존재하는 이유입니다.",
              "ESG is not a side program — it is why our four businesses exist.",
              [("sustainability.html", "지속가능경영", "Sustainability")])
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

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">IMPACT</p>
        <h2 class="h2 t-ko">성과 지표</h2>
        <h2 class="h2 t-en">Our impact</h2>
        <p class="lead"><span class="t-ko">‘예시’로 표기된 수치는 실제 성과 데이터로 교체하세요.</span><span class="t-en">Figures marked “예시 / example” should be replaced with real performance data.</span></p>
      </div>
      <div class="metrics bento-metrics reveal">
        <div class="metric"><span class="v" style="color:#0E4E78"><span data-count="100">0</span>%</span><span class="l"><span class="t-ko">무항생제 양식</span><span class="t-en">Antibiotic-free</span></span></div>
        <div class="metric"><span class="v" style="color:#166578"><span class="t-ko">예시</span><span class="t-en">example</span></span><span class="l"><span class="t-ko">양식수 재이용률</span><span class="t-en">Water reused</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
        <div class="metric"><span class="v" style="color:#6E5D38"><span class="t-ko">예시</span><span class="t-en">example</span></span><span class="l"><span class="t-ko">재활용 굴패각(톤)</span><span class="t-en">Shells recycled</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
        <div class="metric"><span class="v" style="color:#3E7C4F"><span class="t-ko">예시</span><span class="t-en">example</span></span><span class="l"><span class="t-ko">지역 일자리</span><span class="t-en">Local jobs</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
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
      <div class="commitments reveal">
        <div class="commitment"><span class="no">01</span><div><h3><span class="t-ko">무항생제·저배출 생산</span><span class="t-en">Antibiotic-free, low-emission production</span></h3><p><span class="t-ko">BFT 양식과 순환여과로 항생제 사용과 오염 배출을 구조적으로 낮춥니다.</span><span class="t-en">BFT aquaculture and recirculating filtration structurally reduce antibiotics and discharge.</span></p></div></div>
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
# ================================================================= IR / INVESTOR RELATIONS
# Structure is real; figures/filings are placeholders clearly marked
# "준비 중 / soon" since there is no actual financial data yet.
ir_contact = "contact.html?" + urllib.parse.urlencode({"type": "투자 · IR"})
ir = (
    page_hero("INVESTOR RELATIONS", "투자정보", "Investor Relations",
              "지주 체제 아래 투명한 지배구조와 데이터 기반 의사결정을 지향합니다.",
              "Under a holding structure, we pursue transparent governance and data-driven decisions.",
              [("ir.html", "투자정보", "IR")])
    + """  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">GOVERNANCE</p>
        <h2 class="h2 t-ko">지배구조</h2>
        <h2 class="h2 t-en">Governance</h2>
        <p class="lead"><span class="t-ko">컬리버 그룹은 지주회사 체제 아래 네 개 계열사를 하나의 비전으로 정렬합니다.</span><span class="t-en">CULIVER Group aligns its four affiliates under one vision through a holding-company structure.</span></p>
      </div>
      <div class="commitments reveal">
        <div class="commitment"><span class="no">01</span><div><h3><span class="t-ko">지주 체제</span><span class="t-en">Holding structure</span></h3><p><span class="t-ko">지주회사가 네 계열사의 전략과 자원 배분을 통합 관리합니다.</span><span class="t-en">The holding company integrates strategy and capital allocation across the four affiliates.</span></p></div></div>
        <div class="commitment"><span class="no">02</span><div><h3><span class="t-ko">투명한 의사결정</span><span class="t-en">Transparent decisions</span></h3><p><span class="t-ko">데이터에 기반한 의사결정과 정보 공개를 원칙으로 합니다.</span><span class="t-en">Data-driven decision-making and disclosure are our operating principles.</span></p></div></div>
        <div class="commitment"><span class="no">03</span><div><h3><span class="t-ko">순환 기반 성장</span><span class="t-en">Circular growth</span></h3><p><span class="t-ko">한 사업의 부산물이 다음 사업의 원료가 되는 구조로 지속 성장을 추구합니다.</span><span class="t-en">We pursue durable growth through a loop where each business's byproduct feeds the next.</span></p></div></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">KEY FIGURES</p>
        <h2 class="h2 t-ko">주요 지표</h2>
        <h2 class="h2 t-en">Key figures</h2>
        <p class="lead"><span class="t-ko">‘준비 중’ 항목은 실제 재무·경영 데이터로 교체하세요.</span><span class="t-en">Replace the “준비 중 / soon” items with real financial data.</span></p>
      </div>
      <div class="metrics bento-metrics reveal">
        <div class="metric"><span class="v" style="color:#0E4E78">4</span><span class="l"><span class="t-ko">계열사</span><span class="t-en">Affiliates</span></span></div>
        <div class="metric"><span class="v" style="color:#14606E"><span class="t-ko">준비 중</span><span class="t-en">soon</span></span><span class="l"><span class="t-ko">연결 매출</span><span class="t-en">Consolidated revenue</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
        <div class="metric"><span class="v" style="color:#6E5D38"><span class="t-ko">준비 중</span><span class="t-en">soon</span></span><span class="l"><span class="t-ko">영업이익</span><span class="t-en">Operating profit</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
        <div class="metric"><span class="v" style="color:#3E7C4F"><span class="t-ko">준비 중</span><span class="t-en">soon</span></span><span class="l"><span class="t-ko">임직원 수</span><span class="t-en">Employees</span></span><span class="note"><span class="t-ko">실제 수치로 교체</span><span class="t-en">replace</span></span></div>
      </div>
    </div>
  </section>

  <section class="section tall bg-paper">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow">DISCLOSURES</p>
        <h2 class="h2 t-ko">공시 · 자료실</h2>
        <h2 class="h2 t-en">Disclosures &amp; filings</h2>
        <p class="lead"><span class="t-ko">감사보고서·IR 자료는 준비 중입니다. 실제 파일로 링크를 교체하세요.</span><span class="t-en">Audit reports and IR materials are in preparation — replace with real files.</span></p>
      </div>
      <div class="report-row reveal">
        <span class="btn-outline is-disabled" aria-disabled="true"><span class="t-ko">📄 감사보고서 (준비 중)</span><span class="t-en">📄 Audit report (soon)</span></span>
        <span class="btn-outline is-disabled" aria-disabled="true"><span class="t-ko">📄 IR 자료 (준비 중)</span><span class="t-en">📄 IR deck (soon)</span></span>
      </div>
    </div>
  </section>

  <section class="section bg-card">
    <div class="wrap reveal">
      <div class="cta-band" style="background:linear-gradient(160deg,#041821,#0C3A47 60%,#1B6E7D 130%)">
        <div>
          <h2><span class="t-ko">투자·IR 문의</span><span class="t-en">Investor inquiries</span></h2>
          <p><span class="t-ko">투자 및 IR 관련 문의를 환영합니다.</span><span class="t-en">We welcome investment and IR inquiries.</span></p>
        </div>
        <a class="btn btn-primary" href=\"""" + ir_contact + """"><span class="t-ko">IR 문의하기</span><span class="t-en">Contact IR</span> →</a>
      </div>
    </div>
  </section>
"""
)
write("ir.html", ir, active="ir.html")

# ================================================================= NEWSROOM
newsroom = (
    page_hero("NEWSROOM", "컬리버 그룹 소식", "News from the group",
              "컬리버 그룹과 계열사의 보도자료·소식·채용 소식을 전합니다.",
              "Press releases, updates, and hiring news from CULIVER Group and its affiliates.",
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
    page_hero("CAREERS", "기르는 사람들과 함께 자랍니다", "Grow with the growers",
              "바다와 농장, 실험실과 현장을 잇는 사람들을 찾습니다.",
              "We look for people who connect the sea and the farm, the lab and the field.",
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
        <div class="step"><div class="n">4</div><h3><span class="t-ko">입사</span><span class="t-en">Onboarding</span></h3><p><span class="t-ko">온보딩과 함께 컬리버 그룹의 일원이 됩니다.</span><span class="t-en">Join CULIVER Group with a full onboarding.</span></p></div>
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
      <div class="roles reveal">
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
    page_hero("CONTACT", "함께 만들 순환을 제안하세요", "Let's build a loop together",
              "사업 제휴, 투자, 제품·구매, 채용 등 무엇이든 문의해 주세요.",
              "Partnerships, investment, products, hiring — reach out about anything.",
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
          <h3><span class="t-ko">{pko}</span><span class="t-en">{pen}</span></h3>
          <p><span class="t-ko">{dko}</span><span class="t-en">{den}</span></p>
        </div>
""" for (pko, pen, dko, den) in c["products"])
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
      <div class="related-grid reveal">
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

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">TECHNOLOGY</p>
        <h2 class="h2 t-ko">핵심 기술</h2>
        <h2 class="h2 t-en">Core technology</h2>
      </div>
      <div class="feature-grid reveal">
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
      <div class="product-grid reveal">
{prods}      </div>
    </div>
  </section>

  <section class="section tall bg-card">
    <div class="wrap">
      <div class="section-intro reveal">
        <p class="eyebrow" style="color:{c['ink']}">BY THE NUMBERS</p>
        <h2 class="h2 t-ko">주요 지표</h2>
        <h2 class="h2 t-en">Key figures</h2>
        <p class="lead"><span class="t-ko">‘예시’ 표기는 실제 수치로 교체하세요.</span><span class="t-en">Replace any “예시 / replace” figures with real data.</span></p>
      </div>
      <div class="metrics reveal">
{mets}      </div>
    </div>
  </section>
"""
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
    page_hero("NEWSROOM", "컬리버 그룹 소식", "News from the group",
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
