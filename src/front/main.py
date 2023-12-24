import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from moexalgo import Ticker
import plotly.graph_objects as go
import pandas_ta as ta
import matplotlib.pyplot as plt
import statsmodels.api as sm
from dotenv import load_dotenv

import clickhouse_connect
from FrontArgs import FrontArgs

load_dotenv()

st.title('График commodity')

Algo_strategy, tech_indicator = st.tabs([ "Стратегия с бэктестом",  "Идеи для инвестора"])
with Algo_strategy:

    # Клиент создаётся внутри with для избежания ошибок concurrency
    Args = FrontArgs()
    client = clickhouse_connect.get_client(host=Args.clickhouse_host,
                                           port=int(Args.clickhouse_port),
                                           username=Args.clickhouse_user,
                                           password=Args.clickhouse_password,
                                           database='compredict')

    stocks = ('ALI=F', 'BTC=F', 'GC=F')
    selected_stock = st.selectbox("Выбор commodity", stocks)
    #ticker = st.sidebar.text_input('Выбор акции')
    start_date = st.sidebar.date_input('Начальная дата', value = pd.to_datetime('2022-05-02'))
    end_date = st.sidebar.date_input('Конечная дата', value = pd.to_datetime('today'))
    fast_ma = st.sidebar.number_input('Введите значение быстрой МА',value = 20)
    slow_ma = st.sidebar.number_input('Введите значение медленной МА',value = 40)
    ls_ma = st.sidebar.number_input('Введите значение регрессионной МА',value = 20)
    unique_models = st.sidebar.selectbox("Выберите модель прогноза",
        ("ProphetModel"))
    unique_run_dates = client.query_df('''SELECT
        distinct run_date
    FROM forecast
    WHERE
        interval = '1d'
        AND
        stock_name = {stock_name:String}
    ''', {'stock_name': selected_stock})

    run_date = st.sidebar.selectbox("Выберите дату прогноза",
        tuple(unique_run_dates.values))

    run_date = run_date[0]


    df = client.query_df('''SELECT
        open,
        close,
        high,
        low,
        volume,
        ts AS begin
    FROM stock
    WHERE
        interval = '1d'
        AND
        stock_name = {stock_name:String}
        AND
        ts BETWEEN {start_date:DateTime} AND {end_date:DateTime}
    ORDER BY ts ASC
    ''', {'stock_name': selected_stock, 'start_date': start_date, 'end_date': end_date})

    predictions = client.query_df('''SELECT
        forecast_date,
        forecast_value
    FROM forecast
    WHERE
        interval = '1d'
        AND
        stock_name = {stock_name:String}
        AND
        run_date = {run_date:DateTime('UTC')}
    ORDER BY forecast_date ASC
    ''', {'stock_name': selected_stock, 'run_date': run_date})
    #print(df)
    #df= s.candles(date=start_date,till_date = end_date, period='D')#sber.candles(date='2020-01-01',till_date = '2023-12-05', period='D')
    #df = global_df
    #df= pd.DataFrame(df)
    #df1= df['close']
    #st.dataframe(df)
    #st.line_chart(df)
    df = df.set_index('begin')
    df['fast_ma'] = df['close'].rolling(window=fast_ma).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_ma).mean()
    #LSMA
    period = ls_ma
    LSMA = []
    Dates = []

    for i in range(len(df)-(period-1)):
        input_reg = df[i:period+i]
        X = pd.Series(range(len(input_reg.index))).values
        y = input_reg.close
        model = sm.OLS(y, sm.add_constant(X)).fit()
        pred = model.predict()[-1]
        LSMA.append(pred)
        Dates.append(input_reg.iloc[-1].name)

    LSMA_df = pd.DataFrame({'LSMA':LSMA}, index = Dates)
    LSMA_df =LSMA_df['LSMA'].shift(1)
    df = pd.concat([df,LSMA_df], axis=1 )
    #df =df.dropna()
    #Для маркера покупки продажи
    bd=pd.DataFrame()#создаю промежуточную базу для сигналоа по ма
    bd['close']=df['close']
    bd['fast_ma']= df['fast_ma']
    bd['slow_ma'] = df['slow_ma']
    def buy_sell(day_df):         # функция сигналов покупки продажи
        signal_price_buy = []
        signal_price_sell = []
        flag = -1
        for i in range(len(day_df)):
            if day_df['fast_ma'][i]> day_df['slow_ma'][i]:
                if flag !=1:
                    signal_price_buy.append(day_df['close'][i])
                    signal_price_sell.append(np.nan)
                    flag = 1
                else:
                    signal_price_buy.append(np.nan)
                    signal_price_sell.append(np.nan)
            elif day_df['fast_ma'][i] < day_df['slow_ma'][i]:
                if flag != 0:
                    signal_price_buy.append(np.nan)
                    signal_price_sell.append(day_df['close'][i])
                    flag = 0
                else:
                    signal_price_buy.append(np.nan)
                    signal_price_sell.append(np.nan)
            else:
                signal_price_buy.append(np.nan)
                signal_price_sell.append(np.nan)
        return(signal_price_buy, signal_price_sell)

    buy_sell = buy_sell(bd)
    df['buy_signal'] = buy_sell[0] # добавляю в основной датафрейм
    df['sell_signal'] = buy_sell[1]
    #st.write(df)
    #Backtest
    df['pct_change'] = df['close'].pct_change()
    df['Strategy'] = df['pct_change']*(df['fast_ma']>df['slow_ma']) - df['pct_change']*(df['fast_ma']<df['slow_ma']) # реализация торговой системы покупка продажа
    #df =df.dropna()
    df = df.drop(df.index[0:slow_ma-1])
    fig = go.Figure(data=[go.Candlestick(x=df.index, open = df['open'], high = df['high'], low = df['low'], close=df['close'], name= 'Candlestick'),
                          go.Scatter(x=df.index, y=df['fast_ma'], line=dict(color='orange', width=1), name='MA Fast' ),
                          go.Scatter(x=df.index, y=df['close'], line=dict(color='blue', width=2), name='Close' ),
                          go.Scatter(x=df.index, y=df['LSMA'], line=dict(color='black', width=1), name='LSMA' ),
                          go.Scatter(x=df.index, y=df['buy_signal'], mode="markers" , marker=dict(color='green', size = 5), name='Buy' ),
                          go.Scatter(x=df.index, y=df['sell_signal'], mode="markers" , marker=dict(color='red', size = 5), name='Sell' ),
                          go.Scatter(x=df.index, y=df['slow_ma'], line=dict(color='green', width=1), name='MA Slow' ),
                          go.Scatter(x=predictions.forecast_date, y=predictions.forecast_value, line=dict(color='red', width=2), name='Model Prediction' ),])
    fig.update_layout(autosize=True)#, width = 1400,height=800
    st.write('Графики факта и прогноза')
    st.plotly_chart(fig)
    st.write('Дневная доходность в процентах')
    st.line_chart(df['Strategy']*100)#np.cumprod(1+day_df['STRATEGY'])
    st.write('Доходность за указанный период в процентах')
    st.line_chart(df['Strategy'].cumsum()*100)#(np.cumprod(1+df['Strategy']))
    #Улучшение стратегии
    day_df1 = df.reset_index() #создаю доп дф для вычеслений
    def buy_sell_df(df):
        buy_sell_1 = pd.DataFrame(columns=['DATA', 'close', 'signal']) # создали пустой датафрейм  с именами колонок
        signal_price_buy = []
        signal_price_sell = []
        flag = -1
        for i, j in df.iterrows():
            if df['fast_ma'][i]> df['slow_ma'][i]:
                if flag !=1:
                    data = j[0]
                    close=df['close'][i]
                    signal = 'buy'
                    new_row = {'DATA': data, 'close': close, 'signal': signal}
                    #buy_sell_1 = buy_sell_1.append(new_row, ignore_index=True)
                    buy_sell_1 = pd.concat([buy_sell_1, pd.DataFrame([new_row])], ignore_index=True)
                    flag = 1
                else:
                    signal_price_buy.append(np.nan)
                    signal_price_sell.append(np.nan)
            elif df['fast_ma'][i] < df['slow_ma'][i]:
                if flag != 0:
                    data = j[0]
                    close=df['close'][i]
                    signal = 'sell'
                    new_row = { 'DATA': data, 'close': close, 'signal': signal}
                    # buy_sell_1 = buy_sell_1.append(new_row, ignore_index=True)
                    buy_sell_1 = pd.concat([buy_sell_1, pd.DataFrame([new_row])], ignore_index=True)
                    flag = 0
                else:
                    signal_price_buy.append(np.nan)
                    signal_price_sell.append(np.nan)
            else:
                signal_price_buy.append(np.nan)
                signal_price_sell.append(np.nan)
        return(buy_sell_1)
    aa=buy_sell_df(day_df1)
    index=0  # ЗДЕСЬ  ЗАПИСЫВАЮ В ДАТАФРЕЙМ В ОДНУ СТРОКУ  СИГНАЛ ПОКУПКИ И ПРОДАЖИ ДЛЯ КОНФЬЮЖИН МАТРИКС
    open_pos = 0
    position = pd.DataFrame(columns=['data_open_pos', 'price_open_pos', 'signal','price_close_pos', 'data_close_pos'])
    for i, j in aa.iterrows():
        if index == 0:
            open_pos = j[1]
            data_open_pos = j[0]
            signal = j[2]
            index = index+1
        elif index == 1:
            close_pos =j[1]
            data_close_pos=j[0]
            new_row = { 'data_open_pos': data_open_pos, 'price_open_pos': open_pos, 'signal': signal, 'price_close_pos' : close_pos, 'data_close_pos' : data_close_pos}
            #position = position.append(new_row, ignore_index=True)
            position = pd.concat([position, pd.DataFrame([new_row])], ignore_index=True)
            index = 0
    #st.write(position)
    position['label']=np.nan
    for  i, j in position.iterrows():
        if position['price_open_pos'][i]< position['price_close_pos'][i]:
            position['label'][i] = 1 # мы угадали с навправлением и позиция сгенерила доход
        else:
            position['label'][i]=-1 # мы не верно предсказали напрвление движения цены
    position['income'] = (1-position['price_close_pos']/position['price_open_pos'])*(-100) # стратегия работаем только от покупок
    #st.line_chart(position['income'])
    #st.write(position)
    #fig = px.line(df, x = df.index , y = df['close'], title ='ticker')
    # figg = go.Figure(data=[go.Candlestick(x=df.index, open = df['open'], high = df['high'], low = df['low'], close=df['close'])])
    # st.plotly_chart(figg)
#tech_indicator, pricing_data = st.tabs(["Indicator", "pr_dt"])

    df['Cum_sum']=df['pct_change'].cumsum()*100
    def risk_val(row):
        if row['Cum_sum']<=-5:
            return -5
        else:
            return row['Cum_sum']
    df['risk'] = df.apply(risk_val, axis=1)
    st.write('Доходность с учетом риск менеджмента, закрываем позиции если убыток по ним >=5%')
    st.line_chart(df['risk']*1000)
    #st.dataframe(df)
with tech_indicator:
    #st.subheader('Algo')
    dff=pd.DataFrame()
    ind_list = dff.ta.indicators(as_list = True)
    #st.write(ind_list)
    #llenght= st.slider('lenght', min_value=1, max_value=1500, value=20)
    tech_indicatorr = st.selectbox('Выберите технический индикатор/стратегию',options=ind_list)

    method = tech_indicatorr
    indicator = pd.DataFrame(getattr(ta,method)(low=df['low'], close=df['close'], high = df['high'], opne = df['open'], volume = df['volume']))
    indicator['Close']= df['close']
    #st.write(indicator)
    fig_ind = px.line(indicator)
    st.plotly_chart(fig_ind)
