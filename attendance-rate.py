import streamlit as st
from supabase import create_client
from datetime import date
import calendar

# ==================================================
# ページ設定
# ==================================================

st.set_page_config(
    page_title="出席率管理",
    layout="wide"
)

# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

html, body, [class*="css"]{
    background-color:#111111;
    color:white;
}

.stMetric{
    background:#1a1a1a;
    border:1px solid #00aa55;
    border-radius:10px;
    padding:10px;
}

div.stButton > button{
    width:100%;
    border-radius:8px;
    min-height:70px;
}

.day-button{
    width:100%;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# Supabase接続
# ==================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ==================================================
# DB操作
# ==================================================

def load_data():

    result = (
        supabase
        .table("attendance")
        .select("*")
        .execute()
    )

    return result.data

def load_correction():

    try:

        result = (
            supabase
            .table("settings")
            .select("value")
            .eq("key", "correction")
            .execute()
        )

        if result.data:

            return float(
                result.data[0]["value"]
            )

    except Exception:
        pass

    return 0.0


def save_correction(value):

    try:

        (
            supabase
            .table("settings")
            .upsert(
                {
                    "key": "correction",
                    "value": str(value)
                }
            )
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"補正値の保存に失敗しました: {e}"
        )

        return False

def save_data(
    date_str,
    attended,
    absent
):

    (
        supabase
        .table("attendance")
        .upsert(
            {
                "date": date_str,
                "attended": attended,
                "absent": absent
            }
        )
        .execute()
    )


def delete_data(date_str):

    (
        supabase
        .table("attendance")
        .delete()
        .eq("date", date_str)
        .execute()
    )


# ==================================================
# データ取得
# ==================================================

rows = load_data()

attendance_map = {}

for row in rows:

    attendance_map[row["date"]] = {
        "attended": row["attended"],
        "absent": row["absent"]
    }

# ==================================================
# 出席率計算
# ==================================================

total_attended = sum(
    row["attended"]
    for row in rows
)

total_absent = sum(
    row["absent"]
    for row in rows
)

total_classes = (
    total_attended
    + total_absent
)

if total_classes > 0:

    attendance_rate = (
        total_attended
        / total_classes
        * 100
    )

else:

    attendance_rate = 0

# --------------------------
# 補正値読込
# --------------------------

correction = load_correction()

display_rate = (
    attendance_rate
    + correction
)

display_rate = max(
    0,
    min(
        100,
        display_rate
    )
)
# ==================================================
# タイトル
# ==================================================

st.title("📚 出席率管理カレンダー")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
       "出席率",
       f"{display_rate:.2f}%"
    )

with c2:

    st.metric(
        "出席授業数",
        total_attended
    )

with c3:

    st.metric(
        "欠席授業数",
        total_absent
    )

with c4:

    st.metric(
        "総授業数",
        total_classes
    )

# ==================================================
# 表示月
# ==================================================

st.markdown("---")

st.subheader(
    "出席率補正"
)

new_correction = st.number_input(
    "補正値 (%)",
    value=correction,
    step=0.01,
    format="%.2f"
)

if st.button(
    "補正値を保存"
):

    if save_correction(
        new_correction
    ):

        st.success(
            "保存しました"
        )

        st.rerun()
    
today = date.today()

if today.month >= 4:

    start_year = today.year

else:

    start_year = today.year - 1

months = []

for y in [start_year, start_year + 1]:

    for m in range(1, 13):

        if y == start_year and m < 4:
            continue

        if y == start_year + 1 and m > 4:
            continue

        months.append(
            date(y, m, 1)
        )

default_index = 0

for i, d in enumerate(months):

    if (
        d.year == today.year
        and
        d.month == today.month
    ):

        default_index = i
        break

selected_month = st.selectbox(
    "表示月",
    months,
    index=default_index,
    format_func=lambda d:
    f"{d.year}年{d.month}月"
)

year = selected_month.year
month = selected_month.month

# ==================================================
# セッション初期化
# ==================================================

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# ==================================================
# ダイアログ
# ==================================================

@st.dialog("出席情報編集")
def edit_dialog():

    date_str = st.session_state.selected_date

    current = attendance_map.get(
        date_str,
        {
            "attended": 0,
            "absent": 0
        }
    )

    attended = st.number_input(
        "出席授業数",
        min_value=0,
        step=1,
        value=current["attended"]
    )

    absent = st.number_input(
        "欠席授業数",
        min_value=0,
        step=1,
        value=current["absent"]
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "保存",
            use_container_width=True
        ):

            save_data(
                date_str,
                attended,
                absent
            )

            st.session_state.selected_date = None

            st.rerun()

    with col2:

        if st.button(
            "削除",
            use_container_width=True
        ):

            delete_data(date_str)

            st.session_state.selected_date = None

            st.rerun()

# ==================================================
# カレンダー
# ==================================================

week_names = [
    "月",
    "火",
    "水",
    "木",
    "金",
    "土",
    "日"
]

header_cols = st.columns(7)

for i, name in enumerate(week_names):

    header_cols[i].markdown(
        f"### {name}"
    )

cal = calendar.Calendar(
    firstweekday=0
)

weeks = cal.monthdayscalendar(
    year,
    month
)

for week in weeks:

    cols = st.columns(7)

    for i, day in enumerate(week):

        if day == 0:

            cols[i].write("")

            continue

        current_date = date(
            year,
            month,
            day
        )

        date_str = (
            current_date.isoformat()
        )

        record = attendance_map.get(
            date_str
        )

        if record:

            attended = record[
                "attended"
            ]

            absent = record[
                "absent"
            ]

            label = (
                f"{day}\n"
                f"⭕{attended}\n"
                f"❌{absent}"
            )

        else:

            label = str(day)

        with cols[i]:

            if st.button(
                label,
                key=date_str,
                use_container_width=True
            ):

                st.session_state.selected_date = (
                    date_str
                )

                edit_dialog()

# ==================================================
# 月別統計
# ==================================================

st.markdown("---")

month_attended = 0
month_absent = 0

for row in rows:

    row_date = date.fromisoformat(
        row["date"]
    )

    if (
        row_date.year == year
        and
        row_date.month == month
    ):

        month_attended += row[
            "attended"
        ]

        month_absent += row[
            "absent"
        ]

month_total = (
    month_attended
    + month_absent
)

if month_total > 0:

    month_rate = (
        month_attended
        / month_total
        * 100
    )

else:

    month_rate = 0

st.subheader(
    f"{year}年{month}月の統計"
)

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "月間出席率",
        f"{month_rate:.2f}%"
    )

with m2:

    st.metric(
        "月間出席授業数",
        month_attended
    )

with m3:

    st.metric(
        "月間欠席授業数",
        month_absent
    )

with m4:

    st.metric(
        "月間総授業数",
        month_total
    )

# ==================================================
# 明細表示
# ==================================================

st.markdown("---")

st.subheader(
    "登録済みデータ"
)

display_rows = []

for row in rows:

    row_date = date.fromisoformat(
        row["date"]
    )

    if (
        row_date.year == year
        and
        row_date.month == month
    ):

        display_rows.append(
            {
                "日付": row["date"],
                "出席授業数": row[
                    "attended"
                ],
                "欠席授業数": row[
                    "absent"
                ]
            }
        )

if display_rows:

    display_rows = sorted(
        display_rows,
        key=lambda x:
        x["日付"]
    )

    st.dataframe(
        display_rows,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "この月のデータはありません。"
    )

# ==================================================
# スマホ向け補足
# ==================================================

st.markdown("---")

st.caption(
    "日付をタップすると出席授業数・欠席授業数を編集できます。"
)

# ==================================================
# 当日表示
# ==================================================

st.caption(
    f"今日の日付 : {today}"
)
