import glob
import json
from collections.abc import MutableMapping
from datetime import datetime
from pathlib import Path

import great_expectations as gx
import pandas as pd
from great_expectations.data_context.types.resource_identifiers import ExpectationSuiteIdentifier
from great_expectations.exceptions import DataContextError

from config import CONTINUOUS_FEATURES, CATEGORICAL_FEATURES, ROOT
from connection import DataModel
from util_car import send_mail


class Validation:
    def __init__(self, input_frame: pd.DataFrame, source_name: str):
        self.source_name = source_name
        self.data_source = input_frame
        self.data_source['created_at'] = datetime.now().strftime("%Y%m%dT%H%M%S.%fZ")
        if source_name == 'web':
            self.data_source['input_resource'] = 'web'
            self.data_source['process_type'] = 'On-demand'
        else:
            self.data_source['input_resource'] = 'file'
            self.data_source['process_type'] = 'Batch Process'
        self.context = gx.get_context()
        self.validator = self.context.sources.pandas_default.read_dataframe(dataframe=input_frame)
        self.__features = [*CONTINUOUS_FEATURES, *CATEGORICAL_FEATURES]
        for feature in self.__features:
            self.validator.expect_column_to_exist(feature)
            self.validator.expect_column_values_to_not_be_null(feature)

        self.__categorical_boundries = {
            'num_doors': ['two', 'four'],
            'body_style': ['convertible', 'hatchback', 'sedan', 'wagon', 'hardtop'],
            'engine_location': ['front', 'rear'],
            'drive_wheels': ['rwd', 'fwd', '4wd']
        }
        self.__continuous_limits = {
            'engine_size': (0, 300),
            'horsepower': (0, 600)
        }

        for column, values in self.__categorical_boundries.items():
            self.validator.expect_column_distinct_values_to_be_in_set(column, values)

        for column, value_range in self.__continuous_limits.items():
            self.validator.expect_column_values_to_be_between(column, value_range[0], value_range[1])

        self.validation_results = self.validator.validate()

    def validation_records(self):
        failed_columns = []
        for v in self.validation_results.results:
            if not v.success:
                column = v.expectation_config['kwargs']['column']
                if 'value_set' in v.expectation_config['kwargs']:
                    value_set = v.expectation_config['kwargs']['value_set']
                    failed_columns.append(self.data_source[~self.data_source[column].isin(value_set)].copy())
                if 'expect_column_values_to_not_be_null' in v.expectation_config['expectation_type']:
                    empty_rows = self.data_source[self.data_source[column].isna()].copy()
                    failed_columns.append(empty_rows)
                if 'expect_column_values_to_be_between' in v.expectation_config['expectation_type']:
                    range = self.data_source[
                        ~self.data_source[column].between(v.expectation_config['kwargs']['min_value'],
                                                          v.expectation_config['kwargs']['max_value'])].copy()
                    failed_columns.append(range)
        damaged_records = pd.concat(failed_columns) if failed_columns else pd.DataFrame()
        healthy_records = pd.concat([damaged_records, self.data_source]).drop_duplicates(keep=False)
        return damaged_records, healthy_records

    def save_logs(self):
        expectation_suite_name = "Auto_suite"
        try:
            suite = self.context.get_expectation_suite(expectation_suite_name=expectation_suite_name)
            print(
                f'Loaded ExpectationSuite "{suite.expectation_suite_name}" containing {len(suite.expectations)} expectations.')
        except DataContextError:
            suite = self.context.add_expectation_suite(expectation_suite_name=expectation_suite_name)
            print(f'Created ExpectationSuite "{suite.expectation_suite_name}".')
        finally:
            self.context.add_or_update_expectation_suite(expectation_suite=suite)

        suite_identifier = ExpectationSuiteIdentifier(expectation_suite_name=expectation_suite_name)
        self.context.build_data_docs(resource_identifiers=[suite_identifier])

        checkpoint = gx.checkpoint.SimpleCheckpoint(
            name="Auto_checkpoint",
            data_context=self.context,
            validator=self.validator,
        )
        return checkpoint.run()

    def preserve_log(self):
        def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> MutableMapping:
            items = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, MutableMapping):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        checkpoint_result = self.validation_results
        statistics = checkpoint_result.statistics
        meta_id = str(checkpoint_result.meta['validation_time'])
        time_stamp = datetime.strptime(meta_id, '%Y%m%dT%H%M%S.%fZ')
        execution_summery = pd.DataFrame({'meta_id': meta_id, 'source': self.source_name,
                                          'time_stamp': time_stamp, **statistics},
                                         index=[0])

        results = pd.DataFrame([flatten_dict(json.loads(str(i))) for i in checkpoint_result.results])
        results.dropna()
        results = results[results['success'] == False]
        results['time_stamp'] = time_stamp
        results['source'] = self.source_name
        results['result.details.value_counts'] = results['result.details.value_counts'].apply(json.dumps)

        db = DataModel()
        db.write_summery(execution_summery, meta_id)
        db.write_log(results, meta_id)


def validate_data(airflow_directory: str = None, web_file: pd.DataFrame = None):
    if airflow_directory is not None:
        data = pd.read_csv(airflow_directory)
        path = Path(airflow_directory).name
        invalid_path = f'{ROOT}/data/invalid_data/{path}'
        valid_path = f'{ROOT}/data/valid_data/{path}'
        validating = Validation(data, path)
        damaged_records, healthy_records = validating.validation_records()
        damaged_records.to_csv(invalid_path)
        if damaged_records.empty:
            send_mail('There are some errors in the Data, please check it')
        healthy_records.to_csv(valid_path)
    if web_file is not None:
        data = web_file
        path = 'web'
        invalid_path = f'{ROOT}/data/invalid_data/{path}.csv'
        validating = Validation(data, path)
        damaged_records, healthy_records = validating.validation_records()
        damaged_records.to_csv(invalid_path)
    validating.preserve_log()
    validating.save_logs()
    return healthy_records


if __name__ == '__main__':
    # temp = 'auto_test_with_one_invalid_door_number'
    # temp = 'auto_test_with_two_null_engine_size'
    # temp = 'auto_test_with_one_invalid_engine_size'
    # validate_data(airflow_directory='../data/init/auto_test_with_one_invalid_door_number.csv', web_file=None)

    for file in glob.glob(f'{ROOT}/data/init' + '\*.csv'):
        validate_data(airflow_directory=file, web_file=None)
        print(file)
