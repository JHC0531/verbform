"""공유 유틸 함수: 데이터 로딩, 스타일, 너구리 메시지, 수료증 생성"""

import io
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "불규칙동사_레벨분류완성.xlsx"
RULES_CSV_PATH = BASE_DIR / "data" / "중1_과거형_퀴즈_매력적오답.csv"
CERT_CSV_PATH = BASE_DIR / "data" / "과거형_3단변화_30문항_이미지포함.csv"
IMAGES_DIR = BASE_DIR / "data" / "images"
AUDIO_DIR = BASE_DIR / "data" / "audio"
MASCOT_PATH = BASE_DIR / "assets" / "너구리.png"
FONT_REGULAR = BASE_DIR / "assets" / "fonts" / "NanumGothic-Regular.ttf"
FONT_BOLD = BASE_DIR / "assets" / "fonts" / "NanumGothic-Bold.ttf"

LEVEL_LABELS = {
    "Easy": "⭐ Easy",
    "Average": "⭐⭐ Average",
    "Difficult": "⭐⭐⭐ Hard",
}

RACCOON_MESSAGES = {
    "start": [
        "어서와! 동사 연습 시작해볼까? 🦝",
        "자, 카드를 골라서 빈 칸을 채워봐! 🦝",
        "집중집중! 할 수 있어! 🦝",
    ],
    "correct": [
        "정답! 역시 천재! 🎉",
        "완벽해! 🦝✨",
        "맞았어! 대단해! 🎊",
        "Good job! 계속 가자! 🚀",
    ],
    "wrong": [
        "아이쿠, 틀렸어. 다시 봐봐! 🦝",
        "괜찮아, 다음엔 기억할 거야! 💪",
        "아깝다! 정답은 잘 봐둬! 🔍",
    ],
    "end": [
        "완주했어! 진짜 대단해! 🏆",
        "모든 문제 끝냈어! 🎉",
        "동사 마스터 등극! 🦝👑",
    ],
}


@st.cache_data
def load_verbs() -> pd.DataFrame:
    """엑셀 파일을 읽어서 정제된 DataFrame으로 반환"""
    df = pd.read_excel(DATA_PATH)
    df = df.rename(columns={
        "유형": "type",
        "동사원형": "base",
        "과거형": "past",
        "과거분사형": "pp",
        "한글 뜻(핵심어 중심)": "meaning",
        "레벨": "level",
    })
    df = df.fillna("-")
    for col in ["type", "base", "past", "pp", "meaning", "level"]:
        df[col] = df[col].astype(str).str.strip()
    return df


@st.cache_data
def get_irregular_verbs() -> pd.DataFrame:
    df = load_verbs()
    return df[~df["type"].isin(["Regular (-ed)", "special"])].reset_index(drop=True)


@st.cache_data
def load_rules_quiz() -> pd.DataFrame:
    """규칙변화 미니퀴즈 데이터 (규칙번호/동사원형/정답/오답1/오답2/예문)"""
    df = pd.read_csv(RULES_CSV_PATH)
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


@st.cache_data
def load_cert_quiz() -> pd.DataFrame:
    """학습인증 30문항 데이터"""
    df = pd.read_csv(CERT_CSV_PATH)
    # 음성파일이름은 NaN일 수 있으므로 별도 처리
    df["음성파일이름"] = df["음성파일이름"].fillna("").astype(str).str.strip()
    for col in ["유형", "질문", "A", "B", "C", "정답", "그림파일이름"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def random_message(category: str) -> str:
    return random.choice(RACCOON_MESSAGES[category])


def inject_global_css():
    st.markdown("""
    <style>
    :root {
        --green: #2d6a4f;
        --green-light: #52b788;
        --green-pale: #d8f3dc;
        --yellow: #f9c74f;
        --orange: #f8961e;
        --red: #e63946;
    }
    .stApp { background-color: #f1faee; }

    /* Title styling */
    h1, h2, h3 { color: var(--green); }

    /* Card-like containers */
    .vb-card {
        background: white;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.10);
        margin-bottom: 14px;
        border-top: 5px solid var(--green-light);
    }
    .vb-card h3 { font-size: 1.25rem; font-weight: 800; margin-bottom: 4px; }
    .vb-card .tag { font-size: 0.78rem; color: #6b7280; margin-bottom: 8px; }
    .vb-card .example {
        background: var(--green-pale);
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .vb-card .example b { color: var(--green); }

    .t-aaa { border-top-color: #6c757d; }
    .t-aab { border-top-color: #457b9d; }
    .t-aba { border-top-color: #9b5de5; }
    .t-abb { border-top-color: var(--orange); }
    .t-abc { border-top-color: var(--red); }

    /* Raccoon bubble */
    .raccoon-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
    .raccoon-bubble {
        background: white;
        border-radius: 14px 14px 14px 2px;
        padding: 10px 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.10);
        font-size: 1rem;
        font-weight: 600;
    }

    /* Verb display */
    .verb-display {
        background: white;
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.10);
        margin-bottom: 16px;
    }
    .verb-meaning { font-size: 0.9rem; color: #6b7280; margin-bottom: 6px; }
    .verb-base { font-size: 2.6rem; font-weight: 800; color: #1a1a2e; margin-bottom: 10px; }

    .slot-box {
        display: inline-block;
        background: var(--green-pale);
        border-radius: 12px;
        padding: 10px 24px;
        margin: 0 8px;
        min-width: 130px;
    }
    .slot-label { font-size: 0.75rem; color: #6b7280; font-weight: 600; margin-bottom: 4px; }
    .slot-answer { font-size: 1.2rem; font-weight: 700; color: var(--green); }
    .slot-answer.empty { color: #bbb; font-size: 1.6rem; }
    .slot-answer.wrong { color: var(--red); }

    /* rule examples */
    .rule-ex {
        display: inline-block;
        background: var(--green-pale);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--green);
        margin: 3px;
    }
    </style>
    """, unsafe_allow_html=True)


def make_certificate(name: str, score: int, total: int) -> bytes:
    """이름·점수·날짜가 들어간 수료증 PNG를 만들어 bytes로 반환"""
    W, H = 1000, 700
    bg = (241, 250, 238)       # cream
    green = (45, 106, 79)
    green_light = (82, 183, 136)
    gold = (249, 199, 79)
    dark = (26, 26, 46)
    gray = (107, 114, 128)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # 외곽 테두리 (이중)
    draw.rectangle([20, 20, W - 20, H - 20], outline=green, width=6)
    draw.rectangle([34, 34, W - 34, H - 34], outline=gold, width=3)

    def font(bold, size):
        path = str(FONT_BOLD if bold else FONT_REGULAR)
        return ImageFont.truetype(path, size)

    def center(text, y, fnt, fill):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        w = bbox[2] - bbox[0]
        draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)

    # 제목
    center("학 습 수 료 증", 80, font(True, 56), green)
    center("🦝 동사 변화 학습기 🦝", 165, font(True, 30), green_light)

    # 구분선
    draw.line([180, 230, W - 180, 230], fill=gold, width=3)

    # 본문
    center("위 학생은 영어 동사 변화 학습 과정을", 280, font(False, 28), dark)
    center("성실히 이수하였기에 이 증서를 수여합니다.", 320, font(False, 28), dark)

    # 이름 (강조)
    center(f"{name}", 400, font(True, 64), green)

    # 점수
    pct = round(score / total * 100) if total else 0
    center(f"점수:  {score} / {total}   ({pct}점)", 510, font(True, 38), dark)

    # 날짜
    today = datetime.now().strftime("%Y년 %m월 %d일")
    center(today, 580, font(False, 26), gray)

    # 너구리 마스코트 (오른쪽 하단)
    try:
        mascot = Image.open(MASCOT_PATH).convert("RGBA")
        mascot.thumbnail((120, 120))
        img.paste(mascot, (W - 200, H - 200), mascot)
    except Exception:
        pass

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
