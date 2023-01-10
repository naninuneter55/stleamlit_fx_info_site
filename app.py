from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe
import mplfinance as mpf

st.set_page_config(
     page_title="FX Infomation",
     page_icon="🧊",
    #  layout="wide",
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

SWING_HIGH_LOW_WINDOW = 5 + 1 + 5
def swing_high(prices):
    l = len(prices)
    c = l // 2
    result = prices[c]
    for i in range(len(prices)):
        if i != c and prices[i] >= prices[c]:
            result = np.nan
            break
    return result

def swing_low(prices):
    l = len(prices)
    c = l // 2
    result = prices[c]
    for i in range(len(prices)):
        if i != c and prices[i] <= prices[c]:
            result = np.nan
            break
    return result


from_dt = date(2022, 1, 1)
to_dt = date(2022, 6, 30)
df = get_historical_data(from_dt, to_dt)
df["swing_high"] = df["high"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_high)
df["swing_low"] = df["low"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_low)

st.title("FX Infomation")

fig = mpf.figure(figsize=[10, 8], style='yahoo')
ax1 = fig.add_subplot(1,1,1)

series = [
    mpf.make_addplot(
        df["swing_high"],
        type='scatter',
        markersize=30,
        marker='v',
        color='black',
        ax=ax1
    ),
    mpf.make_addplot(
        df["swing_low"],
        type='scatter',
        markersize=30,
        marker='^',
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
         alines=[('2022/05/24', 126.356), ('2022/06/16',131.486)]
)

st.pyplot(fig)
st.dataframe(df, width=1000)
