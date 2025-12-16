import streamlit as st
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

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
        lis = {'Crypto': ['BTC/KRW', 'ETH/KRW', 'XRP/KRW', 'BTC/USD', 'ETH/USD', 'XRP/USD']}
        lis_indexed = pd.DataFrame(lis, index = ['비트코인/빗썸', '이더리움/빗썸', '리플/빗썸', '비트코인/Bitfinex', '이더리움/Bitfinex', '리플/Bitfinex'])
    return lis_indexed

def load_stock(symbol='KRX', subsymbol='005930', datestart=(datetime.today()-timedelta(days=30)).date(), dateend=datetime.today().date()):
    if symbol in ['KRX', 'KOSPI', 'KOSDAQ', 'KONEX']:
        df = fdr.DataReader(subsymbol, datestart, dateend ).drop(columns='Change')
    elif symbol in ['NASDAQ', 'NYSE', 'AMEX', 'S&P500']:
        df = fdr.DataReader(subsymbol, datestart, dateend).drop(columns='Adj Close')
    else:
        df = fdr.DataReader(subsymbol, datestart, dateend).drop(columns='Adj Close')
    return df

with st.sidebar:
    st.title('종목 선택')
    symbol = st.selectbox('거래소 선택', ['KRX','KOSPI', 'KOSDAQ', 'KONEX', 'NASDAQ', 'NYSE', 'AMEX', 'CRYPTO'])
    lis = load_list(symbol)
    name_list = lis.index.tolist()
    '''
    ---
    '''
    name = st.selectbox('종목 선택', name_list)
    row = lis.loc[name]
    sub_symbol = row.iloc[0]
    '''
    ---
    '''
    '기간 선택'
    datestart = st.date_input('시작 날자', value = datetime.today()-timedelta(days=30)) #초기값 = 30일 전
    dateend = st.date_input('종료 날자')                                                #초기값 = 오늘
    df = load_stock(symbol, sub_symbol, datestart, dateend)



window = 20

        
df['MB'] = df['Close'].rolling(window=20).mean()
df['STD'] = df['Close'].rolling(window=20).std()

df['Upper'] = df['MB'] + 2 * df['STD']
df['Lower'] = df['MB'] - 2 * df['STD']

addplots = [
    mpf.make_addplot(df['Upper'], color='blue'),
    mpf.make_addplot(df['MB'], color='orange'),
    mpf.make_addplot(df['Lower'], color='blue')
]




chart_style = 'default'                                            
marketcolors = mpf.make_marketcolors(up='red', down='blue')        
mpf_style = mpf.make_mpf_style(base_mpf_style=chart_style, marketcolors=marketcolors)


fig, ax = mpf.plot(
    data=df,                                 
    volume=True,                                       
    type='candle',                      
    style=mpf_style,                    
    figsize=(10,7),
    mav=(5,10,30),
    addplot=addplots,
    fontscale=1.1,
                          
    mavcolors=('red','green','blue'),   
    returnfig=True                      
)

st.pyplot(fig)