# https://endjin.com/blog/2023/03/a-look-into-pandera-and-great-expectations-for-data-validation
import great_expectations as gx
import pandas as pd
from great_expectations.checkpoint import SimpleCheckpoint
from great_expectations.core.batch import BatchRequest

data = pd.read_csv('C:/Users/amirh/OneDrive/Desktop/auto.csv')

context = gx.get_context()

batch_request = {
    'datasource_name': 'auto_source',
    'data_connector_name': 'default_inferred_data_connector_name',
    'data_asset_name': 'Auto.csv'

}

expectation_suit_name = 'auto_expectations'

validator = context.get_validator(
    batch_request=BatchRequest(**batch_request),
    expectation_suit_name=expectation_suit_name
)

column_names = [f'"{column_name}"' for column_name in validator.columns()]
print(f"Columns: {', '.join(column_names)}.")
validator.head(n_rows=5, fetch_all=False)

exclude_column_names = []

# Run the onboarding Data Assistant
result = context.assistants.onboarding.run(
    batch_request=batch_request,
    exclude_column_names=exclude_column_names,
)
validator.expectation_suite = result.get_expectation_suit(
    expectation_suit_name=expectation_suit_name
)

# save
print(validator.get_expectation_suite(discard_failed_expectations=False))
validator.save_expectation_suite(discard_failed_expectations=False)

checkpoint_config = {
    'class_name': 'SimpleCheckpoint',
    'validations': [
        {
            'batch_request': batch_request,
            'expectation_suite_name': expectation_suit_name,
        }
    ],
}

checkpoint = SimpleCheckpoint(
    f'{validator.active_batch_definition.data_asset_name}_{expectation_suit_name}',
    context,
    **checkpoint_config,
)

checkpoint_result = checkpoint.run()

context.build_data_docs()
validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
context.open_data_docs(resource_identifier=validation_result_identifier)
