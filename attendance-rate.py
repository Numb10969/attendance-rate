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

/* 余白 */
.block-container {
    padding-top: clamp(1rem, 5vw, 4rem);
    padding-bottom: 2rem;
}

/* タイトル */
.main-title {
    font-size: clamp(28px, 5vw, 48px);
    font-weight: bold;
    color: #00ff88;
    margin-bottom: 15px;
}

/* 情報ボックス */
.info-box {
    background-color: #161b22;
    border: 2px solid #00ff88;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 25px;
}

/* 月ボックス */
.month-box {
    background-color: #161b22;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #00ff88;
}

/* 曜日 */
.weekday {
    text-align: center;
    color: #00ff88;
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 8px;
}

/* 日付ボタン */
.stButton button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #333;
    background-color: #111;
    color: white;
    min-height: 60px;
    font-size: 14px;
}

/* hover */
.stButton button:hover {
    border: 1px solid #00ff88;
    color: #00ff88;
}

/* モーダル風 */
.popup-box {
    background-color: #161b22;
    border: 2px solid #00ff88;
    border-radius: 15px;
    padding: 25px;
    margin-top: 25px;
}

/* スマホ */
@media (max-width: 768px) {

    .weekday {
        font-size: 11px;
    }

    .stButton button {
        min-height: 50px;
        font-size: 11px;
        padding: 0.3rem;
    }

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

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

# ======================================
# 初期化
# ======================================
if "attendance_data" not in st.session_state:

    st.session_state.attendance_data = load_data()

attendance_data = st.session_state.attendance_data

# ======================================
# 選択日
# ======================================
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

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
    """
    <div class="main-title">
    出席率管理カレンダー
    </div>
    """,
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
st.markdown(
    f"""
    <div class="info-box">

    <h1 style="color:#00ff88;">
    出席率: {rate:.2f}%
    </h1>

    <h3>
    🟩 出席: {attended}日　
    🟥 欠席: {absent}日　
    📅 合計: {total}日
    </h3>

    </div>
    """,
    unsafe_allow_html=True
)

# ======================================
# 月リスト
# ======================================
months = []

current = start_date

while current <= end_date:

    months.append(current)

    if current.month == 12:
        current = date(current.year + 1, 1, 1)

    else:
        current = date(current.year, current.month + 1, 1)

# ======================================
# 現在月
# ======================================
default_index = 0

for i, m in enumerate(months):

    if (
        m.year == today.year
        and m.month == today.month
    ):
        default_index = i
        break

# ======================================
# 月選択
# ======================================
selected_month = st.selectbox(
    "表示する月",
    options=months,
    index=default_index,
    format_func=lambda d: f"{d.year}年 {d.month}月"
)

year = selected_month.year
month = selected_month.month

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
# 月タイトル
# ======================================
st.markdown(
    f"""
    <div class="month-box">
    <h2 style="color:#00ff88;">
    {year}年 {month}月
    </h2>
    """,
    unsafe_allow_html=True
)

# ======================================
# 曜日
# ======================================
weekdays = ["月", "火", "水", "木", "金", "土", "日"]

header_cols = st.columns(7)

for i, weekday in enumerate(weekdays):

    with header_cols[i]:

        st.markdown(
            f"""
            <div class="weekday">
            {weekday}
            </div>
            """,
            unsafe_allow_html=True
        )

# ======================================
# カレンダー
# ======================================
cal = calendar.Calendar(firstweekday=0)

for week in cal.monthdayscalendar(year, month):

    cols = st.columns(7)

    for i, day in enumerate(week):

        if day == 0:
            cols[i].write("")
            continue

        current_date = date(year, month, day)

        if (
            current_date < start_date
            or current_date > end_date
        ):
            cols[i].write("")
            continue

        date_str = current_date.isoformat()

        status = attendance_data.get(
            date_str,
            "未選択"
        )

        # 状態表示
        if status == "出席":

            label = f"🟩\\n{day}"

        elif status == "欠席":

            label = f"🟥\\n{day}"

        else:

            label = f"⬛\\n{day}"

        with cols[i]:

            if st.button(
                label,
                key=f"open_{date_str}",
                use_container_width=True
            ):

                st.session_state.selected_date = date_str

# ======================================
# モーダル風ポップアップ
# ======================================
if st.session_state.selected_date:

    selected_date = st.session_state.selected_date

    current_status = attendance_data.get(
        selected_date,
        "未選択"
    )

    st.markdown(
        """
        <div class="popup-box">
        """,
        unsafe_allow_html=True
    )

    st.subheader(f"📅 {selected_date}")

    st.write("出欠席を設定してください")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "🟩 出席",
            use_container_width=True
        ):

            set_status(selected_date, "出席")
            st.session_state.selected_date = None
            st.rerun()

    with col2:

        if st.button(
            "🟥 欠席",
            use_container_width=True
        ):

            set_status(selected_date, "欠席")
            st.session_state.selected_date = None
            st.rerun()

    with col3:

        if st.button(
            "⬛ リセット",
            use_container_width=True
        ):

            set_status(selected_date, "未選択")
            st.session_state.selected_date = None
            st.rerun()

    if st.button("閉じる"):

        st.session_state.selected_date = None
        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# ======================================
# 閉じタグ
# ======================================
st.markdown(
    "</div>",
    unsafe_allow_html=True
)
