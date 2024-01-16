"""this file contains main app, all components are joined on this file
"""

# dash dependences
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

# dependences to make graphs and plot
import plotly.express as px
import pandas as pd

# call laout file
from layout.layout import layout, SIDEBAR_HIDEN, SIDEBAR_STYLE, CONTENT_STYLE, CONTENT_STYLE1

# library to connect to database
from dash.dependencies import Input, Output, State
import psycopg2 # libreria que permite la coneccion con la base de datos


stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
                   'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
                   dbc.themes.BOOTSTRAP,]
app = dash.Dash(__name__, external_stylesheets=stylesheets, suppress_callback_exceptions=True)

# set layout to app
app.layout = layout
    
# this call hide and show sidebar
# callback run when an show button in navar is pressed

@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],
    [Input("btn_sidebar", "n_clicks")],
    [State("side_click", "data")]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick


