import logging

from dotenv import find_dotenv, load_dotenv

from src.data.make_dataset import create_dataset_for_stock
from src.data.merge_datasets import merge_datasets_from_files
from src.data.push_dataset_to_clickhouse import push_dataset
from src.models.backtest_model import launch_model_backtesting


# Settings
STOCKS = ["ALI=F", "BTC=F"]  # Prediction will be made for the first stock in the list
TIMEFRAME = "1h"
COL_FOR_TIMESTAMP = "ts"  # Column in ClickHouse for storing datetime information
# MODEL_NAMES = ["NaiveModel", "LinearPerSegmentModel", "CatBoostPerSegmentModel"]  # TBD
MODEL_NAME = "CatBoostPerSegmentModel"
HORIZON = 1  # How many candled to predict on each backtest step
N_FOLDS = 24  # Number of test folds for backtest
PREDICTIONS_FILE_NAME = "../data/predicted/predictions.csv.gz"
MERGED_DATA_FILE_NAME = f"../data/interim/stockdata_merged_{TIMEFRAME}.csv.gz"


# Setup logging
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)


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


# Launch model backtesting for the merged file. Note: the first stock in the file is considered
launch_model_backtesting(
    src_model_name=MODEL_NAME,
    # src_data_file_path=f"../data/interim/stockdata_{STOCKS[0]}_{TIMEFRAME}.csv.gz",  # TBD: replace [0] :)
    src_data_file_path=MERGED_DATA_FILE_NAME,
    src_data_timeframe=TIMEFRAME,
    column_for_timestamp=COL_FOR_TIMESTAMP,
    column_for_target=f"adj_close_{STOCKS[0]}",
    forecast_horizon=HORIZON,
    backtest_n_folds=N_FOLDS,
    out_predictions_file_path=PREDICTIONS_FILE_NAME
)

# Push the result to ClickHouse
# Note: prediction was made for the first stock in the list
push_dataset(PREDICTIONS_FILE_NAME, stock_name=STOCKS[0], timeframe=TIMEFRAME, model_name=MODEL_NAME)
