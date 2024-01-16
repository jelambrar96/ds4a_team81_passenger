""" 
This file render routes predictions

"""


import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2  # libreria que permite la coneccion con la base de datos
from app import app
from pages.footer import footer
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from datetime import date

rutas_1_a_10=["5001-5615", "11001-25307", "11001-76001", "15759-11001", "50001-11001", "63001-63401", "66001-63001", "66001-66682", "76001-11001", "76001-76520"]
rutas_11_a_20=["5045-5172", "5045-5837 ", "11001-73001", "15238-15759", "25307-11001", "52356-76001", "63001-63470", "73001-11001", "73001-25307", "76001-52356"]


# Nombre de las rutas
specific_route = dcc.Dropdown(
    id='my_route',
    options=[
        {'label': "Medellín Norte - Rionegro", 'value': '5001-5615'},
        {'label': "Bogotá Salitre - Girardot", 'value': '11001-25307'},
        {'label': "Bogotá Salitre - Cali", 'value': '11001-76001'},
        {'label': "Sogamoso - Bogotá Salitre", 'value': '15759-11001'},
        {'label': "Villavicencio - Bogotá Salitre", 'value': '50001-11001'},
        {'label': "Armenia - La Tebaida", 'value': '63001-63401'},
        {'label': "Pereira - Armenia", 'value': '66001-63001'},
        {'label': "Pereira - Santa Rosa De Cabal", 'value': '66001-66682'},
        {'label': "Cali - Bogotá Salitre", 'value': '76001-11001'},
        {'label': "Cali - Palmira", 'value': '76001-76520'},
        {'label': "Apartadó - Chigorodó", 'value': '5045-5172'},
        {'label': "Apartadó - Turbo", 'value': '5045-5837 '},
        {'label': "Bogotá Salitre - Ibagué", 'value': '11001-73001'},
        {'label': "Duitama - Sogamoso", 'value': '15238-15759'},
        {'label': "Girardot - Bogotá Salitre", 'value': '25307-11001'},
        {'label': "Ipiales - Cali", 'value': '52356-76001'},
        {'label': "Armenia - Montenegro", 'value': '63001-63470'},
        {'label': "Ibagué - Bogotá Salitre", 'value': '73001-11001'},
        {'label': "Ibagué - Girardot", 'value': '73001-25307'},
        {'label': "Cali - Ipiales", 'value': '76001-52356'},
    ],
    value='11001-25307',
    multi=False,
    clearable=False,
    style={"width": "100%"},
)

#Calendario para la predicion
calendar = dcc.DatePickerSingle(
    id='my-date-picker-range',
    min_date_allowed=date(2019, 8, 1),
    max_date_allowed=date(2021, 9, 16),
    initial_visible_month=date(2021, 8, 16),
    date=date(2021, 8, 16))

#Carga de las estadisticas del modelo
with open(r'pages/Predicciones/Datos/Modelos rutas/dict_modelos_rutas_1_al_10.pkl', 'rb') as file:
    dict_modelos_rutas_1_al_10 = pickle.load(file)

with open(r'pages/Predicciones/Datos/Modelos rutas/dict_modelos_rutas_11_al_20.pkl', 'rb') as file:
    dict_modelos_rutas_11_al_20 = pickle.load(file)


@app.callback(Output('cards2', 'children'),
              [Input("loading-button-terminales", "n_clicks")],
              [State('my_route', 'value')])
def card(n_clicks, route_selected):
    if route_selected in rutas_1_a_10:
        dict_modelos = dict_modelos_rutas_1_al_10
    else:
        dict_modelos = dict_modelos_rutas_11_al_20
    card_time = dbc.Card([
        dbc.CardBody([
            html.H5("Training time", className="card-title", style={'text-align': 'center'}),
            html.P(f"{round(dict_modelos[route_selected]['time'], 2)} min", className="card-text",
                   style={'text-align': 'center'})
        ])
    ])
    card_training = dbc.Card([
        dbc.CardBody([
            html.H5("Training RMSE relative", className="card-title", style={'text-align': 'center'}),
            html.P(f"{round(dict_modelos[route_selected]['metrics']['Train Score Relative'], 2) * 100}%",
                   className="card-text", style={'text-align': 'center'}),
        ])
    ])
    card_test = dbc.Card([
        dbc.CardBody([
            html.H5("Test RMSE relative", className="card-title", style={'text-align': 'center'}),
            html.P(f"{round(dict_modelos[route_selected]['metrics']['Test Score Relative'], 2) * 100}%",
                   className="card-text", style={'text-align': 'center'}),
        ])
    ])

    latoyut_card = dbc.Row([dbc.Col(card_time),
                            dbc.Col(card_training),
                            dbc.Col(card_test)])

    return latoyut_card


@app.callback(Output('forecasting-serie2', 'figure'),
              [Input("loading-button-terminales", "n_clicks")],
              [State('my_route', 'value')])
def fig_line(n_clicks, route_selected):
    if route_selected in rutas_1_a_10:
        dict_routes = dict_modelos_rutas_1_al_10[route_selected]
    else:
        dict_routes = dict_modelos_rutas_11_al_20[route_selected]

    df_forecasting = dict_routes['datasets']['forecasting'][7:].rename(columns={'pasajeros': 'forecasting'})
    df_train = dict_routes['datasets']['trainPredictPlot'][-15:].rename(columns={'predict_pasajeros': 'training'})
    df_test = dict_routes['datasets']['testPredictPlot'].rename(columns={'predict_pasajeros': 'test'})
    df_real = dict_routes['datasets']['dataset'][-22:].rename(columns={'pasajeros': 'real'})

    df = df_forecasting[['fecha', 'forecasting']].merge(df_train[['fecha', 'training']], on='fecha', how='outer')
    df = df.merge(df_test[['fecha', 'test']], on='fecha', how='outer')
    df = df.merge(df_real[['fecha', 'real']], on='fecha', how='outer')
    df.sort_values(by='fecha', inplace=True, ascending=True)
    fig = px.line(df, x="fecha", y=df.columns, title='custom tick labels')

    fig.update_layout(title={'text': "<b>Passenger time series<b>", 'font_size': 20})
    fig.update_xaxes(title={'text': "<b>Time (days)<b>", 'font_size': 15})
    fig.update_yaxes(title={'text': "<b>Passenger<b>", 'font_size': 15})
    fig.update_layout(legend_title_text='Time series')

    return fig

# Prediccion por fecha especifica
# %%

@app.callback(Output('forecasting-value2', 'children'),
            [Input('my_route', 'value'),
            Input('my-date-picker-range', 'date')])
def forecasting_value(route_selected,start_date):

    if route_selected in rutas_1_a_10:
        dict_routes = dict_modelos_rutas_1_al_10[route_selected]
    else:
        dict_routes = dict_modelos_rutas_11_al_20[route_selected]

    df = dict_routes['datasets']['forecasting']
    value = df[df['fecha'] == start_date]['pasajeros'].iloc[0]
    card_training = dbc.Card([dbc.CardBody([html.H5("Passenger forecasting", className="card-title",style = {'text-align':'center'}),
                    html.P(f"{int(value)}", className="card-text",style = {'text-align':'center'})])])
    return card_training


figures_info = {
    "Metrics": "RMSE is the root of the mean square that was obtained when training and testing the model. This metric was relativized for each route by dividing it by the average passenger value of each route.",
}




# information buttons

def make_popover(figure):
    title = figure.replace('Passengers', "Passengers'").replace('-', ' ')
    return dbc.Popover(
        [
            dbc.PopoverHeader(f"{title} info"),
            dbc.PopoverBody(figures_info[figure]),
        ],
        id=f"popover2-{figure}",
        target=f"popover2-{figure}-target",
        placement="bottom",
        is_open=False,
    )

def make_button(figure):
    return dbc.Button(
        html.Span(["", html.I(className="fas fa-info-circle")]),
        id=f"popover2-{figure}-target",
        className="btn btn-sm rounded-circle",
        n_clicks=0,
    )

popovers = {key: html.Div([make_button(key), make_popover(key)]) for key in figures_info.keys()}

def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

for p in figures_info.keys():
    app.callback(
        Output(f"popover2-{p}", "is_open"),
        [Input(f"popover2-{p}-target", "n_clicks")],
        [State(f"popover2-{p}", "is_open")],
    )(toggle_popover)

# Layout de la pagina

routes_boton = html.Div([dbc.Row(
    [html.Div(html.H5('Specific route for analysis', style={'color': 'gray'}), style={'text-align': 'center'})],
    justify="center"),
                         dbc.Row([dbc.Col(specific_route, width={"size": 3, "offset": 2}, align='center',
                                          style={"width": "100vh", 'padding-right': '0px', 'padding-left': '1vh'}),
                                  dbc.Col(dbc.Button(id="loading-button-terminales", n_clicks=0, children=["Search"]),
                                          width=3, style={'padding-left': '1vw'})], justify="center")]
                        , style={"height": "10vh", 'padding-top': '4px', 'margin-bottom': '1vh'})

time_series_plot = html.Div([dbc.Spinner(children=[dcc.Graph(id='forecasting-serie2')],size="lg", color="primary", type="border",fullscreen=False)])

cards_metrics = html.Div(
    [dbc.Row(popovers["Metrics"], justify='end', style={'margin-top': '5vh', 'margin-bottom': '1vh'}),
     html.Div(id='cards2')], style={'margin-top': '3vh'})

banner =  html.Div([html.Div(html.H1('Routes forecasting',style={'color':'white'}),style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})],
                    style={'background-image': "url(/assets/Prediction/Routs-forecasting.png)",'backgroundPosition': 'center center',
                    'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'})

#
subtitulo = html.Div([html.P(
    'On this page, you can see the prediction for the top routes by passenger count on a specific date range. You can get more information by entering the upper right button. If you need information regarding a speficif route not available in the page, please contact some of the developers (contact page).')],
                     style={'text-align': 'left', 'margin-top': '6vh', 'color': 'grey'})

parameter_buttons = html.Div([dbc.Row([
    dbc.Col(
        html.Div([dbc.Row([dbc.Col(html.H5("Date for forecasting", style={'text-align': 'center'}))], justify="center"),
                  dbc.Row([dbc.Col(calendar, style={'padding-left': '9rem'})], justify="center")]), width=4),
    dbc.Col(html.Div(id='forecasting-value2'), width=4)], justify="center")],
    style={"height": "5vh", 'padding-top': '3vh', 'padding-bottom': '5vh'})

layout = html.Div([banner,
                   subtitulo,
                   routes_boton,
                   cards_metrics,
                   time_series_plot,
                   parameter_buttons,
                   html.Div(style={"height": "5vh"}),
                   footer,
                   ])
