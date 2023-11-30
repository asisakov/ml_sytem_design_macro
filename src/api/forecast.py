from fastapi import APIRouter, Response
from clickhouse import client
from StockNames import getForecastStockNamesEnum, getForecastModelNamesEnum
from typing import Literal
from datetime import datetime

router = APIRouter()


@router.get("/forecast/stocks")
def stocks():
    """ Get info about available forecasts and model names """
    res = client.raw_query('''
                           SELECT
                               stock_name,
                               interval,
                               model_name,
                               run_date,
                               count() as cnt
                            FROM
                                forecast
                            GROUP BY
                                stock_name,
                                interval,
                                model_name,
                                run_date
                           ''',
                           fmt='JSON'
                           )
    return Response(content=res, media_type='application/json')


@router.get("/forecast/{stock_name}/{timeframe}/{model_name}")
def forecast(stock_name: getForecastStockNamesEnum(client),
             model_name: getForecastModelNamesEnum(client),
             timeframe: Literal['1h', '1d'],
             run_date: datetime = None):
    """ Returns commodity forecast """

    params = {
              'stock_name': stock_name.value,
              'model_name': model_name.value,
              'timeframe': timeframe,
              }

    q = '''
           SELECT
             *
           FROM
             forecast
           WHERE
             stock_name = {stock_name:String}
             AND
             interval = {timeframe:String}
             AND
             model_name = {model_name:String}
         '''

    if run_date:
        params['run_date'] = run_date
        q += '''
             AND
             run_date = {run_date:String}
             '''

    q += '''
            ORDER BY forecast_date ASC
         '''

    res = client.raw_query(q,
                           parameters=params,
                           fmt="JSON"
                           )
    return Response(content=res, media_type='application/json')
