from parameters import BACKEND_HISTORY_URL, BACKEND_PREDICTION_URL
from baseModel import Auto, DateRange
import pandas as pd
import streamlit_pydantic as sp
import streamlit as st
import requests


def prediction_page():
    # Form Prediction
    st.title('Car Price Prediction Page')
    form = sp.pydantic_form(key='predict_form', model=Auto)
    if form:
        dataframe = pd.DataFrame.from_dict([dict(form)])
        response = requests.post(BACKEND_PREDICTION_URL,
                                 headers={'Content-Type': 'application/json'},
                                 json=dataframe.to_json())
        if response.status_code == 200:
            st.dataframe(response.json()['model'])

    # CSV Prediction
    uploaded_file = st.file_uploader('Upload', accept_multiple_files=False, type='csv')
    if st.button('Make Batch Prediction'):
        # Check if a file was uploaded
        if uploaded_file is not None:
            # Load the CSV file into a Pandas dataframe
            dataframe = pd.read_csv(uploaded_file)
            response = requests.post(BACKEND_PREDICTION_URL,
                                     headers={'Content-Type': 'application/json'},
                                     json=dataframe.to_json())
            if response.status_code == 200:
                st.dataframe(response.json()['model'])
        else:
            st.warning('Please upload CSV')


def history_page():
    st.title('Car Price Prediction History')

    col1, col2 = st.columns([3, 1])

    with col1:
        data = sp.pydantic_form(key='date_from', model=DateRange)
    with col2:
        options = ['All', 'On-demand', 'Batch Process']
        selected_options = st.radio('Filter Process Type', options)

    # Load Filtered Date Selection
    if data:
        response = requests.get(BACKEND_HISTORY_URL,
                                headers={'Content-Type': 'application/json'},
                                params=dict(data))
    else:
        response = requests.get(BACKEND_HISTORY_URL)

    if response.status_code == 200:
        try:
            history_data = response.json()['model']
            history = pd.DataFrame(history_data)
            if selected_options == 'All':
                st.dataframe(history)
            else:
                st.dataframe(history[history['process_type'] == selected_options])
        except ValueError as e:
            st.error(f"Error: {e}")
    else:
        st.error("Failed to retrieve data from the server.")


if __name__ == '__main__':
    st.set_page_config(page_title='My App', layout='wide')
    pages = ['Make a Prediction', 'Past Predictions']
    page = st.sidebar.radio('Go to', pages)
    if page == 'Past Predictions':
        history_page()
    elif page == 'Make a Prediction':
        prediction_page()
