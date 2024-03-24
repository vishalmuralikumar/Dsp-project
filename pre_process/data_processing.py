import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder


def process_user_input(df_user_raw: pd.DataFrame) -> pd.DataFrame:
    # df_user_raw = pd.read_csv(csv_file)

    df_user = df_user_raw.copy()

    headers = ['symboling', 'normalized_losses', 'make', 'fuel_type', 'aspiration', 'num_doors', 'body_style',
               'drive_wheels', 'engine_location', 'wheelbase', 'length', 'width', 'height', 'curb_weight',
               'engine_type',
               'num_cylinders', 'engine_size', 'fuel_system', 'bore', 'stroke', 'compression_ratio', 'horsepower',
               'peak_rpm', 'city_mpg', 'highway_mpg', 'price']

    if not all(isinstance(col, str) for col in df_user.columns):
        df_user.columns = headers

    df_user.replace('?', np.nan, inplace=True)

    number_list = ['normalized_losses', 'price', 'symboling', 'city_mpg', 'engine_size', 'curb_weight', 'highway_mpg',
                   'compression_ratio', 'width', 'length', 'wheelbase', 'height', 'stroke', 'bore', 'peak_rpm',
                   'horsepower']

    category_list = ['make', 'fuel_type', 'aspiration', 'num_doors', 'body_style', 'drive_wheels', 'engine_location',
                     'fuel_system']

    num_imputer = SimpleImputer(strategy='mean')
    cat_imputer = SimpleImputer(strategy='most_frequent')

    num_transformer = Pipeline(steps=[('imputer', num_imputer), ('scaler', MinMaxScaler(feature_range=(0, 1)))])
    cat_transformer = Pipeline(steps=[('imputer', cat_imputer), ('encoder', OneHotEncoder())])

    processor = ColumnTransformer(transformers=[('number_columns', num_transformer, number_list),
                                                ('category_columns', cat_transformer, category_list)])

    pipe = Pipeline(steps=[('processor', processor)])

    df_processed = pd.DataFrame(pipe.fit_transform(df_user))

    return df_processed

if __name__ == '__main__':
    df_user_raw = pd.read_csv('auto.csv')
    print(process_user_input(df_user_raw))