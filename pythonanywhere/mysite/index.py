from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
import numpy as np
import os, re
import io
import base64

from app import app
from routes import home, vindafar, geomap, fdscsv #, vindrosir, vindafar

# dropdown = dbc.DropdownMenu([
#     dbc.DropdownMenuItem("Home",href="/home", className='navbar-option'),
#     dbc.DropdownMenuItem("Veðurgögn",href="/vedurgogn", className='navbar-option'),
#     dbc.DropdownMenuItem(r"Vindrósir",href="/vindarosir", className='navbar-option'),
#     dbc.DropdownMenuItem("FDS CSV",href="/fdscsv", className='navbar-option'),
# ], nav=True, in_navbar=True, label="Síður",)

mydropdown = [
    html.Img(src="/assets/ORUGG.png", height="100vh"),
    dbc.NavItem(dbc.NavLink("Vindgreining",href="/vindgreining", className='navbar-option'), style={'color': 'black'}),
    dbc.NavItem(dbc.NavLink("Veðurgögn",href="/vedurgogn", className='navbar-option')),
    # dbc.NavItem(dbc.NavLink(r"Vindrósir",href="/vindarosir", className='navbar-option')),
    dbc.NavItem(dbc.NavLink("Verkefni og Veðurstöðvar",href="/kort", className='navbar-option')),  
    dbc.NavItem(dbc.NavLink("FDS CSV",href="/fdscsv", className='navbar-option')),  
]

# navbar = html.Div(
#     [
#         #dmc.Button("open", id="drawer-button"),
#         #dmc.ActionIcon(html.Img(src="/assets/ORUGG.png", height="40px"), id="drawer-button"),
#         dmc.ActionIcon(DashIconify(icon="charm:menu-hamburger"), color="red", id="drawer-button"),
#         dmc.Drawer(
#             #title="test",
#             id="drawer",
#             padding="md",
#             size="xs",
#             children=mydropdown
#             ),
#         ]
#     )

navbar = dbc.Navbar(
        html.Div(
            [
                #dmc.Button("open", id="drawer-button"),
                
                html.Div([
                    html.Img(src="/assets/ORUGG_flame_crop_300.png", height="20px"),
                    html.Div([
                        dmc.ActionIcon(DashIconify(icon="charm:menu-hamburger"), color="red", id="drawer-button"),
                        ], style={'display' : 'inline-block', 'position' : 'relative', 'float' : 'right'}, className='ml-auto'),
                    ], style={'display' : 'flex'}),
                html.Div(
                    dmc.Drawer(
                        #title="test",
                        id="drawer",
                        padding="md",
                        size="xs",
                        children=mydropdown,
                        ), 
                    style={'z-index' : "1", 'position' : 'relative'}),
                ]
        ),
        color="dark", dark=True, style={'height' : "30px"},
)

@app.callback(
    Output("drawer", "opened"),
    Output("drawer", "position"),
    Input("drawer-button", "n_clicks"),
    prevent_initial_call=True,
    )
def drawer_demo(n_clicks):
    return True, "left"



# navbar = dbc.Navbar(
#         dbc.Container([
#             html.A(
#                 # Use row and col to control vertical alignment of logo / brand
#                 dbc.Row(
#                     [
#                         dbc.Col(html.Img(src="/assets/ORUGG.png", height="30px")),
#                         #dbc.Col(dbc.NavbarBrand("ÖRUGG", className="ml-2")),
#                     ],
#                     align="center",
#                     #no_gutters=True,
#                 ),
#                 #href="/home",
#                 href="https://www.oruggverk.is/",
#             ),
#             dbc.NavbarToggler(id="navbar-toggler",className="navbar-toggler"),
#             dbc.Collapse(
#                 dbc.Nav(
#                     # right align dropdown menu with ml-auto className
#                     #[dropdown], className="ml-auto", navbar=True
#                     [dropdown], className="navbar-option", navbar=True
#                 ),
#                 id="navbar-collapse",
#                 className="navbar-collapse",
#                 navbar=True,
#             ),
#         ]
#     ),
#     color="dark",
#     dark=True,
#     id='navbar'
#     #className="mb-4",
# )

# navbar = dbc.Navbar(
#         dbc.Container([
#             html.A(
#                 # Use row and col to control vertical alignment of logo / brand
#                 dbc.Row(
#                     [
#                         dbc.Col(html.Img(src="/assets/ORUGG.png", height="30px")),
#                     ],
#                     align="center",
#                     #no_gutters=True,
#                 ),
#                 href="https://www.oruggverk.is/",
#             ),
#             dbc.NavbarToggler(id="navbar-toggler"),
#             dbc.Collapse(
#                 dbc.Nav(
#                     # right align dropdown menu with ml-auto className
#                     [dropdown], className="mr-auto", navbar=True,
#                 ),
#                 id="navbar-collapse",
#                 className="navbar-collapse",
#                 navbar=True,
#             ),
#         ]
#     ),
#     color="dark",
#     dark=True,
#     id='navbar',
#     className="mb-4",
# )

# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

# for i in [2]:
#     app.callback(
#         Output(f"navbar-collapse{i}", "is_open"),
#         [Input(f"navbar-toggler{i}", "n_clicks")],
#         [State(f"navbar-collapse{i}", "is_open")],
#     )(toggle_navbar_collapse)

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'
)    ])

@app.callback(Output(component_id='page-content',
    component_property='children'), 
    Input(component_id='url', component_property='pathname'))
def display_page(pathname):
    if (pathname == '/vindgreining' or pathname == '/'):
        return home.layout
    elif pathname == '/fdscsv':
        return fdscsv.layout
    # elif pathname == '/vindrosir':
    #     return vindrosir.layout
    elif pathname == '/vedurgogn':
        return vindafar.layout
    elif pathname == '/kort':
        return geomap.layout
    else:
        return home.layout

#if __name__ == '__main__':
#    app.run_server(debug=True)
