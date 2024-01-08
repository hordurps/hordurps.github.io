import dash
import dash_bootstrap_components as dbc

#app = dash.Dash(__name__, suppress_callback_exceptions=True,
#        external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#server = app.server
app.config.suppress_callback_exceptions = True
app.title = "HP ÖRUGG"
#import index
#app.layout = index.layout
