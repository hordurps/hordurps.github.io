import os
import pandas as pd
from datetime import datetime as dt
#from readfromgit import get_stationIds, get_rawmetdata, get_session
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


cwd = os.getcwd()
pardir = os.path.abspath(os.path.join(cwd,os.pardir))
parpardir = os.path.abspath(os.path.join(pardir,os.pardir))

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
    df['TIMI'] = pd.to_datetime(df[' Timabil '])
    ndf['MAN'] = df['TIMI'].dt.month
    ndf['AR'] = df['TIMI'].dt.year
    ndf['Dagur'] = df['TIMI'].dt.day
    ndf['klst'] = df['TIMI'].dt.hour
    #ndf['Min'] = df['TIMI'].dt.minute
    ndf['D'] = [convert_to_float(d) for d in df['Vindatt (deg)']]
    ndf['F'] = [convert_to_float(f) for f in df['Vindur (m/s)']]

    ndf.to_csv('mogt_akranes_format.csv')

    return ndf


def get_stationIds():

    # Downloading the csv file from github
    repo = 'rawmetdata'
    path = 'vedurstodvar.csv'
    # Reading the downloaded content and making it a pandas dataframe
    df = pd.read_csv(os.path.join(parpardir, path))
    return df

def get_rawmetdata():
    print(parpardir)
    df = pd.read_csv(os.path.join(parpardir,'mogt','akranes','mogt_akranes.csv'), low_memory=False)
    return df

def main():
    # the station id for this station
    stationId = '300'
    # the station ids that are available on github
    stationIds = get_stationIds()
    # finding the file name with the data for this station
    dataFile = stationIds.query('nr=={stationId}'.format(stationId=stationId))['data']
    # finding the index to read the file name
    idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
    # getting the raw data from github
    data = get_rawmetdata()
    # cleaning the data, i.e. only extract the necessary columns
    ndata = read_from_station(data)


    # sorting
    from sort_station_data import (sort_wdirs, sort_months, sort_hours, sort_windrose)
    from plot_station_data import (plot_windrose, plot_weibull, plot_directions, plot_meanws)

    ndata = sort_wdirs(ndata)
    ndata, months = sort_months(ndata)
    ndata, hours = sort_hours(ndata, [0,8])
    wdata = sort_windrose(ndata)

    # finding the station name for plotting purposes
    stationName = stationIds.query('nr=={stationId}'.format(stationId=stationId))['name'][idx]
    # plotting a wind rose
    plot_windrose(wdata, stationName, months, hours)
    # plotting weibull
    plot_weibull(ndata, stationName, months, hours)



    # plot wind direction frequency
    plot_directions(sort_wdirs(read_from_station(data)), stationName, months, hours)

    # plot wind direction mean wind speed
    plot_meanws(sort_wdirs(read_from_station(data)), stationName, months, hours)









if __name__ == '__main__':
    main()


