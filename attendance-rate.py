import tkinter as tk
from tkinter import ttk
from datetime import date
import calendar


class AttendanceCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("出席率カレンダー")
        self.root.geometry("1400x900")

        # 出席状態
        # True = 出席
        # False = 欠席
        # 未選択 = データなし
        self.attendance_data = {}

        self.buttons = {}

        # 今年4月1日〜来年4月1日
        today = date.today()

        if today.month >= 4:
            self.start_date = date(today.year, 4, 1)
            self.end_date = date(today.year + 1, 4, 1)
        else:
            self.start_date = date(today.year - 1, 4, 1)
            self.end_date = date(today.year, 4, 1)

        # タイトル
        title = tk.Label(
            root,
            text="出席率管理カレンダー",
            font=("Meiryo", 24, "bold")
        )
        title.pack(pady=10)

        # 出席率表示
        self.rate_label = tk.Label(
            root,
            text="出席率: 0.00%",
            font=("Meiryo", 18, "bold"),
            fg="blue"
        )
        self.rate_label.pack(pady=10)

        # 説明
        info = tk.Label(
            root,
            text="クリックで切替： 灰 = 未選択 / 緑 = 出席 / 赤 = 欠席",
            font=("Meiryo", 12)
        )
        info.pack(pady=5)

        # スクロールエリア
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_calendar()

    def create_calendar(self):
        current = self.start_date

        month_index = 0

        while current <= self.end_date:
            year = current.year
            month = current.month

            month_frame = tk.LabelFrame(
                self.scrollable_frame,
                text=f"{year}年 {month}月",
                font=("Meiryo", 14, "bold"),
                padx=5,
                pady=5
            )

            row = month_index // 3
            col = month_index % 3

            month_frame.grid(
                row=row,
                column=col,
                padx=10,
                pady=10,
                sticky="n"
            )

            weekdays = ["月", "火", "水", "木", "金", "土", "日"]

            for i, day_name in enumerate(weekdays):
                label = tk.Label(
                    month_frame,
                    text=day_name,
                    width=4,
                    font=("Meiryo", 10, "bold")
                )
                label.grid(row=0, column=i)

            cal = calendar.Calendar(firstweekday=0)
            month_days = cal.monthdayscalendar(year, month)

            for week_num, week in enumerate(month_days, start=1):
                for day_index, day in enumerate(week):

                    if day == 0:
                        empty = tk.Label(
                            month_frame,
                            text="",
                            width=4
                        )
                        empty.grid(
                            row=week_num,
                            column=day_index
                        )

                    else:
                        current_date = date(year, month, day)

                        # 範囲外の日付は表示しない
                        if (
                            current_date < self.start_date
                            or current_date > self.end_date
                        ):
                            empty = tk.Label(
                                month_frame,
                                text="",
                                width=4
                            )
                            empty.grid(
                                row=week_num,
                                column=day_index
                            )
                            continue

                        btn = tk.Button(
                            month_frame,
                            text=str(day),
                            width=4,
                            bg="lightgray",
                            command=lambda d=current_date:
                            self.toggle_attendance(d)
                        )

                        btn.grid(
                            row=week_num,
                            column=day_index,
                            padx=1,
                            pady=1
                        )

                        self.buttons[current_date] = btn

            # 次の月へ
            if month == 12:
                current = date(year + 1, 1, 1)
            else:
                current = date(year, month + 1, 1)

            month_index += 1

    def toggle_attendance(self, current_date):
        """
        状態遷移
        未選択 → 出席 → 欠席 → 未選択
        """

        current_state = self.attendance_data.get(
            current_date,
            None
        )

        btn = self.buttons[current_date]

        # 未選択 → 出席
        if current_state is None:
            self.attendance_data[current_date] = True
            btn.config(bg="lightgreen")

        # 出席 → 欠席
        elif current_state is True:
            self.attendance_data[current_date] = False
            btn.config(bg="tomato")

        # 欠席 → 未選択
        else:
            del self.attendance_data[current_date]
            btn.config(bg="lightgray")

        self.update_attendance_rate()

    def update_attendance_rate(self):
        attended = sum(
            1 for v in self.attendance_data.values()
            if v
        )

        absent = sum(
            1 for v in self.attendance_data.values()
            if not v
        )

        total = attended + absent

        if total == 0:
            rate = 0
        else:
            rate = (attended / total) * 100

        self.rate_label.config(
            text=(
                f"出席率: {rate:.2f}%   "
                f"出席: {attended}日   "
                f"欠席: {absent}日"
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceCalendar(rootimport streamlit as st
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
    root.mainloop()
