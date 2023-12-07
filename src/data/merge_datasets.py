# import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import logging
import os


def _select_and_rename_df_columns(
    df: pd.DataFrame,
    columns_to_process: tuple[str],
    column_for_stock_name: str
):
    assert not df.empty
    stock_name = df[column_for_stock_name].iloc[0]
    df = df[list(columns_to_process)]  # Have to convert column names from tuple to list
    rename_dict = {x: f"{x}_{stock_name}" for x in columns_to_process}
    df = df.rename(rename_dict, axis="columns")
    return df


# TBD: switch back click
# @click.command()
# @click.argument("stock_name", type=str)
# @click.argument("timeframe", type=str)
# @click.argument("out_file_path", type=click.Path(), default="../../data/interim/stockdata.csv.gz")
# @click.argument("column_for_timestamp", type=str, default="ts")
def merge_datasets_from_files(
    src_file_list: list[str],
    src_data_timeframe: str,
    out_file_path: str,
    columns_to_process: tuple[str] = ("adj_close", ),
    column_for_timestamp: str = "ts",
    column_for_stock_name: str = "stock_name"
):
    """
    Merges specified files into single dataframe.
    :param src_file_list: File names to process. The first file in the list is considered as "target" stock
    :param src_data_timeframe:
    :param out_file_path:
    :param columns_to_process: # Names of columns to leave after loading
    :param column_for_timestamp:
    :param column_for_stock_name:
    :return:
    """
    logger = logging.getLogger(__name__)

    try:

        # Check input params
        if len(src_file_list) < 2:
            raise ValueError(f"Unexpected number of source files (should be >= 2): {len(src_file_list)}")

        logger.info("Reading data from the files")
        df_list: list[pd.DataFrame] = []
        common_start_datatime = None
        for f in src_file_list:
            # Read the data
            src_data_abs_file_path = os.path.abspath(f)
            logger.info(f"Reading data from file {src_data_abs_file_path}")
            # TBD: handle if file not found
            df_tmp = pd.read_csv(src_data_abs_file_path, index_col=column_for_timestamp,
                                 parse_dates=[column_for_timestamp])
            logger.info(f".. loaded data shape: {df_tmp.shape}")
            if df_tmp.empty:
                raise ValueError(f"The specified data file seems to be empty: {src_data_abs_file_path}")

            # Leave only required columns and rename them.
            df_tmp = _select_and_rename_df_columns(df_tmp, columns_to_process=columns_to_process,
                                                   column_for_stock_name=column_for_stock_name)
            logger.info(f".. shape after column renaming: {df_tmp.shape}")

            # Resample the data to fill missing candles, and forward-fill the gaps (including nans if any)
            df_tmp = df_tmp.resample(rule=src_data_timeframe).ffill()
            # Ensure that the data is sorted by timestamp
            assert df_tmp.index.is_monotonic_increasing, "Dates in the data should be monotonically increasing"
            # Replace remaining nans to previous good values (rarely occurred)
            df_tmp = df_tmp.ffill()

            # Update common_start_datatime (at this time point data in all dataframes should exit)
            df_start_dt = df_tmp.index.min()
            if (common_start_datatime is None) or (common_start_datatime < df_start_dt):
                common_start_datatime = df_start_dt

            df_list.append(df_tmp)

        assert len(df_list) > 1

        # Process start of all dataframes
        for i in range(len(df_list)):
            df = df_list[i]
            df_list[i] = df[df.index >= common_start_datatime]
            logger.info(f"Start point of dataframe [{i}] was cut. Shape: {df.shape} -> {df_list[i].shape}")

        # Join all dataframes (trailing missed data could be replaced with NAs)
        df_res = pd.concat(df_list, axis="columns", verify_integrity=True)
        logger.info(f"Shape of combined dataframe: {df_res.shape}")
        if df_res.empty:
            raise Exception(f"The combined dataframe is empty!")

        # Write to output file with possible compression (according to file extension)
        out_file_abs_path = os.path.abspath(out_file_path)
        df_res.to_csv(out_file_abs_path, compression="infer")
        logger.info(f"Saved combined dataframe to file : {out_file_abs_path}")

    except Exception as e:
        logger.error(f"Exception in merge_datasets_from_files; main params: {src_file_list=}, {src_data_timeframe=}, "
                     f"{column_for_timestamp=}. Details: %s", e)
        raise  # Re-raise the exception to report about the problem


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    # merge_datasets_from_files() TBD
