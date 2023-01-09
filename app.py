from datetime import date
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe
import mplfinance as mpf
import zigzag as ulib

st.set_page_config(
     page_title="FX Infomation",
     page_icon="🧊",
     layout="wide",
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
to_dt = date(2022, 12, 31)
df = get_historical_data(from_dt, to_dt)
st.title("FX Infomation")

# --- 外軸モードの設定 ---
# fig1 = mpf.figure()                     # Size指定ならば 仮引数に figsize=(数値, 数値)を追加
# axs1 = fig1.add_subplot(1,1,1)          # 軸領域を設定
# axs1.tick_params("both", labelsize=9)   # 軸ラベルのFontサイズ (単位は pt？) [both=x軸/y軸 両方]


# fig, ax = mpf.subplots()


fig = mpf.figure(style='yahoo', figsize=(12,9))
#fig.subplots_adjust(hspace=0.3)
ax1 = fig.add_subplot(1,1,1)
# ax3 = fig.add_subplot(3,1,3)
# ax1 = fig.add_subplot(3,1,1, sharex=ax3)
# ax2 = fig.add_subplot(3,1,2, sharex=ax3)

# ax1.set_xticklabels([])
# ax2.set_xticklabels([])

# --- ローソク足を描画 ---
mpf.plot(df, type="candle",
         ax = ax1,
         volume=False,
         datetime_format="%m/%d %H:%M",
         xrotation=15,
         axtitle="== Sample Candle Chart ==",
         ylabel="[Cdle Value]" )
# fig, ax = mpf.plot(
#     df,
#     title=f'foo',
#     type="candle",
#     show_nontrading=True,
#     volume=True,
#     style="yahoo",
#     figsize=(15,10),
#     returnfig=True
# )

#  --- ZigZag テクニカル指標の計算 ---
Cdt = df["close"].tolist()                  # データの準備 (リスト型に変換)

XYBF = ulib.ZigZag(Cdt)                     # ZigZagのテクニカル指標 (頂点座標の情報を取得)
# print(XYBF)
PlotBf = ulib.toPlotDataForZigZag(XYBF)     # データ列をプロット形式に変換
# print(" -- Plot -- \n", PlotBf)           # Xdata=PlotBf[0],  Ydata=PlotBf[1]

# --- ZigZagを(x,y)データでプロット ---
ax1.plot(PlotBf[0], PlotBf[1],
          color="r", linewidth=1.5,
          marker="o", markersize=5.0,
          markerfacecolor='#00CC77',
          markeredgecolor="green")

st.pyplot(fig)
st.dataframe(df, width=1000)
