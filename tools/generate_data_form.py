#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates content/data-to-fill.xlsx — a fill-in form listing the site's
data, with a 상태(status) column showing what is already reflected from the
provided company materials (제품DB · IR) vs. what is still needed.

    pip install -r tools/requirements-dev.txt   # openpyxl
    python3 tools/generate_data_form.py

Status legend:
  반영됨  — already applied from the provided docs
  필요    — still missing; please provide
  선택    — optional refinement
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "data-to-fill.xlsx")

HEAD_FILL = PatternFill("solid", fgColor="06202B")
HEAD_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(bold=True, size=15, color="06202B")
SUB_FONT = Font(size=10.5, color="445159")
FILL_COL = PatternFill("solid", fgColor="EAF6F5")     # 입력 칸
DONE_FILL = PatternFill("solid", fgColor="E4F0E6")    # 반영됨
NEED_FILL = PatternFill("solid", fgColor="FBE3D0")    # 필요
OPT_FILL = PatternFill("solid", fgColor="EFEDE7")     # 선택
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top")
THIN = Side(style="thin", color="D9D6CE")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

COLS = ["위치 (페이지)", "항목", "상태", "현재 값 / 반영 내용", "✍️ 채워주실 값", "비고"]
WIDTHS = [18, 22, 10, 38, 34, 26]
STATUS_FILL = {"반영됨": DONE_FILL, "필요": NEED_FILL, "선택": OPT_FILL}


def sheet(wb, name, title, sub):
    ws = wb.create_sheet(name)
    ws["A1"] = title; ws["A1"].font = TITLE_FONT
    ws["A2"] = sub; ws["A2"].font = SUB_FONT
    ws.merge_cells("A1:F1"); ws.merge_cells("A2:F2")
    for i, c in enumerate(COLS, 1):
        cell = ws.cell(row=4, column=i, value=c)
        cell.font = HEAD_FONT; cell.fill = HEAD_FILL
        cell.alignment = Alignment(vertical="center"); cell.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = WIDTHS[i - 1]
    ws.freeze_panes = "A5"; ws.row_dimensions[4].height = 22
    return ws


def rows(ws, data, start=5):
    r = start
    for loc, item, status, cur, hint, note in data:
        ws.cell(row=r, column=1, value=loc).alignment = WRAP
        ws.cell(row=r, column=2, value=item).alignment = WRAP
        st = ws.cell(row=r, column=3, value=status); st.alignment = CENTER
        st.fill = STATUS_FILL.get(status, OPT_FILL); st.font = Font(bold=True, size=10)
        ws.cell(row=r, column=4, value=cur).alignment = WRAP
        fill = ws.cell(row=r, column=5, value=hint); fill.alignment = WRAP
        fill.font = Font(size=9.5, italic=True, color="9AA6A0")
        if status != "반영됨":
            fill.fill = FILL_COL
        ws.cell(row=r, column=6, value=note).alignment = WRAP
        for c in range(1, 7):
            ws.cell(row=r, column=c).border = BORDER
        ws.row_dimensions[r].height = 32
        r += 1
    return r


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb = Workbook(); wb.remove(wb.active)

    # ---- 안내 ----
    g = wb.create_sheet("안내"); g.sheet_view.showGridLines = False
    g["A1"] = "컬리버 그룹 웹사이트 — 데이터 입력 양식 (v2, 자료 반영 후 갱신)"
    g["A1"].font = Font(bold=True, size=16, color="06202B")
    lines = [
        "",
        "제공해주신 자료(제품DB·IR)로 상당 부분을 이미 사이트에 반영했습니다. 이 양식은 '무엇이 반영됐고, 무엇이 아직 필요한지'를 한눈에 보여주도록 갱신했습니다.",
        "",
        "상태 표시",
        "• 반영됨 (초록) — 주신 자료로 이미 사이트에 적용된 항목입니다. 확인만 해주세요. 수정이 필요하면 '채워주실 값'에 적어주세요.",
        "• 필요 (주황) — 자료에 없어 아직 비어 있거나 '준비 중'인 항목입니다. 이걸 우선 채워주세요.",
        "• 선택 (회색) — 있으면 더 좋은 보완 항목입니다.",
        "",
        "사용법",
        "1. '필요'(주황) 항목의 하늘색 '✍️ 채워주실 값' 칸을 먼저 채워주세요.",
        "2. '반영됨' 항목은 내용이 맞는지 확인만 하시고, 고칠 게 있을 때만 값을 적어주세요.",
        "3. 다 채운 파일을 전달해주시면 사이트에 반영합니다.",
        "",
        "이 양식에 없는 것",
        "• 뉴스 기사 — /admin.html 관리자 페이지에서 직접 작성·수정 (이미지 업로드·6개 언어 지원).",
        "• 이미지 파일 — 대표이사 사진, 계열사·제품 사진 등은 파일로 함께 전달해주세요(제품DB의 이미지 파일명만 있고 실제 파일은 미첨부 상태).",
    ]
    for i, ln in enumerate(lines, 3):
        cell = g.cell(row=i, column=1, value=ln)
        cell.font = Font(bold=ln in ("상태 표시", "사용법", "이 양식에 없는 것"), size=11)
        cell.alignment = Alignment(wrap_text=True)
    g.column_dimensions["A"].width = 120

    # ---- ① 회사 기본정보 ----
    ws = sheet(wb, "① 회사 기본정보", "① 회사 기본정보",
               "푸터·문의·그룹개요 전역에 노출. ‘필요’ 항목(이메일·전화)을 우선 채워주세요.")
    rows(ws, [
        ("그룹개요·인사말", "대표이사", "반영됨", "정석 (자료 반영)", "수정 시 기입", ""),
        ("그룹개요·홈·연혁", "설립 연도", "반영됨", "2024년 (컬리버 법인설립)", "수정 시 기입", ""),
        ("푸터·문의·개요", "본사 주소", "반영됨", "전남 순천시 (자료 반영)", "상세 도로명 주소", "번지·건물까지 주시면 정밀 표기"),
        ("푸터·문의", "홈페이지", "반영됨", "culiver.ai (자료 반영)", "수정 시 기입", ""),
        ("푸터·문의", "대표 이메일", "필요", "미표기 (문의는 폼으로만)", "예: info@culiver.ai", "표시용 대표 이메일"),
        ("푸터·문의", "대표 전화", "필요", "미표기", "예: 061-000-0000", "표시용 대표 전화"),
        ("문의 폼 수신", "문의 접수 이메일", "필요", "환경변수 CONTACT_TO_EMAIL 미설정", "폼 제출을 받을 이메일", "Vercel 환경변수로 설정"),
        ("푸터 하단", "사업자 정보", "선택", "미표기", "법인명/사업자등록번호/대표자", "법적 표기용"),
    ])

    # ---- ② 계열사 사업·제품 ----
    ws = sheet(wb, "② 계열사 사업·제품", "② 계열사 사업 · 제품",
               "제품DB 기준으로 반영 완료. 수신제팜만 자료가 없어 ‘준비 중’입니다.")
    rows(ws, [
        ("컬리버 상세", "사업·제품", "반영됨", "통합솔루션(사료·6종 미생물·PCR진단·Shrimp365) + 제품 3종(컬리버1호·숨쉘·Shrimp365)", "보완 시 기입", ""),
        ("에이엠피 상세", "사업·제품", "반영됨", "이차전지 전구체 소재·장비/폐수처리/공조부품 + 제품 6종", "보완 시 기입", ""),
        ("코발티브 상세", "사업·제품", "반영됨", "패각콘크리트 업사이클(가구·오브제·굿즈) + 제품 6종", "보완 시 기입", ""),
        ("수신제팜 상세", "사업·제품", "필요", "자료 없음 → ‘준비 중’ 처리", "사업 분야·제품·근무지 등", "확정되면 상세 페이지 채움"),
        ("전 계열사", "제품 이미지", "필요", "이미지 자리(그라디언트)만 표시", "제품 사진 파일 전달", "제품DB에 파일명만 있고 실물 미첨부"),
    ])

    # ---- ③ 지표·IR ----
    ws = sheet(wb, "③ 지표 · IR", "③ 지표 · 투자정보(IR)",
               "IR 자료의 실측·목표 수치는 반영 완료. 최신·정밀 수치는 보완 가능.")
    rows(ws, [
        ("컬리버·홈·ESG", "실측 성과", "반영됨", "생존율 70% · 수질 정상화 7일 · 미생물 비용 -65% · 6종 미생물", "갱신 시 기입", "IR 자료 반영"),
        ("IR", "시장 지표", "반영됨", "글로벌 양식 160조 · 국내 자급률 10%", "갱신 시 기입", ""),
        ("IR", "매출 로드맵(목표)", "반영됨", "’25 5.5억 → ’27 58억 → ’30 271억 → ’33 730억 (목표)", "갱신 시 기입", "‘목표치’로 명시함"),
        ("IR", "인증·실적", "반영됨", "TIPS·기업부설연구소·벤처확인·전남 청년기업·Shrimp365 상표·아쿠아포닉스 특허 등", "추가 시 기입", ""),
        ("IR", "재무 실적(매출·이익·인원)", "선택", "미표기(목표만 표기)", "공개 가능 시 실적 수치", "공개 가능한 확정 실적이 있으면"),
        ("에이엠피·코발티브", "세부 성과 수치", "선택", "핵심 지표만 표기", "수주액·재활용량 등 있으면", ""),
    ])

    # ---- ④ 자료·파일 ----
    ws = sheet(wb, "④ 자료·파일", "④ 다운로드 자료 (PDF 등)",
               "현재 ‘준비 중’ 버튼으로 비활성. 파일을 주시면 실제 다운로드로 연결합니다.")
    rows(ws, [
        ("투자정보(IR)", "IR 자료(IR Deck)", "필요", "‘준비 중’ 비활성", "PDF/PPT 파일", "주신 34p IR을 게시용으로 올릴지 확인"),
        ("투자정보(IR)", "감사보고서", "필요", "‘준비 중’ 비활성", "PDF 파일", ""),
        ("지속가능경영", "지속가능경영 보고서", "선택", "‘준비 중’ 비활성", "PDF 파일", ""),
    ])

    # ---- ⑤ 채용 ----
    ws = sheet(wb, "⑤ 채용 공고", "⑤ 채용 공고",
               "직무를 실제 사업라인(양식·소재환경·제품디자인)·본사(전남 순천)로 정정 반영. 실제 공고 내용은 보완 가능.")
    rows(ws, [
        ("채용-컬리버", "양식 생산·관리 매니저", "반영됨", "전남 순천 · 실제 사업 기준", "실제 JD로 교체 시 기입", ""),
        ("채용-에이엠피", "소재·환경 엔지니어", "반영됨", "전남 순천(협의) · 실제 사업 기준", "실제 JD로 교체 시 기입", ""),
        ("채용-코발티브", "제품 디자이너", "반영됨", "전남 순천(협의) · 실제 사업 기준", "실제 JD로 교체 시 기입", ""),
        ("채용-수신제팜", "직무", "필요", "‘준비 중’ 처리", "실제 채용 직무", "채용 시 공개"),
        ("채용(공통)", "지원 방법", "선택", "지원하기 → 문의 폼 프리필", "이메일/채용사이트 링크 등", ""),
    ])

    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
