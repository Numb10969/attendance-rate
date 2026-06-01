import streamlit as st
from datetime import date
import calendar
import json
import os

st.set_page_config(
page_title="出席率管理",
layout="wide"
)

SAVE_FILE = "attendance.json"

def load_data():
if os.path.exists(SAVE_FILE):
try:
with open(SAVE_FILE, "r", encoding="utf-8") as f:
return json.load(f)
except:
return {}
return {}

def save_data(data):
with open(SAVE_FILE, "w", encoding="utf-8") as f:
json.dump(
data,
f,
ensure_ascii=False,
indent=2
)

if "data" not in st.session_state:
st.session_state.data = load_data()

data = st.session_state.data

today = date.today()

if today.month >= 4:
start_year = today.year
else:
start_year = today.year - 1

months = []

for y in [start_year, start_year + 1]:
for m in range(1, 13):

```
    if y == start_year and m < 4:
        continue

    if y == start_year + 1 and m > 4:
        continue

    months.append(date(y, m, 1))
```

default_month = date(today.year, today.month, 1)

default_index = 0

for i, d in enumerate(months):
if d.year == default_month.year and d.month == default_month.month:
default_index = i
break

st.title("📚 出席率管理カレンダー")

total_attended = sum(
item.get("attended", 0)
for item in data.values()
)

total_absent = sum(
item.get("absent", 0)
for item in data.values()
)

total_classes = total_attended + total_absent

rate = (
total_attended / total_classes * 100
if total_classes > 0
else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
"出席率",
f"{rate:.2f}%"
)

c2.metric(
"出席授業数",
total_attended
)

c3.metric(
"欠席授業数",
total_absent
)

c4.metric(
"総授業数",
total_classes
)

selected_month = st.selectbox(
"表示月",
months,
index=default_index,
format_func=lambda x:
f"{x.year}年{x.month}月"
)

year = selected_month.year
month = selected_month.month

if "selected_date" not in st.session_state:
st.session_state.selected_date = None

@st.dialog("授業数入力")
def edit_day():

```
date_str = st.session_state.selected_date

current = data.get(
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

        data[date_str] = {
            "attended": attended,
            "absent": absent
        }

        save_data(data)

        st.rerun()

with col2:

    if st.button(
        "削除",
        use_container_width=True
    ):

        if date_str in data:
            del data[date_str]

        save_data(data)

        st.rerun()
```

weekdays = [
"月",
"火",
"水",
"木",
"金",
"土",
"日"
]

header = st.columns(7)

for i, wd in enumerate(weekdays):
header[i].markdown(
f"**{wd}**"
)

cal = calendar.Calendar(
firstweekday=0
)

for week in cal.monthdayscalendar(
year,
month
):

```
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

    date_str = current_date.isoformat()

    value = data.get(
        date_str,
        None
    )

    if value:

        attended = value["attended"]
        absent = value["absent"]

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

            st.session_state.selected_date = date_str
            edit_day()
```
