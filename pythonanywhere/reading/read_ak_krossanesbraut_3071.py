import os
import pandas as pd
from datetime import datetime as dt

from readfromgit import get_stationIds, get_rawmetdata, get_session


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
    TIMI    :   the time in YYYY-MM-DD HH:MM:SS UTC format
    D       :   the wind direction (10 min average degrees)
    F       :   the wind speed (10 min average m/s)
    FG      :   the gust wind speed (max. 3 sec. value from last record m/s)
"""

def convert_to_float(x):
    try:
        return float(x)
    except:
        return float(0)

def read_from_station(df):
    #datafile = 'Straumsvik_oll_gogn.txt'
    #filepath = os.path.join('Straumsvik_vedurgogn', datafile)
    #df = pd.read_csv(filepath, sep='\t')
    
    ndf = pd.DataFrame([])
    df['TIMI'] = pd.to_datetime(df['TIMI'])
    ndf['MAN'] = df['TIMI'].dt.month
    ndf['AR'] = df['TIMI'].dt.year
    ndf['Dagur'] = df['TIMI'].dt.day
    ndf['klst'] = df['TIMI'].dt.hour
    #ndf['Min'] = df['TIMI'].dt.minute
    ndf['D'] = [convert_to_float(d) for d in df.D]
    ndf['F'] = [convert_to_float(f) for f in df.F]

    return ndf


github_session, user = get_session()
stationId = '3471'
stationIds = get_stationIds(github_session, user)
dataFile = stationIds.query('nr=={stationId}'.format(stationId=stationId))['data']
idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
data = get_rawmetdata(github_session, user, source='vi', stationId=stationId, dataFile=dataFile[idx])
ndata = read_from_station(data)
print(ndata)

