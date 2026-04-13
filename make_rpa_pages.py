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
    col_h = 290
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
    card_h = 340
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
    c.drawCentredString(W/2, H*0.67, '네 개의 프로젝트를 통한 성장 기록')

    # 4개 프로젝트 박스 (2x2 그리드)
    projects = [
        ('PROJECT 01', 'AuRa', '향수 이커머스', '4인 팀 · 3주',
         HexColor('#6266f1'), HexColor('#1a1f4e')),
        ('PROJECT 02', 'KISETSU', '도매 패션 이커머스', '1인 솔로 · 2주',
         HexColor('#0fb981'), HexColor('#0d2b22')),
        ('PROJECT 03', '재무제표 자동화', 'Python + BrityRPA', '3인 팀 · 2주',
         HexColor('#f59d0a'), HexColor('#2b1e0a')),
        ('PROJECT 04', '개발환기좀해 ERP', 'Spring Boot + JSP', '1인 솔로 · 5주',
         HexColor('#e05c8a'), HexColor('#2b0d18')),
    ]
    box_w = 118
    box_h = 72
    gap = 10
    total_w = 2 * box_w + gap
    bx_start = W/2 - total_w/2
    row1_y = H * 0.59
    row2_y = row1_y - box_h - gap

    for i, (proj_lbl, title, sub, meta, accent, bg_col) in enumerate(projects):
        col = i % 2
        row = i // 2
        bx = bx_start + col * (box_w + gap)
        by = row1_y - row * (box_h + gap)
        c.setFillColor(bg_col)
        c.setStrokeColor(accent)
        c.setLineWidth(0.8)
        c.roundRect(bx, by, box_w, box_h, 5, fill=1, stroke=1)
        c.setFont('MGBold', 7)
        c.setFillColor(accent)
        c.drawString(bx + 9, by + box_h - 14, proj_lbl)
        c.setFont('MGBold', 11.5)
        c.setFillColor(TEXT_PRI)
        c.drawString(bx + 9, by + box_h - 28, title)
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawString(bx + 9, by + box_h - 42, sub)
        c.setFont('MG', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(bx + 9, by + 10, meta)

    # 기술 스택 태그
    all_tags = ['React', 'Node.js', 'Spring Boot', 'MariaDB', 'JWT',
                'MyBatis', 'JSP', 'Python', 'BrityRPA', 'Spring Security']
    tag_total = sum(c.stringWidth(t, 'MG', 7) + 16 for t in all_tags) + (len(all_tags)-1)*4
    tx = W/2 - tag_total/2
    ty = row2_y - 28
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
    c.drawCentredString(W/2, ty - 18, '2025 — 2026')

    c.showPage()


# ══════════════════════════════════════════════════════════════
# 업데이트 목차 (두 번째 페이지) — PROJECT 03 추가
# ══════════════════════════════════════════════════════════════
def page_toc(c):
    """통합 포트폴리오 목차 — PROJECT 03 포함"""
    full_bg(c)

    # INDEX 배지 + 목차 타이틀
    badge(c, 40, H - 62, 'INDEX', color=ACCENT_G, font_size=8, pad_x=8, pad_h=16)
    c.setFont('MGBold', 24)
    c.setFillColor(TEXT_PRI)
    c.drawString(106, H - 65, '목차')

    # 구분선
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(40, H - 76, W - 40, H - 76)

    def section_header(label, y):
        """▌PROJECT 0X — 프로젝트명 헤더"""
        c.setFillColor(ACCENT_V)
        c.rect(40, y - 1, 3, 13, fill=1, stroke=0)
        c.setFont('MGBold', 9)
        c.setFillColor(ACCENT_VL)
        c.drawString(50, y, label)

    def toc_item(num, title, subtitle, page_n, y, accent_col=ACCENT_V):
        """목차 항목 카드"""
        card_rect(c, 40, y - 30, W - 80, 36)
        # 번호 배지
        badge(c, 50, y - 21, f'{num:02d}', color=accent_col,
              font_size=8, pad_x=6, pad_h=14)
        # 제목
        c.setFont('MGBold', 10)
        c.setFillColor(TEXT_PRI)
        c.drawString(86, y - 11, title)
        # 서브타이틀
        c.setFont('MG', 8)
        c.setFillColor(TEXT_SEC)
        c.drawString(86, y - 23, subtitle)
        # 페이지 번호
        c.setFont('MG', 9)
        c.setFillColor(TEXT_DARK)
        c.drawRightString(W - 50, y - 16, f'{page_n:02d}')

    # ─ PROJECT 01
    y = H - 100
    section_header('PROJECT 01 — AURA 향수 쇼핑몰', y)
    y -= 20
    toc_item(1, '프로젝트 개요', 'AuRa 소개, 기술 스택, 팀 구성', 3,  y)
    y -= 46
    toc_item(2, '주요 기여 — DB 설계 · 인증 · 장바구니 · 카테고리',
             '담당 기능 상세, 코드 구현 방식', 4, y)
    y -= 46
    toc_item(3, '기술적 어필 포인트', '관심사 분리, 중복 방지 로직, 서버단 검증', 5, y)
    y -= 56

    # ─ PROJECT 02
    section_header('PROJECT 02 — KISETSU 도매 패션 이커머스', y)
    y -= 20
    toc_item(4, '프로젝트 개요 · 아키텍처', '기획 배경, 시스템 구조, 기술 스택', 7,
             y, accent_col=ACCENT_G)
    y -= 46
    toc_item(5, '주요 기능 구현',
             'JWT 인증, 실시간 채팅, 전역 상태, 인기검색어', 9,
             y, accent_col=ACCENT_G)
    y -= 46
    toc_item(6, '결과 · 회고', '구현 성과, 배운 점, 성장 스토리', 10,
             y, accent_col=ACCENT_G)
    y -= 56

    # ─ PROJECT 03 (신규)
    section_header('PROJECT 03 — 재무제표 자동화 (Python + BrityRPA)', y)
    y -= 20
    toc_item(7, '프로젝트 개요',
             '기획 배경, 시스템 아키텍처, 담당 역할', 12,
             y, accent_col=ACCENT_O)
    y -= 46
    toc_item(8, '담당 역할 — RPA 자동화 파이프라인',
             '아키텍처 설계, RPA 구현, 데이터 검증 & 관리', 13,
             y, accent_col=ACCENT_O)
    y -= 46
    toc_item(9, '핵심 기능 구현',
             'Python 실행 자동화, Excel 차트, 메일 발송', 14,
             y, accent_col=ACCENT_O)
    y -= 46
    toc_item(10, '결과 · 회고',
             'RPA 성과, 잘된 점, 아쉬운 점, 자체 평가', 15,
             y, accent_col=ACCENT_O)

    draw_footer(c, 'Developer Portfolio', '', 2)
    c.showPage()


# ══════════════════════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════════════════════
def build_full_portfolio(out_path):
    """커버 + 목차 + 기존 본문(p3~p10) + RPA 파트(5페이지) 합치기"""
    import fitz as _fitz

    # ① 커버 + 목차 PDF 생성 (임시)
    tmp_front = out_path.replace('.pdf', '_front_tmp.pdf')
    tmp_rpa   = out_path.replace('.pdf', '_rpa_tmp.pdf')

    c1 = canvas.Canvas(tmp_front, pagesize=A4)
    page_main_cover(c1)
    page_toc(c1)
    c1.save()

    # ② RPA 파트 5페이지 생성 (임시)
    c2 = canvas.Canvas(tmp_rpa, pagesize=A4)
    start_page = 11
    page_cover(c2, start_page)
    page_overview(c2, start_page + 1)
    page_role_detail(c2, start_page + 2)
    page_rpa_impl(c2, start_page + 3)
    page_result(c2, start_page + 4)
    c2.save()

    # ③ 합치기: 새 커버/목차(2) + 기존 p3~p10(8) + RPA(5) = 15페이지
    orig  = _fitz.open('C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오.pdf')
    front = _fitz.open(tmp_front)
    rpa   = _fitz.open(tmp_rpa)

    out = _fitz.open()
    out.insert_pdf(front)                        # p1~2: 새 커버/목차
    out.insert_pdf(orig, from_page=2, to_page=9) # p3~10: 기존 본문
    out.insert_pdf(rpa)                          # p11~15: RPA 파트
    page_count = len(out)
    out.save(out_path)

    # 임시 파일 삭제 (fitz 핸들 닫고 삭제)
    import os
    front.close()
    rpa.close()
    orig.close()
    out.close()
    os.remove(tmp_front)
    os.remove(tmp_rpa)

    print(f'Done: {page_count} pages saved to {out_path}')


if __name__ == '__main__':
    build_full_portfolio(
        'C:/Users/3class_013/Desktop/포트폴리오 수정폴더/통합_포트폴리오_최종.pdf'
    )
