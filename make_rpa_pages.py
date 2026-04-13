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

W, H = A4  # 595 x 842


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
    y_line = 36
    # 구분선
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, y_line + 10, W - 40, y_line + 10)
    # 왼쪽
    c.setFont('MG', 8)
    c.setFillColor(TEXT_DARK)
    c.drawString(40, y_line, left_text)
    # 오른쪽
    c.drawRightString(W - 40, y_line, right_text)
    # 페이지 번호
    c.setFillColor(TEXT_SEC)
    c.drawRightString(W - 38, y_line, str(page_num))

def badge(c, x, y, text, color=ACCENT_V, text_color=TEXT_PRI, font_size=8, pad_x=8, pad_h=14):
    """섹션 번호 배지"""
    c.setFont('MGBold', font_size)
    tw = c.stringWidth(text, 'MGBold', font_size)
    bw = tw + pad_x * 2
    c.setFillColor(color)
    c.roundRect(x, y - 3, bw, pad_h, 3, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.drawString(x + pad_x, y + 2, text)
    return bw

def tag(c, x, y, text, color=BORDER, text_color=TEXT_SEC, font_size=7.5):
    """기술 스택 태그"""
    c.setFont('MG', font_size)
    tw = c.stringWidth(text, 'MG', font_size)
    bw = tw + 12
    bh = 14
    c.setFillColor(CARD)
    c.setStrokeColor(color)
    c.setLineWidth(0.7)
    c.roundRect(x, y - 2, bw, bh, 3, fill=1, stroke=1)
    c.setFillColor(text_color)
    c.drawString(x + 6, y + 2.5, text)
    return bw + 6

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
    card_rect(c, x, y - 2, w, 18, fill=CARD_DARK, stroke=BORDER)
    for i, col in enumerate([RED_DOT, YEL_DOT, GRN_DOT]):
        c.setFillColor(col)
        c.circle(x + 12 + i * 14, y + 7, 4, fill=1, stroke=0)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — PROJECT 03 커버
# ══════════════════════════════════════════════════════════════
def page_cover(c, page_num):
    full_bg(c)

    # 배경 그라디언트 느낌 (원형 glow)
    c.setFillColor(HexColor('#0d1f3c'))
    c.circle(W * 0.5, H * 0.55, 280, fill=1, stroke=0)

    # PROJECT 03 레이블
    c.setFont('MGBold', 9)
    c.setFillColor(ACCENT_VL)
    lbl = 'PROJECT 03'
    lw = c.stringWidth(lbl, 'MGBold', 9)
    # 레이블 배경 라인
    c.setStrokeColor(ACCENT_V)
    c.setLineWidth(0.5)
    c.line(W/2 - lw/2 - 20, H*0.62 + 6, W/2 - lw/2 - 5, H*0.62 + 6)
    c.line(W/2 + lw/2 + 5,  H*0.62 + 6, W/2 + lw/2 + 20, H*0.62 + 6)
    c.drawCentredString(W/2, H*0.62, lbl)

    # 메인 타이틀
    c.setFont('MGBold', 42)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.53, '재무제표 자동화')

    # 서브타이틀
    c.setFont('MG', 13)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.47, 'Python + BrityRPA · 3인 팀 프로젝트')

    # 메타 정보 박스들
    meta_y = H * 0.38
    meta_items = [
        ('유형', '3인 팀 프로젝트'),
        ('기간', '26.02.28 – 03.10'),
        ('역할', '팀장 · RPA 개발'),
        ('파이프라인', 'End-to-End 자동화'),
    ]
    box_w = 110
    total_w = len(meta_items) * box_w + (len(meta_items)-1) * 10
    start_x = W/2 - total_w/2
    for i, (k, v) in enumerate(meta_items):
        bx = start_x + i * (box_w + 10)
        card_rect(c, bx, meta_y, box_w, 42, fill=CARD, stroke=BORDER)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(bx + box_w/2, meta_y + 28, k)
        c.setFont('MGBold', 9)
        c.setFillColor(TEXT_PRI)
        c.drawCentredString(bx + box_w/2, meta_y + 14, v)

    # 기술 스택 태그들
    tags = ['Python', 'BrityRPA', 'Pandas', 'openpyxl', 'SMTP', 'K-IFRS']
    tag_total_w = sum(c.stringWidth(t, 'MG', 7.5) + 18 for t in tags) + (len(tags)-1)*6
    tx = W/2 - tag_total_w/2
    ty = meta_y - 30
    for t in tags:
        tw = tag(c, tx, ty, t, color=BORDER, text_color=TEXT_SEC)
        tx += tw

    # 푸터
    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 2 — 프로젝트 개요
# ══════════════════════════════════════════════════════════════
def page_overview(c, page_num):
    full_bg(c)

    # 배지 + 타이틀
    badge(c, 40, H - 70, '07')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '프로젝트 개요')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, '재무제표구현 — Python + BrityRPA 자동화 팀 프로젝트')

    # 수치 박스 4개
    stats = [
        ('3인', '팀 구성'),
        ('2주', '개발 기간'),
        ('5개', 'RPA 자동화'),
        ('100%', 'Zero-Touch 파이프라인'),
    ]
    stat_y = H - 175
    stat_w = (W - 80 - 30) / 4
    for i, (num, label) in enumerate(stats):
        sx = 40 + i * (stat_w + 10)
        card_rect(c, sx, stat_y, stat_w - 4, 48)
        c.setFont('MGBold', 18)
        c.setFillColor(ACCENT_VL)
        c.drawCentredString(sx + (stat_w-4)/2, stat_y + 26, num)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(sx + (stat_w-4)/2, stat_y + 13, label)

    # 두 칼럼
    col_y = stat_y - 20
    col_h = 310
    col1_x, col2_x = 40, W/2 + 5
    col_w = W/2 - 50

    # 왼쪽: 개발 목적 & 프로젝트 목표
    card_rect(c, col1_x, col_y - col_h, col_w, col_h)
    left_accent_line(c, col1_x + 10, col_y - col_h + 10, col_h - 20)
    c.setFont('MGBold', 10)
    c.setFillColor(TEXT_PRI)
    c.drawString(col1_x + 20, col_y - 20, '▸ 개발 목적')
    c.setFont('MG', 9)
    c.setFillColor(TEXT_SEC)
    desc = '기업 재무팀의 수작업 회계 전표 처리 자동화. 매월 수만 건의 Raw Data를 수작업으로 처리하는 비효율과 휴먼 에러 제거.'
    y_cur = col_y - 36
    for line in [desc[i:i+36] for i in range(0, len(desc), 36)]:
        c.drawString(col1_x + 20, y_cur, line)
        y_cur -= 13

    y_cur -= 8
    c.setFont('MGBold', 10)
    c.setFillColor(TEXT_PRI)
    c.drawString(col1_x + 20, y_cur, '▸ 프로젝트 목표')
    y_cur -= 16
    goals = [
        'Python → 재무 데이터 처리 (ETL)',
        'RPA → 보고서 자동 생성 & 차트',
        '메일 자동 발송 (SMTP)',
        'Raw Data → 재무제표 → 대시보드 → 메일',
    ]
    for g in goals:
        used = bullet_item(c, col1_x + 20, y_cur, g, max_w=col_w - 30, line_h=13)
        y_cur -= used + 4

    y_cur -= 8
    c.setFont('MGBold', 10)
    c.setFillColor(TEXT_PRI)
    c.drawString(col1_x + 20, y_cur, '▸ 시스템 아키텍처')
    y_cur -= 16
    arch_steps = [
        ('Input',   'CSV Raw Data (1만 건 가상 분개장)'),
        ('Process', 'Python · Pandas ETL → 데이터 마트'),
        ('Output',  'BrityRPA → Excel 차트 · 메일 발송'),
    ]
    for step, desc_s in arch_steps:
        card_rect(c, col1_x + 20, y_cur - 22, col_w - 30, 24,
                  fill=CARD_DARK, stroke=BORDER, lw=0.5)
        c.setFont('MGBold', 8)
        c.setFillColor(ACCENT_VL)
        c.drawString(col1_x + 28, y_cur - 13, step)
        sw = c.stringWidth(step, 'MGBold', 8)
        c.setFont('MG', 8.5)
        c.setFillColor(TEXT_PRI)
        c.drawString(col1_x + 28 + sw + 8, y_cur - 13, desc_s)
        y_cur -= 30

    # 오른쪽: 내 담당 역할
    card_rect(c, col2_x, col_y - col_h, col_w, col_h)
    left_accent_line(c, col2_x + 10, col_y - col_h + 10, col_h - 20, color=ACCENT_G)
    c.setFont('MGBold', 10)
    c.setFillColor(TEXT_PRI)
    c.drawString(col2_x + 20, col_y - 20, '▸ 내 담당 역할 (팀장 · RPA 개발)')
    y_cur2 = col_y - 36

    role_groups = [
        ('End-to-End 자동화 아키텍처 설계', [
            'Python + BrityRPA 연계 자동화 구조 설계',
            'ETL → 데이터마트 → Excel 전체 파이프라인 구축',
        ]),
        ('RPA 자동화 구현', [
            'Python 스크립트 실행 및 결과 수집 자동화',
            'Excel 보고서 생성 / 그래프 / 레이아웃 자동 구성',
        ]),
        ('데이터 검증 및 프로젝트 관리', [
            '재무 데이터 정합성 검증 UI 기반 Validation 설계',
            '프로젝트 일정 관리 및 기술 의사결정 리딩',
        ]),
    ]
    for group_title, items in role_groups:
        c.setFont('MGBold', 9)
        c.setFillColor(ACCENT_VL)
        c.drawString(col2_x + 20, y_cur2, group_title)
        y_cur2 -= 14
        for item in items:
            c.setFont('MG', 8.5)
            c.setFillColor(TEXT_SEC)
            c.drawString(col2_x + 28, y_cur2, '· ' + item)
            y_cur2 -= 12
        y_cur2 -= 6

    # 기술 스택 (하단)
    stack_y = col_y - col_h - 40
    c.setFont('MG', 8.5)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, stack_y + 12, '기술 스택')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, stack_y + 8, W - 40, stack_y + 8)

    tag_groups = [
        ('Data Engineering & Logic', ['Python', 'Pandas', 'openpyxl'], ACCENT_V),
        ('Process Automation', ['BrityRPA', 'SMTP'], ACCENT_G),
        ('Data Source', ['CSV Raw Data', 'K-IFRS 기준'], TEXT_DARK),
    ]
    tx = 40
    ty = stack_y - 8
    for group, tags_list, col_accent in tag_groups:
        c.setFont('MG', 7)
        c.setFillColor(TEXT_DARK)
        c.drawString(tx, ty + 14, group)
        for t in tags_list:
            tw = tag(c, tx, ty, t, color=col_accent, text_color=TEXT_SEC)
            tx += tw
        tx += 12

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 3 — 담당 역할 & RPA 구조
# ══════════════════════════════════════════════════════════════
def page_role_detail(c, page_num):
    full_bg(c)

    badge(c, 40, H - 70, '08')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '담당 역할 — RPA 자동화 파이프라인')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, '팀장으로서 End-to-End 자동화 아키텍처 설계 및 BrityRPA 구현 전담')

    # 상단: 파이프라인 흐름도
    flow_y = H - 155
    flow_h = 52
    steps = [
        ('CSV\nRaw Data', CODE_BLUE),
        ('Python\nETL', ACCENT_VL),
        ('Data\nMart', CODE_GREEN),
        ('BrityRPA\n자동화', CODE_ORG),
        ('Excel\n보고서', CODE_PUR),
        ('메일\n발송', ACCENT_G),
    ]
    step_w = (W - 80 - 40) / len(steps)
    for i, (lbl, col) in enumerate(steps):
        sx = 40 + i * (step_w + 8)
        card_rect(c, sx, flow_y - flow_h, step_w, flow_h, fill=CARD, stroke=col, lw=1.5)
        # 화살표
        if i < len(steps) - 1:
            ax = sx + step_w + 1
            ay = flow_y - flow_h/2
            c.setFillColor(BORDER)
            p = c.beginPath()
            p.moveTo(ax, ay - 4)
            p.lineTo(ax + 6, ay)
            p.lineTo(ax, ay + 4)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
        lines = lbl.split('\n')
        for j, line in enumerate(lines):
            c.setFont('MGBold' if j == 0 else 'MG', 8)
            c.setFillColor(col if j == 0 else TEXT_SEC)
            c.drawCentredString(sx + step_w/2, flow_y - 20 - j*14, line)

    # 세 칼럼 카드
    card_y = flow_y - flow_h - 20
    card_h = 360
    card_w = (W - 80 - 20) / 3
    col_data = [
        {
            'title': '① 아키텍처 설계',
            'color': ACCENT_VL,
            'items': [
                ('Hybrid Automation 설계',
                 'Python이 연산, RPA가 시각화/배포를 전담하는 역할 분리 구조'),
                ('인터페이스 규격 수립',
                 'Python ↔ RPA 간 데이터 교환 형식 사전 합의. error_flag.txt로 오류 상태 공유'),
                ('Error Handling 구조',
                 'Python 실행 중 오류 발생 시 플래그 파일 생성 → RPA 자동 중단 설계'),
                ('전체 파이프라인 리딩',
                 'ETL → 데이터마트 → Excel 리포트까지 전체 흐름 총괄'),
            ]
        },
        {
            'title': '② RPA 자동화 구현',
            'color': CODE_ORG,
            'items': [
                ('Python 스크립트 실행',
                 'BrityRPA ExecuteCmd로 apnalchangchang.py 실행 및 결과 수집'),
                ('Excel 차트 자동 생성',
                 '월별 손익 꺾은선 차트 / 비용구조 파이차트 / 포괄손익계산서 차트'),
                ('분기별 재무현황 이관',
                 'Python 결과 파일 → 보고서 템플릿 시트 자동 복사 · 서식 유지'),
                ('엑셀 저장 · 메일 발송',
                 'SMTP 연동, 수신자 자동 설정, 완성된 Excel 보고서 자동 첨부 발송'),
            ]
        },
        {
            'title': '③ 데이터 검증 & 관리',
            'color': ACCENT_G,
            'items': [
                ('재무 데이터 정합성 검증',
                 'UI 기반 Validation 설계로 입력 데이터 오류 사전 차단'),
                ('프로젝트 일정 관리',
                 ' 공통 기획 → Python 개발 → RPA 시각화 → 통합 테스트 단계 리딩'),
                ('기술 의사결정',
                 'Python-RPA 연계 방식, 데이터 마트 구조, 오류 플래그 방식 등 결정'),
                ('팀 협업 조율',
                 '타 기술 스택 담당자와 명확한 데이터 인터페이스 합의 및 소통'),
            ]
        },
    ]
    for ci, col_info in enumerate(col_data):
        cx = 40 + ci * (card_w + 10)
        card_rect(c, cx, card_y - card_h, card_w, card_h)
        left_accent_line(c, cx + 8, card_y - card_h + 12, card_h - 24,
                         color=col_info['color'])
        c.setFont('MGBold', 9.5)
        c.setFillColor(col_info['color'])
        c.drawString(cx + 18, card_y - 20, col_info['title'])
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(cx + 18, card_y - 27, cx + card_w - 10, card_y - 27)

        iy = card_y - 44
        for (item_t, item_d) in col_info['items']:
            c.setFont('MGBold', 8.5)
            c.setFillColor(TEXT_PRI)
            c.drawString(cx + 18, iy, item_t)
            iy -= 13
            # 설명 줄바꿈
            words = item_d.split(' ')
            line = ''
            for w in words:
                test = line + (' ' if line else '') + w
                if c.stringWidth(test, 'MG', 8) <= card_w - 30:
                    line = test
                else:
                    c.setFont('MG', 8)
                    c.setFillColor(TEXT_SEC)
                    c.drawString(cx + 18, iy, line)
                    iy -= 11
                    line = w
            if line:
                c.setFont('MG', 8)
                c.setFillColor(TEXT_SEC)
                c.drawString(cx + 18, iy, line)
                iy -= 11
            iy -= 10

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 4 — 핵심 기능 구현 (RPA 코드 스타일)
# ══════════════════════════════════════════════════════════════
def page_rpa_impl(c, page_num):
    full_bg(c)

    badge(c, 40, H - 70, '09')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '핵심 기능 구현')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, 'BrityRPA 기반 자동화 · Python-RPA Hybrid Architecture')

    # 4개 기능 카드 (2x2 그리드)
    cell_w = (W - 80 - 16) / 2
    cell_h = 170
    cells = [
        {
            'title': '1. 파이썬 실행 자동화',
            'file': 'BrityRPA_ExecuteCmd.bot',
            'desc': 'BrityRPA의 ExecuteCmd 액션으로 Python 데이터 처리 엔진 실행. RPA가 단순 UI 자동화를 넘어 전체 자동화 파이프라인을 제어하는 Orchestrator 역할 수행.',
            'code': [
                ('// 1. Python 스크립트 실행', TEXT_DARK),
                ('ExecuteCmd("python apnalchangchang.py")', CODE_BLUE),
                ('', None),
                ('// 2. 오류 플래그 감지', TEXT_DARK),
                ('IF FileExists("error_flag.txt")', CODE_ORG),
                ('  → RPA 프로세스 중단 처리', TEXT_SEC),
            ],
            'color': CODE_BLUE,
        },
        {
            'title': '2. Excel 차트 자동 생성',
            'file': 'chart_automation.bot',
            'desc': 'Python 결과 데이터 기반 Excel Chart Object 자동 생성. 월별 손익 꺾은선, 비용구조 파이차트, 포괄손익계산서 차트 3종 자동화.',
            'code': [
                ('// 차트 자동화 프로세스', TEXT_DARK),
                ('CreateChart(type="Line")', CODE_GREEN),
                ('  .SetDataRange(monthly_pl)', CODE_PUR),
                ('  .SetTitle("월별 손익 추이")', CODE_ORG),
                ('CreateChart(type="Pie")', CODE_GREEN),
                ('  .SetDataRange(cost_structure)', CODE_PUR),
            ],
            'color': CODE_GREEN,
        },
        {
            'title': '3. 분기별 재무현황 이관',
            'file': 'data_transfer.bot',
            'desc': 'Python 생성 재무현황 데이터를 최종 보고서 Excel 템플릿으로 자동 이관. 기존 서식·레이아웃 유지한 상태로 데이터 배치.',
            'code': [
                ('// 데이터 이관 프로세스', TEXT_DARK),
                ('LoadWorkbook(data_mart.xlsx)', CODE_BLUE),
                ('SelectSheet("분기별재무현황")', CODE_PUR),
                ('CopyRange(A1:Z100)', CODE_ORG),
                ('PasteToTemplate("보고서템플릿")', CODE_GREEN),
                ('MaintainFormatting = True', CODE_ORG),
            ],
            'color': CODE_PUR,
        },
        {
            'title': '4. 엑셀 저장 & 메일 자동 발송',
            'file': 'mail_dispatch.bot',
            'desc': 'SMTP 서버 연동으로 최종 보고서 자동 배포. 수신자 자동 설정, 메일 제목·본문 자동 작성, Excel 첨부 발송까지 완전 자동화.',
            'code': [
                ('// End-to-End 메일 발송', TEXT_DARK),
                ('SaveWorkbook("경영대시보드.xlsx")', CODE_GREEN),
                ('SMTP.Connect(server, port)', CODE_BLUE),
                ('Mail.SetRecipients(recipients)', CODE_PUR),
                ('Mail.AttachFile(report.xlsx)', CODE_ORG),
                ('Mail.Send()  // 자동 발송 완료', CODE_GREEN),
            ],
            'color': ACCENT_G,
        },
    ]
    positions = [
        (40, H - 145),
        (40 + cell_w + 16, H - 145),
        (40, H - 145 - cell_h - 16),
        (40 + cell_w + 16, H - 145 - cell_h - 16),
    ]
    for cell, (cx, cy_top) in zip(cells, positions):
        cy = cy_top - cell_h
        card_rect(c, cx, cy, cell_w, cell_h)
        left_accent_line(c, cx + 8, cy + 10, cell_h - 20, color=cell['color'])

        # 타이틀
        c.setFont('MGBold', 10)
        c.setFillColor(cell['color'])
        c.drawString(cx + 18, cy_top - 20, cell['title'])

        # 파일명
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(cx + 18, cy_top - 33, cell['file'])

        # 설명
        desc_y = cy_top - 48
        for chunk in [cell['desc'][i:i+38] for i in range(0, min(len(cell['desc']), 114), 38)]:
            c.setFont('MG', 8)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx + 18, desc_y, chunk)
            desc_y -= 11

        # 코드 블록
        code_top = cy + 80
        code_h = 70
        terminal_header(c, cx + 18, code_top, cell_w - 28)
        card_rect(c, cx + 18, code_top - code_h, cell_w - 28, code_h + 2,
                  fill=CARD_DARK, stroke=BORDER, lw=0.5, radius=0)
        cl = code_top - 10
        for code_line, col in cell['code']:
            if code_line:
                c.setFont('MG', 7.5)
                c.setFillColor(col or TEXT_SEC)
                c.drawString(cx + 24, cl, code_line)
            cl -= 10

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PAGE 5 — 결과 · 회고
# ══════════════════════════════════════════════════════════════
def page_result(c, page_num):
    full_bg(c)

    badge(c, 40, H - 70, '10')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '결과 · 회고')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, 'RPA 자동화 프로젝트 성과와 팀장으로서의 성장')

    # 성과 수치
    metrics = [
        ('5개', 'RPA 자동화 구현'),
        ('100%', 'Zero-Touch 파이프라인'),
        ('1만 건+', '전표 데이터 처리'),
        ('팀장', 'E2E 아키텍처 리딩'),
    ]
    m_y = H - 165
    m_w = (W - 80 - 30) / 4
    for i, (val, lbl) in enumerate(metrics):
        mx = 40 + i * (m_w + 10)
        card_rect(c, mx, m_y, m_w - 4, 48)
        c.setFont('MGBold', 18)
        c.setFillColor(ACCENT_G)
        c.drawCentredString(mx + (m_w-4)/2, m_y + 26, val)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx + (m_w-4)/2, m_y + 13, lbl)

    # 잘된 점 / 아쉬운 점
    tw = (W - 80 - 16) / 2
    th = 195

    # 잘된 점
    card_rect(c, 40, m_y - th - 20, tw, th)
    left_accent_line(c, 48, m_y - th - 10, th - 20, color=ACCENT_G)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_G)
    c.drawString(58, m_y - 40, '✦ 잘된 점')
    goods = [
        '재무자동화 핵심 프로세스 100% 구현',
        'Python-RPA 하이브리드 아키텍처 완성',
        'Error Flag 구조로 이기종 시스템 안정 연동',
        '원천데이터 파싱 → 메일 발송 Zero-Touch 완성',
        '팀장으로 전체 기술 의사결정 및 일정 리딩',
    ]
    gy = m_y - 58
    for g in goods:
        used = bullet_item(c, 58, gy, g, max_w=tw - 30, bullet_color=ACCENT_G, size=9)
        gy -= used + 4

    # 아쉬운 점
    card_rect(c, 40 + tw + 16, m_y - th - 20, tw, th)
    left_accent_line(c, 40 + tw + 24, m_y - th - 10, th - 20, color=ACCENT_O)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_O)
    c.drawString(40 + tw + 34, m_y - 40, '△ 아쉬운 점 / 개선 방향')
    bads = [
        '초기 원천 데이터 예외 포맷 오류 처리 미흡',
        'RPA 예외처리 로직 더 정교화 필요',
        '동적 방어 코드 추가 및 에러 로깅 고도화 목표',
        '실제 경영진 피드백 기반 대시보드 UI/UX 개선',
    ]
    by = m_y - 58
    for b in bads:
        used = bullet_item(c, 40 + tw + 34, by, b,
                           max_w=tw - 30, bullet_color=ACCENT_O, size=9)
        by -= used + 4

    # 성장 스토리
    story_y = m_y - th - 50
    story_h = 175
    card_rect(c, 40, story_y - story_h, W - 80, story_h)
    left_accent_line(c, 48, story_y - story_h + 10, story_h - 20, color=ACCENT_VL)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_VL)
    c.drawString(58, story_y - 20, '💬 자체 평가 — 윤종빈')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(58, story_y - 28, W - 50, story_y - 28)

    story_text = [
        '단순한 스크립트 코딩을 넘어, 실제 기업 재무 기준을 시스템 로직으로 완벽히 구현해낸 것이 이번 프로젝트의 가장 큰 성과입니다.',
        'Python이 무거운 "데이터 연산"을 전담하고 RPA가 "시각화 및 메일 발송"을 담당하도록 아키텍처를 분리하였습니다.',
        '다른 기술 스택을 담당하는 팀원과 명확한 데이터 인터페이스 규격을 합의하고, 오류 발생 시 즉각적으로 상태를 공유하는',
        'Error Flag 구조를 설계하며 이기종 시스템 간 매끄러운 연동과 소통 기반의 협업 시너지를 제대로 경험할 수 있었습니다.',
    ]
    sy = story_y - 44
    for line in story_text:
        c.setFont('MG', 9)
        c.setFillColor(TEXT_PRI)
        c.drawString(58, sy, line)
        sy -= 14

    draw_footer(c, 'Developer Portfolio', '재무제표 자동화 — Project 03', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# 업데이트 커버 (첫 페이지) — PROJECT 03, 04 추가
# ══════════════════════════════════════════════════════════════
def page_main_cover(c):
    """통합 포트폴리오 첫 페이지 — PROJECT 04 포함"""
    full_bg(c)

    # 배경 글로우 효과
    c.setFillColor(HexColor('#0d1535'))
    c.circle(W * 0.25, H * 0.3, 200, fill=1, stroke=0)
    c.setFillColor(HexColor('#0a1f3a'))
    c.circle(W * 0.78, H * 0.7, 180, fill=1, stroke=0)

    # 상단 레이블
    label = 'FULL-STACK DEVELOPER PORTFOLIO'
    c.setFont('MG', 8)
    lw = c.stringWidth(label, 'MG', 8)
    c.setStrokeColor(HexColor('#3d4f7c'))
    c.setFillColor(HexColor('#3d4f7c'))
    c.setLineWidth(0.6)
    c.roundRect(W/2 - lw/2 - 12, H*0.79, lw + 24, 16, 8, fill=0, stroke=1)
    c.setFillColor(HexColor('#818bf7'))
    c.drawCentredString(W/2, H*0.79 + 4, label)

    # 메인 타이틀 "Portfolio" — 그라디언트 느낌(연보라 → 보라)
    c.setFont('MGBold', 54)
    c.setFillColor(HexColor('#b0b9fc'))
    c.drawCentredString(W/2, H*0.71, 'Portfolio')

    # 서브타이틀
    c.setFont('MG', 12)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.67, '여섯 개의 프로젝트를 통한 성장 기록')

    # 4개 프로젝트 박스 (2x2 그리드)
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
    box_w = 130
    box_h = 68
    gap = 14
    total_w = 2 * box_w + gap
    bx_start = W/2 - total_w/2
    row1_top = H * 0.615

    for i, (proj_lbl, title, sub, meta, accent, bg_col) in enumerate(projects):
        col = i % 2
        row = i // 2
        bx = bx_start + col * (box_w + gap)
        by = row1_top - row * (box_h + gap) - box_h
        c.setFillColor(bg_col)
        c.setStrokeColor(accent)
        c.setLineWidth(0.8)
        c.roundRect(bx, by, box_w, box_h, 5, fill=1, stroke=1)
        c.setFont('MGBold', 7)
        c.setFillColor(accent)
        c.drawString(bx + 9, by + box_h - 13, proj_lbl)
        c.setFont('MGBold', 10.5)
        c.setFillColor(TEXT_PRI)
        c.drawString(bx + 9, by + box_h - 25, title)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_SEC)
        c.drawString(bx + 9, by + box_h - 37, sub)
        c.setFont('MG', 7)
        c.setFillColor(TEXT_DARK)
        c.drawString(bx + 9, by + 9, meta)

    # 기술 스택 태그
    all_tags = ['React', 'Node.js', 'Spring Boot', 'MariaDB', 'JWT',
                'Socket.io', 'MyBatis', 'Python', 'BrityRPA', 'Nodemailer']
    tag_total = sum(c.stringWidth(t, 'MG', 7) + 16 for t in all_tags) + (len(all_tags)-1)*4
    tx = W/2 - tag_total/2
    bottom_box_y = row1_top - 1 * (box_h + gap) - box_h
    ty = bottom_box_y - 22
    for t in all_tags:
        c.setFont('MG', 7)
        tw2 = c.stringWidth(t, 'MG', 7) + 16
        c.setFillColor(CARD)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.6)
        c.roundRect(tx, ty - 2, tw2, 13, 3, fill=1, stroke=1)
        c.setFillColor(TEXT_DARK)
        c.drawString(tx + 8, ty + 2, t)
        tx += tw2 + 4

    # 연도
    c.setFont('MG', 9)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(W/2, ty - 16, '2025 — 2026')

    c.showPage()


# ══════════════════════════════════════════════════════════════
# 업데이트 목차 — PROJECT 03, 04 포함
# ══════════════════════════════════════════════════════════════
ERP_ACCENT   = HexColor('#e05c8a')
FIRST_ACCENT = HexColor('#38bdf8')   # sky-blue — FIRST 팀 프로젝트
SOLO_ACCENT  = HexColor('#fb923c')   # orange   — Solo 계절 프로젝트

def page_toc(c):
    full_bg(c)
    badge(c, 40, H - 62, 'INDEX', color=ACCENT_G, font_size=8, pad_x=8, pad_h=16)
    c.setFont('MGBold', 24)
    c.setFillColor(TEXT_PRI)
    c.drawString(106, H - 65, '목차')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, H - 76, W - 40, H - 76)

    def sec_hdr(label, y, col=ACCENT_VL):
        c.setFillColor(col)
        c.rect(40, y - 1, 3, 12, fill=1, stroke=0)
        c.setFont('MGBold', 8.5)
        c.setFillColor(col)
        c.drawString(50, y, label)

    def item(num, title, subtitle, pg, y, col=ACCENT_V):
        card_rect(c, 40, y - 22, W - 80, 26)
        badge(c, 50, y - 16, f'{num:02d}', color=col, font_size=7.5, pad_x=5, pad_h=11)
        c.setFont('MGBold', 8.5)
        c.setFillColor(TEXT_PRI)
        c.drawString(80, y - 8, title)
        c.setFont('MG', 7)
        c.setFillColor(TEXT_SEC)
        c.drawString(80, y - 18, subtitle)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_DARK)
        c.drawRightString(W - 50, y - 12, f'{pg:02d}')

    y = H - 100
    sec_hdr('PROJECT 01 — AuRa / FIRST 팀 쇼핑몰', y);  y -= 14
    item(1, '프로젝트 개요', 'AuRa 소개, 기술 스택, 팀 구성', 3, y);  y -= 30
    item(2, '주요 기여 — DB · 인증 · 장바구니 · 카테고리', '담당 기능 상세, 코드 구현 방식', 4, y);  y -= 30
    item(3, '기술적 어필 포인트', '관심사 분리, 중복 방지 로직, 서버단 검증', 5, y);  y -= 38

    item(4, '고난과 역경 — Git이 증명하는 개발 여정', '"결제된다 무야호" · 머지 충돌 · IP 전쟁', 7, y, FIRST_ACCENT);  y -= 30
    item(5, '해결 & 회고', '결제 구현 돌파, 협업 충돌 극복, 성장 스토리', 9, y, FIRST_ACCENT);  y -= 38

    sec_hdr('PROJECT 02 — KISETSU 도매 패션 이커머스', y, ACCENT_G);  y -= 14
    item(6, '프로젝트 개요 · 아키텍처', '기획 배경, 시스템 구조, 기술 스택', 10, y, ACCENT_G);  y -= 30
    item(7, '주요 기능 구현', 'JWT 인증, 실시간 채팅, Context API, 인기검색어', 12, y, ACCENT_G);  y -= 30
    item(8, '결과 · 회고', '구현 성과, 배운 점, 성장 스토리', 13, y, ACCENT_G);  y -= 30
    item(9, '고난과 역경 — 10일간의 기록', '환경 불일치 · IP 전쟁 · 채팅 스크롤 사투', 14, y, ACCENT_G);  y -= 30
    item(10, '결과 & 회고 (솔로)', '10일 완성, 전체 기능 솔로 구현, 성장 포인트', 16, y, ACCENT_G);  y -= 38

    sec_hdr('PROJECT 03 — 재무제표 자동화 (Python + BrityRPA)', y, ACCENT_O);  y -= 14
    item(11, '프로젝트 개요', '기획 배경, 시스템 아키텍처, 담당 역할', 18, y, ACCENT_O);  y -= 30
    item(12, '담당 역할 — RPA 자동화 파이프라인', '아키텍처 설계, RPA 구현, 데이터 검증', 19, y, ACCENT_O);  y -= 30
    item(13, '핵심 기능 구현', 'Python 실행, Excel 차트 자동화, 메일 발송', 20, y, ACCENT_O);  y -= 30
    item(14, '결과 · 회고', 'RPA 성과, 잘된 점, 아쉬운 점, 자체 평가', 21, y, ACCENT_O);  y -= 38

    sec_hdr('PROJECT 04 — 개발환기좀해 ERP (Spring Boot + MyBatis)', y, ERP_ACCENT);  y -= 14
    item(15, '프로젝트 개요 · 아키텍처', '기획 배경, 전체 모듈, 기술 스택', 23, y, ERP_ACCENT);  y -= 30
    item(16, '핵심 기능 구현', 'OCR 거래명세서, BOM 자동발주, 재무 리포트', 24, y, ERP_ACCENT);  y -= 30
    item(17, '성능 최적화 · DB 쿼리 튜닝', 'N+1 문제 해결, 인덱스 최적화 (14.25s→0.17s)', 25, y, ERP_ACCENT);  y -= 30
    item(18, '기술적 어필 & 회고', 'Spring Security, 트랜잭션, 성과, 회고', 26, y, ERP_ACCENT)

    draw_footer(c, 'Developer Portfolio', '', 2)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — ERP 커버
# ══════════════════════════════════════════════════════════════
def page_erp_cover(c, page_num):
    full_bg(c)
    c.setFillColor(HexColor('#200d18'))
    c.circle(W * 0.5, H * 0.55, 280, fill=1, stroke=0)

    c.setFont('MGBold', 9)
    c.setFillColor(ERP_ACCENT)
    lbl = 'PROJECT 04'
    lw2 = c.stringWidth(lbl, 'MGBold', 9)
    c.setStrokeColor(ERP_ACCENT)
    c.setLineWidth(0.5)
    c.line(W/2 - lw2/2 - 20, H*0.62 + 6, W/2 - lw2/2 - 5, H*0.62 + 6)
    c.line(W/2 + lw2/2 + 5,  H*0.62 + 6, W/2 + lw2/2 + 20, H*0.62 + 6)
    c.drawCentredString(W/2, H*0.62, lbl)

    c.setFont('MGBold', 34)
    c.setFillColor(TEXT_PRI)
    c.drawCentredString(W/2, H*0.53, '개발환기좀해 ERP')

    c.setFont('MG', 13)
    c.setFillColor(TEXT_SEC)
    c.drawCentredString(W/2, H*0.475, 'Spring Boot + MyBatis · 1인 솔로 풀스택')

    meta_items = [
        ('유형', '1인 솔로 프로젝트'),
        ('기간', '26.03.25 – 04.01'),
        ('규모', '모듈 15개+'),
        ('특이사항', 'OCR · AI API 연동'),
    ]
    meta_y = H * 0.375
    bw2 = 110
    total_mw = len(meta_items) * bw2 + (len(meta_items)-1) * 10
    sx = W/2 - total_mw/2
    for i, (k, v) in enumerate(meta_items):
        mx = sx + i * (bw2 + 10)
        card_rect(c, mx, meta_y, bw2, 42)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(mx + bw2/2, meta_y + 28, k)
        c.setFont('MGBold', 9)
        c.setFillColor(TEXT_PRI)
        c.drawCentredString(mx + bw2/2, meta_y + 14, v)

    erp_tags = ['Spring Boot 3.4', 'Java 17', 'MyBatis', 'MariaDB',
                'Spring Security', 'JSP/JSTL', 'Swagger', 'Gemini OCR', 'Lombok']
    tag_tw = sum(c.stringWidth(t, 'MG', 7) + 16 for t in erp_tags) + (len(erp_tags)-1)*4
    tx2 = W/2 - tag_tw/2
    ty2 = meta_y - 28
    for t in erp_tags:
        c.setFont('MG', 7)
        tw3 = c.stringWidth(t, 'MG', 7) + 16
        c.setFillColor(CARD)
        c.setStrokeColor(ERP_ACCENT)
        c.setLineWidth(0.5)
        c.roundRect(tx2, ty2 - 2, tw3, 13, 3, fill=1, stroke=1)
        c.setFillColor(TEXT_SEC)
        c.drawString(tx2 + 8, ty2 + 2, t)
        tx2 += tw3 + 4

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — ERP 개요 & 모듈
# ══════════════════════════════════════════════════════════════
def page_erp_overview(c, page_num):
    full_bg(c)
    badge(c, 40, H - 70, '11')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '프로젝트 개요 · 전체 모듈')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, '개발환기좀해 ERP — 제조업 기반 통합 자원 관리 시스템 (1인 풀스택)')

    # 수치 박스
    stats = [('15개+', '컨트롤러/모듈'), ('20개+', 'REST API'), ('1인', '솔로 개발'), ('5주', '개발 기간')]
    stat_y = H - 170
    sw2 = (W - 80 - 30) / 4
    for i, (val, lbl) in enumerate(stats):
        sx2 = 40 + i * (sw2 + 10)
        card_rect(c, sx2, stat_y, sw2 - 4, 46)
        c.setFont('MGBold', 18)
        c.setFillColor(ERP_ACCENT)
        c.drawCentredString(sx2 + (sw2-4)/2, stat_y + 26, val)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(sx2 + (sw2-4)/2, stat_y + 12, lbl)

    # 모듈 그리드 (3열)
    modules = [
        ('인증 · 보안',    ERP_ACCENT, ['Spring Security 역할 기반 접근제어', 'BCrypt 패스워드 해싱', 'ADMIN / USER 권한 분리']),
        ('대시보드',       CODE_BLUE,  ['실시간 KPI (제품수, 직원수, 매출)', '재고부족 알림, 월별 작업지시 통계', '최근 주문 · 저재고 품목 리스트']),
        ('인사 · 근태',    ACCENT_G,   ['직원 CRUD + 사진 업로드', '출퇴근 체크인/아웃 API', '연차/병가 등록 · 잔여일수 차감']),
        ('생산 관리',      CODE_ORG,   ['BOM(자재명세서) 관리', '작업지시서 생성 · 상태 관리', 'BOM 기반 재고 부족 시 자동 발주']),
        ('재고 · 창고',    CODE_GREEN, ['재고 CRUD, 입출고 트랜잭션', '창고별 재고 현황 관리', '저재고 기준치 설정 (시스템 설정)']),
        ('구매 · 영업',    ACCENT_VL,  ['발주서 워크플로우 (대기→승인→완료)', '판매 · 배송 관리', '거래처(공급업체) 관리']),
        ('거래명세서',     HexColor('#f87171'), ['OCR (Gemini/Groq AI) 자동 인식', '이미지 업로드 → DB 자동 등록', '인쇄 기능 (거래명세서 출력)']),
        ('재무 분석',      HexColor('#34d399'), ['손익계산서 자동 계산 (월별/연별)', '영업이익률 · 매출총이익 산출', 'Python 연동 Excel 리포트 내보내기']),
        ('관리자',         TEXT_SEC,   ['사용자 계정 관리 (ADMIN)', '저재고 기준치 시스템 설정', 'Swagger UI API 문서 자동화']),
    ]
    mw = (W - 80 - 20) / 3
    mh = 82
    start_y = stat_y - 20
    for i, (title, col, items) in enumerate(modules):
        row, col_idx = divmod(i, 3)
        mx = 40 + col_idx * (mw + 10)
        my = start_y - row * (mh + 8) - mh
        card_rect(c, mx, my, mw, mh)
        left_accent_line(c, mx + 7, my + 8, mh - 16, color=col)
        c.setFont('MGBold', 9)
        c.setFillColor(col)
        c.drawString(mx + 16, my + mh - 16, title)
        iy = my + mh - 30
        for it in items:
            c.setFont('MG', 7.5)
            c.setFillColor(TEXT_SEC)
            c.drawString(mx + 16, iy, it)
            iy -= 11

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 핵심 기능 구현
# ══════════════════════════════════════════════════════════════
def page_erp_features(c, page_num):
    full_bg(c)
    badge(c, 40, H - 70, '12')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '핵심 기능 구현')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, 'OCR 자동 인식 · BOM 자동발주 · 재무 리포트 · Spring Security')

    cells = [
        {
            'title': 'OCR 거래명세서 자동 인식',
            'file': 'OcrController.java',
            'color': HexColor('#f87171'),
            'desc': 'Gemini/Groq AI API 연동. 이미지 업로드 → Python OCR 실행 → JSON 파싱 → DB 자동 저장까지 완전 자동화.',
            'code': [
                ('// 1. 이미지 → Python OCR 실행', TEXT_DARK),
                ('ProcessBuilder pb = new ProcessBuilder(', CODE_BLUE),
                ('  pythonCmd, mainPy, "--erp-mode", file);', CODE_BLUE),
                ('// 2. JSON 파싱 → TransactionStatement', TEXT_DARK),
                ('stmt.setIssueDate(LocalDate.parse(...));', CODE_GREEN),
                ('statementService.insert(stmt, items);', CODE_ORG),
            ],
        },
        {
            'title': 'BOM 기반 자동 부품 발주',
            'file': 'WorkOrderService.java',
            'color': CODE_ORG,
            'desc': '작업지시 시 BOM 조회 → 재고 부족 부품 자동 감지 → 발주서 자동 생성. 부품 원가 변경 시 완제품 원가 BOM 기반 자동 재계산.',
            'code': [
                ('// 재고 부족 부품 자동 발주', TEXT_DARK),
                ('List<BomItem> shortages =', CODE_BLUE),
                ('  bomService.checkShortages(workOrderId);', CODE_BLUE),
                ('for (BomItem item : shortages) {', CODE_PUR),
                ('  purchaseOrderService.autoCreate(item);', CODE_GREEN),
                ('}  // 발주서 자동 생성', TEXT_DARK),
            ],
        },
        {
            'title': '재무 분석 · Python Excel 리포트',
            'file': 'FinancialController.java',
            'color': HexColor('#34d399'),
            'desc': '매출/비용 데이터 기반 손익계산서 자동 산출. Python 스크립트 연동으로 xlsx 리포트 생성 및 다운로드.',
            'code': [
                ('// 영업이익률 자동 계산', TEXT_DARK),
                ('BigDecimal opMargin = opProfit', CODE_BLUE),
                ('  .divide(revenue, 4, HALF_UP)', CODE_BLUE),
                ('  .multiply(BigDecimal.valueOf(100));', CODE_BLUE),
                ('// Python → xlsx 리포트 반환', TEXT_DARK),
                ('byte[] xlsx = runPythonClean(csvBytes);', CODE_GREEN),
            ],
        },
        {
            'title': 'Spring Security 역할 기반 인증',
            'file': 'SecurityConfig.java',
            'color': ACCENT_VL,
            'desc': 'BCrypt 해싱, 폼 로그인, ADMIN/USER 역할 분리. /admin/** 경로는 ADMIN만 접근. JSP Forward/Include 요청 허용 처리.',
            'code': [
                ('// 역할 기반 접근 제어', TEXT_DARK),
                ('.requestMatchers("/admin/**")', CODE_PUR),
                ('  .hasRole("ADMIN")', CODE_ORG),
                ('.anyRequest().authenticated()', CODE_GREEN),
                ('// BCrypt 패스워드 인코더', TEXT_DARK),
                ('return new BCryptPasswordEncoder();', CODE_BLUE),
            ],
        },
    ]
    cw = (W - 80 - 16) / 2
    ch = 172
    positions = [
        (40, H - 143), (40 + cw + 16, H - 143),
        (40, H - 143 - ch - 14), (40 + cw + 16, H - 143 - ch - 14),
    ]
    for cell, (cx2, cy_top) in zip(cells, positions):
        cy2 = cy_top - ch
        card_rect(c, cx2, cy2, cw, ch)
        left_accent_line(c, cx2 + 7, cy2 + 8, ch - 16, color=cell['color'])
        c.setFont('MGBold', 10)
        c.setFillColor(cell['color'])
        c.drawString(cx2 + 17, cy_top - 18, cell['title'])
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(cx2 + 17, cy_top - 30, cell['file'])
        desc_y = cy_top - 44
        for chunk in [cell['desc'][i:i+40] for i in range(0, min(len(cell['desc']), 120), 40)]:
            c.setFont('MG', 8)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx2 + 17, desc_y, chunk)
            desc_y -= 11
        code_top = cy2 + 76
        terminal_header(c, cx2 + 17, code_top, cw - 26)
        card_rect(c, cx2 + 17, code_top - 68, cw - 26, 70, fill=CARD_DARK, stroke=BORDER, lw=0.5, radius=0)
        cl2 = code_top - 10
        for line, col2 in cell['code']:
            c.setFont('MG', 7.5)
            c.setFillColor(col2)
            c.drawString(cx2 + 22, cl2, line)
            cl2 -= 10

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 기술적 어필 & 회고
# ══════════════════════════════════════════════════════════════
def page_erp_review(c, page_num):
    full_bg(c)
    badge(c, 40, H - 70, '14')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '기술적 어필 & 회고')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, '개발환기좀해 ERP — 1인 풀스택 완성 성과')

    # 수치
    metrics = [('15개+', '모듈 구현'), ('100%', '1인 완성'), ('OCR', 'AI 연동'), ('트랜잭션', '원자성 보장')]
    m_y = H - 168
    m_w = (W - 80 - 30) / 4
    for i, (val, lbl) in enumerate(metrics):
        mx2 = 40 + i * (m_w + 10)
        card_rect(c, mx2, m_y, m_w - 4, 46)
        c.setFont('MGBold', 16)
        c.setFillColor(ERP_ACCENT)
        c.drawCentredString(mx2 + (m_w-4)/2, m_y + 26, val)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawCentredString(mx2 + (m_w-4)/2, m_y + 12, lbl)

    # 기술 어필 + 아쉬운점 (2열)
    tw4 = (W - 80 - 16) / 2
    th4 = 190
    card_rect(c, 40, m_y - th4 - 20, tw4, th4)
    left_accent_line(c, 48, m_y - th4 - 10, th4 - 20, color=ERP_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(ERP_ACCENT)
    c.drawString(58, m_y - 38, '✦ 기술적 어필 포인트')
    pts = [
        'OCR + AI API (Gemini/Groq) 연동 거래명세서 자동 등록',
        'BOM 기반 재고 부족 자동 감지 → 발주서 즉시 생성',
        '입고/출고/생산입고 @Transactional 원자성 처리',
        'Spring Security 역할 기반 접근제어 + BCrypt',
        'Python 연동 재무 Excel 리포트 (csv → xlsx 변환)',
        '사이드바 아코디언 UI + 현재 메뉴 자동 펼침',
    ]
    py = m_y - 56
    for p in pts:
        used = bullet_item(c, 58, py, p, max_w=tw4 - 30, bullet_color=ERP_ACCENT, size=8.5)
        py -= used + 3

    card_rect(c, 40 + tw4 + 16, m_y - th4 - 20, tw4, th4)
    left_accent_line(c, 40 + tw4 + 24, m_y - th4 - 10, th4 - 20, color=ACCENT_O)
    c.setFont('MGBold', 11)
    c.setFillColor(ACCENT_O)
    c.drawString(40 + tw4 + 34, m_y - 38, '△ 아쉬운 점 / 개선 방향')
    bads = [
        'JSP + JSTL 한계 → 다음엔 React 프론트 분리 목표',
        'OCR 예외 포맷(누락 · 오타) 처리 로직 보완 필요',
        '테스트 코드 없음 → JUnit + MockMvc 도입 계획',
        '실시간 알림(WebSocket) 추후 적용 예정',
    ]
    by2 = m_y - 56
    for b in bads:
        used = bullet_item(c, 40 + tw4 + 34, by2, b, max_w=tw4 - 30, bullet_color=ACCENT_O, size=8.5)
        by2 -= used + 3

    # 회고
    ry = m_y - th4 - 50
    rh = 158
    card_rect(c, 40, ry - rh, W - 80, rh)
    left_accent_line(c, 48, ry - rh + 10, rh - 20, color=ERP_ACCENT)
    c.setFont('MGBold', 11)
    c.setFillColor(ERP_ACCENT)
    c.drawString(58, ry - 20, '💬 회고 — 개발환기좀해 ERP')
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(58, ry - 28, W - 50, ry - 28)
    story = [
        '제조업 ERP 전 모듈을 1인으로 처음부터 끝까지 구현하면서, 단순한 CRUD를 넘어 실제 업무 프로세스를 코드로',
        '표현하는 경험을 했습니다. BOM 기반 자동 발주, OCR AI 연동, Python 재무 리포트 등 서로 다른 기술 스택을',
        '하나의 시스템으로 통합하는 과정에서 Spring Boot의 계층 구조(Controller-Service-Mapper)와 트랜잭션 관리의',
        '중요성을 몸소 익혔습니다. JSP의 한계를 느끼면서 React 분리의 필요성도 깨달았고, 다음 프로젝트에서는',
        '프론트엔드를 완전히 분리한 REST API 기반 아키텍처를 목표로 합니다.',
    ]
    sy2 = ry - 44
    for line in story:
        c.setFont('MG', 9)
        c.setFillColor(TEXT_PRI)
        c.drawString(58, sy2, line)
        sy2 -= 14

    draw_footer(c, 'Developer Portfolio', '개발환기좀해 ERP — Project 04', page_num)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# PROJECT 04 — 성능 최적화 (p19)
# ══════════════════════════════════════════════════════════════
def page_erp_performance(c, page_num):
    full_bg(c)
    badge(c, 40, H - 70, '13')
    c.setFont('MGBold', 22)
    c.setFillColor(TEXT_PRI)
    c.drawString(40, H - 100, '성능 최적화 · DB 쿼리 튜닝')
    c.setFont('MG', 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(40, H - 116, '발주 · 입고 페이지 로딩 14.25초 → 0.17초 (83배 개선)')

    # ── 임팩트 수치 배너 ────────────────────────────────────────
    banner_y = H - 158
    card_rect(c, 40, banner_y, W - 80, 52, fill=HexColor('#0d1f0d'), stroke=ACCENT_G, lw=1.5)
    left_accent_line(c, 40, banner_y, 52, color=ACCENT_G, lw=4)

    # BEFORE
    c.setFont('MGBold', 9)
    c.setFillColor(TEXT_DARK)
    c.drawString(70, banner_y + 36, 'BEFORE')
    c.setFont('MGBold', 26)
    c.setFillColor(HexColor('#f87171'))
    c.drawString(70, banner_y + 12, '14.25 s')

    # 화살표
    arr_x = W/2 - 20
    c.setFont('MGBold', 28)
    c.setFillColor(ACCENT_G)
    c.drawCentredString(arr_x, banner_y + 16, '→')

    c.setFont('MGBold', 9)
    c.setFillColor(TEXT_DARK)
    c.drawString(arr_x + 32, banner_y + 36, 'AFTER')
    c.setFont('MGBold', 26)
    c.setFillColor(ACCENT_G)
    c.drawString(arr_x + 32, banner_y + 12, '0.17 s  (176 ms)')

    # 배율 뱃지
    c.setFillColor(ACCENT_G)
    c.roundRect(W - 120, banner_y + 12, 70, 26, 4, fill=1, stroke=0)
    c.setFont('MGBold', 14)
    c.setFillColor(HexColor('#0d1f0d'))
    c.drawCentredString(W - 85, banner_y + 20, '83x 향상')

    # ── 문제 ① N+1 ──────────────────────────────────────────────
    sec_y = banner_y - 28
    half_w = (W - 80 - 16) / 2

    def perf_card(cx, cy, title, accent_col, before_lines, after_lines, card_h=248):
        card_rect(c, cx, cy - card_h, half_w, card_h)
        left_accent_line(c, cx + 7, cy - card_h + 10, card_h - 20, color=accent_col)

        c.setFont('MGBold', 10.5)
        c.setFillColor(accent_col)
        c.drawString(cx + 17, cy - 18, title)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(cx + 17, cy - 26, cx + half_w - 10, cy - 26)

        # BEFORE 블록
        before_h = len(before_lines) * 11 + 22
        bby = cy - 44
        card_rect(c, cx + 17, bby - before_h, half_w - 28, before_h + 4,
                  fill=HexColor('#200d0d'), stroke=HexColor('#f87171'), lw=0.7)
        c.setFont('MGBold', 7.5)
        c.setFillColor(HexColor('#f87171'))
        c.drawString(cx + 24, bby - 10, 'BEFORE')
        ly = bby - 22
        for line in before_lines:
            c.setFont('MG', 7.5)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx + 24, ly, line)
            ly -= 11

        # AFTER 블록
        after_h = len(after_lines) * 11 + 22
        aby = bby - before_h - 12
        card_rect(c, cx + 17, aby - after_h, half_w - 28, after_h + 4,
                  fill=HexColor('#0d1f0d'), stroke=ACCENT_G, lw=0.7)
        c.setFont('MGBold', 7.5)
        c.setFillColor(ACCENT_G)
        c.drawString(cx + 24, aby - 10, 'AFTER')
        ly2 = aby - 22
        for line in after_lines:
            c.setFont('MG', 7.5)
            c.setFillColor(TEXT_SEC)
            c.drawString(cx + 24, ly2, line)
            ly2 -= 11

    perf_card(
        40, sec_y,
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
        40 + half_w + 16, sec_y,
        '② JOIN 조건 · 인덱스 최적화',
        CODE_BLUE,
        before_lines=[
            'LIKE 연산자로 customer_name 매칭',
            '→ 인덱스 무효화, 풀 스캔 발생',
            'JOIN suppliers s',
            '  ON o.supplier_info',
            '     LIKE CONCAT(\'%\',s.name,\'%\')',
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
    lesson_y = sec_y - 270
    card_rect(c, 40, lesson_y - 50, W - 80, 55)
    left_accent_line(c, 48, lesson_y - 42, 38, color=CODE_BLUE)
    c.setFont('MGBold', 10)
    c.setFillColor(CODE_BLUE)
    c.drawString(58, lesson_y - 14, '배운 점')
    c.setFont('MG', 9)
    c.setFillColor(TEXT_PRI)
    c.drawString(58, lesson_y - 28, (
        '"기능 구현"에서 끝나지 않고 실제 사용 환경에서 병목을 직접 발견하고 쿼리 구조를 재설계하여 83배의 성능 향상을 달성했습니다.'
    ))
    c.setFont('MG', 9)
    c.setFillColor(TEXT_SEC)
    c.drawString(58, lesson_y - 42, 'N+1 문제와 인덱스 활용의 중요성을 실무 수준으로 체득한 경험입니다.')

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
    c.drawCentredString(W/2, H*0.69, 'AuRa')

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
    c.drawCentredString(W/2, H*0.69, 'KISETSU')

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
    """커버 + 목차 + 기존 p3~10 + FIRST 3p + Solo 3p + RPA 5p + ERP 5p = 26페이지"""
    import fitz as _fitz, os

    tmp_front = out_path.replace('.pdf', '_front_tmp.pdf')
    tmp_rpa   = out_path.replace('.pdf', '_rpa_tmp.pdf')
    tmp_erp   = out_path.replace('.pdf', '_erp_tmp.pdf')
    tmp_first = out_path.replace('.pdf', '_first_tmp.pdf')
    tmp_solo  = out_path.replace('.pdf', '_solo_tmp.pdf')

    # ① 커버 + 목차
    c1 = canvas.Canvas(tmp_front, pagesize=A4)
    page_main_cover(c1)
    page_toc(c1)
    c1.save()

    # ② FIRST 팀 쇼핑몰 = AuRa 새 내용 (p7~9)
    c4 = canvas.Canvas(tmp_first, pagesize=A4)
    page_first_cover_overview(c4, 7)
    page_first_struggle(c4, 8)
    page_first_review(c4, 9)
    c4.save()

    # ③ Solo 계절 = KISETSU 새 내용 (p14~16)
    c5 = canvas.Canvas(tmp_solo, pagesize=A4)
    page_solo_cover_overview(c5, 14)
    page_solo_struggle(c5, 15)
    page_solo_review(c5, 16)
    c5.save()

    # ④ RPA 파트 (p17~21)
    c2 = canvas.Canvas(tmp_rpa, pagesize=A4)
    page_cover(c2, 17);       page_overview(c2, 18)
    page_role_detail(c2, 19); page_rpa_impl(c2, 20); page_result(c2, 21)
    c2.save()

    # ⑤ ERP 파트 (p22~26)
    c3 = canvas.Canvas(tmp_erp, pagesize=A4)
    page_erp_cover(c3, 22);       page_erp_overview(c3, 23)
    page_erp_features(c3, 24);    page_erp_performance(c3, 25)
    page_erp_review(c3, 26)
    c3.save()

    # ⑥ 합치기
    _orig_path = 'C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오.pdf'
    orig_aura   = _fitz.open(_orig_path)   # AuRa 삽입용
    orig_kisetsu = _fitz.open(_orig_path)  # KISETSU 삽입용 (리소스 분리)
    front = _fitz.open(tmp_front)
    rpa   = _fitz.open(tmp_rpa)
    erp   = _fitz.open(tmp_erp)
    first = _fitz.open(tmp_first)
    solo  = _fitz.open(tmp_solo)

    out = _fitz.open()
    out.insert_pdf(front)                                   # p1~2
    out.insert_pdf(orig_aura,   from_page=2, to_page=5)    # AuRa 원본 p3~6
    out.insert_pdf(first)                                   # AuRa 새 내용 p7~9
    out.insert_pdf(orig_kisetsu, from_page=6, to_page=9)   # KISETSU 원본 p10~13
    out.insert_pdf(solo)                                    # KISETSU 새 내용 p14~16
    out.insert_pdf(rpa)                                     # p17~21
    out.insert_pdf(erp)                                     # p22~26
    page_count = len(out)
    out.save(out_path, garbage=4, deflate=True)

    for f in [front, rpa, erp, first, solo, orig_aura, orig_kisetsu, out]: f.close()
    for t in [tmp_front, tmp_rpa, tmp_erp, tmp_first, tmp_solo]: os.remove(t)

    print(f'Done: {page_count} pages -> {out_path}')


if __name__ == '__main__':
    build_full_portfolio(
        'C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오_최종.pdf'
    )
