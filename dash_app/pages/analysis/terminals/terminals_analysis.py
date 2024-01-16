"""
this page render info about terminals analysis
"""


import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
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
from datetime import date
from datetime import datetime
import pickle

from pages.footer import footer


# Coneccion a la base de datos
#%%

conn = psycopg2.connect(host="umovilgr81.cwwzdzhdizxh.us-east-2.rds.amazonaws.com",
                        port = 5432, database="transporte", 
                        user="postgres", password="qUIup2lwFxoXh9yEXo4P")




# Coalendario desplegabe
#%%

calendar =  html.Div(style={'fontSize': 8},
    children = dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2019,8,1),
        max_date_allowed=date(2021,8,15),
        start_date=date(2020, 10, 1),
        end_date=date(2021,8,15),
        calendar_orientation='horizontal'
    ))


# Mapa de las ubicaciones de los terminales
#%%

cur = conn.cursor()
cur.execute("""SELECT * FROM coordenadas_terminales""")
query_results = cur.fetchall()
cur.close()

terminales = pd.DataFrame(query_results,columns= ['indice','terminal',
                                          'latitud_terminales',
                                          'longitud_terminales',
                                          'divipola'] )

del(query_results)

terminales.drop(columns='indice',inplace = True)

fig_map_scattter = px.scatter_mapbox(terminales, lat="latitud_terminales", lon="longitud_terminales",
                        hover_name='terminal',color_discrete_sequence=["fuchsia"], zoom=4,width=400,height=500)

# Estilo del mapa
token = 'pk.eyJ1IjoidmltYWdvcnUiLCJhIjoiY2tpaTJxbmthMDVhMjJ5bjBnb2F2eDRocCJ9.Y5Lokm4pHAKvIaq31Hr5BA' # you will need your own token                                 
fig_map_scattter.update_layout(mapbox_style="dark",
                    mapbox_accesstoken=token,
                    margin={"r":0,"t":60,"l":0,"b":0},
                    title = {'text':"<b>Terminal location<b>",'x': 0.5,'font_size':20})

names_terminals = set(terminales['terminal'])

# Terminales especificas
#%%

teminal_esp = dcc.Dropdown(id='memory-countries', 
                    options=[{'label': terminal[8:], 'value': terminal} for terminal in names_terminals], 
                    multi=True, value=['T.T. DE BOGOTÁ SALITRE','T.T. DE CALI'])


# Heat map de los pasajeros 
#%%


@app.callback(
    Output('fig_heatmap', 'figure'),
    [Input("loading-button", "n_clicks")],
    [State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date')])
def fig_heatmap(n_clicks,start_date,end_date):

    start_date = str(start_date[:10])
    end_date = str(end_date[:10])

    with open(r'pages/analysis/terminals/Datos/heatmap-density.pkl','rb') as file:
        query_results = pickle.load(file)

    if n_clicks:
        query = f"""WITH terminal_pasajeros AS (SELECT terminal, SUM(pasajeros) AS pasajeros FROM pasajeros_origen_destino_ultima3
                WHERE fecha_despacho BETWEEN TO_DATE(CAST('{start_date}' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('{end_date}' AS VARCHAR),'YYYY-MM-DD')
                GROUP BY terminal)

                SELECT coordenadas_terminales.terminal AS terminal, coordenadas_terminales.latitud_terminal AS latitud_terminal, 
                coordenadas_terminales.longitud_terminal AS longitud_terminal, terminal_pasajeros.pasajeros AS pasajeros  FROM  coordenadas_terminales
                INNER JOIN terminal_pasajeros ON  terminal_pasajeros.terminal = coordenadas_terminales.terminal;"""  
    
        cur = conn.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        cur.close() 


    terminales = pd.DataFrame(query_results,columns= ['terminal',
                                            'latitud_terminal',
                                            'longitud_terminal',
                                            'pasajeros'] )

    fig_map_heat_p = px.density_mapbox(terminales, lat="latitud_terminal", lon="longitud_terminal",z='pasajeros',
                                hover_name='terminal',radius=25,zoom=4,width=400,height=500)

    fig_map_heat_p.update_layout(mapbox_style="dark",
                        mapbox_accesstoken=token,
                        margin={"r":0,"t":60,"l":0,"b":0},
                        title = {'text':"<b>Passenger density<b>",'x': 0.5,'font_size':20},
                        coloraxis_showscale=False)


    return fig_map_heat_p



# Serie de tiempo de los terminales
# %%

@app.callback(Output('memory-graph', 'figure'),
            [Input("loading-button-terminales", "n_clicks")],
            [State('memory-countries', 'value'),
            State('my-date-picker-range', 'start_date'),
            State('my-date-picker-range', 'end_date')])
def fig_line(n_clicks,terminal_selected,start_date,end_date):

    ter = f"'{terminal_selected[0]}'"
    for t in terminal_selected[1:]:
        ter = ter+f",'{t}'"

    start_date = str(start_date[:10])
    end_date = str(end_date[:10])

    with open(r'pages/analysis/terminals/Datos/time-series-comparacion.pkl','rb') as file:
        query_results = pickle.load(file)

    if n_clicks:
        query = f"""SELECT terminal ,fecha_despacho, SUM(pasajeros) AS pasajeros FROM pasajeros_origen_destino_ultima3
                    WHERE fecha_despacho BETWEEN TO_DATE(CAST('{start_date}' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('{end_date}' AS VARCHAR),'YYYY-MM-DD') AND terminal IN ({ter})
                    GROUP BY terminal, fecha_despacho;"""

        cur = conn.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        cur.close()

    dataset = pd.DataFrame(query_results,columns = ['terminal','fecha','pasajeros'])

    df_full = dataset.pivot(index= 'terminal',columns='fecha',values = 'pasajeros')
    df_T = df_full.T.reset_index()
    df_T['fecha'] = pd.to_datetime(df_T['fecha'])

    fig = px.line(df_T, x="fecha", y= df_T.columns ,title='custom tick labels')

    fig.update_layout(title = {'text':"<b>Passenger time series<b>",'font_size':20})
    fig.update_xaxes(title={'text':"<b>Time (days)<b>",'font_size':15})
    fig.update_yaxes(title={'text':"<b>Passenger<b>",'font_size':15})
   



    return fig


# Scatterplot PCA
#%%

with open(r'pages/analysis/terminals/Datos/pca.pkl','rb') as file:
    dict_term = pickle.load(file)

var_exp = dict_term['variance_explained']

del dict_term['variance_explained']

pca_1 = [dict_term[x][0] for x in dict_term.keys()]
pca_2 = [dict_term[x][1] for x in dict_term.keys()]
term = list(dict_term.keys())

df_PCA = pd.DataFrame({'terminal':term,'PCA_1':pca_1,'PCA_2':pca_2})

fig_pca = px.scatter(df_PCA, x='PCA_1', y='PCA_2',hover_name ='terminal')

fig_pca.update_layout(title = {'text':"<b>PCA of passenger time series<b>",'font_size':20})
fig_pca.update_xaxes(title={'text':"<b>PCA 1<b>",'font_size':15})
fig_pca.update_yaxes(title={'text':"<b>PCA 2<b>",'font_size':15})



# Informacion
#%%


figures_info = {
    "PCA": "In this graph, you can see the first two principal components of the passenger time series for the different terminals. The first main component shows the level of passengers it carries in relation to the others. The second goes on to explain the variation in passenger behavior.",
    "Passenger-time-series": " In this graph, a time series plot is shown to analyse and compare the number of passengers using the terminals."
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

banner = html.Div([html.Div(html.H1('Terminals',style={'color':'white'}),style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})],
                style={'background-image': "url(/assets/terminals/Imagen1.png)",'backgroundPosition': 'center center',
                'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'})


subtitle = html.Div([html.P('On this page, you can see the behavior of passengers in the terminals, with the possibility of comparing between them. You can get more information about each graph by entering the upper right button.')],
            style={'text-align': 'left','margin-top': '5vh','color':'grey'})



parameter_buttons = html.Div([dbc.Row([html.Div(html.H5('Dates for analysis',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                    dbc.Row([dbc.Col(calendar,width={"size": 4,"offset": 2}, align='center',style={"width": "100vh",'padding-right': '0px', 'padding-left': '3rem'}),
                    dbc.Col(dbc.Button(id="loading-button", n_clicks=0, children=["Search"]),width=3,align='center',style={'padding-left': '0px'})],justify="center")]
                    ,style={"height": "10vh",'padding-top': '4px'})


maps = dbc.Row([dbc.Col(dbc.Spinner(children=[dcc.Graph(figure=fig_map_scattter)], size="lg", color="primary", type="border",
                        fullscreen=False),width=4),
                dbc.Col(width=1),
                dbc.Col(dbc.Spinner(children=[dcc.Graph(id='fig_heatmap')], size="lg", color="primary", type="border",
                        fullscreen=False),width=4)
                ],justify="center",style={'margin-top': '4vh'})


terminal_esp_title = html.Div([dbc.Row([html.Div(html.H5('Select terminals',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                        dbc.Row(dbc.Col(html.Div([dcc.Store(id='memory-output'),teminal_esp])))])


parameter_sec = html.Div([dbc.Row([dbc.Col(terminal_esp_title),
            dbc.Col(dbc.Button(id="loading-button-terminales", n_clicks=0, children=["Search"]),
            style={'padding-left': '0px','padding-top': '4vh'})])],style={'margin-top': '5vh'})


scatter_PCA = html.Div([dbc.Row(popovers["PCA"],justify='end',style={'margin-top': '5vh'}),
                        dcc.Graph(id="scatter-plot",figure = fig_pca)],style={'margin-top': '3vh'})


time_series_plot = html.Div([dbc.Row(popovers["Passenger-time-series"],justify='end',style={'margin-top': '5vh'}),
                    dbc.Spinner(children=[dcc.Graph(id='memory-graph')],size="lg", color="primary", type="border",fullscreen=False)])


layout =html.Div([
            banner,
            subtitle,
            parameter_buttons,
            maps,
            parameter_sec,
            time_series_plot,
            scatter_PCA,
            footer
            ])      
