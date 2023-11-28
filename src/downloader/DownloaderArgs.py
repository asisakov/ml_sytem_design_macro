import argparse
import os


class DownloaderArgs:
    def __init__(self, logging, avail_tickers, avail_intervals):
        self.logging = logging
        self.avail_tickers = avail_tickers
        self.avail_intervals = avail_intervals

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--dir', type=str, help='Direction',
                            choices=['forward', 'backward'],
                            default='forward')

        parser.add_argument('--ticker', type=str, help='Ticker name',
                            choices=self.avail_tickers,
                            default='all')

        parser.add_argument('--interval', type=str, help='Interval',
                            choices=self.avail_intervals,
                            default='1h')

        parser.add_argument('--dry', action='count', default=False,
                            help='Dry run')

        parser.add_argument('--clickhouse-host', type=str,
                            help='Clickhouse host')
        parser.add_argument('--clickhouse-port', type=str,
                            help='Clickhouse port')
        parser.add_argument('--clickhouse-user', type=str,
                            help='Clickhouse user')
        parser.add_argument('--clickhouse-password',
                            type=str, help='Clickhouse password')

        args = parser.parse_args()

        self.validateClickhouseArgs(args)

        self.dir = args.dir
        self.ticker = args.ticker
        self.interval = args.interval
        self.dry = args.dry

    def validateClickhouseArgs(self, args):
        self.clickhouse_host = (args.clickhouse_host
                                or os.environ.get('CLICKHOUSE_HOST'))
        self.clickhouse_port = (args.clickhouse_port
                                or os.environ.get('CLICKHOUSE_PORT'))
        self.clickhouse_user = (args.clickhouse_user
                                or os.environ.get('CLICKHOUSE_USER'))
        self.clickhouse_password = (args.clickhouse_password
                                    or os.environ.get('CLICKHOUSE_PASSWORD'))

        has_error = False
        if not self.clickhouse_host:
            self.logging.error('clickhouse_host is required')
            has_error = True
        if not self.clickhouse_password:
            self.logging.error('clickhouse_password is required')
            has_error = True
        if not self.clickhouse_user:
            self.logging.error('clickhouse_user is required')
            has_error = True
        if not self.clickhouse_port:
            self.logging.error('clickhouse_port is required')
            has_error = True
        if has_error:
            exit(1)
