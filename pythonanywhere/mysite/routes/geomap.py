from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import json


import pandas as pd
import numpy as np
import os, re
import io
import base64
import shutil

from app import app

from reading.readfromgit import get_stationIds, get_projects, get_session
# creating a session to download raw metdata from github
github_session, user = get_session()
# the station ids that are available on github
stationIds = get_stationIds(github_session, user)
projects = get_projects(github_session, user)


folder_on_server = "static_data"



### Authentiation 
import dash_auth
#from os.path import join, dirname
#from dotenv import load_dotenv

#dotenv_path = join(dirname(__file__), '.env')
#load_dotenv(dotenv_path)

#VALID_USER_NAME_PASSWORD_PAIRS = {os.environ.get("username") :
#os.environ.get("passwd")}

#auth = dash_auth.BasicAuth(
#        app,
#        VALID_USER_NAME_PASSWORD_PAIRS
#)


def project_and_metdata_locations(selected):
    if selected == 'projects':
        # projects_data = 'verkefni.csv'
        # projects_df = pd.read_csv(os.path.join('assets', projects_data))

        projects_df = projects
        projects_df['type'] = 'Verkefni'
        df = projects_df
    
    elif selected == 'metdata':
        # stodvar_data = 'vedurstodvar.csv'
        # stodvar_df = pd.read_csv(os.path.join('assets', stodvar_data))

        stodvar_df = stationIds
        stodvar_df['type'] = r'Veðurstöðvar'
        df = stodvar_df

    
    #df = pd.concat([projects_df, stodvar_df],axis=0)
    #markerdata = [dict(name=df.iloc[i]['name'], lat=df.iloc[i].lat, lon=df.iloc[i].lon) for i in range(0, len(df))]
    markers = [dl.CircleMarker(center=[df.iloc[i].lat, df.iloc[i].lon], children=dl.Popup(df.iloc[i]['name'])) for i in range(0, len(df))]
    return markers


# --------------------
# App UI
# --------------------

lat, lng = 64.1314, -21.897
MAP_ID = "map-id"
COORDINATE_CLICK_ID = "coordinate-click-id"
container = html.Div([
    #html.H1("Click on map for coordinates"),
    dcc.Input(
            id='lat-input',
            type='text',
            placeholder='latitude',
            debounce=True,
        ),
    dcc.Input(
            id='lon-input',
            type='text',
            placeholder='longitude',
            debounce=True,
        ),
    html.Div([
        # dl.Map(id=MAP_ID, center=[lat,lng], zoom=12,
        dl.Map(id=MAP_ID, center=[lat,lng], zoom=6.25,
            children=[
                dl.TileLayer(),
                dl.LayersControl(
                    [
                        dl.Overlay(dl.LayerGroup(project_and_metdata_locations('projects')), name="projects", checked=True),
                        dl.Overlay(dl.LayerGroup(project_and_metdata_locations('metdata')), name="metdata", checked=True)]),
                dl.Marker(id='selected-marker', position=(lat, lng), children=dl.Popup("Lat/lon coords are {}, {}".format(lat,lng))),
            ], 
            style={"height" : "100vh", "width" : "100%", "position" : "relative"}),
        ], style={"position" : "relative", "z-index" : "0"}),
    ])

#app.layout = container
layout = container


#project_and_metdata_locations()

# ------------------
# Handle controls
# ------------------
@app.callback([Output('selected-marker', 'position'),
        Output('selected-marker', 'children')],
        [Input(MAP_ID, 'click_lat_lng'),
        Input('lat-input','value'), Input('lon-input','value')],
        prevent_initial_call=True)
def click_coords(e, lat_input, lon_input):
    #    print(lat_input)
    #    if (lat_input is not None and lon_input is not None):
    #        lat = float(lat_input)
    #        lng = float(lon_input)
    #        return [[lat,lng], dl.Popup("Lat/lon coords are {}, {}".format(round(lat,4), round(lng,4)))]
    #    elif e is not None:
    #        coords = json.dumps(e).rsplit()
    #        lat = float(coords[0].split('[')[-1].split(',')[0])
    #        lng = float(coords[-1].split(']')[0])
    #        return [[lat,lng], dl.Popup("Lat/lon coords are {}, {}".format(round(lat,4), round(lng,4)))]
    #    else:
    #        print("HERE")
    #        #lat = float(lat_input)
    #        #lng = float(lon_input)
    #        return [[lat,lng], dl.Popup("Lat/lon coords are {}, {}".format(round(lat,4), round(lng,4)))]
    try:
        lat = float(lat_input)
        lng = float(lon_input)
    except:
        if e is not None:
            coords = json.dumps(e).rsplit()
            lat = float(coords[0].split('[')[-1].split(',')[0])
            lng = float(coords[-1].split(']')[0])
        else:
            lat, lng = 64.1314, -21.897
    return [[lat,lng], dl.Popup("Lat/lon coords are {}, {}".format(round(lat,4), round(lng,4)))]



