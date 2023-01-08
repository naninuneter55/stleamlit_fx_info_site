from datetime import date
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe
import mplfinance as mpf

scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key # スプレッドシートのキー
gc = gspread.authorize(creds)
sh = gc.open_by_key(SP_SHEET_KEY)


@st.cache
def get_historical_data(from_dt, to_dt):
    SP_SHEET = 'シート1' # シート名「シート1」を指定
    worksheet = sh.worksheet(SP_SHEET)
    df = get_as_dataframe(worksheet, header=0, index_col=0)
    df = df.rename(columns = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    for i in df.columns:
        df[i] = df[i].astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.loc[from_dt:to_dt]
    return df

from_dt = date(2022, 1, 1)
to_dt = date(2022, 3, 31)
df = get_historical_data(from_dt, to_dt)
st.title("FX Infomation")

fig, ax = mpf.plot(
    df,
    title=f'foo',
    type="candle",
    show_nontrading=True,
    volume=True,
    style="yahoo",
    figsize=(15,10),
    returnfig=True
)

st.pyplot(fig)
st.dataframe(df)
