import numpy as np
import pandas as pd

def sort_wdirs(ndata, nwd=None):

    if nwd is None:
        # number of wind directions
        nwd = 12

    # create a list of wind dirs
    wdirs = np.arange(0,360,int(360/nwd))
    # adding 0 at the back of the list 
    wdirs = np.append(wdirs,[0])
    # a function to bin the wind diractions according to : d - 15 <= d < d + 15, if nwd is 12 
    bin_wdirs = lambda d : wdirs[round(d/(360/nwd))]
    # adding a column to the dataframe with the binned wind directions
    ndata['wdirs'] = ndata['D'].apply(bin_wdirs)
    return ndata

def sort_months(ndata, months=None):

    if months is None:
        # months to view from the dataset
        months = [6,7,8]

    # extracting the data for any season, if the month (MAN) is in the list 
    ndata = ndata[ndata['MAN'].isin(months)]
    return ndata, months

def sort_hours(ndata, hours=None):

    if hours is None:
        # hours to view from the dataset
        hours = [8,22]

    # extracting the data for any hours, if the hours (klst) is between the values, both inclusive
    ndata = ndata[ndata['klst'].between(left=hours[0], right=hours[1], inclusive='both')]
    return ndata, hours

def sort_windrose(ndata, bins=None):

    if bins is None:
        # binning for wind rose
        bins = [0, 2.5, 4.0, 6.0, 10.0, 15.0]

    df = pd.DataFrame([])
   
    # removing NaN from data set
    ndata.dropna(subset=['F'], inplace=True)
    # removing zeros from data set
    ndata = ndata[ndata.F > 0]

    for i in range(len(bins)-1):
        # binning and extracting wind speeds between bin i and bin j, with inclusive in the upper region
        tdf = ndata[ndata['F'].between(left=bins[i], right=bins[i+1], inclusive='right')]
        # finding the frequency of each wind direction with group by, returns a series with wdirs as index and frequency as value
        ns = (tdf.groupby('wdirs').size()[lambda x : x.index >= 0.0]/len(ndata['F']))*100.0
        # turn into dataframe
        ndf = pd.DataFrame(ns)
        # reset the index so wdirs becomes a column
        ndf = ndf.reset_index(level=0)
        # adding a column with the name of the bins
        ndf['ws'] = "{} - {}".format(bins[i], bins[i+1])
        # appending each bin to a dataframe
        df = df.append(ndf)
    # binning and extracting wind speeds exceeding the last bin
    tdf = ndata[ndata['F'].gt(bins[-1])]
    # same proceedure as above
    ns = (tdf.groupby('wdirs').size()[lambda x : x.index >= 0.0]/len(ndata))*100.0
    ndf = pd.DataFrame(ns)
    ndf = ndf.reset_index(level=0)
    ndf['ws'] = "> {}".format(bins[-1])
    df = df.append(ndf)
    # renaming the columns for plotting
    df.columns = [r'Vindátt (°)', r'Tíðni (%)', r'Vindhraði (m/s)']
    return df
