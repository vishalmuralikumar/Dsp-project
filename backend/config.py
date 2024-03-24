from os import path

# Parameters
PSQL = 'postgresql://ahmobayen:85hSGYVTLHZf@ep-green-salad-117547.eu-central-1.aws.neon.tech/neondb'

# Predict And Train
# CONTINUOUS_FEATURES = ['symboling', 'normalized_losses', 'symboling', 'city_mpg', 'engine_size', 'curb_weight',
#                        'highway_mpg', 'compression_ratio', 'width', 'length', 'wheelbase', 'height', 'stroke', 'bore',
#                        'peak_rpm', 'horsepower']
# CATEGORICAL_FEATURES = ['make', 'fuel_type', 'aspiration', 'num_doors', 'body_style', 'drive_wheels', 'engine_location',
#                         'fuel_system']
CONTINUOUS_FEATURES = ['engine_size', 'horsepower']
CATEGORICAL_FEATURES = ['make', 'num_doors', 'body_style', 'drive_wheels', 'engine_location']
LABEL = 'price'

SCALER_PATH = '../model/scaler.joblib'
ONEHOT_PATH = '../model/onehot.joblib'
MODEL = '../model/model.joblib'

# Date Style
TIME_STYLE = '%Y-%m-%d %H:%M:%S.%f'
DATE_STYLE = '%Y-%m-%d'

# Working Directories
CURRENT_DIR = path.abspath(path.curdir)
ROOT = path.abspath(path.pardir)
