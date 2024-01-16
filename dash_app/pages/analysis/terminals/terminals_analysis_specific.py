""" 
This file render terminal analysis
"""

#%%
# dash dependences
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

# graph
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# number
import pandas as pd
import numpy as np

import datetime
from datetime import date

import psycopg2 # libreria que permite la coneccion con la base de datos
from app import app
from pages.footer import footer
from pandas.api.types import CategoricalDtype
import pickle


# Credenciales
#%% conneccion with amazom RDS
conn = psycopg2.connect(host="umovilgr81.cwwzdzhdizxh.us-east-2.rds.amazonaws.com",
                        port = 5432, database="transporte", 
                        user="postgres", password="qUIup2lwFxoXh9yEXo4P")




# DropDown por terminales
#%%
with open(r'pages/analysis/terminals/Datos/name-terminals.pkl','rb') as file:
    terminales = pickle.load(file)

terminales_dropdown = [{'label': terminal[0][8:], 'value': terminal[0]} for terminal in terminales]

del(terminales)

specific_terminal = dcc.Dropdown(options = terminales_dropdown, 
                                id = 'my_terminal',
                                value = 'T.T. DE MELGAR')



# Calendario para rango de fechas a estudiar
#%%

calendar = dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2019,8,1),
        max_date_allowed=date(2021,8,15),
        start_date=date(2021,1,1),
        end_date=date(2021,8,15),
        calendar_orientation='horizontal')



# Grafica de Scatter plot
#%%


@app.callback(
    Output('fig_scatter_pvsd', 'figure'),
    [Input("loading-button", "n_clicks")],
    [State("my_terminal", "value"),
     State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date'),
     ])
def scatter_pvsd(n_clicks,terminal,start_date,end_date):

    start_date = str(start_date[:10])
    end_date = str(end_date[:10])

    with open(r'pages/analysis/terminals/Datos/Scatter-plot.pkl','rb') as file:
        query_results = pickle.load(file)

    if n_clicks:

        query = f"""SELECT pasajeros, despachos, clase_vehiculo AS clase, fecha_despacho as date
                    FROM pasajeros_origen_destino_ultima3
                    WHERE fecha_despacho BETWEEN TO_DATE(CAST('{start_date}' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('{end_date}' AS VARCHAR),'YYYY-MM-DD') AND terminal = '{terminal}'
                    """  
        cur = conn.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        cur.close()

    scatter_df = pd.DataFrame(query_results,columns= ['pasajeros', 'despachos', 'vehicle_type','date'])

    scatter_df['date'] = pd.to_datetime(scatter_df['date'])
    scatter_df.sort_values(by='date',ascending=True,inplace=True)
    scatter_df['pasajeros'] = scatter_df['pasajeros'].interpolate().fillna(method = 'backfill',axis=0)

    fig_scatter_pvsd = px.scatter(scatter_df, x="pasajeros", y="despachos",color="vehicle_type",hover_data=['date'])

    fig_scatter_pvsd.update_layout(title = {'text':"<b>Dispatches vs Passengers' scatter plot<b>",'x': 0.5,'font_size':20})
    fig_scatter_pvsd.update_xaxes(title={'text':"<b>Passengers<b>",'font_size':15})
    fig_scatter_pvsd.update_yaxes(title={'text':"<b>Dispatches<b>",'font_size':15})

    return fig_scatter_pvsd


#%%

# chagnge heatmap when values changes of form change
@app.callback(
    Output('fig_passenger_flow', 'figure'),
    [Input("loading-button", "n_clicks")],
    [State("my_terminal", "value"),
     State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date'),
     ])
def heatmap_passenger_flow(n_clicks,terminal,start_date,end_date):

    start_date = str(start_date[:10])
    end_date = str(end_date[:10])


    with open(r'pages/analysis/terminals/Datos/Heat-corelation.pkl','rb') as file:
        query_results = pickle.load(file)

    if n_clicks:
 
        query = f"""SELECT EXTRACT(isodow FROM fecha_despacho) AS day, SUM(pasajeros) AS pasajeros, hora_despacho AS hour
                    FROM pasajeros_origen_destino
                    WHERE fecha_despacho BETWEEN TO_DATE(CAST('{start_date}' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('{end_date}' AS VARCHAR),'YYYY-MM-DD') AND terminal = '{terminal}'
                    GROUP BY day,hour
                    """  
        cur = conn.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        cur.close()

    flow_df = pd.DataFrame(query_results,columns= ['day','pasajeros','hour'])

    flow_df.sort_values(by=['day','hour'],ascending=True,inplace=True)
    flow_df['pasajeros'] = flow_df['pasajeros'].interpolate().fillna(method = 'backfill',axis=0)
    flow_df['day'] = flow_df['day'].replace({1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday',6:'Saturday',7:'Sunday'})
    cat_type = CategoricalDtype(categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday','Sunday'], ordered=True)
    flow_df['day'] = flow_df['day'].astype(cat_type)


    flow_plotly = {'z': flow_df['pasajeros'].tolist(),
                   'y': flow_df['day'].tolist(),
                   'x': flow_df['hour'].tolist()}

    fig_passenger_flow = go.Figure(data=go.Heatmap(flow_plotly))

  
    fig_passenger_flow.update_layout(title = {'text':"<b>Passengers' heatmap<b>",'x': 0.5,'font_size':20})
    fig_passenger_flow.update_xaxes(title={'text':"<b>Hours of the day<b>",'font_size':15})
    fig_passenger_flow.update_yaxes(title={'text':"<b>Days of the week<b>",'font_size':15})


    return fig_passenger_flow

# callback when datetime interval is change
@app.callback(
    Output('fig_time_series', 'figure'),
    [Input("loading-button", "n_clicks")],
    [State("my_terminal", "value"),
     State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date'),
     ])
# get data from tiemseries
def time_series(n_clicks,terminal,start_date,end_date):
       

    start_date = str(start_date[:10])
    end_date = str(end_date[:10])

    with open(r'pages/analysis/terminals/Datos/time-series-despachos.pkl','rb') as file:
        query_results = pickle.load(file)

    if n_clicks:
        query = f"""SELECT EXTRACT(YEAR FROM fecha_despacho) AS year, EXTRACT(MONTH FROM fecha_despacho) AS month, EXTRACT(DAY FROM fecha_despacho) AS day,
                    SUM(pasajeros) AS pasajeros, SUM(despachos) AS despachos FROM pasajeros_origen_destino
                    WHERE fecha_despacho BETWEEN TO_DATE(CAST('{start_date}' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('{end_date}' AS VARCHAR),'YYYY-MM-DD') AND terminal = '{terminal}'
                    GROUP BY year, month, day
                """ 
        

        cur = conn.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        cur.close()

    time_df = pd.DataFrame(query_results,columns = ['year','month','day','pasajeros','despachos'])
    # create a new date
    time_df['fecha'] =  [f'{int(year)}-{int(month)}-{int(day)}' for year, month, day in  zip(time_df['year'],time_df['month'],time_df['day'])]
    time_df['fecha'] =  pd.to_datetime(time_df['fecha'])
    
    # gernerate figure
    fig_time_series = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time_series.add_trace(
        go.Scatter(x=time_df["fecha"], y=time_df["pasajeros"], name="Passengers"),
        secondary_y=False,
    )

    fig_time_series.add_trace(
        go.Scatter(x=time_df["fecha"], y=time_df["despachos"], name="Despatchs"),
        secondary_y=True,
    )
    
    fig_time_series.update_xaxes(title = {'text':"<b>Date<b>",'font_size':15})

    # Set y-axes titles    
    fig_time_series.update_layout(title = {'text':"<b>Dispatches and Passengers's dual time series<b>",'x': 0.5,'font_size':20})
    fig_time_series.update_yaxes(title={'text':"<b>Passengers<b>",'font_size':15}, secondary_y=False)
    fig_time_series.update_yaxes(title={'text':"<b>Despatchs<b>",'font_size':15}, secondary_y=True)
    return fig_time_series

figures_info = {
    "Passengers-heatmap": "A weekly and hourly representation of passenger's activity on a period of time",
    "Dispatches-and-Passengers-dual-time-series": "Two time series that ilustrate the activity of both variables through a period of time",
    "Dispatches-vs-Passengers-scatter-plot": "On a certain hour, a terminal can send several dispatches and passengers. The hover data contains useful details per set of dispatchs through a period of time"
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




parameter_buttons = html.Div([dbc.Row([html.Div(html.H5('Dates and terminal for analysis',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                        dbc.Row([dbc.Col(calendar, width =4 ,style={"width": "100vh",'padding-right': '0px', 'padding-left': '5vw'}),
                                dbc.Col(specific_terminal, width=2,align='center'),
                                dbc.Col(dbc.Button(id="loading-button", n_clicks=0, children=["Analyze"]), width=1,align='center',style={'padding-left': '0px'})
                                ],justify="center")])


heatmap_passenger_flow = html.Div([dbc.Row(popovers["Passengers-heatmap"],justify='end',style={"margin-bottom":"0px"}),
                          dbc.Spinner(children=[dcc.Graph(id="fig_passenger_flow")], size="lg", color="primary", type="border",fullscreen=False)])

scatter_pvsd =  html.Div([dbc.Row(popovers["Dispatches-vs-Passengers-scatter-plot"],justify='end',style={"margin-bottom":"0px"}),
                 dbc.Spinner(children=[dcc.Graph(id="fig_scatter_pvsd")], size="lg", color="primary", type="border",fullscreen=False)])

time_series =   html.Div([dbc.Row(popovers["Dispatches-and-Passengers-dual-time-series"],justify='end',style={"margin-bottom":"0px"}),
                          dbc.Spinner(children=[dcc.Graph(id="fig_time_series")], size="lg", color="primary", type="border",fullscreen=False)])



banner = html.Div([html.Div(html.H1('Specific terminals',style={'color':'white'}),style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})],
                          style={'background-image': "url(/assets/terminals/Medellin-terminal.jpg)",'backgroundPosition': 'center center',
                                 'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'})



subtitle = html.Div([html.P('A tab to perform an even more customizable analysis for each of the terminals in a period of time. You can get more information about each graph by entering the upper right button.')],style={'text-align': 'left','color':'grey'})




layout =html.Div([
                banner,
                subtitle,
                parameter_buttons,
                heatmap_passenger_flow,
                scatter_pvsd,
                time_series,
                footer
            ])  



