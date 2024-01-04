import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import os

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}
container = html.Div([
    # ------------------------------------------------------------------
                # header
                html.Div([
                    # description
                    html.Div([
                        html.H4("Vindgreining", className="app__header__title"),
                        html.P(r"hordurps", className="app__header__title--grey")
                    ], className="app__header__desc"),
                    # logo
                    html.Div([
                        html.A(
                            html.Img(
                                #src=app.get_asset_url('ORUGG.png'),
                                src=os.path.join('assets','ORUGG.png'),
                                className="app__menu__img",
                            ),
                            href="https://oruggverk.is/thjonusta/vindur/"
                        )
                    ], className="app__header__logo"),
                ], className="app__header"),
    # ------------------------------------------------------------------

                # body / content
                html.Div([
                    html.Img(
                        src="/assets/blog/straumlinur.jpg",
                        className='w-100 p-3',
                        # width="50%"
                    ),
                    html.Figcaption("Straumlínur úr hermun á vindátt með tölulegu straumfræðilíkani.", style={'color':'#FFF'}),
                    html.Img(
                        src="/assets/blog/wind_original.png",
                        className='w-100 p-3',
                        # width="50%"
                    ),
                    html.Figcaption("Vindur í mannhæð í einni vindátt og sýnir hvar byggingar auka vindhraða og hvar þær draga úr vindhraða. ", style={'color':'#FFF'}),
                    html.Img(
                        src="/assets/blog/sumar.png",
                        className='w-100 p-3',
                        # width="50%"
                    ),
                    html.Figcaption("Vindvist á einni árstíð sem sýnir hvernig svæði nýtast. Græn svæði henta til að sitja lengi. ", style={'color':'#FFF'}),
                    html.Img(
                        src="/assets/blog/safety.png",
                        className='w-100 p-3',
                        # width="50%"
                    ),
                    html.Figcaption("Öryggi yfir árið sem sýnir svæði þar sem vindhraði getur valdið óöryggi. ", style={'color':'#FFF'}),
                    html.Img(
                        src="/assets/blog/wind_mitigation.png",
                        className='w-100 p-3',
                        # width="50%"
                    ),
                    html.Figcaption("Vindur í mannhæð í einni vindátt og sýnir hvernig mótvægisaðgerðir hafa dregið úr vindhraða. ", style={'color':'#FFF'}),
                    # html.H1("Vindgreining", style={"color" : "#FFF"}),                    
                    # html.Hr(),
                    # dcc.Markdown(
                    #     '''

                    #     ''',
                    #     className='markdown',
                    #     style={"color" : "#FFF"}
                    # )
        
                ], className="app__content"),
    # ------------------------------------------------------------------
            ], className="app__container")

layout = container
#layout = html.Div([
#    html.H1('hordurps')
#    ])
