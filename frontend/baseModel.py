from datetime import datetime, timedelta
from typing import Optional

import streamlit as st
from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start_date: str = (datetime.now().date() - timedelta(days=7))
    end_date: str = datetime.now().date()


class Auto(BaseModel):
    """ This is our base model which is allowed null"""
    symboling: str = st.selectbox('Symboling', [-2, -1, 0, 1, 2])
    normalized_losses: int = st.number_input('normalized Losses', min_value=0, max_value=9999, value=0)
    make: Optional[str] = st.text_input('Make', value=None)
    fuel_type: str = st.selectbox('Fuel Type', ['gas', 'diesel'])
    aspiration: str = st.selectbox('Aspiration', ['std', 'turbo'])
    num_doors: str = st.selectbox('Number of Doors', ['two', 'four'])
    body_style: str = st.selectbox('Body Style', ['convertible', 'hatchback', 'sedan', 'wagon', 'hardtop'])
    drive_wheels: str = st.selectbox('Drive Wheels', ['4wd', 'fwd', 'rwd'])
    engine_location: str = st.selectbox('Engine Location', ['front', 'rear'])
    wheelbase: float = st.number_input('Wheelbase', min_value=0.0, max_value=300.0, value=100.0)
    length: float = st.number_input('Length', min_value=0.0, max_value=300.0, value=150.0)
    width: float = st.number_input('Width', min_value=0.0, max_value=150.0, value=60.0)
    height: float = st.number_input('Height', min_value=0.0, max_value=150.0, value=60.0)
    curb_weight: int = st.number_input('Curb Weight', min_value=0, max_value=9000, value=1500)
    engine_type: str = st.selectbox('Engine Type', ['OHC', 'DOHC', 'OHV'])
    num_cylinders: str = st.selectbox('Number of Cylinders', ['two', 'four', 'six', 'eight'])
    engine_size: int = st.number_input('Engine Size', min_value=50, max_value=300, value=80)
    fuel_system: str = st.selectbox('Fuel System', ['MPFI', '2BBL', '4BBL', 'MFI', '1BBL'])
    stroke: Optional[float] = st.number_input('Stroke', min_value=0.0, value=0.0)
    horsepower: int = st.number_input('Horsepower', min_value=10, max_value=600, value=80)
    city_mpg: int = st.number_input('City MPG', min_value=0, max_value=100, value=10)
    compression_ratio: Optional[float] = st.number_input('Compression Ratio', min_value=0.0, value=10.0)
    peak_rpm: Optional[int] = st.number_input('Peak RPM', min_value=0, max_value=9999, value=6000)
    highway_mpg: Optional[int] = st.number_input('Highway MPG', min_value=0, max_value=100, value=15)
    bore: Optional[float] = st.number_input('Bore', min_value=0.0, value=0.0)

    # excluded from form to view (by adding _ in the beginning of the field)
    _price: Optional[int] = None
    _created_at: datetime = Field(default_factory=datetime.now, exclude=True)
    _input_resource: str = 'website'
    _process_type: str = 'on-demand'  # True is on-demand # False is -batch processing
