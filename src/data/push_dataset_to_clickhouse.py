from datetime import datetime, timezone

import clickhouse_connect
import pandas as pd
import logging
import os


# TBD: switch back click
def push_dataset(
    src_file_path: str,
    stock_name: str,
    timeframe: str,
    model_name: str
):
    """
    Loads the required data from clickhouse, writes the obtained data to specified file. TBD: fix this
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

        logger.info(f"Reading predictions from the specified file ..")
        df = pd.read_csv(src_file_path, parse_dates=["timestamp"])  # TBD:, parse_dates=[])
        logger.info(f".. loaded df shape: {df.shape}")

        logger.info(f"Preparing columns")
        # Rename columns with prediction to ClickHouse table fields
        df.rename({"timestamp": "forecast_date"}, axis="columns", inplace=True)
        df.rename({"prediction": "forecast_value"}, axis="columns", inplace=True)
        # Insert additional metadata columns
        df['stock_name'] = stock_name
        df['interval'] = timeframe
        df['run_date'] = datetime.now(timezone.utc)
        df["model_name"] = model_name

        # Ensure that the pushed dataframe does not contain extra columns
        assert len(df.columns) == 6

        logger.info(f"Pushing dataframe with shape: {df.shape} to CLickHouse")
        client.insert_df('forecast', df)

        logger.info(f"Reading data back, just for checking")
        df2 = client.query_df(
            f'''
            SELECT
                *
            FROM
                forecast
           '''
        )
        logger.info(f"Shape of read data: {df2.shape}")


    except Exception as e:
        logger.error(f"Exception in push_dataset. Details: %s", e)
