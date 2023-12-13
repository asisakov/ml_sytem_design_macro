import clickhouse_connect
import logging
from FrontArgs import FrontArgs

Args = FrontArgs()
client = clickhouse_connect.get_client(host=Args.clickhouse_host,
                                       port=int(Args.clickhouse_port),
                                       username=Args.clickhouse_user,
                                       password=Args.clickhouse_password,
                                       database='compredict'
                                       )
