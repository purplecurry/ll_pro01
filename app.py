import streamlit as st
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")

MAV_COLORS_MAP = {
    5: 'red',
    10: 'green',
    20: 'blue',
    30: 'purple',
    60: 'orange',
    120: 'brown'
}
DEFAULT_MAV_SETTING = [5, 10, 20]

@st.cache_data
def load_list(symbol = 'KRX'):
    if symbol in ['KRX', 'KOSPI', 'KOSDAQ', 'KONEX']:
        lis = fdr.StockListing(symbol)
        lis_selected = lis.loc[:, ['Code', 'Name']]
        lis_indexed = lis_selected.set_index('Name')
    elif symbol in ['NASDAQ', 'NYSE', 'AMEX', 'S&P500']:
        lis = fdr.StockListing(symbol)
        lis_selected = lis.loc[:, ['Symbol', 'Name']]
        lis_indexed = lis_selected.set_index('Name')
    else:
        lis = {'Code': ['BTC/KRW', 'ETH/KRW', 'XRP/KRW', 'BTC/USD', 'ETH/USD', 'XRP/USD']}
        lis_indexed = pd.DataFrame(lis, index = ['비트코인/빗썸', '이더리움/빗썸', '리플/빗썸', '비트코인/Bitfinex', '이더리움/Bitfinex', '리플/Bitfinex'])
        lis_indexed.index.name = 'Name'
    return lis_indexed

@st.cache_data
def load_stock(symbol, subsymbol, datestart, dateend):
    try:
        df = fdr.DataReader(subsymbol, datestart, dateend)
        
        if 'Change' in df.columns:
            df = df.drop(columns='Change')
            
        if 'Adj Close' in df.columns:
             df = df.drop(columns='Adj Close')
        
        if 'Volume_USDT' in df.columns:
            df = df.rename(columns={'Volume_USDT': 'Volume'})
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}. 코드를 확인해 주세요: {subsymbol}")
        return pd.DataFrame()


with st.sidebar:
    st.title('종목 및 차트 설정 ⚙️')
    
    symbol = st.selectbox('거래소 선택', ['KRX','KOSPI', 'KOSDAQ', 'KONEX', 'NASDAQ', 'NYSE', 'AMEX', 'CRYPTO'])
    lis = load_list(symbol)
    
    if lis.empty:
        st.error("종목 목록을 불러올 수 없습니다.")
        st.stop()

    name_list = lis.index.tolist()
    st.markdown('---')
    
    name = st.selectbox('종목 선택', name_list)
    
    row = lis.loc[name]
    sub_symbol = row.iloc[0] if isinstance(row, pd.Series) else row['Code'].iloc[0] 
    st.markdown('---')
    
    st.markdown('**기간 선택**')
    datestart = st.date_input('시작 날자', value = datetime.today()-timedelta(days=90))
    dateend = st.date_input('종료 날자')                                             
    st.markdown('---')
    
    st.markdown('**차트 옵션**')
    show_volume = st.checkbox('거래량 표시', value=True)
    show_bollinger_bands = st.checkbox('볼린저 밴드 표시', value=True)


df = load_stock(symbol, sub_symbol, datestart, dateend)

if df.empty or len(df) < 5:
    st.error("선택된 기간에 충분한 데이터가 없습니다. 기간을 다시 선택해 주세요.")
    st.stop()
    
if df.index.name != 'Date':
    df.index.name = 'Date'

st.header("주식/가상화폐 데이터 및 캔들 차트 시각화")

mav_col1, mav_col2 = st.columns([1, 4])

with mav_col1:
    selected_mavs = st.multiselect(
        "**이동 평균선(MAV) 선택 (일):**",
        options=sorted(MAV_COLORS_MAP.keys()),
        default=DEFAULT_MAV_SETTING
    )
    sorted_mav_settings = sorted(selected_mavs)
    mav_colors = [MAV_COLORS_MAP[m] for m in sorted_mav_settings]


chart_style = 'default'                                            
marketcolors = mpf.make_marketcolors(up='red', down='blue')        
mpf_style = mpf.make_mpf_style(base_mpf_style=chart_style, marketcolors=marketcolors)

with mav_col2:
    st.markdown('**🌈 선택된 이동 평균선 정보**')
    if sorted_mav_settings:
        mav_info_html = ""
        for day, color in zip(sorted_mav_settings, mav_colors):
            mav_info_html += f'<span style="color: {color}; font-weight: bold;">{day}일 MAV</span> &nbsp; '
        st.markdown(mav_info_html, unsafe_allow_html=True)
    else:
        st.info("선택된 이동평균선이 없습니다.")

window = 20
df['MB'] = df['Close'].rolling(window=window).mean()
df['STD'] = df['Close'].rolling(window=window).std()
df['Upper'] = df['MB'] + 2 * df['STD']
df['Lower'] = df['MB'] - 2 * df['STD']

addplots = []
if show_bollinger_bands:
    addplots.extend([
        mpf.make_addplot(df['Upper'], color='blue', linestyle='--'),
        mpf.make_addplot(df['MB'], color='orange', linestyle='--'),
        mpf.make_addplot(df['Lower'], color='blue', linestyle='--')
    ])


st.subheader(f"🕯️ {name} ({sub_symbol}) 캔들 차트")

fig, ax = mpf.plot(
    data=df,                                 
    volume=show_volume,         
    type='candle',                      
    style=mpf_style,                    
    figsize=(12,6),                 
    addplot=addplots,               
    fontscale=1.1,
    mav=tuple(sorted_mav_settings), 
    mavcolors=mav_colors,           
    returnfig=True                      
)

st.pyplot(fig, use_container_width=True)

st.markdown('---')