import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
#from app import app

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

stations = {'1475' : r'Veðurstofureitur', '1477' : r'Reykjavíkurflugvöllur', '3471' : r'Akureyri-Krossanesbraut', '3470' : r'Akureyri-Lögreglustöð'}
hours = {'Sólarhringur (00:00 - 24:00)' : "0,24", 'Dagtími (06:00 - 17:00)' : "6,17", 'Kvöldtími (18:00 - 00:00)' : "18,24", 'Dagur og kvöld (06:00 - 00:00)' : "6,24"}
new_hours = {y:x for x,y in hours.items()}
winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}
seasons = [r'Árið', 'Sumar', 'Vetur', 'Vor', 'Haust']

import plotly.subplots as sp
import plotly.graph_objects as go
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

def get_wdir_frequency():
    return  html.Div(id='html-graph', children = [
        # dcc.Graph(id='wdir-frequency-graph'),
                ]#, style={'width': '33.33%', 'float' : 'left', 'display' : 'inline-block'}
            )

def get_windrose(season):
    return  html.Div([
                html.H3(season),
                dcc.Graph(id='windrose '+season),
                ]#, style={'width': '33.33%', 'float' : 'left', 'display' : 'inline-block'}
            )

greiningar = {r'Vindrósir' : 'windrose', r'Vindáttir' : 'winddirs'}
controls = html.Div(id='controls', className='controls', children=[
                html.Div([
                    html.Label(r'Greining'),
                    dcc.Dropdown(
                        id='analysis',
                        options=[{'label': k, 'value' : v} for k,v in greiningar.items()],
                        value=None,
                        placeholder='Select an analysis'
                        ),
                    ], style={'width' : '10%', 'display' : 'inline-block'}),
                html.Div([
                    html.Label(r'Veðurstöð'),
                    dcc.Dropdown(
                        id='station',
                        options=[{'label': station, 'value' : stationId} for stationId, station in stations.items()],
                        value=None,
                        placeholder='Select a station',
                        #disabled=True,
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
                        #disabled=True,
                        ),
                    ],
                    #style={'width' : '40%', 'float' : 'right', 'display' : 'inline-block'}
                    style={'width' : '40%', 'display' : 'inline-block'}
                    ),
                html.Div([
                    html.Br(),
                    dbc.Button("Update", id='btn-update', color='secondary', n_clicks=0) # disabled=True, n_clicks=0)
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
                    ],
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
                                                     id='meanwind-frequency-switch',
                                                     options=[{'label':'Mean wind speed','value': 1}],
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
                    #dbc.Col(id='img-col wrose1', width=4, children=get_windrose(r'Árið')),
                    dbc.Col(id='img-col wrose1', width=8, children=get_wdir_frequency()),
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
            Input(component_id='analysis', component_property='value'),
            Input(component_id='hours', component_property='value'),
        ], 
        [
            State(component_id='station', component_property='value'),
        ],prevent_initial_call=True)

def update_metTime_df(analysis, hours, stationId):
    if hours is not None:
        print("collecting metdata for: ", stationId)
        # Reading the raw data from the met station
        metdata_df = readMetdata.run_readMetdata(os.path.join(os.getcwd(),'routes', 'windrose_app_lib'), stationIds=[stationId])[stationId]
        metdata_df.reset_index(inplace=True) # index currently stationId (nonunique), which will be moved to a separate column
        # Sorting the data for the time interval (e.g. hours : 06:00 to 18:00)
        metTime = sortMetdata.sortTime(stationId, metdata_df, hours)
        dff = {}
        for season in seasons:
            # Sorting the data for the seasons
            data = sortMetdata.sortSeason(metTime, season)
            if 'winddirs' in analysis:
                """
                    The code for a graph of wind directions vs frequency or mean
                    wind speed begins here.

                    Input is a df from sortSeasons
                """
                # Sorting the metdata for the wind directions
                (ws, wg) = sortMetdata.sortMet(data)    # ws is a dict where the wdirs are keys and values are the wind speeds for the wdir in an array
                # Extracting the mean wind speed
                mean_speed = {} # creating an empty dict
                dict_values = [*ws.values()] # getting the values from the ws dict, which is now a list of lists
                flat_values = [item for sublist in dict_values for item in sublist] # flattening the list so all wind speeds are in a single list
                total_count = len(np.array(flat_values) > 0) # counting the total number of instances where the wind speed is greater than 0
                for wdir, wspeed in ws.items(): # for each wind direction, get the wind speeds
                    # into the previously empty dict, make the key be the wdir and
                    # the values is a list of the mean wind speed for the wdir and
                    # the frequency of the wdir
                    mean_speed[wdir] = [round(np.mean(wspeed),2), round((len(wspeed>0)/total_count),3)]
                df = pd.DataFrame(mean_speed) # turn the dict into a dataframe
                df.index = ['mean_ws', 'frequency'] # name the indices since the columns are the wdirs (0, 30, .., 330)
                df = df.T # transpose the dataframe so the wdirs are now the indices
                df['direction']= df.index # create a column with the wdirs (0, 30, .., 330)
                """
                    The code for the graph of wind directions vs frequency or mean
                    wind speed ends here.
                """
            elif 'windrose' in analysis:
                """
                    The code for a graph of the windroses begins here.

                    Input is a df from sortSeasons
                """
                df = sortMetdata.sortWdir(data)
                """
                    The code for a graph of the windroses ends here.
                """
            df['frequency%'] = df['frequency']*100.0 # calculate the frequency of each wdir in %
            df['direction_name'] = [winddirs[str(wd)] for wd in df['direction']] # name the wdirs (0 becomes N, 90 becomes E, etc.)
            df.reset_index(inplace=True) # The indices before where repeated, therefore data was missing in to_json()
            dff[season] = df # collect into a dataframe for each season
        dff = pd.DataFrame([dff]).to_json() # store into json dict to store in a html div
        return [False, dff]
    else:
        print("Preventing update")
        raise PreventUpdate

@app.callback(
    [
        #Output(component_id='wdir-frequency-graph',component_property='figure'),
        Output(component_id='html-graph',component_property='children'),
        Output(component_id='output-div',component_property='children'),
        Output(component_id='fade-transition-windroses',component_property='is_in'),
        Output(component_id='meanwind-frequency-switch',component_property='options'),
    ],
    [
        Input(component_id='btn-update', component_property='n_clicks'),
        Input(component_id='legend-visible-windrose-switch', component_property='value'),
        Input(component_id='meanwind-frequency-switch', component_property='value'),
    ],
    [
        State(component_id='intermediate-df', component_property='children'),
        State(component_id='station', component_property='value'),
        State(component_id='hours', component_property='value'),
        State(component_id='analysis', component_property='value'),
    ])
def update_data_from_button(nclicks, legend_visible, meanws_frequency, df_json, stationId, hours, analysis):
    if (nclicks > 0 and hours is not None):
        df = pd.read_json(df_json)                      # converting the json dict to dataframe
        df = df.loc[0]                                  # json trick, from converting the json dict to dataframe, need the first instance
        cols = list(df.iloc[0])                         # collecting the names of the columns from the dataframe stored in json
        maxMeanWS, freqRange  = {}, {}
        df_dir = pd.DataFrame([], columns=cols+['season'])  # creating a new empty dataframe to collect the data from all seasons
        tmpfigs = []
        for season in seasons:
            dff = pd.DataFrame.from_dict(df[season])    # converting from dictionary to dataframe for the season
            if 'winddirs' in analysis:
                print("Analysing the frequency and mean wind speeds for {}".format(season))
                dff['season'] = season                      # adding a column with the season name
                df_dir = pd.concat([df_dir, dff], axis=0)   # appending the dataframe for each season to the end of the current dataframe
                freqRange[season] = dff.frequency.max()     # maximum frequency each season
                maxMeanWS[season] = dff.mean_ws.max()       # maximum mean wind speed each season
            elif 'windrose' in analysis:
                freqRange[season] = dff.groupby(['direction']).frequency.sum().max()
                #fig = plot_windrose(dff)
                fig = plot_windrose_go(dff, season, legend_visible)
                tmpfigs.append(fig)
        if 'winddirs' in analysis:
            if not meanws_frequency: # Showing the frequency rather than the mean wind speed
                return return_plots(df_dir, 'frequency%', 'Tíðni', '%', legend_visible, stationId, hours)
            else:                    # Showing the mean wind speed rather than the frequency
                return return_plots(df_dir, 'mean_ws', 'Meðalvindhraði', 'm/s', legend_visible, stationId, hours)
        elif 'windrose' in analysis:
            figs = []
            graphs = []
            for fig in tmpfigs:
                if meanws_frequency:
                    maxRange = max(freqRange.values())
                    fig.update_layout(
                        {
                            'polar' : {'radialaxis' : {'range' : [0, maxRange*100]}},
                        }
                    )
                graphs.append(dcc.Graph(figure=fig))
            output_str = r'Vindrósir fyrir veðurstöð: {}, fyrir: {}'.format(stations[stationId], new_hours[hours])
            figs.append(graphs)
            figs.append(output_str)
            figs.append(True)
            figs.append([{'label':'Scale frequency','value': 1}])
            return figs
    else: # return empty plot
        figs = []
        for season in seasons:
            fig = px.bar_polar([])
            fig.update_layout(template = None, xaxis_title = '', yaxis_title = '')
            fig.update_xaxes(showgrid = False, showticklabels = False, zeroline = False)
            fig.update_yaxes(showgrid = False, showticklabels = False, zeroline = False)
            figs.append(fig)
        figs = [dcc.Graph(figure=fig)]   # returning the empty images
        #figs = [figs[0]]    # returning the empty images
        figs.append('')     # returning the empty output string
        figs.append(False)  # returning the False statement for the controls fading in/out
        figs.append([{'label':'Mean wind speed','value': 1}])
    return figs

def return_plots(df_dir, y_column, y_title, y_ticksuffix, legend_visible, stationId, hours):
    figs = []
    fig = plot_wdir_seasonal_frequency(df_dir, y_column)
    fig.update_layout(
            title = y_title+r' vindátta',
            height=700,
            width=1000,
            template='seaborn',
            xaxis_title='Vindáttir',
            yaxis_title=y_title,
            showlegend=False,
            )
    
    fig.update_yaxes(
            ticksuffix=y_ticksuffix,
            showticksuffix='all'
            )
    
    if legend_visible:
        fig.update_layout(
            showlegend=True,
            legend_title='Árstíðir',
        )
        #figs.append(fig)
    figs.append(dcc.Graph(figure=fig))
    output_str = r'{} vindátta fyrir veðurstöð: {}, fyrir: {}'.format(y_title, stations[stationId], new_hours[hours])
    figs.append(output_str)
    figs.append(True)
    figs.append([{'label':'Mean wind speed','value': 1}])
    return figs


def plot_wdir_seasonal_frequency(df, y_column):
    fig = px.line(df, x='direction_name', y=y_column, color='season')
    return fig



def plot_windrose_go(df, season_name, legend_visible):

    # may assign colours to specific bin_names
    # marker_colours = {'0-2.5' : '#BAE3F2', '2.5-4' : '#C9F2EB', '4-6' : '#E6FCED', '6-8': '#FFFCF0', '8-10' : '#FFE1C7', '>15': '#F5C0B5'}
    # https://www.schemecolor.com/pastel-blue-with-red.php


    # need to collect into a subplot
    groupped_data = df.groupby(['Vindhraði (m/s)','direction'])['frequency%'].sum()
    fig = go.Figure()
    data = {}
    for bin_name_direction, frequency in groupped_data.items():
        bin_name, direction = bin_name_direction
        if bin_name in data:
            data[bin_name].append(direction)
            data[bin_name].append(frequency)
        else:
            data[bin_name] = [direction]
            data[bin_name].append(frequency)

        """
            collect to {bin_name : [direction, frequency], 
        """
    desired_keys = ['<2.5', '2.5-4', '4-6', '6-8', '8-10', '10-15', '>15']
    data['<2.5'] = data.pop('0-2.5')
    data = {k: data[k] for k in desired_keys}
    for bin_name, values in data.items():
        direction = values[::2] # every other element starting from 0
        direction_name = [winddirs[str(wd)] for wd in direction] # name the wdirs (0 becomes N, 90 becomes E, etc.)
        frequency = values[1::2] # every other element starting from 1
        fig.add_trace(go.Barpolar(
            r = frequency,      # list of frequency of this velocity bin for each wind direction
            theta = direction_name,  # list of wind directions
            name = bin_name,    # name of the velocity bin
            #marker_color = marker_colours[bin_name], #'rgb(106,81,163)'
            marker_line_color = "black",
            marker_line_width = 2,
            opacity = 0.8
        ))

    fig.update_layout(
            title = 'Vindrós fyrir {}'.format(season_name),
            height=700,
            width=1000,
            showlegend=False,
            polar_radialaxis_ticksuffix='%',
            polar_angularaxis_rotation = 90,
            polar_angularaxis_direction = "clockwise"
            )
    if legend_visible:
        fig.update_layout(
            showlegend=True,
            legend_title='Vindhraði (m/s)',
        )
    return fig

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

if __name__ == "__main__":
    app.layout = container
    app.run_server(debug=True)
