from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from routes import home, fdscsv, vindrosir

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
    ])

@app.callback(Output(component_id='page-content',
    component_property='children'), 
    Input(component_id='url', component_property='pathname'))
def display_page(pathname):
    if (pathname == '/home' or pathname == '/'):
        return home.layout
    elif pathname == '/fdscsv':
        return fdscsv.layout
    elif pathname == '/vindrosir':
        return vindrosir.layout
    else:
        return home.layout

