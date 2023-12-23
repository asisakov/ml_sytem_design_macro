import clickhouse_connect
import logging
import argparse
import os

from YFDownloader import YFDownloader
from DownloaderArgs import DownloaderArgs

logging.basicConfig(level='INFO',
                    format='%(asctime)s\t%(levelname)s\t%(message)s')

AVAIL_TICKERS = ['ALI=F', 'GC=F', 'BTC=F', 'CL=F', 'PL=F',
                 'HG=F', 'BZ=F']
AVAIL_INTERVALS = ['1h', '1d']

Args = DownloaderArgs(logging, AVAIL_TICKERS, AVAIL_INTERVALS)
Args.parse_args()

client = clickhouse_connect.get_client(host=Args.clickhouse_host,
                                       port=int(Args.clickhouse_port),
                                       username=Args.clickhouse_user,
                                       password=Args.clickhouse_password,
                                       database='compredict'
                                       )
YFDl = YFDownloader(logging, client, dry=Args.dry)

tickers = AVAIL_TICKERS
if Args.ticker != 'all':
    tickers = [Args.ticker]

for ticker in tickers:
    if Args.dir == 'forward':
        YFDl.fill_forward(ticker, Args.interval)
    else:
        YFDl.fill_backward(ticker, Args.interval)
