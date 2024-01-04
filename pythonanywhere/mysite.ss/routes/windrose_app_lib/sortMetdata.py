import numpy as np
import pandas as pd

# seasons = sortTime(stationId, daytime)
#daytime = '_'+daytime
#season_str = ["Sumar", "Vetur", r"Allt árið"] 
#for i, season in enumerate(seasons):
#    (ws, wg) = sortMet(season)
#    wd = sortWS(ws)


def sortWdir(data):
    (ws, wg) = sortMet(data)
    wd = sortWS(ws)
    return wd

def sortMet(season):
    """
        Sorting the metdata into wind directions
    """
    D = season['D']
    wdirs = np.arange(0,360,30)
    ws, wg = {}, {}
    # sorting into dicts with keys and values based on the wind direction
    for wdir in wdirs:
        #print("wind direction", wdir)
        if wdir==0: # for 0 deg, the range is from 345 to 15 deg
            """
                For a wind direction X, the sector is X-15 and x+15
                If the recorded wind direction Y is between X+15 (not inclusive) and X-15 (inclusive),
                then the recorded data is placed into that wind direction X

                Tried doing the other way around without any change
            """
            ws[str(wdir)] = (season.query("D < "+str(wdir+15)+"| D >= "+str(wdirs[-1]+15)))['F'].values	# wind speed
            wg[str(wdir)] = (season.query("D < "+str(wdir+15)+"| D >= "+str(wdirs[-1]+15)))['FG'].values # gust speed
        else: # for other degs, the range is -15 degs to +15 degs
            ws[str(wdir)] = (season.query("D < "+str(wdir+15)+"& D >= "+str(wdir-15)))['F'].values		# wind speed
            wg[str(wdir)] = (season.query("D < "+str(wdir+15)+"& D >= "+str(wdir-15)))['FG'].values		# gust speed
    return (ws, wg)


def sortSeason(vi, season):
    #print("Sorting for season", season)
    if ("Sumar" in season or "Summer" in season):
        data = vi.query("MAN < 9 & MAN > 5") # 6,7,8
    elif ("Vetur" in season or "Winter" in season):
        data = vi.query("MAN > 11 | MAN < 3") # 12,1,2
    elif ("Haust" in season or "Autumn" in season):
        data = vi.query("MAN < 12 & MAN > 8") # 9,10,11
    elif ("Vor" in season or "Spring" in season):
        data = vi.query("MAN < 6 & MAN > 2") # 3,4,5
    elif (r"Árið" in season or "Year" in season):
        data = vi
    #print("Unique months", data.MAN.unique())
    return data


def sortWS(ws):
    """
        Sorting for the windrose.

        Creating velocity bins and calculating the frequency of each bin.
    """

    #vels = [0, 5, 8, 11, 14, 14]
    vels = [0, 2.5, 4, 6, 8, 10, 15, 15]
    wd = {}
    data, freq = {}, {}
    # sorting into dicts with keys and values based on the wind direction
    df = pd.DataFrame([])
    velocities = sum([len(x) for x in ws.values()])
    for k, v in ws.items():
        for i, vel in enumerate(vels):
            # if maximum velocity
            if vel == vels[-1]:
                vel_count = (v > vel).sum()
                j = i
                freq[">" + str(vels[-1])] = (vel_count/velocities)
            # if velocity less than the maximum velocity
            else:
                vel_lt = (v <= vel).sum()
                vel_gt = (v < vels[i+1]).sum()
                vel_count = vel_gt-vel_lt
                j = i+1
                freq[str(vels[i])+"-"+str(vels[j])] = (vel_count/velocities)
        d = [int(k)]*int(len(freq))
        tdf = pd.DataFrame([d, list(freq.keys()), list(freq.values())]).T

        df = df.append(tdf)
    #df.columns = ['direction', 'strength','frequency']
    df.columns = ['direction', r'Vindhraði (m/s)','frequency']
    return df

def sortTime(stationId, vi, daytime=None):
    """                         
    STOD                    TIMI      D     F    FG    AR   MAN  Dagur  klst  Min
    3471  2006-06-01 00:00:00 UTC  227.1  1.46  2.41  2006    6      1     0    0
    """
    hrmin, hrmax = daytime.rsplit(',')[0], daytime.rsplit(',')[1]
    if daytime is None:
        return vi
    else:
        if stationId == "3470":
            timeSorted_vi = vi.query("KLST >= "+str(hrmin)+" & KLST <= "+str(hrmax))
            #print("Unique hours", timeSorted_vi["KLST"].unique())
        else:
            timeSorted_vi = vi.query("klst >= "+str(hrmin)+" & klst <= "+str(hrmax))
            #print("Unique hours", timeSorted_vi["klst"].unique())
        return timeSorted_vi
    #vifiles = readvis(stationId)
    #seasons = getMet(vifiles, stationId)
    #sorted_seasons = []
   # for season in seasons:
   #     if "day" in daytime:
   #         newseason = season.query("klst >= 6")
   #     elif "night" in daytime:
   #         newseason = season.query("klst < 6")
   #     else:
   #         import sys
   #         sys.exit("STOP: unable to determine the time of day")
   #     sorted_seasons.append(newseason)
   # return tuple(sorted_seasons)
