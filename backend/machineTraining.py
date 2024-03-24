import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_log_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from config import CONTINUOUS_FEATURES, CATEGORICAL_FEATURES, LABEL, SCALER_PATH, ONEHOT_PATH, MODEL


def filter_columns(input_data: pd.DataFrame, *features_list: list) -> pd.DataFrame:
    return input_data[list(features_list)].copy()


def compute_rmsle(y_test: np.ndarray, y_pred: np.ndarray, precision: int = 2) -> float:
    """
    Computes RMSE between two sets of target values.

    Args:
        y_test: a NumPy array containing the true target values
        y_pred: a NumPy array containing the predicted target values
        precision: an optional integer value specifying
        the number of decimal places to round the RMSE to (default: 2)

    Returns:
        A float representing the RMSE between the two sets of target values.
    """

    rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))
    return round(rmsle, precision)


def clean_data(input_data: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
    # Drop unnecessary columns
    if not is_training:
        return input_data.drop([LABEL], axis=1) if LABEL in input_data else input_data

    if 'Id' in input_data:
        input_data = input_data.drop(['Id'], axis=1)

    # remove duplicates
    input_data = input_data.drop_duplicates()

    # Preprocessing un numerical columns
    input_data = input_data.dropna()
    return input_data


def pre_processing_data(input_data: pd.DataFrame, is_training: bool = True) -> tuple:
    # use pre_processing for train data
    if is_training is True:
        input_data = clean_data(input_data, is_training=True)
        scaler = StandardScaler()
        encoder = OneHotEncoder(handle_unknown='ignore')
        # Split Data
        train_data, test_data = train_test_split(input_data, test_size=0.2, random_state=42)
        pre_train = filter_columns(train_data, *CONTINUOUS_FEATURES, *CATEGORICAL_FEATURES)
        pre_test = filter_columns(test_data, *CONTINUOUS_FEATURES, *CATEGORICAL_FEATURES)
        # fit and export
        scaler.fit(pre_train[CONTINUOUS_FEATURES])
        joblib.dump(scaler, SCALER_PATH)
        encoder.fit(pre_train[CATEGORICAL_FEATURES])
        joblib.dump(encoder, ONEHOT_PATH)

        train_continuous = scaler.transform(pre_train[CONTINUOUS_FEATURES])
        train_categorical = encoder.transform(pre_train[CATEGORICAL_FEATURES])

        test_continuous = scaler.transform(pre_test[CONTINUOUS_FEATURES])
        test_categorical = encoder.transform(pre_test[CATEGORICAL_FEATURES])

        train_x = np.hstack([train_continuous, train_categorical.toarray()])
        test_x = np.hstack([test_continuous, test_categorical.toarray()])
        train_y = train_data[LABEL].values
        test_y = test_data[LABEL].values
        return train_x, train_y, test_x, test_y

    # use this section for validating and predicting data
    else:
        input_data = clean_data(input_data, is_training=False)
        val_scaler = joblib.load(SCALER_PATH)
        val_onehot = joblib.load(ONEHOT_PATH)
        val_data = filter_columns(input_data, *CONTINUOUS_FEATURES, *CATEGORICAL_FEATURES)
        val_continuous = val_scaler.transform(val_data[CONTINUOUS_FEATURES])
        val_categorical = val_onehot.transform(val_data[CATEGORICAL_FEATURES])
        return np.hstack([val_continuous, val_categorical.toarray()])


def build_model(input_data: pd.DataFrame) -> dict[str, str]:
    train_x, train_y, test_x, test_y = pre_processing_data(input_data=input_data, is_training=True)
    model = LinearRegression()
    model.fit(train_x, train_y)

    joblib.dump(model, MODEL)

    # Predict
    train_pred = model.predict(train_x)
    test_pred = model.predict(test_x)

    log_test_pred = np.log(test_pred)
    log_test_pred_without_nan = np.nan_to_num(log_test_pred)

    train_rmse = np.sqrt(compute_rmsle(np.log(train_y), np.log(train_pred)))
    test_rmse = np.sqrt(compute_rmsle(np.log(test_y), log_test_pred_without_nan))

    return {
        "train_rmse": train_rmse,
        "test_rmse": test_rmse
    }


if __name__ == '__main__':
    training_data_df = pd.read_csv('../data/init/auto.csv')
    model_performance_dict = build_model(training_data_df)
    print(model_performance_dict)


