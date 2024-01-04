import os
import pandas as pd
from datetime import datetime as dt
import numpy as np

"""
    Reads the raw data from a weather station, 
    Returns a dataframe that has

    AR      :   the year of the record
    MAN     :   the month of the record
    Dagur   :   the day of the record
    klst    :   the hour of the record
    D       :   the wind direction of the record
    F       :   the wind speed of the record

"""

"""
    The raw data from the weather station has the following
    
    STOD    :   the stationId
    TIMI    :   the time in YYYY-MM-DD HH:MM:SS format
    T       :   the air temperature (1 min average degrees Celsius)
    TX      :   the maximum air temperature (maximum 1 min average from last record)
    TN      :   the minimum air temperature
    RH      :   relative humidity (1 min average %)
    D       :   the wind direction (10 min average degrees)
    F       :   the wind speed (10 min average m/s)
    FX      :   the maximum wind speed (10 min average m/s)
    FG      :   the gust wind speed (max. 3 sec. value from last record m/s)
    R       :   rain (mm)
"""

def convert_to_float(x):
    try:
        return float(x)
    except:
        return float(0)

def read_from_station(df):
    ndf = pd.DataFrame([])
    try: 
        if 'TIMI' in df.columns:
            df['TIMI'] = pd.to_datetime(df['TIMI'])
        else:
            df['TIMI'] = pd.to_datetime(df[' Timabil '])

        ndf['MAN'] = df['TIMI'].dt.month
        ndf['AR'] = df['TIMI'].dt.year
        ndf['Dagur'] = df['TIMI'].dt.day
        ndf['klst'] = df['TIMI'].dt.hour
    except:
        ndf['MAN'] = df['MAN']
        ndf['AR'] = df['AR']
        ndf['Dagur'] = df['Dagur']
        ndf['klst'] = df['klst']

    try:
        ndf['D'] = [convert_to_float(d) for d in df.D]
        ndf['F'] = [convert_to_float(f) for f in df.F]
    except:
        ndf['D'] = [convert_to_float(d) for d in df['Vindatt (deg)']]
        ndf['F'] = [convert_to_float(f) for f in df['Vindur (m/s)']]

    return ndf

