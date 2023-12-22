import click
import clickhouse_connect
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import logging
import os


def create_dataset_for_stock(
    stock_name: str,
    timeframe: str,
    out_file_path: str,
    column_for_timestamp: str,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Loads the required data from clickhouse, writes the obtained data to the specified file.
    :param stock_name: Identifier of instrument. Example: "ALI=F" (futures for aluminium).
    :param timeframe:  Data period. Example: "1h" for hourly candles.
    :param out_file_path: Optional path for output file. If None, saving will be skipped.
    :param column_for_timestamp: Name of ClickHouse column containing timestamps for the data
    :param verbose: Whether to dump debugging info to the log.
    :return: resulting DataFrame with data
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

        df.set_index(column_for_timestamp, drop=True, inplace=True)
        # TBD: find code for checking datetime

        # Sort by timestamp
        df.sort_index(inplace=True, axis="rows")

        # Debug dumps, if required
        if verbose:
            logger.debug(f"df.head:\n{df.head}")
            logger.debug(f"df.tail:\n{df.tail}")

        # If required - write to output file with possible compression (according to file extension)
        if out_file_path != "":
            out_file_abs_path = os.path.abspath(out_file_path)
            df.to_csv(out_file_abs_path, compression="infer")
            logger.info(f"Saved dataframe to file : {out_file_abs_path}")
        else:
            logger.info(f"Saved dataframe to file is skipped due to empty out_file_path param")

        return df

    except Exception as e:
        logger.error(f"Exception in create_dataset_for_stock; main params: {stock_name=}, {timeframe=}, "
                     f"{column_for_timestamp=}. Details: %s", e)
        raise  # Re-rase the exception


@click.command()
@click.option("--stock_name", type=str, default="ALI=F")
@click.option("--timeframe", type=str, default="1h")
@click.option("--out_file_path", type=click.Path(), default="../../data/interim/stockdata.csv.gz")
@click.option("--column_for_timestamp", type=str, default="ts")
@click.option("--verbose", type=bool, default=False)
def create_dataset_for_stock__cli(
    stock_name: str,
    timeframe: str,
    out_file_path: str,
    column_for_timestamp: str,
    verbose: bool
):
    """
    CLI wrapper. Parses command-line params and calls the main function
    """
    create_dataset_for_stock(stock_name, timeframe, out_file_path, column_for_timestamp, verbose)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    create_dataset_for_stock__cli()
