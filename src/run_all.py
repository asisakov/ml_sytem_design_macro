import logging

from dotenv import find_dotenv, load_dotenv

from src.data.make_dataset import create_dataset_for_stock
from src.data.push_dataset_to_clickhouse import push_dataset
from src.models.backtest_model import launch_model_backtesting


# Settings
STOCKS = ["ALI=F", "BTC=F"]
TIMEFRAME = "1h"
# MODEL_NAMES = ["NaiveModel", "LinearPerSegmentModel", "CatBoostPerSegmentModel"]  # TBD
MODEL_NAME = "CatBoostPerSegmentModel"
HORIZON = 1  # How many candled to predict on each backtest step
N_FOLDS = 24  # Number of test folds for backtest
PREDICTIONS_FILE_NAME = "../data/predicted/predictions.csv.gz"


# Setup logging
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)

# Load required creds / setting
load_dotenv(find_dotenv())


# Download required stocks
for stock in STOCKS:
    create_dataset_for_stock(
        stock_name=stock, timeframe=TIMEFRAME, column_for_timestamp="ts",
        out_file_path=f"../data/interim/stockdata_{stock}_{TIMEFRAME}.csv.gz"
    )

# Merge required stocks into single dataframe
# TBD

# Launch model backtesting
launch_model_backtesting(
    src_model_name=MODEL_NAME,
    src_data_file_path=f"../data/interim/stockdata_{STOCKS[0]}_{TIMEFRAME}.csv.gz",  # TBD: replace [0] :)
    src_data_timeframe=TIMEFRAME,
    column_for_timestamp="ts",
    column_for_target="adj_close",
    forecast_horizon=HORIZON,
    backtest_n_folds=N_FOLDS,
    out_predictions_file_path=PREDICTIONS_FILE_NAME
)

# Push the result to ClickHouse
push_dataset(PREDICTIONS_FILE_NAME, stock_name=STOCKS[0], timeframe=TIMEFRAME, model_name=MODEL_NAME)
