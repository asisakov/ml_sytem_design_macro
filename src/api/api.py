import clickhouse_connect
import logging

from fastapi import FastAPI, Response
from ApiArgs import ApiArgs
from datetime import date, timedelta
from typing import Literal
from StockNames import getStockNamesEnum


logging.basicConfig(level='INFO',
                    format='%(asctime)s\t%(levelname)s\t%(message)s')

app = FastAPI()
Args = ApiArgs()

client = clickhouse_connect.get_client(host=Args.clickhouse_host,
                                       port=int(Args.clickhouse_port),
                                       username=Args.clickhouse_user,
                                       password=Args.clickhouse_password,
                                       database='compredict'
                                       )


@app.get("/")
async def root():
    return {"message": f"Hi!"}


@app.get("/history/{stock_name}/{timeframe}")
async def history(stock_name: getStockNamesEnum(client),
                  timeframe: Literal['1h', '1d'],
                  date_from: date = None, date_to: date = None):
    """ Returns commodity history data """

    if date_to is None:
        date_to = date.today()
    if date_from is None or date_from > date_to:
        delta = timedelta(days=2)
        date_from = date_to - delta

    params = {
              'stock_name': stock_name,
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
