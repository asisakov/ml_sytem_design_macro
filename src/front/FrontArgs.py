import argparse
import os
import logging


class FrontArgs:
    def __init__(self):
        self.logging = logging
        self.validateClickhouseArgs()

    def validateClickhouseArgs(self):
        self.clickhouse_host = os.environ.get('CLICKHOUSE_HOST')
        self.clickhouse_port = os.environ.get('CLICKHOUSE_PORT')
        self.clickhouse_user = os.environ.get('CLICKHOUSE_USER')
        self.clickhouse_password = os.environ.get('CLICKHOUSE_PASSWORD')

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

