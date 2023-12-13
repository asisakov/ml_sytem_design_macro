import click
import clickhouse_connect
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import logging
import os


# TBD: switch back click
# @click.command()
# @click.argument("stock_name", type=str)
# @click.argument("timeframe", type=str)
# @click.argument("out_file_path", type=click.Path(), default="../../data/interim/stockdata.csv.gz")
# @click.argument("column_for_timestamp", type=str, default="ts")
def create_dataset_for_stock(
    stock_name: str,
    timeframe: str,
    out_file_path: str,
    column_for_timestamp: str
):
    """
    Loads the required data from clickhouse, writes the obtained data to specified file.
    """
    logger = logging.getLogger(__name__)

    try:

        logger.info("Reading creds from .env file")
        clickhouse_host = os.getenv("CLICKHOUSE_HOST")
        clickhouse_port = int(os.getenv("CLICKHOUSE_PORT"))
        clickhouse_db = os.getenv("CLICKHOUSE_DB")
        clickhouse_user = os.getenv("CLICKHOUSE_USER")
        clickhouse_password = os.getenv("CLICKHOUSE_PASSWORD")

        logger.info("Create connection to ClickHouse")
        client = clickhouse_connect.get_client(
            host=clickhouse_host,
            port=clickhouse_port,
            database=clickhouse_db,
            username=clickhouse_user,
            password=clickhouse_password
        )

        logger.info(f"Start loading data from ClickHouse for {stock_name=} and {timeframe=}")
        df = client.query_df(
            f'''
            SELECT
                *
            FROM
                stock
            WHERE
                stock_name='{stock_name}'
                AND
                interval='{timeframe}'
           '''
        )

        assert isinstance(df, pd.DataFrame)
        logger.info(f"Got dataframe with shape: {df.shape}")
        if df.empty:
            raise Exception(f"Empty dataframe received for {stock_name=} and {timeframe=}.")

        df.set_index(column_for_timestamp, drop=True, inplace=True,)
        # TBD: find the code for checking datetime

        # Write to output file with possible compression (according to file extension)
        out_file_abs_path = os.path.abspath(out_file_path)
        df.to_csv(out_file_abs_path, compression="infer")
        logger.info(f"Saved dataframe to file : {out_file_abs_path}")

    except Exception as e:
        logger.error(f"Exception in create_dataset_for_stock; main params: {stock_name=}, {timeframe=}, "
                     f"{column_for_timestamp=}. Details: %s", e)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    # create_dataset_for_stock() TBD
