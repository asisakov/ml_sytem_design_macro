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
    model_name: str,
    col_for_timestamp: str = "timestamp",
    col_for_prediction: str = "prediction"
):
    """
    Loads pandas dataframe with predictions from the specified file, and uploads it to clickhouse.
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
        df = pd.read_csv(src_file_path, parse_dates=[col_for_timestamp])
        logger.info(f".. loaded df shape: {df.shape}")

        logger.info(f"Preparing columns")
        # Rename columns with prediction to ClickHouse table fields
        assert col_for_timestamp in df.columns
        assert col_for_prediction in df.columns
        df.rename({col_for_timestamp: "forecast_date"}, axis="columns", inplace=True)
        df.rename({col_for_prediction: "forecast_value"}, axis="columns", inplace=True)
        # Insert additional metadata columns
        df['stock_name'] = stock_name
        df['interval'] = timeframe
        df['run_date'] = datetime.now(timezone.utc)
        df["model_name"] = model_name

        # Ensure that the pushed dataframe does not contain extra columns
        assert len(df.columns) == 6
        # TBD: change this approach to dataclass
        # TBD: load column names from config (question: how to map column and values in config?)
        # Example:
        # my_columns = config.output_table_columns
        # assert len(my_columns) == len(df.columns)
        # assert set(my_columns) == set(df.columns)

        logger.info(f"Pushing dataframe with shape: {df.shape} to CLickHouse")
        client.insert_df('forecast', df)

        logger.info(f"Reading data back, just for checking")
        df2: pd.DataFrame = client.query_df(
            f'''
            SELECT
                *
            FROM
                forecast
           '''
        )
        logger.info(f"Shape of read data: {df2.shape}")
        # In debug mode - show head and tail of the current ClickHouse table
        if logger.isEnabledFor(logging.DEBUG):
            df2.sort_values(by=["run_date", "forecast_date"], inplace=True)
            # Tell pandas to show all columns without width limitations
            opt_name = "display.max_columns"
            val_before = pd.get_option(opt_name)
            pd.set_option(opt_name, None)
            logger.debug(f"Head of read data:\n{df2.head()}")
            logger.debug(f"Tail of read data:\n{df2.tail()}")
            # Restore the setting
            pd.set_option(opt_name, val_before)


    except Exception as e:
        logger.error(f"Exception in push_dataset. Details: %s", e)
