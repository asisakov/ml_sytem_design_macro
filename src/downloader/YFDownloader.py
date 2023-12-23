import yfinance as yf
import clickhouse_connect
import logging

from datetime import datetime, timezone, timedelta


class YFDownloader:
    DRY_MODE = False

    MAX_PERIOD_1H_DAYS = 720
    MAX_PERIOD_1D_DAYS = 365*10

    STOCK_TABLE = 'stock'

    MIN_UPDATE_INTERVAL_FOR_1H_SECS = 3600*8

    def __init__(self, logging, clickhouse_client, dry=False):
        self.logging = logging
        self.clickhouse_client = clickhouse_client
        self.DRY_MODE = dry

    def get_min_update_interval(self, interval):
        if interval == '1h':
            return self.MIN_UPDATE_INTERVAL_FOR_1H_SECS
        if interval == '1d':
            return self.MIN_UPDATE_INTERVAL_FOR_1H_SECS

        raise RuntimeError(f'Unsupported interval {interval}')

    def get_max_period(self, interval):
        if interval == '1h':
            return self.MAX_PERIOD_1H_DAYS
        if interval == '1d':
            return self.MAX_PERIOD_1D_DAYS

        raise RuntimeError(f'Unsupported interval {interval}')

    def get_date_boundaries(self, ticker, interval):
        params = {'table': self.STOCK_TABLE,
                  'ticker': ticker, 'interval': interval}
        res = (self.
               clickhouse_client
               .query('''SELECT
                                min(ts),
                                max(ts)
                            FROM
                                {table:Identifier}
                            WHERE
                                stock_name = {ticker:String}
                                AND
                                interval = {interval:String}
                            ''',
                      params))
        return res.result_rows[0]

    def download_ticker(self, ticker, start, end, interval):
        self.logging.info(f'Start downloading {ticker}/{interval}'
                          + f' from {start} to {end}')
        data = yf.download(tickers=ticker,
                           start=start, end=end,
                           interval=interval)
        self.logging.info(f'Downloaded {len(data)}')
        row_data = []
        for ts in data.index:
            row = [ticker, interval, ts]
            for name in ['Open', 'High', 'Low',
                         'Close', 'Adj Close', 'Volume']:
                row.append(str(data[name][ts]))
            row_data.append(row)
        return row_data

    def calculate_yf_period(self, max_ts, interval):
        now_ts = datetime.now(timezone.utc)
        delta = now_ts - max_ts
        if delta.days <= 0:
            raise Exception(f'delta {delta.days} <= 0')

        if delta.days < MAX_PERIOD_1H_DAYS:
            return f'{delta.days}d'

        raise Exception(f'delta {delta.days} > max {MAX_PERIOD_1H_DAYS}')

    def insert_into_clickhouse(self, data):
        return self.clickhouse_client.insert(self.STOCK_TABLE,
                                             data, database='compredict',
                                             column_names=[
                                                           'stock_name',
                                                           'interval',
                                                           'ts',
                                                           'open', 'high',
                                                           'low', 'close',
                                                           'adj_close',
                                                           'volume'
                                                          ]
                                             )

    def fill_forward(self, ticker, interval):
        min_ts, max_ts = self.get_date_boundaries(ticker, interval)
        now_ts = datetime.now(timezone.utc)
        delta = now_ts - max_ts

        logging.info(f'{ticker}/{interval} last date: {max_ts}'
                     + f', delta days: {delta.days}'
                     + f', delta seconds: {delta.total_seconds()}')

        if max_ts.timestamp() == 0:
            self.logging.warning(f'Skip filling forward {ticker}/{interval}'
                                 + ', boundary doesn`t exist')
            return

        min_update_interval = self.get_min_update_interval(interval)
        if delta.total_seconds() <= min_update_interval:
            self.logging.info(f'Skip filling forward {ticker}/{interval}'
                              + f', delta {delta.total_seconds()}'
                              + f' <= {min_update_interval}')
            return

        if delta.days >= self.MAX_PERIOD_1H_DAYS:
            self.logging.info(f'Skip filling forward {ticker}/{interval}'
                              + f', delta {delta.days}'
                              + f'>= {MAX_PERIOD_1H_DAYS}')
            return

        if self.DRY_MODE:
            self.logging.info('Skip download in dry mode')
            return

        data = self.download_ticker(ticker=ticker, interval=interval,
                                    start=max_ts, end=now_ts)

        filtered = [r for r in data
                    if r[2].replace(tzinfo=timezone.utc) > max_ts]

        self.logging.info(f'Filtered out {len(filtered)} of {len(data)}')

        self.insert_into_clickhouse(filtered)

    def fill_backward(self, ticker, interval):
        min_ts, max_ts = self.get_date_boundaries(ticker, interval)
        now_ts = datetime.now(timezone.utc)

        if min_ts.timestamp() > now_ts.timestamp():
            logging.warn(f'Skip filling backward {ticker}/{interval}'
                         + f', min date {min_ts} is in future.')
            return

        max_allowed_delta = timedelta(days=self.get_max_period(interval))

        lower_bound = now_ts - max_allowed_delta
        upper_bound = min_ts
        if upper_bound.timestamp() == 0:
            upper_bound = now_ts

        logging.info(f'{ticker}/{interval} lower bound: {lower_bound}'
                     + f', upper bound: {upper_bound}')

        delta = upper_bound - lower_bound
        min_update_interval = self.get_min_update_interval(interval)
        if delta.total_seconds() <= min_update_interval:
            self.logging.info(f'Skip filling backward {ticker}/{interval}'
                              + f', delta {delta.total_seconds()}'
                              + f' <= {min_update_interval}')
            return

        if self.DRY_MODE:
            self.logging.info('Skip download in dry mode')
            return

        data = self.download_ticker(ticker=ticker, interval=interval,
                                    start=lower_bound, end=upper_bound)

        filtered = [r for r in data
                    if r[2].replace(tzinfo=timezone.utc) < upper_bound]

        self.logging.info(f'Filtered out {len(filtered)} of {len(data)}')

        self.insert_into_clickhouse(filtered)
