from datetime import date
import streamlit as st
import mplfinance as mpf
import myfxlib as fx

def prologe():
    st.set_page_config(
        page_title="FX Infomation",
        page_icon="🧊",
         layout="wide",
        # layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!",
        }
    )

def get_historical_data():
    sp_sheet_key = st.secrets.sp_sheet_key.key # スプレッドシートのキー
    account = st.secrets["gcp_service_account"]
    from_dt = date(2022, 1, 1)
    to_dt = date(2022, 6, 30)
    df = fx.get_historical_data(sp_sheet_key, account, from_dt, to_dt)
    return df

def get_fig(df):
    fig = mpf.figure(figsize=[20, 8], style='yahoo')
    ax1 = fig.add_subplot(1,1,1)
    alines = fx.get_zigzag_alines(df)
    series = [
        mpf.make_addplot(
            fx.get_swing_highs(df),
            type='scatter',
            markersize=50,
            marker='v',
            color='black',
            ax=ax1
        ),
        mpf.make_addplot(
            fx.get_swing_lows(df),
            type='scatter',
            markersize=50,
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
            alines=alines
    )
    return fig

def create_sidebar():
    st.sidebar.markdown("## Controls")
    st.sidebar.markdown("You can **change** the values to change the *chart*.")
    x = st.sidebar.slider('Slope', min_value=0.01, max_value=0.10, step=0.01)
    y = st.sidebar.slider('Noise', min_value=0.01, max_value=0.10, step=0.01)
    import time


def main():

    prologe()
    create_sidebar()

    st.title("FX Infomation")

    col1, col2, col3 = st.columns([1.5, 3, 1.5])

    with col1:
        st.header("A cat")

    with col2:
        st.header("A dog")
        with st.spinner("Loading historical data ..."):
            df = get_historical_data()
        fig = get_fig(df)
        st.pyplot(fig)
        st.dataframe(df, width=1000)

    with col3:
        st.header("An owl")



if __name__ == "__main__":
    main()