import click
from etna.models import NaiveModel
import joblib
import pandas as pd
import logging
import os


@click.command()
@click.argument("out_model_file_path", type=click.Path())
@click.argument("src_data_file_path", type=click.Path(), default="../../data/interim/stockdata.csv.gz")
@click.argument("column_for_timestamp", type=str, default="ts")
def train_model(
    src_data_file_path: str,
    out_model_file_path: str,
    column_for_timestamp: str
):
    """
    Loads training data from specified file, trains the model and exports it to the specified file.
    """
    logger = logging.getLogger(__name__)

    # TBD: check exceptions
    src_file_abs_path = os.path.abspath(src_data_file_path)
    logger.info(f"Reading train data from file {src_file_abs_path}")
    df = pd.read_csv(src_file_abs_path, index_col=column_for_timestamp)
    assert isinstance(df, pd.DataFrame)

    # "Train" the model using df
    model = NaiveModel(lag=1)  # Create a model

    # Export the "trained" model to output file
    out_model_abs_file_path = os.path.abspath(out_model_file_path)
    assert out_model_abs_file_path.endswith('.joblib.gz'), f"Unexpected extension, must be '.joblib.gz'"
    joblib.dump(model, out_model_abs_file_path, compress=('gzip', 3))
    logger.info(f"Saved trained model in file: {out_model_abs_file_path}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    train_model()


# TBD 2023-11: tune mlflow
# import os
# print("TM pwd:", os.getcwd())
#
# from catboost import CatBoostClassifier
# import mlflow
#
# import sys
# print("TM path: ", sys.path)
# sys.path.append('.')
# from src.data.load_dataset import load_dataset_eth_contest
#
#
# def train_cb_default():
#     mlflow.set_tracking_uri("http://127.0.0.1:5000")
#     mlflow.set_experiment("catboost default")
#     mlflow.sklearn.autolog()
#     with mlflow.start_run():
#         df_train_X, df_train_y, df_test_X, df_test_y = load_dataset_eth_contest()
#         cb_model = CatBoostClassifier(iterations=100, max_depth=3, random_state=42, text_features=["message__all"])
#         cb_model.fit(df_train_X, df_train_y)
#
#         y_pred = cb_model.predict(df_test_X)
#
# if __name__ == "__main__":
#     train_cb_default()
