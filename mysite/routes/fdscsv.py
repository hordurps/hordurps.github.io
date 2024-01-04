from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px


import pandas as pd
import numpy as np
import os, re
import io
import base64
import shutil

from app import app


folder_on_server = "static_data"
def uniqueColumnNames(cols):
    # Retrieving a list of the columns, returns a list of tuple [('s', 'Time'), ('kW', 'HRR')] etc.
    # Converting the tuple to string Field [Unit]
    fields = [col[1]+' ['+col[0]+']' for col in cols]
    # checking if HRR in data
    if any(["HRR" in field for field in fields]):
        hrr = True
    else:
        hrr = False
    # pattern assuming the devices are split by '_'
    p = [] # splitting the fields by '_' into lists and collecting those lists into a single list
    for field in fields[1:]:
        if '_' in field:
            p.append(field.split('_'))
        elif (' ' in field and hrr):
            p.append(field.split(' '))
        else:
            p.append([field])
    # finding the unique strings in the devices, i is item, si is subitem
    uniqueFields = set([i for si in p for i in si])
    p = re.compile('d\d+')
    m = [p.search(uniqueField) for uniqueField in uniqueFields]
    idx = [i for i, v in enumerate(m) if v is None]
    uniqueFields = np.array(list(uniqueFields))[idx]
    return uniqueFields


#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

## Authentiation 
#import dash_auth
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


# preset for initialisation
#csvs = ['hrr.csv']
csvs = ['hrr']
#arrayNames = {csvs[0] : ['GT','HRR','VF','GT_plume','GT_frame', 'VF_RL', 'VF_DOOR']}
arrayNames = {csvs[0] : ['Select a field']}
# --------------------
# Control UI
# --------------------
controls = [
        dbc.Card(
            [
                dbc.CardHeader("Select field"),
                dbc.CardBody(
                    [
                        html.P("File name"),
                        dcc.Dropdown(
                            id="selected-file",
                            options=[{"label" : csv, "value" : csv } for csv in csvs],
                            value=csvs[0],
                            placeholder="Upload a csv file",
                            searchable=True,
                            multi=False,
                        ),
                        html.Br(),
                        html.P("Field name"),
                        dcc.Dropdown(
                            id="selected-field",
                            options=[{"label" : array, "value" : array } for array in arrayNames[csvs[0]]],
                            placeholder="Select a field",
                            searchable=True,
                            multi=True,
                        ),
                        dbc.Fade(
                            children=[
                                html.Br(),
                                html.P("Labels"),
                                dcc.Input(
                                    id='x-label-input',
                                    type='text',
                                    placeholder='X label',
                                    debounce=True,
                                    ),
                                dcc.Input(
                                    id='y-label-input',
                                    type='text',
                                    placeholder='Y label',
                                    debounce=True,
                                    ),
                                html.Br(),
                                html.Br(),
                                html.P("X range"),
                                dcc.Input(
                                    id='x-range-min-input',
                                    type='text',
                                    placeholder='X min',
                                    debounce=True,
                                    ),
                                dcc.Input(
                                    id='x-range-max-input',
                                    type='text',
                                    placeholder='X max',
                                    debounce=True,
                                    ),
                                html.Br(),
                                html.Br(),
                                html.P("Y range"),
                                dcc.Input(
                                    id='y-range-min-input',
                                    type='text',
                                    placeholder='Y min',
                                    debounce=True,
                                    ),
                                dcc.Input(
                                    id='y-range-max-input',
                                    type='text',
                                    placeholder='Y max',
                                    debounce=True,
                                    ),
                                html.Br(),
                                html.Br(),
                                html.P("Increments"),
                                dcc.Input(
                                    id='x-range-dx-input',
                                    type='text',
                                    placeholder='X dx',
                                    debounce=True,
                                    ),
                                dcc.Input(
                                    id='y-range-dy-input',
                                    type='text',
                                    placeholder='Y dx',
                                    debounce=True,
                                    ),
                                html.Br(),
                                html.Br(),
                                dbc.Checklist(
                                    id='legend-visible',
                                    options=[{'label':'Legend visible','value': 1}],
                                    value=[1],
                                    switch=True,
                                    ),
                                dcc.Input(
                                    id='legend-title-input',
                                    type='text',
                                    placeholder='Legend title',
                                    ),
                                html.Br(),
                                html.Br(),
                                dbc.Checklist(
                                    id='critical-value-visible',
                                    options=[{'label':'Critical value visible','value': 1}],
                                    value=[],
                                    switch=True,
                                    ),
                                dcc.Input(
                                    id='critical-time-input',
                                    type='text',
                                    placeholder='Critical time',
                                    debounce=True,
                                    ),
                                dcc.Input(
                                    id='critical-value-input',
                                    type='text',
                                    placeholder='Critical value',
                                    debounce=True,
                                    ),
                                dbc.Checklist(
                                    id='sum-max-visible',
                                    options=[{'label':'Sum values','value': 1},
                                        {'label' : 'Max values', 'value' : 2}],
                                    value=[],
                                    switch=True,
                                    ),
                                ],
                            id='fade-transition', is_in=False,
                            style={'transition' : 'opacitiy 2000ms ease'},
                            timeout=2000,
                        ), # end of fade
                    ],
                ),
            ],
        ),
    ]


# --------------------
# App UI
# --------------------
container = dbc.Container(
        fluid=True,
        style={"margin-top" : "15px", "height" : "calc(100vh - 30px)"},
        children=[
            dbc.Row(
                [
                    dbc.Col(width=3, 
                        children=controls
                        ),
                    dbc.Col(
                        width=8,
                        children=[
                            dbc.Row(
                                [
                                        dcc.Upload(
                                            id='upload-data',
                                            children=html.Div([
                                                'Drag and Drop or ',
                                                html.A('Select Files'),
                                            ]),
                                            style={
                                                'width' : '100%',
                                                'height' : '60px',
                                                'lineHeight' : '60px',
                                                'borderWidth' : '1px',
                                                'borderStyle' : 'dashed',
                                                'borderRadius' : '5px',
                                                'textAlign' : 'center',
                                                'margin' : '10px'
                                                },
                                            multiple=True
                                        ),
                                ],style={"width" : "100%"},
                            ),
                            html.Div(dcc.Graph(id='my-csv-graph', figure={}),
                                style={"height" : "100%", "width" : "100%", "border": "1px"})
                        ],
                    ),
                ],
                style={"height" : "100%"},
            ),
            dbc.Row(
                html.Div(id='intermediate-value-df', style={'display': 'none'}),
            ),
            dbc.Row(
                html.Div(id='intermediate-value-cols', style={'display': 'none'}),
            ),
        ],
    )


#app.layout = container
layout = container



def store_contents(contents, filename, folder_on_server): 
    content_type, content_string = contents.split(',')
    if 'csv' in filename:
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),header = [0,1])
        tmp_arrayNames = uniqueColumnNames(df)
        df.to_csv(os.path.join(folder_on_server, filename))
        return tmp_arrayNames

def read_contents(filename, folder_on_server):
    df = pd.read_csv(os.path.join(folder_on_server, filename), header=[0,1])
    cols = list(df)
    # Converting the tuple to string Field [Unit]
    fields = [col[1]+' ['+col[0]+']' for col in cols]
    df.columns = fields
    df = df.set_index(df.columns[1])
    return df
    

# ------------------
# Handle controls
# ------------------
@app.callback(
        [
            Output(component_id="intermediate-value-cols", component_property="children"),
            Output(component_id="selected-file", component_property="options"),
            Output(component_id="selected-file", component_property="value"),
        ],
        [
            Input(component_id="upload-data", component_property='contents'),
            Input(component_id="upload-data", component_property='filename'),
        ],
        )
def update_csvs(list_of_contents, list_of_names):
    # print("Call 1 : update_file_list/upload_csv")
    if list_of_contents is not None:
        if os.path.exists(folder_on_server):
            shutil.rmtree(folder_on_server) # removes directory and it's contents
        os.makedirs(folder_on_server, exist_ok=True)
        arrayNames = {}
        for contents, names in zip(list_of_contents, list_of_names):
            tmp_arrayNames = store_contents(contents, names, folder_on_server)
            arrayNames[names] = [tmp_arrayNames]
        dff = pd.DataFrame.from_dict(arrayNames)
        options=[{"label" : csv, "value" : csv } for csv in list_of_names]
        value=list_of_names[0]
        return [dff.to_json(), options, value]
    else:
        options = [{'label' : 'Upload a csv file', 'value' : 'Upload a csv file'}]
        value = ""
        return ["Please upload a csv file", options, value]



@app.callback(
        [
            Output(component_id="selected-field", component_property="options"),
            Output(component_id="selected-field", component_property="value"),
            Output(component_id="fade-transition", component_property="is_in"),
        ],
        [
            Input(component_id="selected-file", component_property="value"),
        ],
        [
            State(component_id="intermediate-value-cols", component_property="children"),
        ], prevent_initial_call=True
    )
def update_selected_fields(selectedFile, arrayNames_json):
    #    print("Call 2 : update_selected_fields")
    if (selectedFile and selectedFile.endswith('.csv')):
        arrayNames = pd.read_json(arrayNames_json).loc[0]
        options=[{"label" : array, "value" : array } for array in arrayNames[selectedFile]]
        #value=arrayNames[selectedFile][0]
        value = "Select a field"
        return [options, value, True]
    else:
        raise PreventUpdate
        #options = [{'label' : 'Upload a csv file', 'value' : 'Upload a csv file'}]
        #value = "Select a field"


@app.callback(
        [
            Output(component_id="my-csv-graph", component_property="figure"),
        ],
        [
            Input(component_id="x-label-input", component_property="value"),
            Input(component_id="y-label-input", component_property="value"),
            Input(component_id="x-range-min-input", component_property="value"),
            Input(component_id="x-range-max-input", component_property="value"),
            Input(component_id="x-range-dx-input", component_property="value"),
            Input(component_id="y-range-min-input", component_property="value"),
            Input(component_id="y-range-max-input", component_property="value"),
            Input(component_id="y-range-dy-input", component_property="value"),
            Input(component_id="legend-title-input", component_property="value"),
            Input(component_id="legend-visible", component_property="value"),
            Input(component_id="critical-value-input", component_property="value"),
            Input(component_id="critical-value-visible", component_property="value"),
            Input(component_id="critical-time-input", component_property="value"),
            Input(component_id="sum-max-visible", component_property="value"),
            Input(component_id="selected-field", component_property="value"),
        ],
        [
            State(component_id="selected-file", component_property="value"),
        ]
    )
def update_graph(xlabel, ylabel, xrangeMin, xrangeMax, dx, yrangeMin, yrangeMax, dy, legend_title, legend_visible, critical_value, critical_value_visible, critical_time, sum_max_values, selectedFields, selectedFile):
    # print("Call 3 : update_graph")
    if ((selectedFile and selectedFile.endswith('.csv')) and (selectedFields != 'Select a field' and selectedFields)):
        #data = pd.read_json(data_json)
        #df = data[selectedFile].copy()
        #df = pd.DataFrame(df.loc[0])
        df = read_contents(selectedFile, folder_on_server)
        cols = list(df)
        plotFields = [col for col in cols if all(selectedField in col for selectedField in selectedFields)]
        if not plotFields:
            plotFields = [col for col in cols if any(selectedField in col for selectedField in selectedFields)]

        dff = df[plotFields]
        dff.index = dff.index.astype(str).astype(float)
        if sum_max_values:
            if sum_max_values[0] == 1:
                if 'Max' in dff.columns:
                    dff['Sum'] = dff.iloc[:,:-1].sum(axis=1)
                else:
                    dff['Sum'] = dff.sum(axis=1)
            if sum_max_values[0] == 2:
                if 'Sum' in dff.columns:
                    dff['Max'] = dff.iloc[:,:-1].max(axis=1)
                else:
                    dff['Max'] = dff.max(axis=1)


        fig = px.line(
                data_frame=dff, 
                markers=True
                )
        try: 
            xrangeMin = float(xrangeMin)
        except:
            xrangeMin = 0
        try: 
            yrangeMin = float(yrangeMin)
        except:
            yrangeMin = 0
        try: 
            xrangeMax = int(xrangeMax)
        except:
            xrangeMax = int(round(float(dff.index.max()),1))
        try: 
            yrangeMax = float(yrangeMax)
        except:
            yrangeMax = round(max(dff.max()),1)
        try: 
            dx = float(dx)
        except:
            if xrangeMax > 300:
                dx = 300
            else:
                dx = (xrangeMax-xrangeMin)/5
                if dx == 0:
                    dx = 0.001
        try: 
            dy = float(dy)
        except:
            dy = (yrangeMax-yrangeMin)/5
            if dy == 0:
                dy = 0.001


        crit_val_ctd, crit_time_ctd = False, False
        if (critical_value_visible is not None and critical_value_visible):
            # check if critical_value is not None type, and if string is not
            # empty ('')
            if (critical_value is not None and critical_value):
                crit_val = [float(val) for val in critical_value.split(',')]
                crit_val_ctd = True
            if (critical_time is not None and critical_time):
                crit_time = [float(val) for val in critical_time.split(',')]
                crit_time_ctd = True
            if crit_val_ctd:
                if len(crit_val) == 1:
                    crit_time = [xrangeMin, xrangeMax]
                    crit_val = [crit_val[0] for i in range(len(crit_time))]
                    crit_time_ctd = True
            if (crit_val_ctd and crit_time_ctd):
                if len(crit_time) == len(crit_val):
                    tmp_dict = {'Time' : crit_time, 'Critical value': crit_val}
                    tmp_df = pd.DataFrame(tmp_dict)
                    tmp_df.set_index('Time',inplace=True)
                    fig2 = px.line(tmp_df, markers=True,
                            color_discrete_sequence=['black']) # need to create new fig
                    fig.add_trace(fig2.data[0]) # add the trace from fig2 to fig
                    fig2.data = [] # remove the traces from fig2 from memory

        try: 
            xticks = np.arange(xrangeMin, xrangeMax+dx, dx)
            if len(xticks) > 100:
                xticks = ['']
        except: 
            xticks = ['']
        try:
            yticks = np.arange(yrangeMin, yrangeMax+dy, dy)
            if len(yticks) > 100:
                yticks = ['']
        except: 
            yticks = ['']
    
        fig.update_layout(
                height = 700,
                template='seaborn',
                xaxis_title=xlabel,
                yaxis_title=ylabel,
                xaxis_range=[xrangeMin, xrangeMax],
                yaxis_range=[yrangeMin, yrangeMax],
                xaxis = dict(
                            tickmode = 'array',
                            tickvals = xticks
                        ),
                yaxis = dict(
                        tickmode = 'array',
                        tickvals = yticks
                    ),
                legend_title=legend_title,
                )
        if not legend_visible:
            fig.update_layout(
                    showlegend=False
                    )
        return [fig]
    else:
        fig = px.scatter([])
        fig.update_layout(template = None, xaxis_title='', yaxis_title='')
        fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
        fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
        return [fig]




#if __name__ == "__main__":
#    app.run_server(debug=True)
