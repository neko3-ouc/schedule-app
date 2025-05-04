import streamlit as st
import pandas as pd

st.set_page_config(page_title="📆 予定調整", page_icon="📅")

st.title("📆 予定調整")

# セッションステートの初期化
if "events" not in st.session_state:
    st.session_state.events = {}

# 新しいイベントの追加フォーム
with st.form("add_event_form"):
    new_event = st.text_input("イベント名を入力")
    new_dates = st.text_input("候補日（カンマ区切り例: 2025-05-05,2025-05-06）")
    start_hour = st.number_input("開始時刻（例: 9）", min_value=0, max_value=23, value=9)
    end_hour = st.number_input("終了時刻（例: 21）", min_value=1, max_value=24, value=21)
    submitted_event = st.form_submit_button("イベント追加")

    if submitted_event:
        if new_event and new_dates and start_hour < end_hour:
            dates_list = [d.strip() for d in new_dates.split(",")]
            data = []
            for date in dates_list:
                for hour in range(start_hour, end_hour):
                    slot = f"{hour}:00 - {hour+1}:00"
                    data.append({"日付": date, "時間帯": slot, "OK人数": 0})
            st.session_state.events[new_event] = pd.DataFrame(data)
            st.success(f"イベント「{new_event}」を追加しました！")
        else:
            st.error("全ての項目を正しく入力してください。")

# イベント選択
event_names = list(st.session_state.events.keys())
if event_names:
    selected_event = st.selectbox("予定を調整するイベントを選んでください", event_names)

    # 入力フォーム
    with st.form("availability_form"):
        name = st.text_input("あなたの名前")

        selections = {}
        dates = st.session_state.events[selected_event]["日付"].unique()
        time_slots = st.session_state.events[selected_event]["時間帯"].unique()
        for date in dates:
            st.write(f"### 📅 {date}")
            for slot in time_slots:
                key = f"{date}_{slot}"
                selections[key] = st.checkbox(f"{slot}", key=f"{selected_event}_{key}")

        submitted = st.form_submit_button("予定を送信")

        if submitted:
            if name:
                for date in dates:
                    for slot in time_slots:
                        key = f"{date}_{slot}"
                        if selections.get(key, False):
                            idx = (st.session_state.events[selected_event]["日付"] == date) & (st.session_state.events[selected_event]["時間帯"] == slot)
                            st.session_state.events[selected_event].loc[idx, "OK人数"] += 1
                st.success(f"{name} さんの予定を登録しました！")
            else:
                st.error("名前を入力してください。")

    # 空き状況表示
    st.subheader(f"📊 「{selected_event}」の空き状況")
    st.dataframe(st.session_state.events[selected_event])
else:
    st.info("まずはイベントを追加してください。")
