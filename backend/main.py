from dataValidator import validate_data
from util_car import make_predictions
from config import TIME_STYLE, DATE_STYLE
from connection import DataModel
from fastapi import FastAPI, Request
from datetime import datetime

import pandas as pd
import json

app = FastAPI()
data_model = DataModel()


@app.get('/show_history')
async def show_history_data(request: Request):
    """GET all data from database and return it to UI"""
    if request.query_params:
        start_date = datetime.strptime(request.query_params.get('start_date'), DATE_STYLE).strftime(TIME_STYLE)
        end_date = datetime.strptime(request.query_params.get('end_date'), DATE_STYLE).strftime(TIME_STYLE)

        # Filter Output query based on the date
        if start_date and end_date is not None:
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            return {'model': data_model.filter_date(start_date, end_date)}

    # Load all Data
    return {'model': data_model.read_all()}


@app.post('/predict_price')
async def predict_price(request: Request):
    """Receive Data from user, process it then return the results"""
    result = await request.json()
    result = json.loads(result)
    df = pd.DataFrame.from_dict(result)
    healthy_records = validate_data(web_file=df)
    predicted_price = make_predictions(healthy_records)
    # write to database
    data_model.write(predicted_price)

    # should change with prediction (requires to work on auto_obj)
    return {'model': predicted_price.to_dict()}
