import logging
import yaml

from dotenv import find_dotenv, load_dotenv

from data.make_dataset import create_dataset_for_stock
from data.merge_datasets import merge_datasets_from_files
from data.push_dataset_to_clickhouse import push_dataset
from models.backtest_model import launch_model_backtesting


# Setup logging
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# logging.basicConfig(level=logging.INFO, format=log_fmt)
logging.basicConfig(level=logging.DEBUG, format=log_fmt)


# Load settings from config
# TBD: probably, use pydantic or dataclass class for storing all config variables as fields
with open("run_all_config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

STOCKS = config["STOCKS"]  # Prediction will be made for the first stock in the list
TIMEFRAME = config["TIMEFRAME"]
COL_FOR_TIMESTAMP = config["COL_FOR_TIMESTAMP"]

PREDICTIONS_FILE_NAME = config["PREDICTIONS_FILE_NAME"]
MERGED_DATA_FILE_NAME = config["MERGED_DATA_FILE_NAME"]

MODEL_NAME = config["MODEL_NAME"]

USE_BACKTEST_MODE = config["USE_BACKTEST_MODE"]

# Settings for backtest mode
BACKTEST_HORIZON = config["BACKTEST_HORIZON"]
BACKTEST_N_FOLDS = config["BACKTEST_N_FOLDS"]

# Settings for forecast mode
FORECAST_HORIZON = config["FORECAST_HORIZON"]


def main():


    # Load required creds / setting
    load_dotenv(find_dotenv())


    # Download required stocks
    # Note: Prediction will be made for the first stock in the list
    file_list = []
    for stock in STOCKS:
        out_fpath = f"../data/interim/stockdata_{stock}_{TIMEFRAME}.csv.gz"
        create_dataset_for_stock(
            stock_name=stock, timeframe=TIMEFRAME, column_for_timestamp=COL_FOR_TIMESTAMP,
            out_file_path=out_fpath
        )
        file_list.append(out_fpath)


    # Merge the downloaded stocks into single dataframe, save it to the file
    merge_datasets_from_files(src_file_list=file_list, src_data_timeframe=TIMEFRAME,
                              column_for_timestamp=COL_FOR_TIMESTAMP,
                              out_file_path=MERGED_DATA_FILE_NAME)


    # Launch model forecasting/backtesting for the merged file. Note: the first stock in the file is considered
    if USE_BACKTEST_MODE:
        horizon = BACKTEST_HORIZON
        n_folds = BACKTEST_N_FOLDS
    else:
        horizon = FORECAST_HORIZON
        n_folds = -1

    launch_model_backtesting(
        src_model_name=MODEL_NAME,
        # src_data_file_path=f"../data/interim/stockdata_{STOCKS[0]}_{TIMEFRAME}.csv.gz",  # TBD: replace [0] :)
        src_data_file_path=MERGED_DATA_FILE_NAME,
        src_data_timeframe=TIMEFRAME,
        column_for_timestamp=COL_FOR_TIMESTAMP,
        column_for_target=f"adj_close_{STOCKS[0]}",
        forecast_horizon=horizon,
        backtest_n_folds=n_folds,
        out_predictions_file_path=PREDICTIONS_FILE_NAME,
        use_backtest_mode=USE_BACKTEST_MODE
    )

    # Push the result to ClickHouse
    # Note: prediction was made for the first stock in the list
    push_dataset(PREDICTIONS_FILE_NAME, stock_name=STOCKS[0], timeframe=TIMEFRAME, model_name=MODEL_NAME)


if __name__ == '__main__':
    main()
    logging.info('OK!')
