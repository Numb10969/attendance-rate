import streamlit as st
from datetime import date
import calendar
import json
import os

# =====================================
# ページ設定
# =====================================
st.set_page_config(
    page_title="出席率カレンダー",
    layout="wide"
)

# =====================================
# CSS
# =====================================
st.markdown("""
<style>

.stApp {
    background-color: #0f1117;
    color: white;
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #00ff88;
    margin-bottom: 10px;
}

.rate-box {
    background-color: #1a1d26;
    border: 2px solid #00ff88;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 25px;
}

.month-box {
    background-color: #1a1d26;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 30px;
    border: 1px solid #2dff9f;
}

.day-card {
    background-color: #161922;
    padding: 8px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 8px;
    border: 1px solid #333;
}

.day-number {
    color: #00ff88;
    font-weight: bold;
    font-size: 20px;
}

.week-label {
    text-align: center;
    color: #00ff88;
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 10px;
}

.small-text {
    color: #cccccc;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# 保存ファイル
# =====================================
SAVE_FILE = "attendance_data.json"

# =====================================
# データ読み込み
# =====================================
def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# =====================================
# データ保存
# =====================================
def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =====================================
# セッション初期化
# =====================================
if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = load_data()

attendance_data = st.session_state.attendance_data

# =====================================
# 期間設定
# =====================================
today = date.today()

if today.month >= 4:
    start_date = date(today.year, 4, 1)
    end_date = date(today.year + 1, 4, 1)
else:
    start_date = date(today.year - 1, 4, 1)
    end_date = date(today.year, 4, 1)

# =====================================
# タイトル
# =====================================
st.markdown(
    '<div class="main-title">出席率管理カレンダー</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="small-text">
🟩 出席 / 🟥 欠席 / ⬜ 未選択
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================================
# 出席率計算
# =====================================
attended = sum(
    1 for v in attendance_data.values()
    if v == "出席"
)

absent = sum(
    1 for v in attendance_data.values()
    if v == "欠席"
)

total = attended + absent

if total == 0:
    rate = 0
else:
    rate = (attended / total) * 100

# =====================================
# ステータス表示
# =====================================
st.markdown('<div class="rate-box">', unsafe_allow_html=True)

st.markdown(
    f"""
    <h1 style="color:#00ff88;">
        出席率: {rate:.2f}%
    </h1>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🟩 出席", attended)

with col2:
    st.metric("🟥 欠席", absent)

with col3:
    st.metric("📅 合計", total)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================
# 月ごと表示
# =====================================
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

    for i, day_name in enumerate(weekdays):
        with header_cols[i]:
            st.markdown(
                f'<div class="week-label">{day_name}</div>',
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

            current_value = attendance_data.get(
                date_str,
                "未選択"
            )

            with cols[i]:

                st.markdown(
                    f"""
                    <div class="day-card">
                    <div class="day-number">{day}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ← バグ修正
                # selectbox の値を直接保存する
                selected = st.radio(
                    label="",
                    options=["未選択", "出席", "欠席"],
                    index=["未選択", "出席", "欠席"].index(current_value),
                    key=f"radio_{date_str}",
                    horizontal=False
                )

                attendance_data[date_str] = selected

    st.markdown("</div>", unsafe_allow_html=True)

    # 次の月へ
    if month == 12:
        current = date(year + 1, 1, 1)
    else:
        current = date(year, month + 1, 1)

# =====================================
# 保存
# =====================================
save_data(attendance_data)

st.success("データは自動保存されています")
