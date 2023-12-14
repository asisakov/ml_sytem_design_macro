import click
from etna.datasets.tsdataset import TSDataset
from etna.metrics import MAE, MSE, SMAPE, MAPE
from etna.models import CatBoostPerSegmentModel, LinearPerSegmentModel, NaiveModel, ProphetModel
from etna.pipeline import Pipeline
import joblib
import pandas as pd
import logging
import os

from etna.transforms import LogTransform, LagTransform

# TBD: change module name ?backtest_or_forecast_model


# @click.command()
# # @click.argument("src_model_file_path", type=click.Path())
# @click.argument("src_model_name", type=str, default="CatBoostPerSegmentModel")  # TBD: discuss with the team
# @click.argument("src_data_file_path", type=click.Path(), default="../../data/interim/stockdata.csv.gz")
# @click.argument("src_data_timeframe", type=str, default="H")
# @click.argument("column_for_timestamp", type=str, default="ts")
# @click.argument("column_for_target", type=str, default="adj_close")
# @click.argument("forecast_horizon", type=int, default=1)
# @click.argument("backtest_n_folds", type=int, default=24)
# @click.argument("out_predictions_file_path", type=click.Path(), default="../../data/predicted/predictions.csv.gz")
def launch_model_backtesting(
    # src_model_file_path: str,
    src_model_name: str,        # Hard-coded (TBD) ETNA model name
    src_data_file_path: str,    # Path to data. If more than one stocks, then prediction is made for the first one(TBD)
    src_data_timeframe: str,    # Frequency of data record. Ex: "MS" for months, "H" for 1h
    column_for_timestamp: str,
    column_for_target: str,
    forecast_horizon: int,      # Set the horizon for predictions
    backtest_n_folds: int,      # Is ignored in forecast mode. May be set to -1
    out_predictions_file_path: str,
    use_backtest_mode: bool = False  # Either forcast (False) or backtest (True) pipeline modes.
):
    """
    Loads trained model, loads data, do predictions for the data, and exports them to the specified file.
    """
    logger = logging.getLogger(__name__)

    # Input checks
    if use_backtest_mode and backtest_n_folds != -1:
        logger.warning(f"The `backtest_n_folds` parameter with non-default value {backtest_n_folds} is ignored!")

    # TBD: check exceptions

    # Load the trained model from file
    # src_model_abs_file_path = os.path.abspath(src_model_file_path)
    # logger.info(f"Reading trained model from file {src_model_abs_file_path}")
    # model = joblib.load(src_model_abs_file_path)  # TBD: file not found, file corrupted

    # Create model by the specified name (TBD: discuss. Alternative: pass alredy creted model instance as parameter,
    # but what to do in case of CLI operation?)
    use_lag_transforms = False
    if src_model_name == "NaiveModel":
        model = NaiveModel(lag=1)
    elif src_model_name == "LinearPerSegmentModel":
        model = LinearPerSegmentModel()
        use_lag_transforms = True
    elif src_model_name == "CatBoostPerSegmentModel":
        model = CatBoostPerSegmentModel(iterations=100, random_state=42)
        use_lag_transforms = True
    elif src_model_name == "ProphetModel":
        model = ProphetModel()
    else:
        raise NotImplementedError(f"The model {src_model_name} is not yet supported.")

    # Read the data
    src_data_abs_file_path = os.path.abspath(src_data_file_path)
    logger.info(f"Reading data from file {src_data_abs_file_path}")
    # TBD: handle if file not found
    df_src = pd.read_csv(src_data_abs_file_path, index_col=column_for_timestamp, parse_dates=[column_for_timestamp])
    # Remove timezone-info from the index (required by Prophet!), convert to UTC
    df_src.index = df_src.index.tz_convert(None)
    logger.info(f".. loaded data shape: {df_src.shape}")

    # Resample the data to fill missing candles, and forward-fill the gaps (including nans if any)
    df_src = df_src.resample(rule=src_data_timeframe).ffill()
    # Replace remaining nans to previous good values (rarely occurred)
    df_src = df_src.ffill()  # TBD: could be critical for some features with large missing data in the end

    # Prepare columns "timestamp", "segment", "target" that are required by ETNA
    df_src["timestamp"] = df_src.index      # For now - just create copy of index. TBD: try to rename the index
    df_src["segment"] = "dummy_segment"     # Segments are required by ETNA
    df_src["target"] = df_src[column_for_target]    # TBD: check if "target" exists.

    # TBD:
    df_src = df_src[["timestamp", "segment", "target"]]

    # TBD: optimize memory (do not copy the columns)
    # Convert pandas dataframe to ETNA Dataset format.
    df_ts_format = TSDataset.to_dataset(df_src)
    # TBD: map "1h" to ETNA "H"
    tsd_dataset = TSDataset(df_ts_format, freq=src_data_timeframe)

    # A list of transforms
    transforms = [
        # This ffill transformer gives an error like "NaNs in y_true" -> replaced with manual resample.
        # TimeSeriesImputerTransform(in_column="target", strategy=ImputerMode.forward_fill)
        LogTransform(in_column="target"),
    ]
    if use_lag_transforms:
        transforms.append(LagTransform(in_column="target", lags=[1, 2, 3, 4, 5]))

    # Create pipeline
    pipeline = Pipeline(model=model, transforms=transforms, horizon=forecast_horizon)

    if use_backtest_mode:
        # This method will launch %backtest_n_folds% iterations of train-test with metric calculations
        df_metrics, df_forecast, df_fold_info = pipeline.backtest(
            ts=tsd_dataset,
            metrics=[MAE(), MSE(), SMAPE(), MAPE()],
            n_folds=backtest_n_folds, )
    else:
        pipeline.fit(tsd_dataset)
        tsd_forecast = pipeline.forecast()  # Use train dataset as source of timestamps for new forecast dates
        df_forecast = tsd_forecast.to_pandas()

    # Prepare output dataframe (take the last column)
    out_df = pd.DataFrame(index=df_forecast.index, data=df_forecast.iloc[:, -1].rename("prediction"))
    # TBD: in backtest mode we can take N last candles from tsd_dataset and put them to "ground_truth" column
    # If required, we could get N + history_len candles. See charts in
    # https://etna-docs.netlify.app/tutorials/backtest#4.-Validation-visualisation

    # Write the forecast to output file with possible compression (according to file extension)
    out_predictions_ans_file_path = os.path.abspath(out_predictions_file_path)
    out_df.to_csv(out_predictions_ans_file_path, compression="infer")
    logger.info(f"Saved dataframe with forecast to file : {out_predictions_ans_file_path}")


if __name__ == "__main__":
    # Setup logging
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Main function call
    launch_model_backtesting()
