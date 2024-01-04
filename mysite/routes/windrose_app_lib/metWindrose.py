
stations = {'1475' : r'Veðurstofureitur', '1477' : r'Reykjavíkurflugvöllur', '3471' : r'Akureyri-Krossanesbraut', '3470' : r'Akureyri-Lögreglustöð'}
hours = {'Allur dagur' : "0,24", 'Dagtími (06:00 - 17:00)' : "6,17", 'Kvöldtími (18:00 - 00:00)' : "18,24", 'Dagur og kvöld (06:00 - 00:00)' : "6,24"}
winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}

import plotly.express as px
import pandas as pd
import numpy as np

from windrose_app_lib import readMetdata
from windrose_app_lib import sortMetdata
import os

stationIds = [stationId for stationId, stationName in stations.items()]
metdata = readMetdata.run_readMetdata(os.path.join(os.getcwd(),'windrose_app_lib'), stationIds=stationIds)
seasons = [r'Árið', 'Sumar', 'Vetur', 'Vor', 'Haust']

def max_frequency(metdata,hours):
    seasons = [None, 'Sumar', 'Vetur', 'Vor', 'Haust']
    max_freq_station = {}
    for stationId in metdata.keys():
        max_freq_hours = {}
        for daytime, hour in hours.items():
            max_freq_season = []
            for season in seasons:
                data = metdata[stationId]
                data = sortMetdata.sortTime(stationId, data, hour)
                if season is not None:
                    data = sortMetdata.sortSeason(data, season)
                df = sortMetdata.sortWdir(data)
                max_freq_season.append(df.groupby(['direction']).frequency.sum().max())
            max_freq_hours[hour] = max(max_freq_season)
        max_freq_station[stationId] = max_freq_hours
    return max_freq_station


#print(max_freq_station['1475']['6,17'])



def plotWindrose(df,max_freq_station,stationId,hour,figName):
    if not os.path.exists(os.path.join(stationId, 'windroses')):
        os.makedirs(os.path.join(stationId, 'windroses'))
    dfc1 = df.copy()
    maxRange = max_freq_station[stationId][hour]
    dfc1['frequency%'] = df['frequency']*100.0
    dfc1['direction_name'] = [winddirs[str(wd)] for wd in df['direction']]
    fig = px.bar_polar(dfc1, r="frequency%", theta="direction_name",# 0.3],
            color=r"Vindhraði (m/s)", template="plotly", #template="plotly_dark",
            color_discrete_sequence= px.colors.qualitative.Pastel2) #sequential.PuBuGn) #px.colors.sequential.Plasma_r)

    """
        Change to to 'polar' : 'angularaxis'/'radialaxis' : 'visible' : False, to only see the sectors
        Change the gridcolor from 'white' to 'rgba(0, 0, 0, 0)' or viceversa 
        change the linecolor from 'white' to 'black' or viceversa
    """
    fig.update_layout(
        {
            'paper_bgcolor' : 'rgba(0, 0, 0, 0)',
            'plot_bgcolor' : 'rgba(0, 0, 0, 0)',
            'font' : {'color' : 'grey'},
            'polar' : {'radialaxis' : {'ticks' : '', 'ticksuffix' : '%', 'range' : [0, maxRange*100]}},
            #'polar' : {'angularaxis' : {'visible' : True, 'gridcolor' : 'rgba(0, 0, 0, 0)', 'linecolor' : 'black', 'ticks' : ''},
            #    'bgcolor' : 'rgba(0, 0, 0, 0)',
            #    'radialaxis' : {'visible': True, 'showgrid': True, 'gridcolor' : 'rgba(0,0,0,0)', 'linecolor' : 'black', 'ticks' : '', 'ticksuffix' : '%', 'range' : [0, maxRange*100]}},
        }
        #{
        #    'paper_bgcolor' : 'rgba(0, 0, 0, 0)',
        #    'plot_bgcolor' : 'rgba(0, 0, 0, 0)',
        #    'font' : {'color' : 'grey'},
        #    'polar' : {'angularaxis' : {'visible' : True, 'gridcolor' : 'rgba(0, 0, 0, 0)', 'linecolor' : 'black', 'ticks' : ''},
        #        'bgcolor' : 'rgba(0, 0, 0, 0)',
        #        'radialaxis' : {'visible': True, 'showgrid': True, 'gridcolor' : 'rgba(0,0,0,0)', 'linecolor' : 'black', 'ticks' : '', 'ticksuffix' : '%', 'range' : [0, maxRange*100]}},
        #}
    )
    fig.write_image(os.path.join(stationId, 'windroses',figName+'_shield.png'))
    fig.update_layout(
        {
            'polar' : {
                'angularaxis' : {'gridcolor' : 'black', 'linecolor' : 'black'},
                'bgcolor' : 'rgba(0, 0, 0, 0)',
                'radialaxis' : {'gridcolor' : 'black', 'linecolor': 'black', 'ticks' : '', 'ticksuffix' : '%', 'range' : [0, maxRange*100]}},
        }
    )
    fig.write_image(os.path.join(stationId, 'windroses',figName+'_transparent.png'))


def plotWindroseLine(df,max_freq_station,stationId,hour,figName):
    if not os.path.exists(os.path.join(stationId, 'windroses')):
        os.makedirs(os.path.join(stationId, 'windroses'))
    maxRange = max_freq_station[stationId][hour]
    dfc2 = df.groupby('direction')['frequency'].sum().reset_index()
    dfc2['frequency%'] = dfc2['frequency']*100.0
    dfc2['direction_name'] = [winddirs[str(wd)] for wd in dfc2['direction']]
    fig = px.line_polar(dfc2, r="frequency%", theta="direction_name",# 0.3],
            template="plotly", #template="plotly_dark",
            #color_discrete_sequence= px.colors.qualitative.Pastel2, line_close=True) #sequential.PuBuGn) #px.colors.sequential.Plasma_r)
            #color_discrete_sequence= px.colors.sequential.PuBuGn, 
            line_close=True) #sequential.PuBuGn) #px.colors.sequential.Plasma_r)

    """
        Change to to 'polar' : 'angularaxis'/'radialaxis' : 'visible' : False, to only see the sectors
        Change the gridcolor from 'white' to 'rgba(0, 0, 0, 0)' or viceversa 
        change the linecolor from 'white' to 'black' or viceversa
    """
    fig.update_layout(
        {
            'paper_bgcolor' : 'rgba(0, 0, 0, 0)',
            'plot_bgcolor' : 'rgba(0, 0, 0, 0)',
            'font' : {'color' : 'grey'},
            'polar' : {'angularaxis' : {'visible' : True, 'gridcolor' : 'white', 'linecolor' : 'rgba(0, 0, 0, 0)', 'ticks' : ''},
                'bgcolor' : 'rgba(0, 0, 0, 0)',
                'radialaxis' : {'visible': False, 'gridcolor' : 'rgba(0, 0, 0, 0)', 'linecolor' : 'rgba(0, 0, 0, 0)', 'ticks' : '', 'ticksuffix' : '%', 'range' : [0, maxRange*100]}},
        }
    )
    fig.write_image(os.path.join(stationId, 'windroses',figName+'_line.png'))



if __name__ == "__main__":
    max_freq_station = max_frequency(metdata, hours)
    print('*******************')
    hour = '6,17'
    if not os.path.exists('windroses'):
        os.makedirs('windroses')
    else:
        import sys
        sys.exit("STOP: folder windroses exists, please remove the folder before rerunning!")
    for stationId in stationIds:
        for season in seasons:
            data = metdata[stationId]
            data = sortMetdata.sortSeason(data,season)
            data = sortMetdata.sortTime(stationId, data, hour)
            (ws, wg) = sortMetdata.sortMet(data)
            wd = sortMetdata.sortWS(ws)
            plotWindrose(wd, max_freq_station, stationId, hour, figName=stationId+'_'+hour+'_'+season)
            plotWindroseLine(wd, max_freq_station, stationId, hour, figName=stationId+'_'+hour+'_'+season)


