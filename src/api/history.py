from fastapi import APIRouter, Response
from clickhouse import client
from StockNames import getStockNamesEnum
from typing import Literal
from datetime import date, timedelta

router = APIRouter()


@router.get("/history/stocks")
def stocks():
    res = client.raw_query('''
                           SELECT
                               stock_name,
                               interval,
                               min(ts) as min_ts,
                               max(ts) as max_ts,
                               count() as cnt
                            FROM
                                stock
                            GROUP BY
                                stock_name,
                                interval
                           ''',
                           fmt='JSON'
                           )
    return Response(content=res, media_type='application/json')


@router.get("/history/{stock_name}/{timeframe}")
def history(stock_name: getStockNamesEnum(client),
            timeframe: Literal['1h', '1d'],
            date_from: date = None, date_to: date = None):
    """ Returns commodity history data """

    if date_to is None:
        date_to = date.today()
    if date_from is None or date_from > date_to:
        delta = timedelta(days=2)
        date_from = date_to - delta

    params = {
              'stock_name': stock_name.value,
              'timeframe': timeframe,
              'date_from': date_from,
              'date_to': date_to,
              }

    res = client.raw_query('''
                           SELECT
                             *
                           FROM
                             stock
                           WHERE
                             stock_name = {stock_name:String}
                             AND
                             interval = {timeframe:String}
                             AND
                             ts BETWEEN
                                 {date_from:DateTime}
                                 AND
                                 {date_to:DateTime}
                             ORDER BY ts ASC
                            ''',
                           parameters=params,
                           fmt="JSON"
                           )
    return Response(content=res, media_type='application/json')
