""" 
this file render home page, home page have a images and messages about the proyect
"""

# depedneces from dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# ploty
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# useful math librearies
import pandas as pd
import numpy as np

# datetime
import datetime
import psycopg2 # libreria que permite la coneccion con la base de datos

from app import app
from pages.footer import footer


card_terminal = dbc.Card([
    dbc.CardBody([
        html.H5("49 bus terminals", className="card-title",style = {'text-align':'center'}),
    ])
])
card_departures = dbc.Card([
    dbc.CardBody([
        html.H5(" 19,042.123 bus departures", className="card-title",style = {'text-align':'center'}),
    ])
])
card_passengers = dbc.Card([
    dbc.CardBody([
        html.H5("132.939.175 passengers", className="card-title",style = {'text-align':'center'}),
    ])
])
card_routes = dbc.Card([
    dbc.CardBody([
        html.H5("2.878 routes", className="card-title",style = {'text-align':'center'}),
    ])
])

# strcuture of page
# image-tittle 
# title
# images
# and fotter

layout = html.Div([
    html.Div([html.Div(html.H1('Driven by Data',style={'color':'white'}),style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})],
                    style={'background-image': "url(/assets/home/Baner-home-2.png)",'backgroundPosition': 'center center',
                     'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'}),
    html.H2(
        'Statistics of passenger transportation services in Colombia', 
        style={
            'textAlign': 'center',
            'padding-bottom': '15px',
        }
    ),
    html.P(
        'From August 1, 2019 to August 18, 2021', 
        style={
            'textAlign': 'center',
            'padding-bottom': '15px',
        }
    ),
    dbc.Row([
            dbc.Col(card_terminal),
            dbc.Col(card_departures),
            dbc.Col(card_passengers),
            dbc.Col(card_routes),
    ]),
    html.Div([
        dbc.Row([
            dbc.Col(dbc.CardImg(src="assets/buses/buses_image_0.jpg"), width=7),
            dbc.Col(
                html.Div([
                html.P("According to the 2019 official report “Transporte en Cifras” (Ministerio de Transporte, 2019), approximately 136 million of passengers were mobilized in the Colombian roadways in 2019.")
                    ],style={'padding-top': '15vh'}), width=4  
            ),
        ]), 
    ], style={"margin": "2rem"}),

    html.Div([
        dbc.Row([
            dbc.Col(
                html.Div([
                html.P("A big share of the total of the Colombian passengers travelled by bus for going from one city terminal to another. It represents an important logistical challenge with significant economic impacts. Therefore, bus companies should count on methods or techniques to make better decisions.")
                    ],style={'padding-top': '15vh'}),width=4 
            ),
            dbc.Col(dbc.CardImg(src="assets/buses/buses_image_1.jpeg"), width=7),
        ])
    ], style={"margin": "2rem"}),

    html.Div([
        dbc.Row([
            dbc.Col(dbc.CardImg(src="assets/buses/buses_image_2.jpg"), width=7),
            dbc.Col(
                html.Div([
                html.P("This project seeks to develop a computational approach based on data science techniques to forecast passenger demand in different bus terminals and routes over the country.")
                    ],style={'padding-top': '15vh'}), width=4 
            ),
        ])
    ],  style={"margin": "2rem"}),
    
    footer,
])
