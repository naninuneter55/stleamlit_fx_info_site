import pandas as pd
import numpy as np
import gspread
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe

SWING_HIGH_LOW_WINDOW = 5 + 1 + 5

def get_historical_data(ss_sheet_name, gcp_service_account, from_dt, to_dt):

    scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_info(gcp_service_account, scopes=scope)
    gc = gspread.authorize(creds)
    sh = gc.open(ss_sheet_name)
    SP_SHEET = "USDJPY_M5"
    worksheet = sh.worksheet(SP_SHEET)
    df = get_as_dataframe(worksheet, header=0, index_col=0)
    df = df.rename(columns = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'TickVolume': 'volume', 'Spread': 'spread', 'RealVolume': 'rv', })
    for i in df.columns:
        df[i] = df[i].astype(float)
    print(df.dtypes)
    print(df.index.dtype)
    df.index = pd.to_datetime(df.index)
    print(df.index.dtype)
    df = df.loc[from_dt:to_dt]
    return df

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

def get_zigzag(df_src, negative=False):
    sr_high= df_src["high"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_high)
    sr_low = df_src["low"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_low)
    sr = sr_high
    sr_low = sr_low.apply(lambda x : x if np.isnan(x) else -x)
    sr.update(sr_low)
    df = pd.DataFrame(sr.dropna())
    df = df.rename(columns={"high": "price"})
    df["sign"] = np.sign(df["price"])
    df['shift'] = df['sign'].shift()
    df['diff'] = df['sign'] != df['shift']
    df['cont_group'] = df['diff'].cumsum()
    df_grouped = df.groupby("cont_group")
    exclusion_list = []
    for k, v in df_grouped.groups.items():
        v_size = len(v)
        if(v_size == 1):
            continue
        compare = {}
        for i in range(v_size):
            dt = v[i]
            compare[dt] = df["price"][dt]
        if np.sign(list(compare.values())[0]) == 1.0:
            top = max(compare, key=compare.get)
        else:
            top = max(compare, key=compare.get)
        for dt in v:
            if top != dt:
                df.at[dt, "price"] = np.nan
                sr[dt] = np.nan
    sr = sr.apply(np.abs)
    return sr
    
def get_zigzag_alines(df_src):
    ser = get_zigzag(df_src)
    ser = ser.dropna()
    l = ser.reset_index().values.tolist()
    l = [tuple(n) for n in l]
    return l

def get_swing_highs(df_src):
    sr = df_src["high"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_high)
    return sr

def get_swing_lows(df_src):
    sr = df_src["low"].rolling(window=SWING_HIGH_LOW_WINDOW, center=True).apply(swing_low)
    return sr