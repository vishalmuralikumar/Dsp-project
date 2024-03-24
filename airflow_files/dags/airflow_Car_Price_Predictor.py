from datetime import datetime, timedelta
from airflow import DAG
import  pandas as pd
from airflow.operators.python import PythonOperator




default_args = {
    'owner': 'airflow_car',
    'depends_on_past': False,
    'start_date': datetime(2023, 6, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('car_price_prediction_2',
          default_args=default_args,
          schedule='*/5 * * * *')




def validate_data(web_file: pd.DataFrame = None):
    if web_file is not None:
        data = web_file
        invalid_path = f'{ROOT}/data/invalid_data/web.csv'
        valid_path = None  # Update this based on your requirements

        validating = Validation(data)
        damaged_records, healthy_records = validating.validation_records()
        damaged_records.to_csv(invalid_path)

        if valid_path is not None:
            healthy_records.to_csv(valid_path)

        validating.preserve_log()
        validating.save_logs()
        return True if damaged_records is not None else False
    else:
        return False


with dag:

    AF_validate_data = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
        dag=dag
    )

    AF_validate_data