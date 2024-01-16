
""" 
This file render terminals predictions

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
import psycopg2 # libreria que permite la coneccion con la base de datos
from app import app
from pages.footer import footer
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from datetime import date

# Nombre de los terminales
#%%
with open(r'pages/analysis/terminals/Datos/name-terminals.pkl','rb') as file:
    terminales = pickle.load(file)

terminales_dropdown = [{'label': terminal[0][8:], 'value': terminal[0]} for terminal in terminales]

del(terminales)

specific_terminal = dcc.Dropdown(options = terminales_dropdown, 
                                id = 'my_terminal',
                                value = 'T.T. DE BOGOTÁ SALITRE')

# Calendario para la predicion
#%%

calendar = dcc.DatePickerSingle(
        id='my-date-picker-range',
        min_date_allowed=date(2019,8,1),
        max_date_allowed=date(2021,9,16),
        initial_visible_month=date(2021,8,16),
        date=date(2021,8,16))


# Carga de las estadisticas del modelo
#%%
with open(r'pages/Predicciones/Datos/Modelos terminales/dict_modelos.pkl','rb') as file:
    dict_modelos = pickle.load(file)


# Estadisticas del modelo
#%%

@app.callback(Output('cards', 'children'),
            [Input("loading-button-terminales", "n_clicks")],
            [State('my_terminal', 'value')])
def card(n_clicks,terminal_selected):

    card_time = dbc.Card([
        dbc.CardBody([
            html.H5("Training time", className="card-title",style = {'text-align':'center'}),
            html.P(f"{round(dict_modelos[terminal_selected]['time'],2)} min",className="card-text",style = {'text-align':'center'})
        ])
    ])
    card_training = dbc.Card([
        dbc.CardBody([
            html.H5("Training RMSE relative", className="card-title",style = {'text-align':'center'}),
            html.P(f"{round(dict_modelos[terminal_selected]['metrics']['Train Score Relative'],2)*100}%", className="card-text",style = {'text-align':'center'}),
        ])
    ])
    card_test = dbc.Card([
        dbc.CardBody([
            html.H5("Test RMSE relative", className="card-title",style = {'text-align':'center'}),
            html.P(f"{round(dict_modelos[terminal_selected]['metrics']['Test Score Relative'],2)*100}%", className="card-text",style = {'text-align':'center'}),
        ])
    ])

    latoyut_card = dbc.Row([dbc.Col(card_time),
            dbc.Col(card_training),
            dbc.Col(card_test)])


    return latoyut_card


# Prediccion de los Modelos 
#%%


@app.callback(Output('forecasting-serie', 'figure'),
            [Input("loading-button-terminales", "n_clicks")],
            [State('my_terminal', 'value')])
def fig_line(n_clicks,terminal_selected):


    dict_terminal = dict_modelos[terminal_selected]

    df_forecasting = dict_terminal['datasets']['forecasting'][7:].rename(columns={'pasajeros':'forecasting'})
    df_train = dict_terminal['datasets']['trainPredictPlot'][-15:].rename(columns={'predict_pasajeros':'training'})
    df_test = dict_terminal['datasets']['testPredictPlot'].rename(columns={'predict_pasajeros':'test'})
    df_real = dict_terminal['datasets']['dataset'][-22:].rename(columns={'pasajeros':'real'})

    df = df_forecasting[['fecha','forecasting']].merge(df_train[['fecha','training']],on ='fecha',how='outer')
    df = df.merge(df_test[['fecha','test']],on = 'fecha',how='outer')
    df = df.merge(df_real[['fecha','real']],on='fecha',how='outer')
    df.sort_values(by='fecha',inplace=True,ascending=True)
    fig = px.line(df,x="fecha", y = df.columns ,title='custom tick labels')

    fig.update_layout(title = {'text':"<b>Passenger time series<b>",'font_size':20})
    fig.update_xaxes(title={'text':"<b>Time (days)<b>",'font_size':15})
    fig.update_yaxes(title={'text':"<b>Passenger<b>",'font_size':15})
    fig.update_layout(legend_title_text='Time series')
   
    return fig

# Prediccion por fecha especifica
#%%

@app.callback(Output('forecasting-value', 'children'),
            [Input('my_terminal', 'value'),
            Input('my-date-picker-range', 'date')])
def forecasting_value(terminal_selected,start_date):

    dict_terminal = dict_modelos[terminal_selected]

    df = dict_terminal['datasets']['forecasting']

    value = df[df['fecha'] == start_date]['pasajeros'].iloc[0]


    card_training = dbc.Card([dbc.CardBody([html.H5("Passenger forecasting", className="card-title",style = {'text-align':'center'}),
                    html.P(f"{int(value)}", className="card-text",style = {'text-align':'center'})])])

    return card_training



# Botones de informacion
#%%

figures_info = {
    "Metrics": "RMSE is the root of the mean square that was obtained when training and testing the model. This metric was relativized for each terminal by dividing it by the average passenger value of each terminal.",
}

def make_popover(figure):
    title = figure.replace('Passengers',"Passengers'").replace('-',' ')
    return dbc.Popover(
        [   
            dbc.PopoverHeader(f"{title} info"),
            dbc.PopoverBody(figures_info[figure]),
        ],
        id=f"popover-{figure}",
        target=f"popover-{figure}-target",
        placement="bottom",
        is_open=False,
    )

def make_button(figure):
    return dbc.Button(
        html.Span(["", html.I(className="fas fa-info-circle")]),
        id=f"popover-{figure}-target",
        className="btn btn-sm rounded-circle",
        n_clicks=0,
    )


popovers = {key:html.Div([make_button(key),make_popover(key)]) for key in figures_info.keys()}


def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

for p in figures_info.keys():
    app.callback(
        Output(f"popover-{p}", "is_open"),
        [Input(f"popover-{p}-target", "n_clicks")],
        [State(f"popover-{p}", "is_open")],
    )(toggle_popover)





# Layout de la pagina 
#%%

terminal_boton = html.Div([dbc.Row([html.Div(html.H5('Specific terminal for analysis',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                    dbc.Row([dbc.Col(specific_terminal,width={"size": 3,"offset": 2}, align='center',style={"width": "100vh",'padding-right': '0px', 'padding-left': '1vh'}),
                    dbc.Col(dbc.Button(id="loading-button-terminales", n_clicks=0, children=["Search"]),width=3,style={'padding-left': '1vw'})],justify="center")]
                    ,style={"height": "10vh",'padding-top': '4px','margin-bottom': '1vh'})



time_series_plot = html.Div([dbc.Spinner(children=[dcc.Graph(id='forecasting-serie')],size="lg", color="primary", type="border",fullscreen=False)])


cards_metrics = html.Div([dbc.Row(popovers["Metrics"],justify='end',style={'margin-top': '5vh','margin-bottom': '1vh'}),
                        html.Div(id ='cards')],style={'margin-top': '3vh'})


banner =  html.Div([html.Div(html.H1('Terminal forecasting',style={'color':'white'}),style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})],
                    style={'background-image': "url(/assets/Prediction/Terminal-forecasting.png)",'backgroundPosition': 'center center',
                    'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'})

subtitulo = html.Div([html.P('On this page, you can see the prediction for each terminal on a specific date range. You can get more information by entering the upper right button.')],
            style={'text-align': 'left','margin-top': '6vh','color':'grey'})



parameter_buttons = html.Div([dbc.Row([
                    dbc.Col(html.Div([dbc.Row([dbc.Col(html.H5("Date for forecasting",style = {'text-align':'center'}))],justify="center"),
                    dbc.Row([dbc.Col(calendar,style= {'padding-left': '9rem'})],justify="center")]),width=4),
                    dbc.Col(html.Div(id='forecasting-value'),width = 4)],justify="center")],
                    style={"height": "5vh",'padding-top': '3vh','padding-bottom': '5vh'})



layout = html.Div([banner,
        subtitulo,
        terminal_boton,
        cards_metrics,
        time_series_plot,
        parameter_buttons,
        html.Div(style={"height": "5vh"}),    
        footer,
])














