import time
import pyupbit
import datetime
import pandas as pd

access = "access"
secret = "secret"


def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.5
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_ma60(ticker):
    """60일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=60)
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    return ma60


def get_ma20(ticker):
    """20일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    return ma20


def coin_selection():
    """투자 코인 선별"""
    items = pyupbit.get_tickers()
    item = []
    for i in items:
        if 'KRW' in i:
            item.append(i)
    selc_coin = []
    for j in items:
        current = float(pyupbit.get_ohlcv(j,interval="day", count=1)['open'])
        if current > get_ma20(j) > get_ma60(j):
            selc_coin.append(j)
    return selc_coin


def get_dataframe(ticker_list):
    """현재가격,매수가격 데이터프레임"""
    price = []
    for i in ticker_list:
        price.append(pyupbit.get_current_price(i))
    target = []
    for i in ticker_list:
        target.append(get_target_price(i))
    dict = {'price': price, 'target': target}
    return pd.DataFrame(dict, index=ticker_list)


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #9:00
        end_time = start_time + datetime.timedelta(days=1)

        selc_coin = coin_selection() #코인선택
        df = get_dataframe(selc_coin) #각코인의 현재가격,목표매수가 저장

        buy_coin = "" #매수한종목저장
        if start_time < now < end_time - datetime.timedelta(minutes=5):
            buy_item = list(df.loc[df['price'] >= df['target']].index) #매수종목반환
            if bool(buy_item):
                buy_coin = buy_item[0]
                krw = get_balance("KRW") #원화잔고조회
                if krw > 5000:
                    upbit.buy_market_order(buy_coin, krw * 0.9995)
        else:
            btc = get_balance(buy_coin)
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc * 0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)