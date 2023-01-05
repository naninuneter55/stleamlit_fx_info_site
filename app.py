import streamlit as st
import plotly.graph_objs as go
import requests
import os
import sys
import subprocess
import shutil
import numpy
import platform
import pandas as pd
import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe
import mplfinance as mpf

if platform.system() == "Linux":
    # shutil.rmtree("/tmp/ta-lib")
    # check if the library folder already exists, to avoid building everytime you load the pahe
    if not os.path.isdir("/tmp/ta-lib"):

        # Download ta-lib to disk
        with open("/tmp/ta-lib-0.4.0-src.tar.gz", "wb") as file:
            response = requests.get(
                "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
            )
            file.write(response.content)
        # get our current dir, to configure it back again. Just house keeping
        default_cwd = os.getcwd()
        os.chdir("/tmp")
        # untar
        os.system("tar -zxvf ta-lib-0.4.0-src.tar.gz")
        os.chdir("/tmp/ta-lib")
        os.system("ls -la /app/equity/")
        # build
        os.system("./configure --prefix=/home/appuser")
        os.system("make")
        # install
        os.system("make install")
        # back to the cwd
        os.chdir(default_cwd)
        sys.stdout.flush()

    # add the library to our current environment
    from ctypes import *

    lib = CDLL("/home/appuser/lib/libta_lib.so.0.0.0")
    # import library
    try:
        import talib
    except ImportError:
        os.environ['CFLAGS'] = '-I/home/appuser/include/'
        os.environ['LDFLAGS'] = '-L/home/appuser/lib/'
        # subprocess.check_call([sys.executable, "-m", "pip", "install", "--global-option=build_ext", "--global-option=-L/home/appuser/lib/", "--global-option=-I/home/appuser/include/", "TA-Lib"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "TA-Lib"])
    # finally:
    #     import talib

import talib as ta

scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
creds = service_account.Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=scope)

gc = gspread.authorize(creds)
SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key # スプレッドシートのキー
sh = gc.open_by_key(SP_SHEET_KEY)
SP_SHEET = 'シート1' # シート名「シート1」を指定
worksheet = sh.worksheet(SP_SHEET)
df = get_as_dataframe(worksheet)
df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time")
df.rename(columns={'tick_volume':'volume'}, inplace=True)

close = df['close']
macd, macdsignal, _ = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
df['macd'] = macd
df['macd_signal'] = macdsignal
# data = worksheet.get_all_values() 
# print(len(data))


st.title("FX Infomation")
# close = numpy.random.random(100)
# output = talib.SMA(close)
# df = pd.DataFrame(data)
st.dataframe(df)

mdf = df.tail(100)  # 直近100日分のデータ


# import matplotlib.pyplot as plt
# import numpy as np

# arr = np.random.normal(1, 1, size=100)
# fig, ax = plt.subplots()
# ax.hist(arr, bins=20)

# st.pyplot(fig)


fig = go.Figure(data = [go.Candlestick(x = mdf.index,\
    open = mdf['open'],\
    high = mdf['high'],\
    low = mdf['low'],\
    close = mdf['close'])])
st.plotly_chart(fig, theme="streamlit", use_container_width=True)