from dash import dcc, html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app import app

#external_stylesheets = [dbc.themes.BOOTSTRAP]
#
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

stations = {'1475' : r'Veðurstofureitur', '1477' : r'Reykjavíkurflugvöllur', '3471' : r'Akureyri-Krossanesbraut', '3470' : r'Akureyri-Lögreglustöð', '1473' : r'Straumsvík'}
hours = {'Sólarhringur (00:00 - 24:00)' : "0,24", 'Dagtími (06:00 - 17:00)' : "6,17", 'Kvöldtími (18:00 - 00:00)' : "18,24", 'Dagur og kvöld (06:00 - 00:00)' : "6,24"}
new_hours = {y:x for x,y in hours.items()}
winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}
seasons = [r'Árið', 'Sumar', 'Vetur', 'Vor', 'Haust']

import plotly.express as px
import pandas as pd
import numpy as np

from routes.windrose_app_lib import readMetdata
from routes.windrose_app_lib import sortMetdata
import os, time

stationIds = [stationId for stationId, stationName in stations.items()]

def get_logo():
    return html.Div(id='div-logo',
                children=[
                    html.A(href='https://oruggverk.is/', children=[
                    html.Img(id='logo',className='logo',
                        src=app.get_asset_url('ORUGG.png'),
                        style={'height': '50%', 'width' : '50%'},
                        )]),
                ]
            )

def get_windrose(season):
    return  html.Div([
                html.H3(season),
                dcc.Graph(id='windrose '+season),
                ]#, style={'width': '33.33%', 'float' : 'left', 'display' : 'inline-block'}
            )

controls = html.Div(id='controls', className='controls', children=[
                html.Div([
                    html.Label(r'Veðurstöð'),
                    dcc.Dropdown(
                        id='station',
                        options=[{'label': station, 'value' : stationId} for stationId, station in stations.items()],
                        value=None,
                        placeholder='Select a station'
                        )
                    ], 
                    style={'width' : '40%', 'display' : 'inline-block'}
                    ),
                html.Div([
                    html.Label(r'Tími dags'),
                    dcc.Dropdown(
                        id='hours',
                        options=[{'label': name, 'value' : hours} for name,hours in hours.items()],
                        value=None,
                        placeholder="Select time of day",
                        disabled=True,
                        ),
                    ],
                    #style={'width' : '40%', 'float' : 'right', 'display' : 'inline-block'}
                    style={'width' : '40%', 'display' : 'inline-block'}
                    ),
                html.Div([
                    html.Br(),
                    dbc.Button("Update", id='btn-update', color='secondary', disabled=True, n_clicks=0)
                    ], 
                    style={'width' : '8%', 'float' : 'right', 'display' : 'inline-block'}
                    )
                #], style={'borderBottom' : 'thin lightgrey solid', 'backgroundColor' : '#19223d', 'padding' : '10px 5px'}),
                ], #style={'borderBottom' : 'thin lightgrey solid', 'backgroundColor' : 'rgb(250, 250, 250)', 'padding' : '10px 5px'}),
                )

container = dbc.Container(
        fluid=True,
        style={"margin-top" : "15px", "height" : "calc(100vh - 30px)"},
        children=[
            dbc.Row(
                id="top-row",
                children=[
                    dbc.Col(children=controls),
                ],
            ),
            dbc.Row(
                id='output-row',
                children=[
                    html.Div(id='output-div'),
                    ], style={'textAlign' : 'center'},
                ),
            dbc.Row(
                id="img-row top",
                children=[
                    dbc.Col(id='img-col logo', width=4, children=[
                        get_logo(),
                        dbc.Fade( 
                            children=[
                                dbc.Card(
                                    [
                                    dbc.CardHeader("Selections"),
                                    dbc.CardBody(
                                        [
                                            html.Div([
                                                 dbc.Checklist(
                                                     id='legend-visible-windrose-switch',
                                                     options=[{'label':'Legend visible','value': 1}],
                                                     value=[1],
                                                     switch=True,
                                                 ),
                                                 dbc.Checklist(
                                                     id='freq-range-switch',
                                                     options=[{'label':'Scale frequency','value': 1}],
                                                     value=[],
                                                     switch=True,
                                                 )
                                                 #], style={"display" : "inline-block", "width" :"100%"}) # end of html.div
                                                ])# , style={"display" : "flex"}) # end of html.div
                                        ]) # end of card body
                                    ]), # end of card
                            ], 
                                id='fade-transition-windroses', 
                                is_in=False,
                                style={'transition' : 'opacity 2000ms ease'}, 
                                timeout=2000
                                ), # end of fade
                        ]),
                    dbc.Col(id='img-col wrose1', width=4, children=get_windrose(r'Árið')),
                    dbc.Col(id='img-col wrose2', width=4, children=get_windrose('Sumar')),
                ],
            ),
            dbc.Row(
                id="img-row bottom",
                children=[
                    dbc.Col(id='img-col wrose3', width=4, children=get_windrose('Vetur')),
                    dbc.Col(id='img-col wrose4', width=4, children=get_windrose('Vor')),
                    dbc.Col(id='img-col wrose5', width=4, children=get_windrose('Haust')),
                ],
            ),
            dbc.Row(
                html.Div(id='intermediate-df', style={'display' : 'none'}),
                ),
        ],
    )

@app.callback(
        [
            Output(component_id='hours', component_property='disabled'),
            Output(component_id='hours', component_property='value'),
        ],
        [
            Input(component_id='station', component_property='value'),
        ], prevent_initial_call=True)
def update_met_df(stationId):
    if stationId is not None:
        return [False, None]
    else:
        raise PreventUpdate

@app.callback(
        [
            Output(component_id='btn-update', component_property='disabled'),
            Output(component_id='intermediate-df', component_property='children')
        ],
        [
            Input(component_id='hours', component_property='value'),
        ], 
        [
            State(component_id='station', component_property='value'),
        ],prevent_initial_call=True)

def update_metTime_df(hours, stationId):
    if hours is not None:
        metdata_df = readMetdata.run_readMetdata(os.path.join(os.getcwd(),'mysite', 'routes', 'windrose_app_lib'), stationIds=[stationId])[stationId]
        metdata_df.reset_index(inplace=True) # index currently stationId (nonunique), which will be moved to a separate column
        metTime = sortMetdata.sortTime(stationId, metdata_df, hours)
        dff = {}
        for season in seasons:
            data = sortMetdata.sortSeason(metTime, season)
            df = sortMetdata.sortWdir(data)
            df['frequency%'] = df['frequency']*100.0
            df['direction_name'] = [winddirs[str(wd)] for wd in df['direction']]
            df.reset_index(inplace=True) # The indices before where repeated, therefore data was missing in to_json()
            dff[season] = df
        dff = pd.DataFrame([dff]).to_json()
        return [False, dff]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output(component_id=r'windrose Árið',component_property='figure'),
        Output(component_id='windrose Sumar',component_property='figure'),
        Output(component_id='windrose Vetur',component_property='figure'),
        Output(component_id='windrose Vor',component_property='figure'),
        Output(component_id='windrose Haust',component_property='figure'),
        Output(component_id='output-div',component_property='children'),
        Output(component_id='fade-transition-windroses',component_property='is_in'),
    ],
    [
        Input(component_id='btn-update', component_property='n_clicks'),
        Input(component_id='legend-visible-windrose-switch', component_property='value'),
        Input(component_id='freq-range-switch', component_property='value'),
    ],
    [
        State(component_id='intermediate-df', component_property='children'),
        State(component_id='station', component_property='value'),
        State(component_id='hours', component_property='value'),
    ])
def update_data_from_button(nclicks, legend_visible, scale_frequency, df_json, stationId, hours):
    if (nclicks > 0 and hours is not None):
        df = pd.read_json(df_json)
        df = df.loc[0]
        dff, freqRange, figs = {}, {}, []
        for season in seasons:
            dff[season] = pd.DataFrame.from_dict(df[season])
            freqRange[season] = dff[season].groupby(['direction']).frequency.sum().max()
            fig = plot_windrose(dff[season])
            maxRange = freqRange[season]
            fig.update_layout(
                {
                    'polar' : {'radialaxis' : {'range' : [0, maxRange*100]}},
                }
            )
            if legend_visible:
                fig.update_layout(
                    showlegend=True
                )
            figs.append(fig)
        if scale_frequency:
            maxRange = max(freqRange.values())
            for fig in figs:
                fig.update_layout(
                    {
                        'polar' : {'radialaxis' : {'range' : [0, maxRange*100]}},
                    }
                )
        output_str = r'Vindrósir fyrir veðurstöð: {}, fyrir: {}'.format(stations[stationId], new_hours[hours])
        figs.append(output_str)
        figs.append(True)
    else:
        figs = []
        for season in seasons:
            fig = px.bar_polar([])
            fig.update_layout(template = None, xaxis_title = '', yaxis_title = '')
            fig.update_xaxes(showgrid = False, showticklabels = False, zeroline = False)
            fig.update_yaxes(showgrid = False, showticklabels = False, zeroline = False)
            figs.append(fig)
        figs.append('')
        figs.append(False)
    return figs


def plot_windrose(df):
    fig = px.bar_polar(df, r="frequency%", theta="direction_name",# 0.3],
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
            'polar' : {'radialaxis' : {'ticks' : '', 'ticksuffix' : '%'}},
        }
        )
    fig.update_layout(
        showlegend=False
    )
    fig.update_layout(transition_duration=500)
    return fig


layout = container

#if __name__ == "__main__":
#    app.layout = container
#    app.run_server(debug=True)
