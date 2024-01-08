import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app import app
import sys, os
#sys.path.append("../..")
sys.path.append("..")
from reading.readfromgit import get_stationIds, get_rawmetdata, get_session
from reading.read_generic_station import read_from_station

#external_stylesheets = [dbc.themes.BOOTSTRAP]
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

import os, time

# sorting
from reading.sort_station_data import (sort_wdirs, sort_months, sort_hours, sort_windrose)
from reading.plot_station_data import (plot_windrose, plot_weibull, plot_directions, plot_meanws)

# creating a session to download raw metdata from github
github_session, user = get_session()
# the station ids that are available on github
stationIds = get_stationIds(github_session, user)
stationIdsList = list(zip(stationIds['name'], stationIds['nr']))
# default station 
defaultStationId = '1475'
defaultStationName = [stationId for stationName, stationId in stationIdsList if str(stationId) == defaultStationId][0]
# seasons and times
seasonsDict = { r'Árið' : "1,2,3,4,5,6,7,8,9,10,11,12", 'Vetur (des-feb)' : "12,1,2", 'Sumar (jún-ágú)' : "6,7,8", 'Vor (mar-maí)' : "3,4,5", 'Haust (sep-nóv)' : "9,10,11", 'Lengra sumar (maí-sep)' : "5,6,7,8,9"}
timesDict = {'Dagtími (08-18)' : "8,18", 'Kvöldtími (18-24)' : "18,24", 'Næturtími (00-08)' : "0,8", 'Dagur (08-22)' : "8, 22", 'Allur dagur (08-24)' : "8, 24", 'Sólarhringur' : '0,24'}
# default season and time
defaultSeason = 'Sumar (jún-ágú)'
defaultTime = 'Dagur (08-22)'

# app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}
app_color = {"graph_bg": "#19223d", "graph_line": "#007ACE"}
container = html.Div([
    # ------------------------------------------------------------------
                # header
                html.Div([
                    # description
                    html.Div([
                        html.H4("Veðurgögn", className="app__header__title"),
                        html.P(r"hordurps", className="app__header__title--grey")
                    ], className="app__header__desc"),
                    # logo
                    html.Div([
                        html.A(
                            html.Img(
                                src=app.get_asset_url('ORUGG.png'),
                                #src=os.path.join('assets','ORUGG.png'),
                                className="app__menu__img",
                            ),
                            href="https://oruggverk.is/thjonusta/vindur/"
                        )
                    ], className="app__header__logo"),
                ], className="app__header"),
    # ------------------------------------------------------------------

                # body / content
                html.Div([
        # -------------------------------------------------------------
                    # top row
                    html.Div([
            # ---------------------------------------------------------
                        # direction
                        html.Div([
                            html.Div([
                                html.H6("Vindrós", className="graph__title")
                            ]),
                            dcc.Loading(id="loading01", 
                                children=dcc.Graph(id='wind-rose', 
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    )
                                )
                            ),
                        ], className="one-half column graph__container"),
            # ---------------------------------------------------------
                        # mean ws
                        html.Div([
                            html.Div([
                                html.H6("Weibull líkindadreifing", className="graph__title")
                            ]),
                            dcc.Loading(id="loading02", 
                                children=dcc.Graph(id='wind-weibull', 
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    )
                                )
                            ),
                        ], className="one-half column graph__container"),
            # ---------------------------------------------------------
                        # controls
                        html.Div([
                            dcc.Dropdown(
                                id='stationId-selection',
                                options=[{'label': stationName, 'value' :
                                    stationId} for stationName, stationId in stationIdsList],
                                value=defaultStationName,
                                clearable=False,
                                style={'font' : 'Montserrat'}
                            ),
                            dcc.RadioItems(
                                id='season-selection', style={'color' : 'white', 'width' : '100%'},
                                options=[seasonName for seasonName, seasonId in seasonsDict.items()],
                                value='Sumar (jún-ágú)',
                                inline=True,
                                labelStyle={'display': 'inline-block', 'text-align' : 'justify', 'margin-right' : 10, 'font' : 'Montserrat'},
                            ),
                            dcc.RadioItems(
                                id='time-selection', style={'color' : 'white', 'width' : '100%'},
                                options=[timeName for timeName, timeId in timesDict.items()],
                                value='Sólarhringur',
                                inline=True,
                                labelStyle={'display': 'inline-block', 'text-align' : 'justify', 'margin-right' : 10, 'font' : 'Montserrat'},
                            )
                        ]),
                        dcc.Store(id="session", storage_type="session"),
                    ], className="row"),                    
        # -------------------------------------------------------------
                    # bottom row
                    html.Div([
            # ---------------------------------------------------------
                        # direction
                        html.Div([
                            html.Div([
                                html.H6("Vindáttir", className="graph__title")
                            ]),
                            dcc.Loading(id="loading03", 
                                children=dcc.Graph(id='wind-direction', 
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    )
                                )
                            ),
                        ], className="one-half column graph__container"),
            # ---------------------------------------------------------
                        # mean ws
                        html.Div([
                            html.Div([
                                html.H6("Vindhraði", className="graph__title")
                            ]),
                            dcc.Loading(id="loading04", 
                                children=dcc.Graph(id='wind-meanws', 
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    )
                                )
                            ),
                        ], className="one-half column graph__container"),
            # ---------------------------------------------------------
                    ], className="row"),
                    html.Div(id="heimildir"),
        # -------------------------------------------------------------
                ], className="app__content"),
    # ------------------------------------------------------------------
                html.Div(id='store-df', style={'display' : 'none'}),
            ], className="app__container")

layout = container
#layout = html.Div([
#    html.H1('hordurps')
#    ])
# Storing the data frame with raw met data in to a html div
@callback(
        Output("store-df", "children"),
        Output("session", "data"),
        Input("stationId-selection", "value"),
)
def collect_station_data(stationId):
    stationId = str(stationId)
    # finding the file name with the data for this station
    dataFile = stationIds.query('nr=={stationId}'.format(stationId=stationId))['data']
    # finding the index to read the file name
    idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
    # finding the source of the station
    sourceName = stationIds.query('nr=={stationId}'.format(stationId=stationId))['source'][idx]
    # getting the raw data from github
    #data = get_rawmetdata(github_session, user, source='vi', stationId=stationId, dataFile=dataFile[idx])
    data = get_rawmetdata(github_session, user, source=sourceName, stationId=stationId, dataFile=dataFile[idx])
    # cleaning the data, i.e. only extract the necessary columns
    ndata = read_from_station(data)
    ndata = sort_wdirs(ndata)
    df = ndata.to_json() # store into json dict to store in a html div
    return df, stationId


# Calling the raw data frame and creating a wind rose
@callback(
        [
            Output("wind-rose", "figure"),
            Output("wind-weibull", "figure"),
        ],
        [
            #Input("stationId-selection", "value"),
            Input("session", "modified_timestamp"),
            Input("season-selection", "value"),
            Input("time-selection", "value"),
        ],
        [
            State("store-df", "children"),
            State("session", "data")
            ],
)
#def return_windrose(stationId, season, timeofday, ts, df_json):
def return_windrose(ts, season, timeofday, df_json, stationId):
    if df_json is not None:
        df = pd.read_json(df_json)                      # converting the json dict to dataframe
        ndata = df
        ndata, months = sort_months(ndata, [int(s) for s in seasonsDict[season].split(',')])
        ndata, hours = sort_hours(ndata, [int(t) for t in timesDict[timeofday].split(',')])

        wdata = sort_windrose(ndata)

        # finding the index to read the file name
        idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
        # finding the station name for plotting purposes
        stationName = stationIds.query('nr=={stationId}'.format(stationId=stationId))['name'][idx]
        # plotting a wind rose
        fig = plot_windrose(wdata, stationName, months, hours)
        # plotting weibull
        fig2 = plot_weibull(ndata, stationName, months, hours)
        # plotting the frequency of each wind direction in the season
        fig3 = plot_directions(df, stationName, months, hours)
        # plotting the mean wind speed of each wind direction in the season
        fig4 = plot_meanws(df, stationName, months, hours)

        return [fig, fig2]
    else:
        fig = px.bar_polar([])
        fig.update_layout(template = None, xaxis_title = '', yaxis_title = '')
        fig.update_xaxes(showgrid = False, showticklabels = False, zeroline = False)
        fig.update_yaxes(showgrid = False, showticklabels = False, zeroline = False)
        fig.update_layout(plot_bgcolor=app_color["graph_bg"], paper_bgcolor=app_color["graph_bg"])
        return [fig, fig]


# Calling the raw data frame and creating a wind rose
@callback(
        [
            Output("wind-direction", "figure"),
            Output("wind-meanws", "figure")
        ],
        [
            #Input("stationId-selection", "value"),
            Input("session", "modified_timestamp"),
            Input("time-selection", "value"),
        ],
        [
            State("season-selection", "value"),
            State("store-df", "children"),
            State("session", "data")
        ],
)
def return_meanws_directions(ts, timeofday, season, df_json, stationId):
    if df_json is not None:
        df = pd.read_json(df_json)                      # converting the json dict to dataframe
        ndata = df
        ndata, months = sort_months(ndata, [int(s) for s in seasonsDict[season].split(',')])
        ndata, hours = sort_hours(ndata, [int(t) for t in timesDict[timeofday].split(',')])

        wdata = sort_windrose(ndata)

        # finding the index to read the file name
        idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
        # finding the station name for plotting purposes
        stationName = stationIds.query('nr=={stationId}'.format(stationId=stationId))['name'][idx]
        # plotting the frequency of each wind direction in the season
        fig3 = plot_directions(df, stationName, months, hours)
        # plotting the mean wind speed of each wind direction in the season
        fig4 = plot_meanws(df, stationName, months, hours)

        return [fig3, fig4]
    else:
        fig = px.bar_polar([])
        fig.update_layout(template = None, xaxis_title = '', yaxis_title = '')
        fig.update_xaxes(showgrid = False, showticklabels = False, zeroline = False)
        fig.update_yaxes(showgrid = False, showticklabels = False, zeroline = False)
        fig.update_layout(plot_bgcolor=app_color["graph_bg"], paper_bgcolor=app_color["graph_bg"])
        return [fig, fig]

@callback(
    Output("heimildir", "children"),
    Input("stationId-selection", "value"),
    Input("session", "modified_timestamp"),
    prevent_initial_call=True
    )
def return_owner(stationId,ts):
    idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
    ownersName = stationIds.query('nr=={stationId}'.format(stationId=stationId))['owner'][idx]
    return 'Eigandi gagna {owner}'.format(owner=ownersName)