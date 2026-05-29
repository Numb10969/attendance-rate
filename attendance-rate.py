import streamlit as st
from datetime import date
import calendar
import json
import os

# =========================
# 保存ファイル
# =========================
SAVE_FILE = "attendance_data.json"

# =========================
# データ読み込み
# =========================
def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# =========================
# データ保存
# =========================
def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================
# 初期化
# =========================
if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = load_data()

attendance_data = st.session_state.attendance_data

# =========================
# 期間設定
# =========================
today = date.today()

if today.month >= 4:
    start_date = date(today.year, 4, 1)
    end_date = date(today.year + 1, 4, 1)
else:
    start_date = date(today.year - 1, 4, 1)
    end_date = date(today.year, 4, 1)

# =========================
# タイトル
# =========================
st.title("出席率管理カレンダー")

st.write("出席率を自動計算します。")

# =========================
# 出席率計算
# =========================
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

# =========================
# 表示
# =========================
st.subheader(f"出席率: {rate:.2f}%")

col1, col2, col3 = st.columns(3)

col1.metric("出席", attended)
col2.metric("欠席", absent)
col3.metric("合計", total)

st.divider()

# =========================
# カレンダー
# =========================
current = start_date

while current <= end_date:

    year = current.year
    month = current.month

    st.header(f"{year}年 {month}月")

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    header_cols = st.columns(7)

    for i, day_name in enumerate(weekdays):
        header_cols[i].markdown(f"### {day_name}")

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

                st.write(f"### {day}")

                new_value = st.selectbox(
                    "",
                    ["未選択", "出席", "欠席"],
                    index=["未選択", "出席", "欠席"].index(current_value),
                    key=date_str
                )

                attendance_data[date_str] = new_value

    # 次の月
    if month == 12:
        current = date(year + 1, 1, 1)
    else:
        current = date(year, month + 1, 1)

# =========================
# 保存
# =========================
save_data(attendance_data)

st.success("保存済み")
