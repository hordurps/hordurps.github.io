import os
import pandas as pd
from datetime import datetime as dt


"""
    Reads the raw data from a weather station, 
    Returns a dataframe that has

    AR      :   the year of the record
    MAN     :   the month of the record
    Dagur   :   the day of the record
    klst    :   the hour of the record
    D       :   the wind direction of the record
    F       :   the wind speed of the record
    FG      :   the gust wind speed of the record

"""

def convert_to_float(x):
    try:
        return float(x)
    except:
        return float(0)

def read_from_station():
    datafile = 'Straumsvik_oll_gogn.txt'
    #filepath = os.path.join('Straumsvik_vedurgogn', datafile)
    filepath = os.path.join(os.getcwd(), 'mysite', 'routes','windrose_app_lib','metdata','VI','1473', datafile)


    df = pd.read_csv(filepath, sep='\t')
    
    ndf = pd.DataFrame([])
    df['TIMI'] = pd.to_datetime(df['TIMI'])
    ndf['MAN'] = df['TIMI'].dt.month
    ndf['AR'] = df['TIMI'].dt.year
    ndf['Dagur'] = df['TIMI'].dt.day
    ndf['klst'] = df['TIMI'].dt.hour
    #ndf['Min'] = df['TIMI'].dt.minute
    ndf['D'] = [convert_to_float(d) for d in df.D]
    ndf['F'] = [convert_to_float(f) for f in df.F]
    ndf['FG'] = [convert_to_float(fg) for fg in df.FG]

    return ndf

