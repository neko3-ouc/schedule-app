import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証とスプレッドシート接続の設定（例）
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open("schedule-app")


# イベント名一覧を取得する関数
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

                valid_dates = []
                for d in dates:
                    try:
                        datetime.strptime(d, "%Y-%m-%d")
                        valid_dates.append(d)
                    except ValueError:
                        st.error(f"⚠️ 日付の形式が不正です: {d}")

                for date in valid_dates:
                    date_str = f"'{date}"  # ← ここでシングルクォート付けて文字列にする
                    for hour in range(start_hour, end_hour):
                        slot = f"{hour}:00-{hour+1}:00"
                        ws.append_row(["", date_str, slot])

                st.success(f"✅ イベント「{new_event}」を追加しました！")
                st.rerun()
        else:
            st.error("⚠️ 全ての項目を正しく入力してください。")

st.subheader("🗑️ イベントを削除")

event_names = get_event_names()

if event_names:
    event_to_delete = st.selectbox("削除するイベントを選択してください", event_names)
    if st.button("イベントを削除する"):
        try:
            worksheet_to_delete = spreadsheet.worksheet(event_to_delete)
            spreadsheet.del_worksheet(worksheet_to_delete)
            st.success(f"✅ イベント「{event_to_delete}」を削除しました！")
            st.rerun()
        except Exception as e:
            st.error(f"削除に失敗しました: {e}")
else:
    st.info("削除できるイベントがありません。")



