import streamlit as st
from datetime import date
import calendar
import json
import os

# ======================================
# ページ設定
# ======================================
st.set_page_config(
    page_title="出席率カレンダー",
    layout="wide"
)

# ======================================
# CSS
# ======================================
st.markdown("""
<style>

/* 全体 */
.stApp {
    background-color: #0d1117;
    color: white;
}

/* 上余白調整 */
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 1rem;
}

/* タイトル */
.main-title {
    font-size: clamp(28px, 5vw, 48px);
    font-weight: bold;
    color: #00ff88;
    margin-bottom: 10px;
    word-break: break-word;
}

/* 情報ボックス */
.info-box {
    background-color: #161b22;
    border: 2px solid #00ff88;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 30px;
}

/* 月 */
.month-box {
    background-color: #161b22;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 30px;
    border: 1px solid #00ff88;
}

/* 日付カード */
.day-card {
    background-color: #0f141b;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    text-align: center;
    border: 1px solid #333;
}

/* 日付 */
.day-number {
    color: #00ff88;
    font-size: 24px;
    font-weight: bold;
}

/* 曜日 */
.weekday {
    text-align: center;
    color: #00ff88;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}

/* ボタン */
.stButton button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #00ff88;
    background-color: #111;
    color: white;
    margin-bottom: 5px;
}

/* ボタン hover */
.stButton button:hover {
    border: 1px solid #00ff88;
    color: #00ff88;
}

/* スクロールバー */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #00ff88;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ======================================
# 保存ファイル
# ======================================
SAVE_FILE = "attendance_data.json"

# ======================================
# データ読み込み
# ======================================
def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# ======================================
# データ保存
# ======================================
def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======================================
# 初期化
# ======================================
if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = load_data()

attendance_data = st.session_state.attendance_data

# ======================================
# 期間設定
# ======================================
today = date.today()

if today.month >= 4:
    start_date = date(today.year, 4, 1)
    end_date = date(today.year + 1, 4, 1)
else:
    start_date = date(today.year - 1, 4, 1)
    end_date = date(today.year, 4, 1)

# ======================================
# タイトル
# ======================================
st.markdown(
    '<div class="main-title">出席率管理カレンダー</div>',
    unsafe_allow_html=True
)

# ======================================
# 出席率計算
# ======================================
attended = sum(
    1 for v in attendance_data.values()
    if v == "出席"
)

absent = sum(
    1 for v in attendance_data.values()
    if v == "欠席"
)

total = attended + absent

rate = 0 if total == 0 else (attended / total) * 100

# ======================================
# 情報表示
# ======================================
st.markdown('<div class="info-box">', unsafe_allow_html=True)

st.markdown(
    f"""
    <h1 style="color:#00ff88;">
    出席率: {rate:.2f}%
    </h1>

    <h3>
    🟩 出席: {attended}日　
    🟥 欠席: {absent}日　
    📅 合計: {total}日
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# 状態変更
# ======================================
def set_status(date_str, status):

    if status == "未選択":
        if date_str in attendance_data:
            del attendance_data[date_str]
    else:
        attendance_data[date_str] = status

    save_data(attendance_data)

# ======================================
# カレンダー
# ======================================
current = start_date

while current <= end_date:

    year = current.year
    month = current.month

    st.markdown(
        f"""
        <div class="month-box">
        <h2 style="color:#00ff88;">
        {year}年 {month}月
        </h2>
        """,
        unsafe_allow_html=True
    )

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    header_cols = st.columns(7)

    for i, w in enumerate(weekdays):
        with header_cols[i]:
            st.markdown(
                f'<div class="weekday">{w}</div>',
                unsafe_allow_html=True
            )

    cal = calendar.Calendar(firstweekday=0)

    for week in cal.monthdayscalendar(year, month):

        cols = st.columns(7)

        for i, day in enumerate(week):

            if day == 0:
                cols[i].write("")
                continue

            current_date = date(year, month, day)

            if current_date < start_date or current_date > end_date:
                cols[i].write("")
                continue

            date_str = current_date.isoformat()

            status = attendance_data.get(
                date_str,
                "未選択"
            )

            # 状態表示
            if status == "出席":
                status_text = "🟩 出席"
            elif status == "欠席":
                status_text = "🟥 欠席"
            else:
                status_text = "⬜ 未選択"

            with cols[i]:

                st.markdown(
                    f"""
                    <div class="day-card">
                    <div class="day-number">{day}</div>
                    <div>{status_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 出席
                if st.button(
                    "出席",
                    key=f"attend_{date_str}"
                ):
                    set_status(date_str, "出席")
                    st.rerun()

                # 欠席
                if st.button(
                    "欠席",
                    key=f"absent_{date_str}"
                ):
                    set_status(date_str, "欠席")
                    st.rerun()

                # リセット
                if st.button(
                    "リセット",
                    key=f"reset_{date_str}"
                ):
                    set_status(date_str, "未選択")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 次の月
    if month == 12:
        current = date(year + 1, 1, 1)
    else:
        current = date(year, month + 1, 1)
