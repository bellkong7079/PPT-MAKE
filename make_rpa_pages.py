"""
윤종빈 RPA 파트 - 통합 포트폴리오 디자인 시스템으로 재현
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import fitz

# ── 폰트 등록 ──────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('MG',     'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGBold', 'C:/Windows/Fonts/malgunbd.ttf'))

# ── 색상 팔레트 ────────────────────────────────────────────────
BG         = HexColor('#0e1729')   # 메인 배경
CARD       = HexColor('#1d293b')   # 카드 배경
CARD_DARK  = HexColor('#202b3e')   # 어두운 카드 (코드 블록)
BORDER     = HexColor('#334054')   # 카드 테두리
TEXT_PRI   = HexColor('#f1f5f9')   # 주 텍스트
TEXT_SEC   = HexColor('#94a2b8')   # 보조 텍스트
TEXT_DARK  = HexColor('#64738b')   # 어두운 보조
ACCENT_V   = HexColor('#6266f1')   # 보라 (배지, 강조)
ACCENT_VL  = HexColor('#818bf7')   # 연보라
ACCENT_G   = HexColor('#0fb981')   # 초록 (성과)
ACCENT_O   = HexColor('#f59d0a')   # 주황 (주의)
CODE_BLUE  = HexColor('#a5d5ff')   # 코드 파란
CODE_GREEN = HexColor('#6ee7b6')   # 코드 초록
CODE_PUR   = HexColor('#d1a7ff')   # 코드 보라
CODE_ORG   = HexColor('#ffa657')   # 코드 주황
RED_DOT    = HexColor('#ff5f56')
YEL_DOT    = HexColor('#ffbd2e')
GRN_DOT    = HexColor('#27c93f')
FOOTER_BG  = HexColor('#0a1120')

W, H = 1920, 1080   # 네이티브 1920×1080

SCREEN_W, SCREEN_H = W, H


# ── 헬퍼 함수 ──────────────────────────────────────────────────
def set_fill(c, color):
    c.setFillColor(color)

def set_stroke(c, color):
    c.setStrokeColor(color)

def full_bg(c, color=BG):
    """전체 배경 채우기"""
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_footer(c, left_text, right_text, page_num):
    """하단 푸터"""
    y_line = 52
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.7)
    c.line(80, y_line + 16, W - 80, y_line + 16)
    c.setFont('MG', 13)
    c.setFillColor(TEXT_DARK)
    c.drawString(80, y_line, left_text)
    c.drawRightString(W - 80, y_line, right_text)
    c.setFillColor(TEXT_SEC)
    c.drawRightString(W - 78, y_line, str(page_num))

def badge(c, x, y, text, color=ACCENT_V, text_color=TEXT_PRI, font_size=13, pad_x=12, pad_h=22):
    """섹션 번호 배지"""
    c.setFont('MGBold', font_size)
    tw = c.stringWidth(text, 'MGBold', font_size)
    bw = tw + pad_x * 2
    c.setFillColor(color)
    c.roundRect(x, y - 4, bw, pad_h, 5, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.drawString(x + pad_x, y + 3, text)
    return bw

def tag(c, x, y, text, color=BORDER, text_color=TEXT_SEC, font_size=12):
    """기술 스택 태그"""
    c.setFont('MG', font_size)
    tw = c.stringWidth(text, 'MG', font_size)
    bw = tw + 18
    bh = 22
    c.setFillColor(CARD)
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.roundRect(x, y - 2, bw, bh, 4, fill=1, stroke=1)
    c.setFillColor(text_color)
    c.drawString(x + 9, y + 4, text)
    return bw + 8

def card_rect(c, x, y, w, h, fill=CARD, stroke=BORDER, lw=0.8, radius=5):
    """카드 배경"""
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def left_accent_line(c, x, y, h, color=ACCENT_V, lw=3):
    """카드 왼쪽 세로 강조선"""
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x, y, x, y + h)

def text_block(c, x, y, text, font='MG', size=9.5, color=TEXT_PRI,
               max_width=None, line_height=14):
    """텍스트 블록 (줄바꿈 지원)"""
    c.setFont(font, size)
    c.setFillColor(color)
    if max_width is None:
        c.drawString(x, y, text)
        return y
    words = text.split(' ')
    line = ''
    cy = y
    for word in words:
        test = line + (' ' if line else '') + word
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, cy, line)
            cy -= line_height
            line = word
    if line:
        c.drawString(x, cy, line)
        cy -= line_height
    return cy

def bullet_item(c, x, y, text, font='MG', size=9, color=TEXT_PRI,
                max_w=200, line_h=13, bullet_color=ACCENT_V):
    """불릿 포인트 아이템"""
    # 삼각형 불릿
    c.setFillColor(bullet_color)
    p = c.beginPath()
    p.moveTo(x, y + 3.5)
    p.lineTo(x + 5, y + 6.5)
    p.lineTo(x, y + 9.5)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # 텍스트
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split(' ')
    line = ''
    cx = x + 9
    cy = y
    for word in words:
        test = line + (' ' if line else '') + word
        if c.stringWidth(test, font, size) <= max_w - 9:
            line = test
        else:
            c.drawString(cx, cy, line)
            cy -= line_h
            cx = x + 9
            line = word
    if line:
        c.drawString(cx, cy, line)
        cy -= line_h
    return y - cy + line_h

def terminal_header(c, x, y, w):
    """터미널 헤더 (빨강/노랑/초록 점)"""
    card_rect(c, x, y - 2, w, 28, fill=CARD_DARK, stroke=BORDER)
    for i, col in enumerate([RED_DOT, YEL_DOT, GRN_DOT]):
        c.setFillColor(col)
        c.circle(x + 18 + i * 20, y + 10, 6, fill=1, stroke=0)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — PROJECT 03 커버
# ══════════════════════════════════════════════════════════════
def page_cover(c, page_num):
    full_bg(c)
    c.setFillColor(HexColor('#0d1f3c'))
    c.circle(W * 0.5, H * 0.52, 420, fill=1, stroke=0)

    lbl = 'PROJECT 03'
    c.setFont('MGBold', 14)
    c.setFillColor(ACCENT_VL)
    lw = c.stringWidth(lbl, 'MGBold', 14)
    c.setStrokeColor(ACCENT_V)
    c.setLineWidth(0.8)
    c.line(W/2 - lw/2 - 30, H*0.64 + 8, W/2 - lw/2 - 8, H*0.64 + 8)
    c.line(W/2 + lw/2 + 8,  H*0.64 + 8, W/2 + lw/2 + 30, H*0.64 + 8)
    c.drawCentredString(W/2, H*0.64, lbl)

    c.setFont('MGBold', 64)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.53, '재무제표 자동화')

    c.setFont('MG', 20)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.46, 'Python + BrityRPA · 3인 팀 프로젝트')

    meta_items = [
        ('유형', '3인 팀 프로젝트'),
        ('기간', '26.02.28 – 03.10'),
        ('역할', '팀장 · RPA 개발'),
        ('파이프라인', 'End-to-End 자동화'),
    ]
    box_w = 180
    meta_y = H * 0.34
    total_w = len(meta_items) * box_w + (len(meta_items)-1) * 16
    sx = W/2 - total_w/2
    for i, (k, v) in enumerate(meta_items):
        bx = sx + i * (box_w + 16)
        card_rect(c, bx, meta_y, box_w, 64)
        c.setFont('MG', 12)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(bx + box_w/2, meta_y + 44, k)
        c.setFont('MGBold', 15)
        c.setFillColor(TEXT_PRI)
        c.drawCentredString(bx + box_w/2, meta_y + 22, v)

    tags = ['Python', 'BrityRPA', 'Pandas', 'openpyxl', 'SMTP', 'K-IFRS']
    tag_total_w = sum(c.stringWidth(t, 'MG', 12) + 22 for t in tags) + (len(tags)-1)*8
    tx = W/2 - tag_total_w/2
    ty = meta_y - 44
    for t in tags:
        tw = tag(c, tx, ty, t, color=BORDER, text_color=TEXT_SEC)
        tx += tw

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 2 — 프로젝트 개요
# ══════════════════════════════════════════════════════════════
def page_overview(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '07')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '프로젝트 개요')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, '재무제표 자동화 — Python + BrityRPA 자동화 팀 프로젝트')

    # 수치 박스 4개
    stats = [('3인', '팀 구성'), ('2주', '개발 기간'), ('5개', 'RPA 자동화'), ('100%', 'Zero-Touch')]
    stat_y = H - 250
    stat_w = (W - M*2 - 48) / 4
    for i, (num, lbl) in enumerate(stats):
        sx = M + i * (stat_w + 16)
        card_rect(c, sx, stat_y, stat_w, 80)
        c.setFont('MGBold', 30)
        c.setFillColor(ACCENT_VL)
        c.drawCentredString(sx + stat_w/2, stat_y + 46, num)
        c.setFont('MG', 13)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(sx + stat_w/2, stat_y + 20, lbl)

    # 3 칼럼
    col_y = stat_y - 24
    col_h = 580
    col_w = (W - M*2 - 40) / 3
    cols = [
        (M,                  '▸ 개발 목적 & 목표', ACCENT_V,  [
            ('개발 목적', '기업 재무팀 수작업 회계 전표 처리 자동화. 수만 건 Raw Data 비효율 및 휴먼 에러 제거.'),
            ('목표 ①', 'Python → 재무 데이터 처리 (ETL)'),
            ('목표 ②', 'RPA → 보고서 자동 생성 & 차트'),
            ('목표 ③', '메일 자동 발송 (SMTP)'),
            ('목표 ④', 'Raw Data → 재무제표 → 대시보드 → 메일'),
        ]),
        (M + col_w + 20,     '▸ 시스템 아키텍처', ACCENT_G,  [
            ('Input',   'CSV Raw Data — 1만 건 가상 분개장'),
            ('ETL',     'Python · Pandas → 계정별 집계'),
            ('Mart',    '데이터마트 → 재무제표 구조화'),
            ('RPA',     'BrityRPA → Excel 차트 자동 구성'),
            ('Output',  'SMTP → 경영진 메일 자동 발송'),
        ]),
        (M + col_w*2 + 40,   '▸ 담당 역할 (팀장 · RPA)', ACCENT_O, [
            ('아키텍처 설계', 'Python-RPA Hybrid 역할 분리 구조 설계'),
            ('인터페이스', 'error_flag.txt 오류 공유 규격 합의'),
            ('RPA 구현', 'Python 실행 · Excel 차트 · 메일 자동화'),
            ('검증', 'UI 기반 재무 데이터 정합성 Validation'),
            ('PM', '일정 관리 및 전체 기술 의사결정 리딩'),
        ]),
    ]
    for cx, hdr, accent, items in cols:
        card_rect(c, cx, col_y - col_h, col_w, col_h)
        left_accent_line(c, cx + 12, col_y - col_h + 14, col_h - 28, color=accent)
        c.setFont('MGBold', 16)
        c.setFillColor(accent)
        c.drawString(cx + 26, col_y - 26, hdr)
        c.setStrokeColor(BORDER); c.setLineWidth(0.6)
        c.line(cx + 26, col_y - 36, cx + col_w - 14, col_y - 36)
        iy = col_y - 60
        for lbl, desc in items:
            c.setFont('MGBold', 14)
            c.setFillColor(TEXT_PRI)
            c.drawString(cx + 26, iy, lbl)
            iy -= 20
            y_cur = text_block(c, cx + 26, iy, desc, font='MG', size=13,
                               color=TEXT_SEC, max_width=col_w - 42, line_height=18)
            iy = y_cur - 12

    # 기술 스택
    stack_y = col_y - col_h - 30
    c.setFont('MG', 13)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, stack_y + 18, '기술 스택')
    c.setStrokeColor(BORDER); c.setLineWidth(0.6)
    c.line(M, stack_y + 14, W - M, stack_y + 14)
    tag_groups = [
        ('Data Engineering', ['Python', 'Pandas', 'openpyxl'], ACCENT_V),
        ('Process Automation', ['BrityRPA', 'SMTP'], ACCENT_G),
        ('Data Source', ['CSV Raw Data', 'K-IFRS'], TEXT_DARK),
    ]
    tx = M; ty = stack_y - 6
    for group, tags_list, col_accent in tag_groups:
        c.setFont('MG', 11); c.setFillColor(TEXT_DARK)
        c.drawString(tx, ty + 20, group)
        for t in tags_list:
            tw = tag(c, tx, ty, t, color=col_accent, text_color=TEXT_SEC)
            tx += tw
        tx += 18

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 3 — 담당 역할 & RPA 구조
# ══════════════════════════════════════════════════════════════
def page_role_detail(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '08')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '담당 역할 — RPA 자동화 파이프라인')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, '팀장으로서 End-to-End 자동화 아키텍처 설계 및 BrityRPA 구현 전담')

    # 파이프라인 흐름도
    flow_y = H - 250
    flow_h = 80
    steps = [
        ('CSV\nRaw Data', CODE_BLUE), ('Python\nETL', ACCENT_VL),
        ('Data\nMart', CODE_GREEN),   ('BrityRPA\n자동화', CODE_ORG),
        ('Excel\n보고서', CODE_PUR),  ('메일\n발송', ACCENT_G),
    ]
    step_w = (W - M*2 - 50) / len(steps)
    for i, (lbl, col) in enumerate(steps):
        sx = M + i * (step_w + 10)
        card_rect(c, sx, flow_y - flow_h, step_w, flow_h, fill=CARD, stroke=col, lw=2)
        if i < len(steps) - 1:
            ax = sx + step_w + 2; ay = flow_y - flow_h/2
            c.setFillColor(BORDER)
            p = c.beginPath()
            p.moveTo(ax, ay - 6); p.lineTo(ax + 8, ay); p.lineTo(ax, ay + 6); p.close()
            c.drawPath(p, fill=1, stroke=0)
        lines = lbl.split('\n')
        for j, line in enumerate(lines):
            c.setFont('MGBold' if j == 0 else 'MG', 13)
            c.setFillColor(col if j == 0 else TEXT_SEC)
            c.drawCentredString(sx + step_w/2, flow_y - 28 - j*20, line)

    # 3 칼럼 카드
    card_y = flow_y - flow_h - 24
    card_h = 580
    card_w = (W - M*2 - 40) / 3
    col_data = [
        {'title': '① 아키텍처 설계', 'color': ACCENT_VL, 'items': [
            ('Hybrid Automation 설계', 'Python이 연산, RPA가 시각화/배포를 전담하는 역할 분리 구조'),
            ('인터페이스 규격 수립', 'Python ↔ RPA 간 데이터 교환 형식 합의. error_flag.txt로 오류 공유'),
            ('Error Handling', 'Python 오류 시 플래그 파일 생성 → RPA 자동 중단 설계'),
            ('파이프라인 리딩', 'ETL → 데이터마트 → Excel 전체 흐름 총괄'),
        ]},
        {'title': '② RPA 자동화 구현', 'color': CODE_ORG, 'items': [
            ('Python 스크립트 실행', 'BrityRPA ExecuteCmd로 apnalchangchang.py 실행 및 결과 수집'),
            ('Excel 차트 자동 생성', '월별 손익 꺾은선 / 비용구조 파이차트 / 포괄손익계산서 3종'),
            ('분기별 재무현황 이관', 'Python 결과 파일 → 보고서 템플릿 시트 자동 복사 · 서식 유지'),
            ('메일 자동 발송', 'SMTP 연동, 수신자 자동 설정, Excel 보고서 첨부 발송'),
        ]},
        {'title': '③ 데이터 검증 & 관리', 'color': ACCENT_G, 'items': [
            ('재무 데이터 정합성', 'UI 기반 Validation으로 입력 오류 사전 차단'),
            ('일정 관리', '기획 → Python 개발 → RPA 시각화 → 통합 테스트 단계 리딩'),
            ('기술 의사결정', 'Python-RPA 연계 방식, 데이터 마트 구조 결정'),
            ('팀 협업', '타 기술 스택 담당자와 데이터 인터페이스 합의 및 소통'),
        ]},
    ]
    for ci, col_info in enumerate(col_data):
        cx = M + ci * (card_w + 20)
        card_rect(c, cx, card_y - card_h, card_w, card_h)
        left_accent_line(c, cx + 12, card_y - card_h + 14, card_h - 28, color=col_info['color'])
        c.setFont('MGBold', 16)
        c.setFillColor(col_info['color'])
        c.drawString(cx + 26, card_y - 28, col_info['title'])
        c.setStrokeColor(BORDER); c.setLineWidth(0.6)
        c.line(cx + 26, card_y - 38, cx + card_w - 14, card_y - 38)
        iy = card_y - 62
        for item_t, item_d in col_info['items']:
            c.setFont('MGBold', 14)
            c.setFillColor(TEXT_PRI)
            c.drawString(cx + 26, iy, item_t)
            iy -= 22
            y_next = text_block(c, cx + 26, iy, item_d, font='MG', size=13,
                                color=TEXT_SEC, max_width=card_w - 42, line_height=18)
            iy = y_next - 16
            iy -= 10

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 4 — 핵심 기능 구현 (RPA 코드 스타일)
# ══════════════════════════════════════════════════════════════
def page_rpa_impl(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '09')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '핵심 기능 구현')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, 'BrityRPA 기반 자동화 · Python-RPA Hybrid Architecture')

    # 4개 기능 카드 — 1행 4열 가로 배치
    cell_w = (W - M*2 - 48) / 4
    cell_h = 620
    cells = [
        {'title': '1. 파이썬 실행 자동화', 'file': 'BrityRPA_ExecuteCmd.bot', 'color': CODE_BLUE,
         'desc': 'BrityRPA의 ExecuteCmd 액션으로 Python 데이터 처리 엔진 실행. RPA가 전체 자동화 파이프라인을 제어하는 Orchestrator 역할.',
         'code': [('// 1. Python 스크립트 실행', TEXT_DARK),
                  ('ExecuteCmd(', CODE_BLUE), ('"python apnalchangchang.py")', CODE_BLUE),
                  ('', None), ('// 2. 오류 플래그 감지', TEXT_DARK),
                  ('IF FileExists("error_flag.txt")', CODE_ORG),
                  ('  → RPA 프로세스 중단', TEXT_SEC)]},
        {'title': '2. Excel 차트 자동 생성', 'file': 'chart_automation.bot', 'color': CODE_GREEN,
         'desc': 'Python 결과 데이터 기반 Excel Chart Object 자동 생성. 꺾은선 · 파이차트 · 포괄손익계산서 3종 자동화.',
         'code': [('// 차트 자동화', TEXT_DARK),
                  ('CreateChart(type="Line")', CODE_GREEN),
                  ('  .SetDataRange(monthly_pl)', CODE_PUR),
                  ('  .SetTitle("월별 손익")', CODE_ORG),
                  ('CreateChart(type="Pie")', CODE_GREEN),
                  ('  .SetDataRange(cost_structure)', CODE_PUR),
                  ('  .Export("report.xlsx")', CODE_ORG)]},
        {'title': '3. 분기별 재무현황 이관', 'file': 'data_transfer.bot', 'color': CODE_PUR,
         'desc': 'Python 생성 재무현황 데이터를 최종 보고서 Excel 템플릿으로 자동 이관. 서식·레이아웃 유지.',
         'code': [('// 데이터 이관', TEXT_DARK),
                  ('LoadWorkbook(data_mart.xlsx)', CODE_BLUE),
                  ('SelectSheet("분기별재무현황")', CODE_PUR),
                  ('CopyRange(A1:Z100)', CODE_ORG),
                  ('PasteToTemplate(', CODE_GREEN), ('"보고서템플릿")', CODE_GREEN),
                  ('MaintainFormatting = True', CODE_ORG)]},
        {'title': '4. 엑셀 저장 & 메일 발송', 'file': 'mail_dispatch.bot', 'color': ACCENT_G,
         'desc': 'SMTP 서버 연동으로 최종 보고서 자동 배포. 수신자 설정, 메일 본문 작성, Excel 첨부 발송 완전 자동화.',
         'code': [('// End-to-End 메일 발송', TEXT_DARK),
                  ('SaveWorkbook("경영대시보드.xlsx")', CODE_GREEN),
                  ('SMTP.Connect(server, port)', CODE_BLUE),
                  ('Mail.SetRecipients(list)', CODE_PUR),
                  ('Mail.AttachFile(report.xlsx)', CODE_ORG),
                  ('Mail.Send()', CODE_GREEN),
                  ('// 자동 발송 완료 ✓', TEXT_DARK)]},
    ]
    cy_top = H - 230
    for i, cell in enumerate(cells):
        cx = M + i * (cell_w + 16)
        cy = cy_top - cell_h
        card_rect(c, cx, cy, cell_w, cell_h)
        left_accent_line(c, cx + 12, cy + 14, cell_h - 28, color=cell['color'])
        c.setFont('MGBold', 15)
        c.setFillColor(cell['color'])
        c.drawString(cx + 26, cy_top - 26, cell['title'])
        c.setFont('MG', 12)
        c.setFillColor(TEXT_DARK)
        c.drawString(cx + 26, cy_top - 46, cell['file'])
        desc_y = cy_top - 70
        desc_y = text_block(c, cx + 26, desc_y, cell['desc'], font='MG', size=13,
                            color=TEXT_SEC, max_width=cell_w - 42, line_height=18)
        # 코드 블록
        code_top = cy + 200
        code_h = 180
        terminal_header(c, cx + 26, code_top, cell_w - 42)
        card_rect(c, cx + 26, code_top - code_h, cell_w - 42, code_h + 2,
                  fill=CARD_DARK, stroke=BORDER, lw=0.6, radius=0)
        cl = code_top - 16
        for code_line, col in cell['code']:
            if code_line:
                c.setFont('MG', 12)
                c.setFillColor(col or TEXT_SEC)
                c.drawString(cx + 34, cl, code_line)
            cl -= 16

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 5 — 결과 · 회고
# ══════════════════════════════════════════════════════════════
def page_result(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '10')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '결과 · 회고')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, 'RPA 자동화 프로젝트 성과와 팀장으로서의 성장')

    # 성과 수치
    metrics = [('5개', 'RPA 자동화 구현'), ('100%', 'Zero-Touch'), ('1만 건+', '전표 처리'), ('팀장', 'E2E 리딩')]
    m_y = H - 250
    m_w = (W - M*2 - 48) / 4
    for i, (val, lbl) in enumerate(metrics):
        mx = M + i * (m_w + 16)
        card_rect(c, mx, m_y, m_w, 80)
        c.setFont('MGBold', 30)
        c.setFillColor(ACCENT_G)
        c.drawCentredString(mx + m_w/2, m_y + 46, val)
        c.setFont('MG', 13)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx + m_w/2, m_y + 20, lbl)

    # 잘된점 / 아쉬운점
    tw = (W - M*2 - 20) / 2
    th = 280
    card_rect(c, M, m_y - th - 24, tw, th)
    left_accent_line(c, M + 12, m_y - th - 12, th - 24, color=ACCENT_G)
    c.setFont('MGBold', 18)
    c.setFillColor(ACCENT_G)
    c.drawString(M + 26, m_y - 46, '✦ 잘된 점')
    goods = ['재무자동화 핵심 프로세스 100% 구현', 'Python-RPA 하이브리드 아키텍처 완성',
             'Error Flag 구조로 이기종 시스템 안정 연동', '원천데이터 파싱 → 메일 발송 Zero-Touch 완성',
             '팀장으로 전체 기술 의사결정 및 일정 리딩']
    gy = m_y - 76
    for g in goods:
        used = bullet_item(c, M + 26, gy, g, max_w=tw - 48, bullet_color=ACCENT_G, size=14)
        gy -= used + 6

    card_rect(c, M + tw + 20, m_y - th - 24, tw, th)
    left_accent_line(c, M + tw + 32, m_y - th - 12, th - 24, color=ACCENT_O)
    c.setFont('MGBold', 18)
    c.setFillColor(ACCENT_O)
    c.drawString(M + tw + 46, m_y - 46, '△ 아쉬운 점 / 개선 방향')
    bads = ['초기 원천 데이터 예외 포맷 오류 처리 미흡', 'RPA 예외처리 로직 정교화 필요',
            '동적 방어 코드 추가 및 에러 로깅 고도화 목표', '경영진 피드백 기반 대시보드 UI/UX 개선']
    by = m_y - 76
    for b in bads:
        used = bullet_item(c, M + tw + 46, by, b, max_w=tw - 48, bullet_color=ACCENT_O, size=14)
        by -= used + 6

    # 자체 평가
    story_y = m_y - th - 56
    story_h = 260
    card_rect(c, M, story_y - story_h, W - M*2, story_h)
    left_accent_line(c, M + 12, story_y - story_h + 14, story_h - 28, color=ACCENT_VL)
    c.setFont('MGBold', 18)
    c.setFillColor(ACCENT_VL)
    c.drawString(M + 26, story_y - 30, '💬 자체 평가 — 윤종빈')
    c.setStrokeColor(BORDER); c.setLineWidth(0.6)
    c.line(M + 26, story_y - 42, W - M - 14, story_y - 42)
    story_full = (
        '단순한 스크립트 코딩을 넘어, 실제 기업 재무 기준을 시스템 로직으로 완벽히 구현해낸 것이 이번 프로젝트의 가장 큰 성과입니다. '
        'Python이 "데이터 연산"을 전담하고 RPA가 "시각화 및 메일 발송"을 담당하도록 아키텍처를 분리하였습니다. '
        '타 기술 스택 담당자와 명확한 데이터 인터페이스 규격을 합의하고, 오류 발생 시 즉각 상태를 공유하는 '
        'Error Flag 구조를 설계하며 이기종 시스템 간 매끄러운 연동과 협업 시너지를 제대로 경험할 수 있었습니다.'
    )
    text_block(c, M + 26, story_y - 62, story_full, font='MG', size=15, color=TEXT_PRI,
               max_width=W - M*2 - 52, line_height=22)

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# 업데이트 커버 (첫 페이지) — PROJECT 03, 04 추가
# ══════════════════════════════════════════════════════════════
def page_main_cover(c):
    """통합 포트폴리오 커버 — 1920×1080"""
    full_bg(c)

    # 배경 글로우
    c.setFillColor(HexColor('#0d1535'))
    c.circle(W * 0.18, H * 0.28, 340, fill=1, stroke=0)
    c.setFillColor(HexColor('#0a1f3a'))
    c.circle(W * 0.82, H * 0.72, 300, fill=1, stroke=0)

    # 상단 레이블
    label = 'FULL-STACK DEVELOPER PORTFOLIO'
    c.setFont('MG', 13)
    lw = c.stringWidth(label, 'MG', 13)
    c.setStrokeColor(HexColor('#3d4f7c'))
    c.setFillColor(HexColor('#3d4f7c'))
    c.setLineWidth(0.8)
    c.roundRect(W/2 - lw/2 - 18, H*0.82, lw + 36, 26, 13, fill=0, stroke=1)
    c.setFillColor(HexColor('#818bf7'))
    c.drawCentredString(W/2, H*0.82 + 6, label)

    # 메인 타이틀
    c.setFont('MGBold', 90)
    c.setFillColor(HexColor('#b0b9fc'))
    c.drawCentredString(W/2, H*0.64, 'Portfolio')

    # 서브타이틀
    c.setFont('MG', 20)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.576, '네 개의 프로젝트를 통한 성장 기록')

    # 4개 프로젝트 박스 — 1행 4열
    projects = [
        ('PROJECT 01', 'AuRa', 'FIRST 팀 쇼핑몰 · React + Node.js', '4인 팀 · 3주',
         HexColor('#6266f1'), HexColor('#1a1f4e')),
        ('PROJECT 02', 'KISETSU', '계절 솔로 · React + Socket.io', '1인 솔로 · 10일',
         HexColor('#0fb981'), HexColor('#0d2b22')),
        ('PROJECT 03', '재무제표 자동화', 'Python + BrityRPA', '3인 팀 · 2주',
         HexColor('#f59d0a'), HexColor('#2b1e0a')),
        ('PROJECT 04', '개발환기좀해 ERP', 'Spring Boot + JSP', '1인 솔로 · 5주',
         HexColor('#e05c8a'), HexColor('#2b0d18')),
    ]
    box_w = 390
    box_h = 120
    gap = 22
    total_w = 4 * box_w + 3 * gap
    bx_start = W/2 - total_w/2
    by = H * 0.38

    for i, (proj_lbl, title, sub, meta, accent, bg_col) in enumerate(projects):
        bx = bx_start + i * (box_w + gap)
        c.setFillColor(bg_col)
        c.setStrokeColor(accent)
        c.setLineWidth(1.2)
        c.roundRect(bx, by, box_w, box_h, 8, fill=1, stroke=1)
        c.setFont('MGBold', 11)
        c.setFillColor(accent)
        c.drawString(bx + 16, by + box_h - 22, proj_lbl)
        c.setFont('MGBold', 18)
        c.setFillColor(TEXT_PRI)
        c.drawString(bx + 16, by + box_h - 46, title)
        c.setFont('MG', 13)
        c.setFillColor(TEXT_SEC)
        c.drawString(bx + 16, by + box_h - 68, sub)
        c.setFont('MG', 12)
        c.setFillColor(TEXT_DARK)
        c.drawString(bx + 16, by + 16, meta)

    # 기술 스택 태그
    all_tags = ['React', 'Node.js', 'Spring Boot', 'MariaDB', 'JWT',
                'Socket.io', 'MyBatis', 'Python', 'BrityRPA', 'Nodemailer']
    tag_total = sum(c.stringWidth(t, 'MG', 12) + 22 for t in all_tags) + (len(all_tags)-1)*6
    tx = W/2 - tag_total/2
    ty = by - 40
    for t in all_tags:
        c.setFont('MG', 12)
        tw2 = c.stringWidth(t, 'MG', 12) + 22
        c.setFillColor(CARD); c.setStrokeColor(BORDER); c.setLineWidth(0.7)
        c.roundRect(tx, ty - 2, tw2, 20, 4, fill=1, stroke=1)
        c.setFillColor(TEXT_DARK)
        c.drawString(tx + 11, ty + 3, t)
        tx += tw2 + 6

    c.setFont('MG', 15)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(W/2, ty - 28, '2025 — 2026')

    c.showPage()


# ══════════════════════════════════════════════════════════════
# 업데이트 목차 — PROJECT 03, 04 포함
# ══════════════════════════════════════════════════════════════
ERP_ACCENT   = HexColor('#e05c8a')
FIRST_ACCENT = HexColor('#38bdf8')   # sky-blue — FIRST 팀 프로젝트
SOLO_ACCENT  = HexColor('#fb923c')   # orange   — Solo 계절 프로젝트

def page_toc(c):
    full_bg(c)
    badge(c, 80, H - 96, 'INDEX', color=ACCENT_G, font_size=13, pad_x=12, pad_h=24)
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(192, H - 104, '목차')
    c.setStrokeColor(BORDER); c.setLineWidth(0.7)
    c.line(80, H - 118, W - 80, H - 118)

    LX = 80          # left column x
    RX = W // 2 + 30  # right column x
    CW = W // 2 - 130 # column width

    def sec_hdr(label, y, x=80, col=ACCENT_VL):
        c.setFillColor(col)
        c.rect(x, y - 2, 5, 20, fill=1, stroke=0)
        c.setFont('MGBold', 14)
        c.setFillColor(col)
        c.drawString(x + 14, y, label)

    def item(num, title, subtitle, pg, y, x=80, col=ACCENT_V, w=None):
        w = w or CW
        card_rect(c, x, y - 40, w, 44)
        badge(c, x + 14, y - 30, f'{num:02d}', color=col, font_size=12, pad_x=8, pad_h=20)
        c.setFont('MGBold', 14)
        c.setFillColor(TEXT_PRI)
        c.drawString(x + 62, y - 12, title)
        c.setFont('MG', 12)
        c.setFillColor(TEXT_SEC)
        c.drawString(x + 62, y - 28, subtitle)
        c.setFont('MG', 13)
        c.setFillColor(TEXT_DARK)
        c.drawRightString(x + w - 16, y - 18, f'{pg:02d}')

    # 왼쪽 컬럼: PROJECT 01 + 02
    y = H - 150
    sec_hdr('PROJECT 01 — AuRa / FIRST 팀 쇼핑몰', y, LX);  y -= 24
    item(1, '프로젝트 개요', 'AuRa 소개, 기술 스택, 팀 구성', 3, y, LX);  y -= 52
    item(2, '주요 기여 — DB · 인증 · 장바구니', '담당 기능 상세, 코드 구현 방식', 4, y, LX);  y -= 52
    item(3, '기술적 어필 포인트', '관심사 분리, 중복 방지, 서버단 검증', 5, y, LX);  y -= 62

    sec_hdr('PROJECT 02 — KISETSU / 계절 솔로', y, LX, ACCENT_G);  y -= 24
    item(4, '프로젝트 개요 · 아키텍처', '기획 배경, 시스템 구조, 기술 스택', 7, y, LX, ACCENT_G);  y -= 52
    item(5, '주요 기능 구현', 'JWT, 실시간 채팅, Context API', 9, y, LX, ACCENT_G);  y -= 52
    item(6, '결과 · 회고', '구현 성과, 배운 점, 성장 스토리', 10, y, LX, ACCENT_G)

    # 오른쪽 컬럼: PROJECT 03 + 04
    y = H - 150
    sec_hdr('PROJECT 03 — 재무제표 자동화 (Python + BrityRPA)', y, RX, ACCENT_O);  y -= 24
    item(7,  '프로젝트 개요', '기획 배경, 시스템 아키텍처, 담당 역할', 12, y, RX, ACCENT_O, CW);  y -= 52
    item(8,  '담당 역할 — RPA 자동화 파이프라인', '아키텍처 설계, RPA 구현, 데이터 검증', 13, y, RX, ACCENT_O, CW);  y -= 52
    item(9,  '핵심 기능 구현', 'Python 실행, Excel 차트, 메일 발송', 14, y, RX, ACCENT_O, CW);  y -= 52
    item(10, '결과 · 회고', 'RPA 성과, 잘된 점, 아쉬운 점', 15, y, RX, ACCENT_O, CW);  y -= 62

    sec_hdr('PROJECT 04 — 개발환기좀해 ERP (Spring Boot + MyBatis)', y, RX, ERP_ACCENT);  y -= 24
    item(11, '프로젝트 개요 · 아키텍처', '기획 배경, 전체 모듈, 기술 스택', 17, y, RX, ERP_ACCENT, CW);  y -= 52
    item(12, '핵심 기능 구현', 'OCR, BOM 자동발주, 재무 리포트', 18, y, RX, ERP_ACCENT, CW);  y -= 52
    item(13, '성능 최적화 · DB 쿼리 튜닝', 'N+1, 인덱스 최적화 (14.25s→0.17s)', 19, y, RX, ERP_ACCENT, CW);  y -= 52
    item(14, '기술적 어필 & 회고', 'Spring Security, 트랜잭션, 성과', 20, y, RX, ERP_ACCENT, CW)

    draw_footer(c, 'Developer Portfolio', '', 2)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — ERP 커버
# ══════════════════════════════════════════════════════════════
def page_erp_cover(c, page_num):
    full_bg(c)
    c.setFillColor(HexColor('#200d18'))
    c.circle(W * 0.5, H * 0.52, 420, fill=1, stroke=0)

    lbl = 'PROJECT 04'
    c.setFont('MGBold', 14)
    c.setFillColor(ERP_ACCENT)
    lw2 = c.stringWidth(lbl, 'MGBold', 14)
    c.setStrokeColor(ERP_ACCENT); c.setLineWidth(0.8)
    c.line(W/2 - lw2/2 - 30, H*0.64 + 8, W/2 - lw2/2 - 8, H*0.64 + 8)
    c.line(W/2 + lw2/2 + 8,  H*0.64 + 8, W/2 + lw2/2 + 30, H*0.64 + 8)
    c.drawCentredString(W/2, H*0.64, lbl)

    c.setFont('MGBold', 64)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.53, '개발환기좀해 ERP')

    c.setFont('MG', 20)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.46, 'Spring Boot + MyBatis · 1인 솔로 풀스택')

    meta_items = [
        ('유형', '1인 솔로 프로젝트'), ('기간', '26.03.25 – 04.01'),
        ('규모', '모듈 15개+'), ('특이사항', 'OCR · AI API 연동'),
    ]
    bw2 = 180; meta_y = H * 0.34
    total_mw = len(meta_items) * bw2 + (len(meta_items)-1) * 16
    sx = W/2 - total_mw/2
    for i, (k, v) in enumerate(meta_items):
        mx = sx + i * (bw2 + 16)
        card_rect(c, mx, meta_y, bw2, 64)
        c.setFont('MG', 12); c.setFillColor(TEXT_DARK)
        c.drawCentredString(mx + bw2/2, meta_y + 44, k)
        c.setFont('MGBold', 15); c.setFillColor(TEXT_PRI)
        c.drawCentredString(mx + bw2/2, meta_y + 22, v)

    erp_tags = ['Spring Boot 3.4', 'Java 17', 'MyBatis', 'MariaDB',
                'Spring Security', 'JSP/JSTL', 'Swagger', 'Gemini OCR', 'Lombok']
    tag_tw = sum(c.stringWidth(t, 'MG', 12) + 22 for t in erp_tags) + (len(erp_tags)-1)*6
    tx2 = W/2 - tag_tw/2; ty2 = meta_y - 44
    for t in erp_tags:
        c.setFont('MG', 12)
        tw3 = c.stringWidth(t, 'MG', 12) + 22
        c.setFillColor(CARD); c.setStrokeColor(ERP_ACCENT); c.setLineWidth(0.7)
        c.roundRect(tx2, ty2 - 2, tw3, 20, 4, fill=1, stroke=1)
        c.setFillColor(TEXT_SEC); c.drawString(tx2 + 11, ty2 + 3, t)
        tx2 += tw3 + 6

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — ERP 개요 & 모듈
# ══════════════════════════════════════════════════════════════
def page_erp_overview(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '11')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '프로젝트 개요 · 전체 모듈')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, '개발환기좀해 ERP — 제조업 기반 통합 자원 관리 시스템 (1인 풀스택)')

    stats = [('15개+', '컨트롤러/모듈'), ('20개+', 'REST API'), ('1인', '솔로 개발'), ('5주', '개발 기간')]
    stat_y = H - 250
    sw2 = (W - M*2 - 48) / 4
    for i, (val, lbl) in enumerate(stats):
        sx2 = M + i * (sw2 + 16)
        card_rect(c, sx2, stat_y, sw2, 80)
        c.setFont('MGBold', 30); c.setFillColor(ERP_ACCENT)
        c.drawCentredString(sx2 + sw2/2, stat_y + 46, val)
        c.setFont('MG', 13); c.setFillColor(TEXT_SEC)
        c.drawCentredString(sx2 + sw2/2, stat_y + 20, lbl)

    # 모듈 그리드 (3열 × 3행)
    modules = [
        ('인증 · 보안',  ERP_ACCENT,          ['Spring Security 역할 기반 접근제어', 'BCrypt 패스워드 해싱', 'ADMIN / USER 권한 분리']),
        ('대시보드',     CODE_BLUE,            ['실시간 KPI (제품수, 직원수, 매출)', '재고부족 알림, 월별 작업지시 통계', '최근 주문 · 저재고 품목 리스트']),
        ('인사 · 근태',  ACCENT_G,             ['직원 CRUD + 사진 업로드', '출퇴근 체크인/아웃 API', '연차/병가 등록 · 잔여일수 차감']),
        ('생산 관리',    CODE_ORG,             ['BOM(자재명세서) 관리', '작업지시서 생성 · 상태 관리', 'BOM 기반 재고 부족 시 자동 발주']),
        ('재고 · 창고',  CODE_GREEN,           ['재고 CRUD, 입출고 트랜잭션', '창고별 재고 현황 관리', '저재고 기준치 설정']),
        ('구매 · 영업',  ACCENT_VL,            ['발주서 워크플로우 (대기→승인→완료)', '판매 · 배송 관리', '거래처(공급업체) 관리']),
        ('거래명세서',   HexColor('#f87171'),   ['OCR (Gemini/Groq AI) 자동 인식', '이미지 업로드 → DB 자동 등록', '인쇄 기능 (거래명세서 출력)']),
        ('재무 분석',    HexColor('#34d399'),   ['손익계산서 자동 계산 (월별/연별)', '영업이익률 · 매출총이익 산출', 'Python 연동 Excel 리포트 내보내기']),
        ('관리자',       TEXT_SEC,             ['사용자 계정 관리 (ADMIN)', '저재고 기준치 시스템 설정', 'Swagger UI API 문서 자동화']),
    ]
    mw = (W - M*2 - 40) / 3
    mh = 128
    start_y = stat_y - 24
    for i, (title, col, items) in enumerate(modules):
        row, ci = divmod(i, 3)
        mx = M + ci * (mw + 20)
        my = start_y - row * (mh + 12) - mh
        card_rect(c, mx, my, mw, mh)
        left_accent_line(c, mx + 10, my + 12, mh - 24, color=col)
        c.setFont('MGBold', 15); c.setFillColor(col)
        c.drawString(mx + 24, my + mh - 24, title)
        iy = my + mh - 48
        for it in items:
            c.setFont('MG', 13); c.setFillColor(TEXT_SEC)
            c.drawString(mx + 24, iy, it)
            iy -= 18

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 핵심 기능 구현
# ══════════════════════════════════════════════════════════════
def page_erp_features(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '12')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '핵심 기능 구현')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, 'OCR 자동 인식 · BOM 자동발주 · 재무 리포트 · Spring Security')

    # 4 기능 카드 — 1행 4열
    cells = [
        {'title': 'OCR 거래명세서 자동 인식', 'file': 'OcrController.java',
         'color': HexColor('#f87171'),
         'desc': 'Gemini/Groq AI API 연동. 이미지 업로드 → Python OCR → JSON 파싱 → DB 자동 저장까지 완전 자동화.',
         'code': [('// 1. 이미지 → Python OCR', TEXT_DARK),
                  ('ProcessBuilder pb = new', CODE_BLUE), ('ProcessBuilder(pythonCmd,', CODE_BLUE),
                  ('  mainPy, "--erp-mode", file);', CODE_BLUE),
                  ('// 2. JSON 파싱 → DB 저장', TEXT_DARK),
                  ('stmt.setIssueDate(', CODE_GREEN), ('  LocalDate.parse(...));', CODE_GREEN),
                  ('statementService.insert(stmt);', CODE_ORG)]},
        {'title': 'BOM 기반 자동 부품 발주', 'file': 'WorkOrderService.java',
         'color': CODE_ORG,
         'desc': '작업지시 시 BOM 조회 → 재고 부족 자동 감지 → 발주서 자동 생성. 부품 원가 변경 시 완제품 원가 자동 재계산.',
         'code': [('// 재고 부족 부품 자동 발주', TEXT_DARK),
                  ('List<BomItem> shortages =', CODE_BLUE),
                  ('  bomService.checkShortages(', CODE_BLUE), ('    workOrderId);', CODE_BLUE),
                  ('for (BomItem item : shortages) {', CODE_PUR),
                  ('  purchaseOrderService', CODE_GREEN), ('    .autoCreate(item);', CODE_GREEN),
                  ('}  // 발주서 자동 생성', TEXT_DARK)]},
        {'title': '재무 분석 · Python Excel', 'file': 'FinancialController.java',
         'color': HexColor('#34d399'),
         'desc': '매출/비용 데이터 기반 손익계산서 자동 산출. Python 스크립트 연동으로 xlsx 리포트 생성 및 다운로드.',
         'code': [('// 영업이익률 자동 계산', TEXT_DARK),
                  ('BigDecimal opMargin =', CODE_BLUE), ('  opProfit.divide(revenue,', CODE_BLUE),
                  ('    4, HALF_UP)', CODE_BLUE),
                  ('  .multiply(', CODE_BLUE), ('    BigDecimal.valueOf(100));', CODE_BLUE),
                  ('// Python → xlsx 리포트', TEXT_DARK),
                  ('byte[] xlsx = runPython(csv);', CODE_GREEN)]},
        {'title': 'Spring Security 역할 인증', 'file': 'SecurityConfig.java',
         'color': ACCENT_VL,
         'desc': 'BCrypt 해싱, 폼 로그인, ADMIN/USER 역할 분리. /admin/** 경로는 ADMIN만 접근 가능.',
         'code': [('// 역할 기반 접근 제어', TEXT_DARK),
                  ('.requestMatchers(', CODE_PUR), ('  "/admin/**")', CODE_PUR),
                  ('  .hasRole("ADMIN")', CODE_ORG),
                  ('.anyRequest()', CODE_GREEN), ('  .authenticated()', CODE_GREEN),
                  ('// BCrypt 인코더', TEXT_DARK),
                  ('return new BCryptPasswordEncoder();', CODE_BLUE)]},
    ]
    cw = (W - M*2 - 48) / 4
    ch = 620
    cy_top = H - 230
    for i, cell in enumerate(cells):
        cx2 = M + i * (cw + 16)
        cy2 = cy_top - ch
        card_rect(c, cx2, cy2, cw, ch)
        left_accent_line(c, cx2 + 12, cy2 + 14, ch - 28, color=cell['color'])
        c.setFont('MGBold', 15); c.setFillColor(cell['color'])
        c.drawString(cx2 + 26, cy_top - 26, cell['title'])
        c.setFont('MG', 12); c.setFillColor(TEXT_DARK)
        c.drawString(cx2 + 26, cy_top - 48, cell['file'])
        desc_y = cy_top - 74
        desc_y = text_block(c, cx2 + 26, desc_y, cell['desc'], font='MG', size=13,
                            color=TEXT_SEC, max_width=cw - 42, line_height=18)
        code_top = cy2 + 210
        code_h = 190
        terminal_header(c, cx2 + 26, code_top, cw - 42)
        card_rect(c, cx2 + 26, code_top - code_h, cw - 42, code_h + 2,
                  fill=CARD_DARK, stroke=BORDER, lw=0.6, radius=0)
        cl2 = code_top - 16
        for line, col2 in cell['code']:
            c.setFont('MG', 12); c.setFillColor(col2)
            c.drawString(cx2 + 34, cl2, line)
            cl2 -= 16

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 기술적 어필 & 회고
# ══════════════════════════════════════════════════════════════
def page_erp_review(c, page_num):
    full_bg(c)
    M = 80
    badge(c, M, H - 100, '14')
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 168, '기술적 어필 & 회고')
    c.setFont('MG', 16)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 200, '개발환기좀해 ERP — 1인 풀스택 완성 성과')

    metrics = [('15개+', '모듈 구현'), ('100%', '1인 완성'), ('OCR', 'AI 연동'), ('트랜잭션', '원자성 보장')]
    m_y = H - 250
    m_w = (W - M*2 - 48) / 4
    for i, (val, lbl) in enumerate(metrics):
        mx2 = M + i * (m_w + 16)
        card_rect(c, mx2, m_y, m_w, 80)
        c.setFont('MGBold', 30); c.setFillColor(ERP_ACCENT)
        c.drawCentredString(mx2 + m_w/2, m_y + 46, val)
        c.setFont('MG', 13); c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx2 + m_w/2, m_y + 20, lbl)

    tw4 = (W - M*2 - 20) / 2
    th4 = 280
    card_rect(c, M, m_y - th4 - 24, tw4, th4)
    left_accent_line(c, M + 12, m_y - th4 - 12, th4 - 24, color=ERP_ACCENT)
    c.setFont('MGBold', 18); c.setFillColor(ERP_ACCENT)
    c.drawString(M + 26, m_y - 46, '✦ 기술적 어필 포인트')
    pts = [
        'OCR + AI API (Gemini/Groq) 연동 거래명세서 자동 등록',
        'BOM 기반 재고 부족 자동 감지 → 발주서 즉시 생성',
        '입고/출고/생산입고 @Transactional 원자성 처리',
        'Spring Security 역할 기반 접근제어 + BCrypt',
        'Python 연동 재무 Excel 리포트 (csv → xlsx 변환)',
        '사이드바 아코디언 UI + 현재 메뉴 자동 펼침',
    ]
    py = m_y - 76
    for p in pts:
        used = bullet_item(c, M + 26, py, p, max_w=tw4 - 48, bullet_color=ERP_ACCENT, size=14)
        py -= used + 6

    card_rect(c, M + tw4 + 20, m_y - th4 - 24, tw4, th4)
    left_accent_line(c, M + tw4 + 32, m_y - th4 - 12, th4 - 24, color=ACCENT_O)
    c.setFont('MGBold', 18); c.setFillColor(ACCENT_O)
    c.drawString(M + tw4 + 46, m_y - 46, '△ 아쉬운 점 / 개선 방향')
    bads = [
        'JSP + JSTL 한계 → 다음엔 React 프론트 분리 목표',
        'OCR 예외 포맷(누락 · 오타) 처리 로직 보완 필요',
        '테스트 코드 없음 → JUnit + MockMvc 도입 계획',
        '실시간 알림(WebSocket) 추후 적용 예정',
    ]
    by2 = m_y - 76
    for b in bads:
        used = bullet_item(c, M + tw4 + 46, by2, b, max_w=tw4 - 48, bullet_color=ACCENT_O, size=14)
        by2 -= used + 6

    ry = m_y - th4 - 56
    rh = 260
    card_rect(c, M, ry - rh, W - M*2, rh)
    left_accent_line(c, M + 12, ry - rh + 14, rh - 28, color=ERP_ACCENT)
    c.setFont('MGBold', 18); c.setFillColor(ERP_ACCENT)
    c.drawString(M + 26, ry - 30, '💬 회고 — 개발환기좀해 ERP')
    c.setStrokeColor(BORDER); c.setLineWidth(0.6)
    c.line(M + 26, ry - 44, W - M - 14, ry - 44)
    story_full = (
        '제조업 ERP 전 모듈을 1인으로 처음부터 끝까지 구현하면서, 단순한 CRUD를 넘어 실제 업무 프로세스를 코드로 '
        '표현하는 경험을 했습니다. BOM 기반 자동 발주, OCR AI 연동, Python 재무 리포트 등 서로 다른 기술 스택을 '
        '하나의 시스템으로 통합하는 과정에서 Spring Boot의 계층 구조(Controller-Service-Mapper)와 트랜잭션 관리의 '
        '중요성을 몸소 익혔습니다. JSP의 한계를 느끼면서 React 분리의 필요성도 깨달았고, 다음 프로젝트에서는 '
        '프론트엔드를 완전히 분리한 REST API 기반 아키텍처를 목표로 합니다.'
    )
    text_block(c, M + 26, ry - 64, story_full, font='MG', size=15, color=TEXT_PRI,
               max_width=W - M*2 - 52, line_height=22)

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 성능 최적화 (p19)
# ══════════════════════════════════════════════════════════════
def page_erp_performance(c, page_num):
    full_bg(c)
    M = 80

    badge(c, M, H - 100, '성능 최적화')
    c.setFont('MGBold', 32)
    c.setFillColor(TEXT_PRI)
    c.drawString(M, H - 148, '성능 최적화 · DB 쿼리 튜닝')
    c.setFont('MG', 17)
    c.setFillColor(TEXT_SEC)
    c.drawString(M, H - 178, '발주 · 입고 페이지 로딩  14.25초 → 0.17초 (83배 개선)')

    # ── 임팩트 수치 배너 ────────────────────────────────────────
    banner_y = H - 218
    banner_h = 72
    card_rect(c, M, banner_y, W - M*2, banner_h,
              fill=HexColor('#0d1f0d'), stroke=ACCENT_G, lw=2)
    left_accent_line(c, M, banner_y, banner_h, color=ACCENT_G, lw=6)

    # BEFORE
    c.setFont('MGBold', 13)
    c.setFillColor(TEXT_DARK)
    c.drawString(M + 30, banner_y + 53, 'BEFORE')
    c.setFont('MGBold', 36)
    c.setFillColor(HexColor('#f87171'))
    c.drawString(M + 30, banner_y + 18, '14.25 s')

    # 화살표
    arr_x = W / 2 - 30
    c.setFont('MGBold', 40)
    c.setFillColor(ACCENT_G)
    c.drawCentredString(arr_x, banner_y + 22, '→')

    # AFTER
    c.setFont('MGBold', 13)
    c.setFillColor(TEXT_DARK)
    c.drawString(arr_x + 50, banner_y + 53, 'AFTER')
    c.setFont('MGBold', 36)
    c.setFillColor(ACCENT_G)
    c.drawString(arr_x + 50, banner_y + 18, '0.17 s')
    c.setFont('MG', 13)
    c.setFillColor(TEXT_DARK)
    c.drawString(arr_x + 50, banner_y + 6, '(176 ms)')

    # 배율 뱃지 (우측)
    badge_w, badge_h = 120, 40
    c.setFillColor(ACCENT_G)
    c.roundRect(W - M - badge_w, banner_y + 16, badge_w, badge_h, 6, fill=1, stroke=0)
    c.setFont('MGBold', 20)
    c.setFillColor(HexColor('#0d1f0d'))
    c.drawCentredString(W - M - badge_w / 2, banner_y + 28, '83x 향상')

    # ── 두 열 카드 ──────────────────────────────────────────────
    sec_y = banner_y - 22
    half_w = (W - M * 2 - 20) / 2
    card_h = 390

    def perf_card(cx, cy, title, accent_col, before_lines, after_lines):
        card_rect(c, cx, cy - card_h, half_w, card_h)
        left_accent_line(c, cx + 10, cy - card_h + 14, card_h - 28, color=accent_col)

        c.setFont('MGBold', 16)
        c.setFillColor(accent_col)
        c.drawString(cx + 24, cy - 26, title)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(cx + 24, cy - 38, cx + half_w - 14, cy - 38)

        # BEFORE 블록
        line_h_b = 16
        before_h = len(before_lines) * line_h_b + 30
        bby = cy - 56
        card_rect(c, cx + 24, bby - before_h, half_w - 40, before_h + 4,
                  fill=HexColor('#200d0d'), stroke=HexColor('#f87171'), lw=1)
        c.setFont('MGBold', 11)
        c.setFillColor(HexColor('#f87171'))
        c.drawString(cx + 34, bby - 14, 'BEFORE')
        ly = bby - 30
        for line in before_lines:
            c.setFont('MG', 11)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx + 34, ly, line)
            ly -= line_h_b

        # AFTER 블록
        line_h_a = 16
        after_h = len(after_lines) * line_h_a + 30
        aby = bby - before_h - 16
        card_rect(c, cx + 24, aby - after_h, half_w - 40, after_h + 4,
                  fill=HexColor('#0d1f0d'), stroke=ACCENT_G, lw=1)
        c.setFont('MGBold', 11)
        c.setFillColor(ACCENT_G)
        c.drawString(cx + 34, aby - 14, 'AFTER')
        ly2 = aby - 30
        for line in after_lines:
            c.setFont('MG', 11)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx + 34, ly2, line)
            ly2 -= line_h_a

    perf_card(
        M, sec_y,
        '① N+1 쿼리 문제 해결',
        HexColor('#f87171'),
        before_lines=[
            '목록 각 행마다 SUM() 서브쿼리 반복 실행',
            '→ 데이터 100건 = SQL 101번 호출 (과부하)',
            'SELECT *, (SELECT SUM(...)',
            '  FROM items WHERE order_id = o.id)',
            'FROM orders o  -- 행마다 재실행!',
        ],
        after_lines=[
            '파생 테이블로 SUM 미리 집계 후 1회 JOIN',
            '→ 데이터 100건도 SQL 1번으로 처리',
            'SELECT o.*, s.total FROM orders o',
            'LEFT JOIN (SELECT order_id,',
            '  SUM(qty) total FROM items',
            '  GROUP BY order_id) s ON o.id=s.order_id',
        ],
    )

    perf_card(
        M + half_w + 20, sec_y,
        '② JOIN 조건 · 인덱스 최적화',
        CODE_BLUE,
        before_lines=[
            'LIKE 연산자로 customer_name 매칭',
            '→ 인덱스 무효화, 풀 스캔 발생',
            'JOIN suppliers s',
            '  ON o.supplier_info',
            "     LIKE CONCAT('%',s.name,'%')",
            '-- 전체 스캔으로 매우 느림',
        ],
        after_lines=[
            'customer_name 컬럼 직접 참조로 변경',
            '→ 인덱스 즉시 활용, 속도 대폭 향상',
            'JOIN suppliers s',
            '  ON o.customer_name = s.name',
            '-- 인덱스 활용 → 즉시 탐색',
            '-- 14.25s → 0.17s 달성',
        ],
    )

    # ── 배운 점 ─────────────────────────────────────────────────
    lesson_y = sec_y - card_h - 14
    lesson_h = 70
    card_rect(c, M, lesson_y, W - M * 2, lesson_h)
    left_accent_line(c, M + 10, lesson_y + 10, lesson_h - 20, color=CODE_BLUE)
    c.setFont('MGBold', 15)
    c.setFillColor(CODE_BLUE)
    c.drawString(M + 22, lesson_y + lesson_h - 22, '배운 점')
    c.setFont('MG', 14)
    c.setFillColor(TEXT_PRI)
    c.drawString(M + 22, lesson_y + lesson_h - 42,
        '"기능 구현"에서 끝나지 않고 실제 사용 환경에서 병목을 직접 발견하고 쿼리 구조를 재설계하여 83배의 성능 향상을 달성했습니다.')
    c.setFont('MG', 13)
    c.setFillColor(TEXT_SEC)
    c.drawString(M + 22, lesson_y + 14,
        'N+1 문제와 인덱스 활용의 중요성을 실무 수준으로 체득한 경험입니다.')

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 05 — FIRST 팀 쇼핑몰
# ══════════════════════════════════════════════════════════════
def page_first_cover_overview(c, page_num):
    """PROJECT 05 커버 + 개요"""
    full_bg(c)
    c.setFillColor(HexColor('#051828'))
    c.circle(W * 0.5, H * 0.55, 280, fill=1, stroke=0)

    # PROJECT 05 레이블
    c.setFont('MGBold', 9)
    c.setFillColor(FIRST_ACCENT)
    lbl = 'PROJECT 01'
    lw_ = c.stringWidth(lbl, 'MGBold', 9)
    c.setStrokeColor(FIRST_ACCENT)
    c.setLineWidth(0.5)
    c.line(W/2 - lw_/2 - 20, H*0.76 + 6, W/2 - lw_/2 - 5, H*0.76 + 6)
    c.line(W/2 + lw_/2 + 5,  H*0.76 + 6, W/2 + lw_/2 + 20, H*0.76 + 6)
    c.drawCentredString(W/2, H*0.76, lbl)

    c.setFont('MGBold', 36)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.69, 'AuRa / FIRST 팀 쇼핑몰')

    c.setFont('MG', 12)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.645, 'React + Node.js · 4인 팀 프로젝트 · 3주')

    meta_items = [('유형', '4인 팀 프로젝트'), ('기간', '25.12.02 – 12.18'), ('역할', '결제·관리자'), ('팀 저장소', 'kyeol1202/Team4-Project')]
    meta_y = H * 0.59
    bw_ = 118
    total_mw = len(meta_items) * bw_ + (len(meta_items)-1) * 10
    sx_ = W/2 - total_mw/2
    for i_, (k_, v_) in enumerate(meta_items):
        mx_ = sx_ + i_ * (bw_ + 10)
        card_rect(c, mx_, meta_y, bw_, 38)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx_ + 10, meta_y + 26, k_)
        c.setFont('MGBold', 8.5)
        c.setFillColor(FIRST_ACCENT)
        c.drawString(mx_ + 10, meta_y + 12, v_)

    # 기술 스택
    tags_ = ['React 18', 'Node.js', 'Express 5', 'MySQL2', 'MariaDB', 'OpenAI', 'Multer', 'React Router']
    tx_ = W/2 - (sum(c.stringWidth(t,'MG',7.5)+16 for t in tags_) + (len(tags_)-1)*5) / 2
    ty_ = meta_y - 30
    for t_ in tags_:
        tw_ = c.stringWidth(t_, 'MG', 7.5) + 16
        c.setFillColor(CARD)
        c.setStrokeColor(FIRST_ACCENT)
        c.setLineWidth(0.5)
        c.roundRect(tx_, ty_ - 2, tw_, 14, 3, fill=1, stroke=1)
        c.setFont('MG', 7.5)
        c.setFillColor(FIRST_ACCENT)
        c.drawString(tx_ + 8, ty_ + 2, t_)
        tx_ += tw_ + 5

    # 주요 기능 카드 (2열)
    feat_y = meta_y - 68
    feats = [
        (FIRST_ACCENT, '결제 시스템', '카드 결제 흐름 구현 (주문 생성 → 결제 처리 → 성공/실패 분기)'),
        (HexColor('#34d399'), '관리자 페이지', '상품/주문/회원 CRUD, 관리자 로그인 JWT 인증'),
        (HexColor('#f87171'), 'AI 챗봇', 'OpenAI API 연동 상품 추천 & Q&A 자동 응답'),
        (HexColor('#fbbf24'), '위시리스트 · 장바구니', 'Context API 전역 상태, DB 연동 위시/장바구니'),
        (HexColor('#a78bfa'), '교환 · 반품', '반품/환불 접수 폼, 마이페이지 주문 내역 연동'),
        (HexColor('#94a3b8'), '검색 · 카테고리', '상품 검색, 카테고리별 필터링, 상품 상세'),
    ]
    fw = (W - 80 - 12) / 2
    fh = 44
    for idx_, (col_, ttl_, desc_) in enumerate(feats):
        fx_ = 40 + (idx_ % 2) * (fw + 12)
        fy_ = feat_y - (idx_ // 2) * (fh + 8) - fh
        card_rect(c, fx_, fy_, fw, fh)
        left_accent_line(c, fx_ + 7, fy_ + 6, fh - 12, color=col_, lw=2)
        c.setFont('MGBold', 9)
        c.setFillColor(col_)
        c.drawString(fx_ + 16, fy_ + fh - 14, ttl_)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_SEC)
        c.drawString(fx_ + 16, fy_ + fh - 26, desc_[:50])
        if len(desc_) > 50:
            c.drawString(fx_ + 16, fy_ + fh - 36, desc_[50:])

    draw_footer(c, 'Developer Portfolio', 'AuRa — Project 01', page_num)
    c.showPage()


def page_first_struggle(c, page_num):
    """PROJECT 05 — 고난과 역경 (Git 기록)"""
    full_bg(c)

    badge(c, 40, H - 70, '16', color=FIRST_ACCENT)
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '고난과 역경')
    c.setFont('MG', 10)
    c.setFillColor(FIRST_ACCENT)
    c.drawString(40, H - 116, 'Git이 증명하는 개발 여정 — 실제 커밋 메시지 기록')

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, H - 124, W - 40, H - 124)

    # 전체를 좌(타임라인) + 우(결론) 2열로 구성
    # 왼쪽: git commit 타임라인 카드들
    # 오른쪽: 해결 요약 + 배운 점

    struggle_items = [
        (RED_DOT,   'Dec 10',  '관리자용수정중인데모르겟서요엉엉',
         '어드민 페이지 구조를 어떻게 설계해야 할지 막막했던 순간. 권한 분리, JWT 인증 경로, 라우팅 구조 전부 처음이었음.'),
        (YEL_DOT,   'Dec 12',  '진짜진짜진짜',
         '결제 로직이 계속 오류. 주문 생성 → 결제 연결 → DB 저장까지 흐름이 연결이 안 됨. 커밋 이름이 절박함을 표현.'),
        (GRN_DOT,   'Dec 12',  '결제된다 무야호',
         '드디어 결제 흐름 완성! /api/order/create 라우트와 프론트 Payment 컴포넌트가 맞물림. 팀 최고 명장면.'),
        (YEL_DOT,   'Dec ~',   '장바구니 디자인 복구',
         'develop 브랜치 머지 이후 cart-pay.css가 충돌로 깨짐. 308줄 삭제하고 재설계. 머지 충돌의 교훈.'),
        (YEL_DOT,   'Dec 4',   'ip변경 (203 → 224)',
         'DB_HOST가 컴퓨터마다 달라 .env를 계속 수정. 팀 공통 DB 서버 IP를 통일하는 과정.'),
    ]

    tl_x = 40
    tl_w = W - 80
    item_h = 78
    item_gap = 10
    start_y = H - 142

    for dot_col, date_, commit_msg, explain in struggle_items:
        cy_ = start_y - item_h
        card_rect(c, tl_x, cy_, tl_w, item_h, fill=CARD, stroke=BORDER)

        # 좌측 상태 점
        c.setFillColor(dot_col)
        c.circle(tl_x + 18, cy_ + item_h/2, 5, fill=1, stroke=0)

        # 날짜
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(tl_x + 30, cy_ + item_h - 14, date_)

        # 커밋 메시지 (터미널 스타일)
        terminal_header(c, tl_x + 80, cy_ + item_h - 12, 220)
        card_rect(c, tl_x + 80, cy_ + item_h - 30, 220, 18, fill=CARD_DARK, stroke=BORDER, lw=0.5, radius=0)
        c.setFont('MGBold', 8.5)
        if dot_col == GRN_DOT:
            c.setFillColor(ACCENT_G)
        elif dot_col == YEL_DOT:
            c.setFillColor(ACCENT_O)
        else:
            c.setFillColor(HexColor('#f87171'))
        c.drawString(tl_x + 86, cy_ + item_h - 24, commit_msg)

        # 설명
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        for ii_, chunk_ in enumerate([explain[j:j+62] for j in range(0, min(len(explain), 186), 62)]):
            c.drawString(tl_x + 80, cy_ + item_h - 48 - ii_ * 11, chunk_)

        start_y = cy_ - item_gap

    draw_footer(c, 'Developer Portfolio', 'AuRa — Project 01', page_num)
    c.showPage()


def page_first_review(c, page_num):
    """PROJECT 05 — 해결 & 회고"""
    full_bg(c)

    badge(c, 40, H - 70, '17', color=FIRST_ACCENT)
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '해결 & 회고')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, 'AuRa — 협업 충돌 극복 & 성장 스토리')

    # 성과 수치
    metrics = [('결제', '완전 구현'), ('팀원', '4명 협업'), ('머지', '충돌 극복'), ('OpenAI', 'API 연동')]
    m_y = H - 168
    m_w = (W - 80 - 30) / 4
    for i_, (val_, lbl_) in enumerate(metrics):
        mx_ = 40 + i_ * (m_w + 10)
        card_rect(c, mx_, m_y, m_w - 4, 46)
        c.setFont('MGBold', 16)
        c.setFillColor(FIRST_ACCENT)
        c.drawCentredString(mx_ + (m_w-4)/2, m_y + 28, val_)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx_ + (m_w-4)/2, m_y + 14, lbl_)

    # 어떻게 해결했나 + 아쉬운 점
    tw_ = (W - 80 - 16) / 2
    th_ = 220

    card_rect(c, 40, m_y - th_ - 20, tw_, th_)
    left_accent_line(c, 48, m_y - th_ - 10, th_ - 20, color=FIRST_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(FIRST_ACCENT)
    c.drawString(58, m_y - 38, '✦ 어떻게 극복했나')
    fixes = [
        '결제: POST /api/order/create 라우트 직접 설계, Payment 컴포넌트와 흐름 맞춤',
        '관리자: JWT 미들웨어 분리 후 adminController로 책임 분산',
        '머지 충돌: cart-pay.css 전량 삭제 후 Payment.css로 통합 재설계',
        'IP 이슈: 팀 공용 .env 파일 규칙 설정 (DB_HOST 통일)',
        '브랜치 전략: front-dev / back-dev 분리 운영 → develop 머지 프로세스',
    ]
    fy_ = m_y - 56
    for f_ in fixes:
        used_ = bullet_item(c, 58, fy_, f_, max_w=tw_ - 30, bullet_color=FIRST_ACCENT, size=8.5)
        fy_ -= used_ + 3

    card_rect(c, 40 + tw_ + 16, m_y - th_ - 20, tw_, th_)
    left_accent_line(c, 40 + tw_ + 24, m_y - th_ - 10, th_ - 20, color=ACCENT_O)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_O)
    c.drawString(40 + tw_ + 34, m_y - 38, '△ 아쉬운 점 / 배운 점')
    bads_ = [
        '초반 브랜치 전략 없이 시작 → 머지 충돌 빈발',
        '공통 컴포넌트 설계 없이 각자 스타일 → CSS 충돌',
        '결제 흐름 설계 문서화 없이 코딩 → 시행착오 반복',
        '다음엔 API 명세서 먼저 작성 후 개발 시작 목표',
    ]
    by_ = m_y - 56
    for b_ in bads_:
        used_ = bullet_item(c, 40 + tw_ + 34, by_, b_, max_w=tw_ - 30, bullet_color=ACCENT_O, size=8.5)
        by_ -= used_ + 3

    # 성장 스토리
    ry_ = m_y - th_ - 50
    rh_ = 155
    card_rect(c, 40, ry_ - rh_, W - 80, rh_)
    left_accent_line(c, 48, ry_ - rh_ + 10, rh_ - 20, color=FIRST_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(FIRST_ACCENT)
    c.drawString(58, ry_ - 20, '💬 회고 — AuRa 팀 프로젝트')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(58, ry_ - 28, W - 50, ry_ - 28)
    story_ = [
        '"결제된다 무야호" 라는 커밋 메시지가 이 프로젝트의 모든 것을 담고 있습니다. 막혀 있던 결제 흐름이',
        '뚫린 순간의 기쁨은, 그 이전까지의 좌절 — "진짜진짜진짜", "관리자용수정중인데모르겟서요엉엉" — 이',
        '있었기 때문입니다. 처음으로 팀 협업에서 머지 충돌을 경험하고, 브랜치 전략의 필요성을 몸으로 배웠습니다.',
        '혼자 해결할 수 없던 문제들을 팀원과 함께 풀어가며, 소통과 역할 분담이 기술만큼 중요하다는 것을 깨달았습니다.',
    ]
    sy_ = ry_ - 44
    for line_ in story_:
        c.setFont('MG', 9)
        c.setFillColor(TEXT_PRI)
        c.drawString(58, sy_, line_)
        sy_ -= 14

    draw_footer(c, 'Developer Portfolio', 'AuRa — Project 01', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 06 — 계절 솔로 쇼핑몰
# ══════════════════════════════════════════════════════════════
def page_solo_cover_overview(c, page_num):
    """PROJECT 06 커버 + 개요"""
    full_bg(c)
    c.setFillColor(HexColor('#1c0d00'))
    c.circle(W * 0.5, H * 0.55, 280, fill=1, stroke=0)

    c.setFont('MGBold', 9)
    c.setFillColor(SOLO_ACCENT)
    lbl = 'PROJECT 02'
    lw_ = c.stringWidth(lbl, 'MGBold', 9)
    c.setStrokeColor(SOLO_ACCENT)
    c.setLineWidth(0.5)
    c.line(W/2 - lw_/2 - 20, H*0.76 + 6, W/2 - lw_/2 - 5, H*0.76 + 6)
    c.line(W/2 + lw_/2 + 5,  H*0.76 + 6, W/2 + lw_/2 + 20, H*0.76 + 6)
    c.drawCentredString(W/2, H*0.76, lbl)

    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.69, 'KISETSU / 계절')

    c.setFont('MG', 13)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.645, '패션 쇼핑몰 · React + Node.js + Socket.io · 1인 솔로 10일')

    meta_items = [('유형', '1인 솔로'), ('기간', '26.01.15 – 01.24'), ('커밋', '21 commits'), ('특이사항', 'Socket.io · Nodemailer')]
    meta_y = H * 0.59
    bw_ = 118
    total_mw = len(meta_items) * bw_ + (len(meta_items)-1) * 10
    sx_ = W/2 - total_mw/2
    for i_, (k_, v_) in enumerate(meta_items):
        mx_ = sx_ + i_ * (bw_ + 10)
        card_rect(c, mx_, meta_y, bw_, 38)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx_ + 10, meta_y + 26, k_)
        c.setFont('MGBold', 8.5)
        c.setFillColor(SOLO_ACCENT)
        c.drawString(mx_ + 10, meta_y + 12, v_)

    tags_ = ['React 18', 'Vite', 'Node.js', 'Express 5', 'MySQL', 'JWT', 'Socket.io', 'Nodemailer', 'Multer', 'Chart.js', 'bcryptjs']
    tx_ = W/2 - (sum(c.stringWidth(t,'MG',7)+16 for t in tags_) + (len(tags_)-1)*4) / 2
    ty_ = meta_y - 30
    for t_ in tags_:
        tw__ = c.stringWidth(t_, 'MG', 7) + 16
        c.setFillColor(CARD)
        c.setStrokeColor(SOLO_ACCENT)
        c.setLineWidth(0.5)
        c.roundRect(tx_, ty_ - 2, tw__, 14, 3, fill=1, stroke=1)
        c.setFont('MG', 7)
        c.setFillColor(SOLO_ACCENT)
        c.drawString(tx_ + 8, ty_ + 2, t_)
        tx_ += tw__ + 4

    # 주요 기능
    feats = [
        (SOLO_ACCENT,          '실시간 채팅',          'Socket.io 1:1 고객 상담 · 관리자 채팅 관리 · 읽음 처리'),
        (HexColor('#34d399'),  '등급 시스템',          '구매액 기반 자동 산정 (일반/브론즈/실버/골드/VIP)'),
        (HexColor('#a78bfa'),  '비밀번호 찾기',         'Nodemailer Gmail SMTP 이메일 인증 링크 방식'),
        (HexColor('#f87171'),  '관리자 대시보드',        'Chart.js 매출 분석 · 월별/시간대별/요일별 통계'),
        (HexColor('#fbbf24'),  '주문 · 재고',           'DB 트랜잭션으로 주문 취소 시 재고 자동 복구'),
        (HexColor('#60a5fa'),  '장바구니',              'Context API 전역 상태 · 수량 조절 · 실시간 금액 계산'),
    ]
    fw = (W - 80 - 12) / 2
    fh = 44
    feat_y = meta_y - 68
    for idx_, (col_, ttl_, desc_) in enumerate(feats):
        fx_ = 40 + (idx_ % 2) * (fw + 12)
        fy_ = feat_y - (idx_ // 2) * (fh + 8) - fh
        card_rect(c, fx_, fy_, fw, fh)
        left_accent_line(c, fx_ + 7, fy_ + 6, fh - 12, color=col_, lw=2)
        c.setFont('MGBold', 9)
        c.setFillColor(col_)
        c.drawString(fx_ + 16, fy_ + fh - 14, ttl_)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_SEC)
        c.drawString(fx_ + 16, fy_ + fh - 26, desc_[:50])
        if len(desc_) > 50:
            c.drawString(fx_ + 16, fy_ + fh - 36, desc_[50:])

    draw_footer(c, 'Developer Portfolio', 'KISETSU — Project 02', page_num)
    c.showPage()


def page_solo_struggle(c, page_num):
    """PROJECT 06 — 고난과 역경 (10일 여정)"""
    full_bg(c)

    badge(c, 40, H - 70, '19', color=SOLO_ACCENT)
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '고난과 역경')
    c.setFont('MG', 10)
    c.setFillColor(SOLO_ACCENT)
    c.drawString(40, H - 116, '10일간의 솔로 개발 기록 — 실제 커밋이 증명하는 여정')

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, H - 124, W - 40, H - 124)

    # Day 진행 바 (1일차~10일차 시각화)
    bar_y = H - 152
    bar_total_w = W - 80
    day_w = bar_total_w / 10
    days_info = [
        ('1일', CARD, TEXT_DARK),
        ('2일', CARD, TEXT_DARK),
        ('3일', HexColor('#3b1f0a'), ACCENT_O),   # 두 번 커밋
        ('4일', CARD, TEXT_DARK),
        ('5일', CARD, TEXT_DARK),
        ('6일', CARD, TEXT_DARK),
        ('7일', CARD, TEXT_DARK),
        ('8일', CARD, TEXT_DARK),
        ('9일', CARD, TEXT_DARK),
        ('10일', HexColor('#0a2e1e'), ACCENT_G),   # 완성!
    ]
    for di, (dlbl, dbg, dtxt) in enumerate(days_info):
        dx = 40 + di * day_w
        c.setFillColor(dbg)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.rect(dx, bar_y - 18, day_w - 2, 18, fill=1, stroke=1)
        c.setFont('MG', 7.5)
        c.setFillColor(dtxt)
        c.drawCentredString(dx + (day_w-2)/2, bar_y - 11, dlbl)

    c.setFont('MG', 7)
    c.setFillColor(ACCENT_O)
    c.drawString(40 + 2*day_w, bar_y - 29, '^ 3일차 두번 커밋')
    c.setFillColor(ACCENT_G)
    c.drawString(40 + 9*day_w - 5, bar_y - 29, '^ 완성!')

    # 고난 카드들
    struggle_items = [
        (YEL_DOT,  '1일차',  '학교↔집 환경 불일치',
         '"123", "12313" 커밋 — IP 불일치로 axios baseURL 계속 수정. 집과 학교 DB 서버가 달랐음.',
         'baseURL: http://192.168.0.219:5000  →  http://192.168.0.225:5000'),
        (RED_DOT,  '3일차',  '카테고리 + 채팅 동시 막힘',
         '같은 날 커밋 2번 — "3일차 (카테고리 수정 및 채팅)" 이후 바로 다시 커밋. 한 번에 두 기능이 막힘.',
         '380개 파일 한번에 스테이징 → 이후 단건 커밋 방식으로 전환'),
        (YEL_DOT,  '2-3일차', '집에서 고친거 사이드바 고침',
         '"집에서 고친거 사이드바 고침" — 학교에서 잘 되던 사이드바가 집 환경에서 깨짐. 머지 충돌.',
         'ProductListPage.css 175줄 변경 + 382개 파일 재동기화 필요'),
        (GRN_DOT,  '10일차', '비밀번호 찾기 + 스크롤 + IP 최종 해결',
         '"10일차 비밀번호 찾기 구현, IP 수정(225), 채팅 스크롤 개선, vite host 설정" — 마지막 날 일괄 해결!',
         'Nodemailer Gmail SMTP, Socket.io 스크롤 자동이동, vite.config host:true'),
    ]

    start_y = bar_y - 48
    item_h = 78
    item_gap = 8

    for dot_col, date_, title_, explain_, detail_ in struggle_items:
        cy_ = start_y - item_h
        card_rect(c, 40, cy_, W - 80, item_h, fill=CARD, stroke=BORDER)

        c.setFillColor(dot_col)
        c.circle(58, cy_ + item_h/2, 5, fill=1, stroke=0)

        c.setFont('MGBold', 8.5)
        if dot_col == GRN_DOT:
            c.setFillColor(ACCENT_G)
        elif dot_col == YEL_DOT:
            c.setFillColor(ACCENT_O)
        else:
            c.setFillColor(HexColor('#f87171'))
        c.drawString(72, cy_ + item_h - 14, f'[{date_}] {title_}')

        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawString(72, cy_ + item_h - 28, explain_[:68])
        if len(explain_) > 68:
            c.drawString(72, cy_ + item_h - 40, explain_[68:])

        # detail 코드 스타일
        c.setFillColor(CARD_DARK)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.4)
        c.roundRect(72, cy_ + 8, W - 120, 16, 2, fill=1, stroke=1)
        c.setFont('MG', 7.5)
        c.setFillColor(CODE_BLUE)
        c.drawString(78, cy_ + 13, detail_)

        start_y = cy_ - item_gap

    draw_footer(c, 'Developer Portfolio', 'KISETSU — Project 02', page_num)
    c.showPage()


def page_solo_review(c, page_num):
    """PROJECT 06 — 결과 & 회고"""
    full_bg(c)

    badge(c, 40, H - 70, '20', color=SOLO_ACCENT)
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '결과 & 회고')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, 'KISETSU — 10일 만에 완성한 풀스택 쇼핑몰')

    # 수치
    metrics = [('10일', '완성'), ('21개', '커밋'), ('Socket.io', '실시간 채팅'), ('100%', '솔로 구현')]
    m_y = H - 168
    m_w = (W - 80 - 30) / 4
    for i_, (val_, lbl_) in enumerate(metrics):
        mx_ = 40 + i_ * (m_w + 10)
        card_rect(c, mx_, m_y, m_w - 4, 46)
        c.setFont('MGBold', 16)
        c.setFillColor(SOLO_ACCENT)
        c.drawCentredString(mx_ + (m_w-4)/2, m_y + 28, val_)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx_ + (m_w-4)/2, m_y + 14, lbl_)

    tw_ = (W - 80 - 16) / 2
    th_ = 220

    # 잘된 점
    card_rect(c, 40, m_y - th_ - 20, tw_, th_)
    left_accent_line(c, 48, m_y - th_ - 10, th_ - 20, color=SOLO_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(SOLO_ACCENT)
    c.drawString(58, m_y - 38, '✦ 잘된 점')
    goods_ = [
        '사용자·관리자 기능 전체를 1인으로 10일 완성',
        'Socket.io 실시간 채팅 + 읽음 처리 구현',
        'Nodemailer Gmail SMTP 비밀번호 찾기 구현',
        'Chart.js 매출/상품/고객 분석 대시보드',
        'DB 트랜잭션 주문 취소 → 재고 자동 복구',
        '구매액 기반 자동 등급 산정 (5단계)',
    ]
    gy_ = m_y - 56
    for g_ in goods_:
        used_ = bullet_item(c, 58, gy_, g_, max_w=tw_ - 30, bullet_color=SOLO_ACCENT, size=8.5)
        gy_ -= used_ + 3

    # 아쉬운 점
    card_rect(c, 40 + tw_ + 16, m_y - th_ - 20, tw_, th_)
    left_accent_line(c, 40 + tw_ + 24, m_y - th_ - 10, th_ - 20, color=ACCENT_O)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_O)
    c.drawString(40 + tw_ + 34, m_y - 38, '△ 아쉬운 점 / 성장 포인트')
    bads_ = [
        '초반 IP 환경 통일 없이 시작 → 반복 수정 낭비',
        '3일차 대용량 커밋 → 이후 단건 커밋으로 개선',
        '타입스크립트 미적용 → 다음 프로젝트 도입 목표',
        '테스트 코드 없음 → Jest + RTL 도입 계획',
        'CSS-in-JS 미사용 → 스타일 충돌 발생',
    ]
    by_ = m_y - 56
    for b_ in bads_:
        used_ = bullet_item(c, 40 + tw_ + 34, by_, b_, max_w=tw_ - 30, bullet_color=ACCENT_O, size=8.5)
        by_ -= used_ + 3

    # 성장 스토리
    ry_ = m_y - th_ - 50
    rh_ = 158
    card_rect(c, 40, ry_ - rh_, W - 80, rh_)
    left_accent_line(c, 48, ry_ - rh_ + 10, rh_ - 20, color=SOLO_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(SOLO_ACCENT)
    c.drawString(58, ry_ - 20, '💬 회고 — KISETSU 솔로 프로젝트')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(58, ry_ - 28, W - 50, ry_ - 28)
    story_ = [
        '"123", "집에서 고친거", "IP 수정" 같은 커밋들이 부끄럽게 보일 수도 있지만, 그것들이 바로 10일 동안',
        '혼자서 벽에 부딪히고 해결해 나간 증거입니다. 매일 커밋이 쌓일 때마다 기능 하나씩 완성되어 갔고,',
        '10일차 마지막 커밋 "비밀번호 찾기 구현, IP 수정(225), 채팅 스크롤 개선" 에서 모든 것이 완성되었습니다.',
        '혼자서 프론트엔드부터 백엔드, DB, 실시간 채팅, 이메일 인증까지 전체를 구현하며 풀스택 역량의 토대를 쌓았습니다.',
    ]
    sy_ = ry_ - 44
    for line_ in story_:
        c.setFont('MG', 9)
        c.setFillColor(TEXT_PRI)
        c.drawString(58, sy_, line_)
        sy_ -= 14

    draw_footer(c, 'Developer Portfolio', 'KISETSU — Project 02', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════════════════════
def build_full_portfolio(out_path):
    """커버 + 목차 + 기존 p3~10 + RPA 5p + ERP 5p = 20페이지"""
    import fitz as _fitz, os

    tmp_front = out_path.replace('.pdf', '_front_tmp.pdf')
    tmp_rpa   = out_path.replace('.pdf', '_rpa_tmp.pdf')
    tmp_erp   = out_path.replace('.pdf', '_erp_tmp.pdf')

    # ① 커버 + 목차
    c1 = canvas.Canvas(tmp_front, pagesize=(SCREEN_W, SCREEN_H))
    page_main_cover(c1)
    page_toc(c1)
    c1.save()

    # ② RPA 파트 (p11~15)
    c2 = canvas.Canvas(tmp_rpa, pagesize=(SCREEN_W, SCREEN_H))
    page_cover(c2, 11);       page_overview(c2, 12)
    page_role_detail(c2, 13); page_rpa_impl(c2, 14); page_result(c2, 15)
    c2.save()

    # ③ ERP 파트 (p16~20)
    c3 = canvas.Canvas(tmp_erp, pagesize=(SCREEN_W, SCREEN_H))
    page_erp_cover(c3, 16);       page_erp_overview(c3, 17)
    page_erp_features(c3, 18);    page_erp_performance(c3, 19)
    page_erp_review(c3, 20)
    c3.save()

    # ④ 합치기
    import os as _os
    _orig_path = (
        'C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오.pdf'
        if _os.path.exists('C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오.pdf')
        else _os.path.join(_os.path.dirname(__file__), '통합_포트폴리오.pdf')
    )
    orig_aura    = _fitz.open(_orig_path)   # AuRa 삽입용
    orig_kisetsu = _fitz.open(_orig_path)   # KISETSU 삽입용 (리소스 분리)
    front = _fitz.open(tmp_front)
    rpa   = _fitz.open(tmp_rpa)
    erp   = _fitz.open(tmp_erp)

    # 원본 A4 페이지를 1920×1080으로 스케일해서 삽입하는 헬퍼
    _BG_RGB = (0x0e/255, 0x17/255, 0x29/255)  # BG = #0e1729
    def insert_scaled(doc, src_doc, page_idx):
        sp = src_doc[page_idx]
        ow, oh = sp.rect.width, sp.rect.height
        sc = SCREEN_H / oh
        xo = (SCREEN_W - ow * sc) / 2
        np_ = doc.new_page(width=SCREEN_W, height=SCREEN_H)
        sh_ = np_.new_shape()
        sh_.draw_rect(np_.rect)
        sh_.finish(fill=_BG_RGB, color=None)
        sh_.commit()
        np_.show_pdf_page(_fitz.Rect(xo, 0, xo + ow * sc, SCREEN_H), src_doc, page_idx)

    out = _fitz.open()
    out.insert_pdf(front)                                    # p1~2
    for i in range(2, 6):   insert_scaled(out, orig_aura,    i)  # AuRa 원본 p3~6
    for i in range(6, 10):  insert_scaled(out, orig_kisetsu, i)  # KISETSU 원본 p7~10
    out.insert_pdf(rpa)                                      # p11~15
    out.insert_pdf(erp)                                      # p16~20
    page_count = len(out)
    out.save(out_path, garbage=4, deflate=True)

    for f in [front, rpa, erp, orig_aura, orig_kisetsu, out]: f.close()
    for t in [tmp_front, tmp_rpa, tmp_erp]: os.remove(t)

    print(f'Done: {page_count} pages -> {out_path}')


if __name__ == '__main__':
    import os as _os_main
    _out_path = (
        'C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오_최종.pdf'
        if _os_main.path.exists('C:/Users/3class_013/Desktop/포트폴리오 수정폴더')
        else _os_main.path.join(_os_main.path.dirname(_os_main.path.abspath(__file__)), '통합_포트폴리오_최종.pdf')
    )
    build_full_portfolio(_out_path)
