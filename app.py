import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 認証設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
service_account_info = st.secrets["service_account"]
credentials = Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES)
gc = gspread.authorize(credentials)

SPREADSHEET_KEY = "14r37SfIpamPXNnGgUT5D3w94Vf-iqOBfbKMFCrPZ4b0"
spreadsheet = gc.open_by_key(SPREADSHEET_KEY)

st.set_page_config(page_title="📆 予定調整", page_icon="📅")
st.title("📆 予定調整アプリ")

# イベント一覧取得
def get_event_names():
    return [ws.title for ws in spreadsheet.worksheets()]

# イベント追加フォーム
with st.form("add_event_form"):
    st.subheader("📝 新しいイベントを追加")
    new_event = st.text_input("イベント名")
    new_dates = st.text_input("候補日（例: 2025-05-05,2025-05-06）")
    start_hour = st.number_input("開始時刻 (0-23)", 0, 23, 9)
    end_hour = st.number_input("終了時刻 (1-24)", 1, 24, 21)
    submitted_event = st.form_submit_button("イベントを追加する")

    if submitted_event:
        if new_event and new_dates and start_hour < end_hour:
            event_names = get_event_names()
            if new_event in event_names:
                st.warning("⚠️ 同じ名前のイベントがあります。")
            else:
                spreadsheet.add_worksheet(title=new_event, rows="500", cols="5")
                ws = spreadsheet.worksheet(new_event)
                ws.append_row(["名前", "日付", "時間帯"])
                dates = [d.strip() for d in new_dates.split(",")]
                for date in dates:
                    for hour in range(start_hour, end_hour):
                        slot = f"{hour}:00-{hour+1}:00"
                        ws.append_row(["", date, slot])
                st.success(f"✅ イベント「{new_event}」を追加しました！")
                st.rerun()
        else:
            st.error("⚠️ 全ての項目を正しく入力してください。")

# イベント選択
event_names = get_event_names()

if event_names:
    selected_event = st.selectbox("📅 イベントを選択してください", event_names)

    ws = spreadsheet.worksheet(selected_event)
    records = ws.get_all_records()
    df = pd.DataFrame(records)

    if not df.empty:
        with st.form("availability_form"):
            st.subheader(f"✏️ {selected_event} に参加できる時間を選んでください")
            name = st.text_input("あなたの名前")
            dates = df["日付"].unique()
            selections = {}

            for date in dates:
                st.write(f"### 📆 {date}")
                slots = df[df["日付"] == date]["時間帯"].unique()
                for slot in slots:
                    key = f"{date}_{slot}"
                    selections[key] = st.checkbox(f"{slot}", key=key)

            submitted = st.form_submit_button("予定を送信する")

            if submitted:
                if name:
                    for key, checked in selections.items():
                        if checked:
                            date, slot = key.split("_")
                            ws.append_row([name, date, slot])
                    st.success(f"✅ {name} さんの予定を登録しました！")
                    st.rerun()
                else:
                    st.error("⚠️ 名前を入力してください。")
    else:
        st.write("まだ候補日が登録されていません。")

    # 空き状況表示
    st.subheader(f"📊 「{selected_event}」の空き状況")
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("まだ参加者が登録されていません。")

else:
    st.info("まずイベントを追加してください。")
# 空き状況表示
st.subheader(f"📊 「{selected_event}」の空き状況")

if not df.empty:
    dates = df["日付"].unique()

    for date in dates:
        st.write(f"### 📅 {date}")
        slots = df[df["日付"] == date]["時間帯"].unique()

        result_data = []
        for slot in slots:
            count = df[(df["日付"] == date) & (df["時間帯"] == slot) & (df["名前"] != "")].shape[0]
            result_data.append({"時間帯": slot, "希望人数": f"{count}人"})

        result_df = pd.DataFrame(result_data)
        st.table(result_df)
else:
    st.write("まだ参加者が登録されていません。")





