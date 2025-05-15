import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証とスプレッドシート接続の設定
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
service_account_info = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("schedule-app")

# イベント名一覧を取得する関数
def get_event_names():
    return [ws.title for ws in spreadsheet.worksheets()]

# --- StreamlitアプリのUI部 ---
st.title("📅 スケジュール調整アプリ")

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
                    date_str = f"'{date}"
                    for hour in range(start_hour, end_hour):
                        slot = f"{hour}:00-{hour+1}:00"
                        ws.append_row(["", date_str, slot])

                st.success(f"✅ イベント「{new_event}」を追加しました！")
                st.rerun()
        else:
            st.error("⚠️ 全ての項目を正しく入力してください。")

# イベント削除
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

st.subheader("📨 予定を登録する")

# イベント一覧取得
event_names = get_event_names()

if event_names:
    selected_event = st.selectbox("登録するイベントを選んでください", event_names)

    with st.form("add_schedule_form"):
        name = st.text_input("名前")
        date = st.text_input("希望日（例: 2025-05-05）")
        time_slot = st.text_input("希望時間帯（例: 14:00-15:00）")
        submitted_schedule = st.form_submit_button("予定を登録する")

        if submitted_schedule:
            if name and date and time_slot:
                try:
                    # 該当のイベントシート取得
                    ws = spreadsheet.worksheet(selected_event)
                    ws.append_row([name, f"'{date}", time_slot])
                    st.success(f"✅ {name}さんの予定を登録しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"登録に失敗しました: {e}")
            else:
                st.error("⚠️ 全ての項目を入力してください。")
else:
    st.info("登録できるイベントがまだありません。")
import pandas as pd

st.subheader("📊 参加希望集計")

if event_names:
    selected_event_for_summary = st.selectbox("集計するイベントを選んでください", event_names, key="summary_event")

    if st.button("集計する"):
        try:
            ws = spreadsheet.worksheet(selected_event_for_summary)
            data = ws.get_all_records()  # ヘッダー付きのデータを取得

            if data:
                df = pd.DataFrame(data)
                # 時間帯ごとに名前が入力されている数をカウント
                summary = df.groupby("時間帯").apply(lambda x: x["名前"].apply(bool).sum()).reset_index()
                summary.columns = ["時間帯", "人数"]

                st.dataframe(summary)
            else:
                st.info("データがありません。")

        except Exception as e:
            st.error(f"集計に失敗しました: {e}")
else:
    st.info("集計できるイベントがありません。")
