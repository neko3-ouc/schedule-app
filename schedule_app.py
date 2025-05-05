import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["service_account"],
    scopes=scope
)

gc = gspread.authorize(credentials)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14r37SfIpamPXNnGgUT5D3w94Vf-iqOBfbKMFCrPZ4b0/edit#gid=0"

try:
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.sheet1
    values = worksheet.get_all_values()

    st.success("✅ 接続OK")
    st.write("データ内容")
    st.write(values)

except Exception as e:
    st.error(f"❌ エラー: {e}")


except Exception as e:
    st.error(f"❌ エラー: {e}")
