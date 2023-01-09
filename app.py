from datetime import date
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe
import mplfinance as mpf

st.set_page_config(
     page_title="FX Infomation",
     page_icon="🧊",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!",
     }
 )

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
to_dt = date(2022, 1, 31)
df = get_historical_data(from_dt, to_dt)
st.title("FX Infomation")

fig = mpf.figure(style='yahoo')
ax1 = fig.add_subplot(1,1,1)

series = [
    mpf.make_addplot(
        df["close"],
        type='scatter',
        markersize=20,
        marker='o',
        color='black',
        ax=ax1
    ),
]

mpf.plot(df,
         type="candle",
         ax = ax1,
         volume=False,
         datetime_format="%m/%d %H:%M",
         xrotation=15,
         axtitle="== Sample Candle Chart ==",
         ylabel="[Cdle Value]",
         addplot=series,
)

st.pyplot(fig)
st.dataframe(df, width=1000)
