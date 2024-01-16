""" 
This file render routes analysis
"""

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app import app
from datetime import date
from datetime import datetime
import dash_table
import psycopg2  # libreria que permite la coneccion con la base de datos
from pages.footer import footer

# Credentials and connection with AWS database

conn = psycopg2.connect(host="umovilgr81.cwwzdzhdizxh.us-east-2.rds.amazonaws.com",
                        port=5432, database="transporte",
                        user="postgres", password="qUIup2lwFxoXh9yEXo4P")

token = 'pk.eyJ1IjoidmltYWdvcnUiLCJhIjoiY2tpaTJxbmthMDVhMjJ5bjBnb2F2eDRocCJ9.Y5Lokm4pHAKvIaq31Hr5BA'  # You will need your own token by mapbpx style

# Query the central coordinates table and save the data in a dataframe

cur3 = conn.cursor()
querycoord = """SELECT * FROM divipola_coord_centrales"""
cur3.execute(querycoord)
querycoord_results = cur3.fetchall()
cur3.close()
coordcentrales = pd.DataFrame(querycoord_results, columns=['index', 'region',
                                                           'codigo_dane_del_departamento',
                                                           'departamento',
                                                           'codigo_dane_del_municipio',
                                                           'municipio', 'latitud_centro_municipio',
                                                           'longitud_centro_municipio'])

# Query a terminal table and save the data in a dataframe
cur44 = conn.cursor()
queryterminales = """SELECT * FROM coordenadas_terminales"""
cur44.execute(queryterminales)
queryterminales = cur44.fetchall()
cur44.close()
terminalesvictor = pd.DataFrame(queryterminales, columns=['index', 'terminal', 'latitud_terminal',
                                                          'longitud_terminal',
                                                          'codigo_dane_del_municipio'])


# Preload data in table of routes page for initial bar graph
initialpasajerosdf = [('5001-5615', 1614265), ('11001-76001', 1570860), ('76001-76520', 1471642),
                      ('63001-63401', 1376713), ('11001-25307', 1265489), ('15759-11001', 1242937),
                      ('66001-63001', 1236683), ('76001-11001', 1213122), ('66001-66682', 1163781),
                      ('50001-11001', 1128320)]
initialpasajerosdf = pd.DataFrame(initialpasajerosdf, columns=['ruta', 'Total_Passengers'])
initialpasajerosdf[['cod_origen', 'cod_destino']] = initialpasajerosdf['ruta'].str.split('-', 1, expand=True).astype(
    int)
initialpasajerosdf["nom_origen"] = initialpasajerosdf["cod_origen"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
initialpasajerosdf["nom_destino"] = initialpasajerosdf["cod_destino"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
initialpasajerosdf["lon_origen"] = initialpasajerosdf["cod_origen"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
initialpasajerosdf["lat_origen"] = initialpasajerosdf["cod_origen"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
initialpasajerosdf["lon_destino"] = initialpasajerosdf["cod_destino"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
initialpasajerosdf["lat_destino"] = initialpasajerosdf["cod_destino"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
initialpasajerosdf["Origin-Destination"] = initialpasajerosdf["nom_origen"] + "-" + initialpasajerosdf["nom_destino"]

# Make database connection for preloaded table

currout = conn.cursor()
queryrout = "SELECT CONCAT(municipio_origen_ruta, '-', municipio_destino_ruta) as ruta FROM pasajeros_origen_destino_2021 GROUP BY ruta"
currout.execute(queryrout)
queryrout_results = currout.fetchall()
currout.close()
list_routes = pd.DataFrame(queryrout_results, columns=['route'])
list_routes[['cod_origen', 'cod_destino']] = list_routes['route'].str.split('-', 1, expand=True).astype(int)
list_routes["nom_origen"] = list_routes["cod_origen"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
list_routes["nom_destino"] = list_routes["cod_destino"].map(
    coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
diccionario_rutas = list_routes.groupby('nom_origen')['nom_destino'].apply(list).to_dict()

# Make dynamic dropdown so that according to the origin of the route it obtains the destinations

drop_type_origin = dcc.Dropdown(
    id='drop_origin',
    options=[{'label': k, 'value': k} for k in diccionario_rutas.keys()],
    value='Cali',
    multi=False,
    clearable=False,
    style={"width": "100%"},
)

# Función para obtener tabla y mapa dinámico que cambia con el dropdown anterior de origen y destino puestos por el usuario
def obtaintabledin(rutan):
    curtabla = conn.cursor()
    querytabla = "WITH tabla1 as(SELECT CONCAT(municipio_origen_ruta, '-', municipio_destino_ruta) as ruta, pasajeros, terminal FROM pasajeros_origen_destino_2021) SELECT tabla1.terminal, SUM(tabla1.pasajeros) as totpas FROM tabla1 WHERE ruta = '" + rutan + "' GROUP BY tabla1.terminal ORDER BY totpas DESC;"
    curtabla.execute(querytabla)
    querytabla_results = curtabla.fetchall()
    curtabla.close()
    dftabladin = pd.DataFrame(querytabla_results, columns=['terminal',
                                                           'totpas'])
    dftabladin['codigo_dane_del_municipio'] = dftabladin['terminal'].map(
        terminalesvictor.set_index('terminal')['codigo_dane_del_municipio'])
    dftabladin['nombre'] = dftabladin['codigo_dane_del_municipio'].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])

    for i in dftabladin['terminal']:
        if i == 'T.T. DE BOGOTÁ SALITRE':
            idx = dftabladin.index[dftabladin['terminal'] == i]
            dftabladin.at[idx, 'nombre'] = 'Bogotá Salitre'
        elif i == 'T.T. DE BOGOTÁ SUR':
            idx = dftabladin.index[dftabladin['terminal'] == i]
            dftabladin.at[idx, 'nombre'] = 'Bogotá Sur'
        elif i == 'T.T. DE BOGOTÁ NORTE':
            idx = dftabladin.index[dftabladin['terminal'] == i]
            dftabladin.at[idx, 'nombre'] = 'Bogotá Norte'
        elif i == 'T.T. DE MEDELLÍN NORTE':
            idx = dftabladin.index[dftabladin['terminal'] == i]
            dftabladin.at[idx, 'nombre'] = 'Medellín Norte'
        elif i == 'T.T. DE MEDELLÍN SUR':
            idx = dftabladin.index[dftabladin['terminal'] == i]
            dftabladin.at[idx, 'nombre'] = 'Medellín Sur'
    dftabladin['departamento'] = dftabladin['codigo_dane_del_municipio'].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['departamento'])
    dftabladin['latitud_terminal'] = dftabladin['terminal'].map(
        terminalesvictor.set_index('terminal')['latitud_terminal'])
    dftabladin['longitud_terminal'] = dftabladin['terminal'].map(
        terminalesvictor.set_index('terminal')['longitud_terminal'])
    return dftabladin


# Callback para figura precargada sobre rutas
@app.callback(
    Output('fig_scatter', 'figure'),
    [Input("loading-button2", "n_clicks")],
    [State("drop_origin", 'value'),
     State("drop_destination", 'value')])
def update_mapa(n_clicks,origint, destinationt):
    
    token1 = 'pk.eyJ1IjoidmltYWdvcnUiLCJhIjoiY2tpaTJxbmthMDVhMjJ5bjBnb2F2eDRocCJ9.Y5Lokm4pHAKvIaq31Hr5BA'  # you will need your own token 
    latitudd = latitudesbase[7]
    longitudd = longitudesbase[7]
    nombress = ["Cali", "Buga","Tuluá", "Armenia", "Ibagué", "Girardot", "Melgar","Bogotá"]
    dfbase = pd.DataFrame()
    dfbase['nombress'] = nombress
    dfbase['latitudd'] = latitudd
    dfbase['longitudd'] = longitudd

    fig_scatterbase = px.scatter_mapbox(dfbase, lat="latitudd", lon="longitudd",
                                    hover_name='nombress', zoom=5)
    fig_scatterbase.update_layout(mapbox_style="dark",
                              mapbox_accesstoken=token1,
                              margin={"r": 0, "t": 0, "l": 0, "b": 0},
                              coloraxis_showscale=False)
    if n_clicks:
        aa1 = coordcentrales.loc[coordcentrales['municipio'] == origint, 'codigo_dane_del_municipio'].values[0]
        bb1 = coordcentrales.loc[coordcentrales['municipio'] == destinationt, 'codigo_dane_del_municipio'].values[0]
        rutann = aa1.astype(str) + "-" + bb1.astype(str)
        dffdinn = obtaintabledin(rutann)
        dffdinn2 = dffdinn[['nombre', 'totpas', 'latitud_terminal', 'longitud_terminal']]
        bb1lat = coordcentrales.loc[coordcentrales['codigo_dane_del_municipio'] == bb1, 'latitud_centro_municipio'].values[0]
        bb1lon = coordcentrales.loc[coordcentrales['codigo_dane_del_municipio'] == bb1, 'longitud_centro_municipio'].values[0]
        dffdinn2.loc[dffdinn2.index.max() + 1] = [destinationt, 0, bb1lat, bb1lon]
        test1 = aa1 in terminalesvictor.codigo_dane_del_municipio.values
        if test1 is False:
            aa1lat = coordcentrales.loc[coordcentrales['codigo_dane_del_municipio'] == aa1, 'latitud_centro_municipio'].values[0]
            aa1lon =coordcentrales.loc[coordcentrales['codigo_dane_del_municipio'] == aa1, 'longitud_centro_municipio'].values[0]
            dffdinn2.loc[dffdinn2.index.max() + 1] = [origint, 0, aa1lat, aa1lon]
        fig_scatter = px.scatter_mapbox(dffdinn2, lat="latitud_terminal", lon="longitud_terminal",
                                           hover_name='nombre', zoom=5)
        fig_scatter.update_layout(mapbox_style="dark",
                                     mapbox_accesstoken=token1,
                                     margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                     coloraxis_showscale=False)
        return fig_scatter
    return fig_scatterbase

# Callback para tabla dinámica de final de página
@app.callback(
    Output('table2', 'children'),
    [Input("loading-button2", "n_clicks")],
    [State("drop_origin", 'value'),
     State("drop_destination", 'value')])
def update_tabledim(n_clicks,origint, destinationt):
    nombress = ["Cali", "Buga", "Tuluá", "Armenia", "Ibagué", "Girardot", "Melgar", "Bogotá"]
    deptos = ["Valle del Cauca", "Valle del Cauca", "Valle del Cauca","Quindío", "Tolima", "Cundinamarca", "Tolima", "Bogotá D.C."]
    passse = [98185, 10995, 63610, 32318, 18033, 418, 218,0]
    dfbase2 = pd.DataFrame()
    dfbase2['Bus terminal in the route'] = nombress
    dfbase2['Departament'] = deptos
    dfbase2['Boarding passengers in 2021'] = passse
    data2 = dfbase2.to_dict('rows')
    columns2 = [{"name": i, "id": i, } for i in dfbase2.columns]
    if n_clicks:
        a1 = coordcentrales.loc[coordcentrales['municipio'] == origint, 'codigo_dane_del_municipio'].values[0]
        b1 = coordcentrales.loc[coordcentrales['municipio'] == destinationt, 'codigo_dane_del_municipio'].values[0]
        rutan = a1.astype(str) + "-" + b1.astype(str)
        dffdin = obtaintabledin(rutan)
        dftabladin2 = dffdin[['nombre', 'departamento', 'totpas']]
        dftabladin3 = dftabladin2[(dftabladin2['totpas'] >= 1)]
        c1depto = coordcentrales.loc[coordcentrales['municipio'] == destinationt, 'departamento'].values[0]
        dftabladin3.loc[dftabladin3.index.max() + 1] = [destinationt, c1depto, 0]
        test1 = a1 in terminalesvictor.codigo_dane_del_municipio.values
        if test1 is False:
            aa1dpto = coordcentrales.loc[coordcentrales['codigo_dane_del_municipio'] == a1, 'departamento'].values[0]
            dftabladin3.loc[-1] = [origint, aa1dpto, 'Not Available']  # adding a row
            dftabladin3.index = dftabladin3.index + 1  # shifting index
            dftabladin3.sort_index(inplace=True)
        dftabladin3 = dftabladin3.rename(
            columns={"nombre": "Bus terminal in the route", "departamento": "Departament",
                     "totpas": "Boarding passengers in 2021"})
        data = dftabladin3.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in dftabladin3.columns]
        return dash_table.DataTable(
            data=data,
            columns=columns,
            style_cell={
                'textAlign': 'center',
                'height': 'auto',
                'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
                'whiteSpace': 'normal'
            },
            style_as_list_view=True,
            style_table={'overflowX': 'auto'},
            fill_width=False)
    else:
        return dash_table.DataTable(
            data=data2,
            columns=columns2,
            style_cell={
                'textAlign': 'center',
                'height': 'auto',
                'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
                'whiteSpace': 'normal'
            },
            style_as_list_view=True,
            style_table={'overflowX': 'auto'},
            fill_width=False)

# Callback para tabla obtener los destinos disponibles desde un origen en dropdown
@app.callback(
    Output('drop_destination', 'options'),
    Input('drop_origin', 'value'))
def set_cities_options(selected_origin):
    return [{'label': i, 'value': i} for i in diccionario_rutas[selected_origin]]

# Callback para tabla obtener los destinos disponibles desde un origen en dropdown
@app.callback(
    Output('drop_destination', 'value'),
    Input('drop_destination', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']

# Coordenadas fijas obtenidas para mapa de rutas precargado
latitudesbase = [
    [6.28038, 6.21691, 6.14722409],
    [4.6551, 4.59784, 4.338480851, 4.208154892, 4.313078337, 4.439608991, 4.535989502, 4.085261239, 3.414414305],
    [3.414414305, 3.532349153],
    [4.535989502, 4.453650416],
    [4.6551, 4.59784, 4.338480851, 4.208154892, 4.313078337],
    [4.805680265, 6.155818729],
    [5.72568939, 5.82298568, 5.539953238, 4.6551],
    [3.414414305, 3.900823544, 4.085261239, 4.535989502, 4.439608991, 4.313078337, 4.208154892, 4.6551],
    [4.805680265, 4.867526454],
    [4.1238615, 4.6551],
    [4.313078337, 4.208154892, 4.338480851, 4.6551],
    [0.827734241442, 1.212124365, 2.482503391, 3.414414305],
    [4.439608991, 4.151314221, 4.313078337, 4.208154892, 4.338480851, 4.6551],
    [4.6551, 4.59784, 4.338480851, 4.208154892, 4.313078337, 4.151314221, 4.4396089910],
    [7.883417406, 7.666300439]]

longitudesbase = [
    [-75.57067, -75.58868, -75.37676938],
    [-74.11538, -74.17602, -74.36633393, -74.6298504, -74.79779459, -75.19371478, -75.68075076, -76.19769968,-76.52156515],
    [-76.52156515, -76.29858255],
    [-75.68075076, -75.78646018],
    [-74.11538, -74.17602, -74.36633393, -74.6298504, -74.79779459],
    [-75.71712306, -75.78683783],
    [-72.92304769, -73.03060967, -73.35548873, -74.11538],
    [-76.52156515, -76.29896113, -76.19769968, -75.68075076, -75.19371478, -74.79779459, -74.6298504, -74.11538],
    [-75.71712306, -75.62001066],
    [-73.62709204, -74.11538],
    [-74.79779459, -74.6298504, -74.36633393, -74.11538],
    [-77.64640075, -77.27857635, -76.57406468, -76.52156515],
    [-75.19371478, -74.88544976, -74.79779459, -74.6298504, -74.36633393, -74.11538],
    [-74.11538, -74.17602, -74.36633393, -74.6298504, -74.79779459, -74.88544976, -75.193714780],
    [-76.62596065, -76.6812164]
]

# Tabla precargada de rutas en seccion media de pagina
@app.callback(Output('table1', 'children'),
              [Input('selection_type_2', 'value')])
def tableee(top_routes):
    if top_routes == 0:
        dict_ruta = {
            "Mellín Norte": ("Antioquia", 326040),
            "Mellín Sur": ("Antioquia", 20785),
            "Rionegro": ("Antioquia", 0)
        }
    elif top_routes == 1:
        dict_ruta = {
            "Bogotá Salitre": ("Bogotá D.C.", 113854),
            "Bogotá Sur": ("Bogotá D.C.", 30822),
            "Fusagasugá": ("Cundinamarca", 4056),
            "Melgar": ("Tolima", 12347),
            "Girardot": ("Cundinamarca", 4583),
            "Ibagué": ("Tolima", 153300),
            "Armenia": ("Antioquia", 69412),
            "Tuluá": ("Valle del Cauca", 350877),
            "Cali": ("Valle del Cauca", 0)
        }
    elif top_routes == 2:
        dict_ruta = {
            "Cali": ("Valle del Cauca", "109067"),
            "Palmira": ("Valle del Cauca", "0"),
        }
    elif top_routes == 3:
        dict_ruta = {
            "Armenia": ("Antioquia", "252759"),
            "La Tebaida": ("Quindío", "0"),
        }
    elif top_routes == 4:
        dict_ruta = {
            "Bogotá Salitre": ("Bogotá D.C.", "92278"),
            "Bogotá Sur": ("Bogotá D.C.", "117361"),
            "Fusagasugá": ("Cundinamarca", "20834"),
            "Melgar": ("Tolima", "6333"),
            "Girardot": ("Cundinamarca", "0"),
        }
    elif top_routes == 5:
        dict_ruta = {
            "Pereira": ("Risaralda", "266972"),
            "Armenia": ("Antioquia", "0"),
        }
    elif top_routes == 6:
        dict_ruta = {
            "Sogamoso": ("Boyacá", "110438"),
            "Duitama": ("Boyacá", "79039"),
            "Tunja": ("Boyacá", "111591"),
            "Bogotá Salitre": ("Bogotá D.C.", "0"),
        }
    elif top_routes == 7:
        dict_ruta = {
            "Cali": ("Valle del Cauca", "97928"),
            "Buga": ("Valle del Cauca", "10954"),
            "Tulúa": ("Valle del Cauca", "63479"),
            "Armenia": ("Antioquia", "32204"),
            "Ibagué": ("Tolima", "18024"),
            "Girardot": ("Cundinamarca", "418"),
            "Melgar": ("Tolima", "218"),
            "Bogotá Salitre": ("Bogotá D.C.", "0"),
        }
    elif top_routes == 8:
        dict_ruta = {
            "Pereira": ("Risaralda", "222575"),
            "Santa Rosa De Cabal": ("Valle del Cauca", "0"),
        }
    elif top_routes == 9:
        dict_ruta = {
            "Villavicencio": ("Meta", "272339"),
            "Bogotá Salitre": ("Bogotá D.C.", "0"),
        }
    elif top_routes == 10:
        dict_ruta = {
            "Girardot": ("Cundinamarca", "162919"),
            "Melgar": ("Tolima", "46881"),
            "Fusagasugá": ("Cundinamarca", "22537"),
            "Bogotá Salitre": ("Bogotá D.C.", "0"),
        }
    elif top_routes == 11:
        dict_ruta = {
            "Ipiales": ("Nariño", "72032"),
            "Pasto": ("Nariño", "52085"),
            "Popayán": ("Cauca", "32729"),
            "Cali": ("Valle del Cauca", "0"),
        }
    elif top_routes == 12:
        dict_ruta = {
            "Ibagué": ("Tolima", "199789"),
            "Espinal": ("Tolima", "3220"),
            "Girardot": ("Cundinamarca", "144"),
            "Melgar": ("Tolima", "28316"),
            "Fusagasugá": ("Cundinamarca", "352"),
            "Bogotá Salitre": ("Bogotá D.C.", "0"),
        }
    elif top_routes == 13:
        dict_ruta = {
            "Bogotá Salitre": ("Bogotá D.C.", "100129"),
            "Bogotá Sur": ("Bogotá D.C.", "71580"),
            "Fusagasugá": ("Cundinamarca", "4379"),
            "Melgar": ("Tolima", "25682"),
            "Girardot": ("Cundinamarca", "3143"),
            "Espinal": ("Tolima", "51"),
            "Ibagué": ("Tolima", "0"),
        }
    else:
        dict_ruta = {
            "Apartadó": ("Antioquia", "219413"),
            "Chigorodó": ("Antioquia", "0"),
        }
    df54 = pd.DataFrame.from_dict(dict_ruta, 'index').reset_index()
    df556 = df54.rename(
        columns={"index": "Bus terminal in the route", 0: "Departament", 1: "Boarding passengers"})
    data = df556.to_dict('rows')
    columns = [{"name": i, "id": i, } for i in (df556.columns)]
    return dash_table.DataTable(
        data=data,
        columns=columns,
        style_cell={
            'textAlign': 'center',
            'height': 'auto',
            # all three widths are needed
            'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
            'whiteSpace': 'normal'
        },
        style_as_list_view=True,
        style_table={'overflowX': 'auto'},
        fill_width=False)

# Primer dropdown sobre filtrar grafico de barras por pasajeros o despachos
drop_type = dcc.Dropdown(
    id='selection_type',
    options=[
        {'label': 'Passenger', 'value': 'Passengers'},
        {'label': 'Dispatches', 'value': 'Dispatches'},
    ],
    value='Passengers',
    multi=False,
    clearable=False,
    style={"width": "100%"},
)
input_top = dbc.Input(
    id="routes_num",
    type="number",
    min=1,
    max=20,
    step=1,
    value=10
)
# Calendario sobre filtrar grafico de barras por pasajeros o despachos
calendar2 = html.Div(
    children=dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2019, 8, 1),
        max_date_allowed=date(2021, 8, 18),
        start_date=date(2019, 8, 1),
        end_date=date(2021, 8, 18),
        calendar_orientation='horizontal'
    ))
# Opcion de seleccionar ruta para dibujarla en mapa
radio_item_routes_for_map = dcc.RadioItems(
    id='selection_type_2',
    options=[
        {'label': " Medellín Norte - Rionegro", 'value': 0},
        {'label': " Bogotá Salitre - Cali", 'value': 1},
        {'label': " Cali - Palmira", 'value': 2},
        {'label': " Armenia - La Tebaida", 'value': 3},
        {'label': " Bogotá Salitre - Girardot", 'value': 4},
        {'label': " Pereira - Armenia", 'value': 5},
        {'label': " Sogamoso - Bogotá Salitre", 'value': 6},
        {'label': " Cali - Bogotá Salitre", 'value': 7},
        {'label': " Pereira - Santa Rosa De Cabal", 'value': 8},
        {'label': " Villavicencio - Bogotá Salitre", 'value': 9},
        {'label': " Girardot - Bogotá Salitre", 'value': 10},
        {'label': " Ipiales - Cali", 'value': 11},
        {'label': " Ibagué - Bogotá Salitre", 'value': 12},
        {'label': " Bogotá Salitre - Ibagué", 'value': 13},
        {'label': " Apartadó - Chigodoró", 'value': 14}
    ],
    value=1,
    labelStyle={'display': 'block'}
)


# Callback de la gráfica de barras inicial que muestra top rutas según fechas de calendario
@app.callback(
    Output("the_graph", 'figure'),
    [Input("loading-button", "n_clicks")],
    [State("routes_num", "value"),
     State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date'),
     State("selection_type", "value")],
)
def update_graph(n_clicks, input1, input2, input3, input4):

    numtop = str(input1)
    start_date2 = str(input2[:10])
    end_date2 = str(input3[:10])
    selection_type2 = str(input4)

    if n_clicks:
        if selection_type2 == 'Passengers':
            dff = top_rutas_pasajeros_year(numtop, start_date2, end_date2, coordcentrales)
            barchart = px.bar(data_frame=dff, x="Origin-Destination",y="Total_Passengers")

            barchart.update_layout(title = {'text':f"<b>Top {numtop} routes with more passengers between {start_date2} and {end_date2} <b>",'font_size':20})
            barchart.update_xaxes(title={'text':"<b>Origin-Destination<b>",'font_size':15})
            barchart.update_yaxes(title={'text':"<b>Total passengers<b>",'font_size':15})
            return barchart

        elif selection_type2 == 'Dispatches':
            dff = top_rutas_despachos_year(numtop, start_date2, end_date2, coordcentrales)
            barchart = px.bar(data_frame=dff,x="Origin-Destination",y="Total of dispatches")


            # title="Top " + numtop + " routes with more dispatches between " + start_date2 + " and " + end_date2

            barchart.update_layout(title = {'text':f"<b>Top {numtop} routes with more dispatches between {start_date2} and {end_date2}<b>",'font_size':20})
            barchart.update_xaxes(title={'text':"<b>Origin-Destination<b>",'font_size':15})
            barchart.update_yaxes(title={'text':"<b>Total dispatches",'font_size':15})

            return barchart

    barchart = px.bar(data_frame=initialpasajerosdf,x="Origin-Destination",y="Total_Passengers")
    
    barchart.update_layout(title = {'text':f"<b>Top {numtop} routes with more dispatches between {start_date2} and {end_date2}<b>",'font_size':20})
    barchart.update_xaxes(title={'text':"<b>Origin-Destination<b>",'font_size':15})
    barchart.update_yaxes(title={'text':"<b>Total Passengers",'font_size':15})
   
    return barchart




# Callback de mapa final
@app.callback(
    Output('fig_top_rout', 'figure'),
    [Input('selection_type_2', 'value')])
def map_top_pas(top15):
    lat22 = latitudesbase[top15]
    lon22 = longitudesbase[top15]
    fig_top_rout = go.Figure()
    fig_top_rout.add_trace(go.Scattermapbox(
        mode="markers+lines",
        lon=lon22,
        lat=lat22,
        marker={'size': 10}))

    fig_top_rout.update_layout(
        margin={'l':0, 't': 0, 'b': 0, 'r': 0},
        mapbox={'center': {'lon': -74, 'lat': 4},'style': "carto-darkmatter",'center': {'lon': -74, 'lat': 4},'zoom': 4})

    return fig_top_rout

# Query sobre top rutas
def top_rutas_pasajeros_year(numtop, start_date2, end_date2, coordcentrales):
    cur1 = conn.cursor()
    query1 = "WITH tabla1 as(SELECT CONCAT(municipio_origen_ruta, '-', municipio_destino_ruta) as ruta, pasajeros " \
             "FROM pasajeros_origen_destino_ultima3 " \
             "WHERE fecha_despacho BETWEEN TO_DATE(CAST('" + start_date2 + "' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('" + end_date2 + "' AS VARCHAR),'YYYY-MM-DD'))" \
                                                                                                                                          "SELECT tabla1.ruta, SUM(tabla1.pasajeros) as totpas " \
                                                                                                                                          "FROM tabla1 GROUP BY tabla1.ruta ORDER BY totpas DESC LIMIT " + numtop + ";"
    cur1.execute(query1)
    query_results_pasajeros = cur1.fetchall()
    cur1.close()

    pasajerosdf = pd.DataFrame(query_results_pasajeros, columns=['ruta',
                                                                 'Total_Passengers'])
    pasajerosdf[['cod_origen', 'cod_destino']] = pasajerosdf['ruta'].str.split('-', 1, expand=True).astype(int)
    pasajerosdf["nom_origen"] = pasajerosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
    pasajerosdf["nom_destino"] = pasajerosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
    pasajerosdf["lon_origen"] = pasajerosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
    pasajerosdf["lat_origen"] = pasajerosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
    pasajerosdf["lon_destino"] = pasajerosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
    pasajerosdf["lat_destino"] = pasajerosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
    pasajerosdf["Origin-Destination"] = pasajerosdf["nom_origen"] + "-" + pasajerosdf["nom_destino"]
    return pasajerosdf

# Query sobre top despachos
def top_rutas_despachos_year(numtop, start_date2, end_date2, coordcentrales):
    cur2 = conn.cursor()
    query2 = "WITH tabla1 as(SELECT CONCAT(municipio_origen_ruta, '-', municipio_destino_ruta) as ruta, despachos " \
             "FROM pasajeros_origen_destino_ultima3 " \
             "WHERE fecha_despacho BETWEEN TO_DATE(CAST('" + start_date2 + "' AS VARCHAR),'YYYY-MM-DD') AND TO_DATE(CAST('" + end_date2 + "' AS VARCHAR),'YYYY-MM-DD'))" \
                                                                                                                                          "SELECT tabla1.ruta, SUM(tabla1.despachos) as totdes " \
                                                                                                                                          "FROM tabla1 GROUP BY tabla1.ruta ORDER BY totdes DESC LIMIT " + numtop + ";"
    cur2.execute(query2)
    query_results_despachos = cur2.fetchall()
    cur2.close()
    despachosdf = pd.DataFrame(query_results_despachos, columns=['ruta',
                                                                 'Total of dispatches'])
    despachosdf[['cod_origen', 'cod_destino']] = despachosdf['ruta'].str.split('-', 1, expand=True).astype(int)
    despachosdf["nom_origen"] = despachosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
    despachosdf["nom_destino"] = despachosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['municipio'])
    despachosdf["lon_origen"] = despachosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
    despachosdf["lat_origen"] = despachosdf["cod_origen"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
    despachosdf["lon_destino"] = despachosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['longitud_centro_municipio'])
    despachosdf["lat_destino"] = despachosdf["cod_destino"].map(
        coordcentrales.set_index('codigo_dane_del_municipio')['latitud_centro_municipio'])
    despachosdf["Origin-Destination"] = despachosdf["nom_origen"] + "-" + despachosdf["nom_destino"]
    return despachosdf



# Informacion
#%%


figures_info = {
    "Bar-chart": "Select the type of aggregation (by passengers or dispatches), the number of top routes and the dates of the analysis.",
    "Routes-maps":"Next, you can analyze the top 15 routes by passengers and the terminals on the route with the number of boarding passengers from 01-08-2019 to 06-07-2021.",
    "Routes-specific":"If you want information about a specific route, select the origin in the left dropdown, select one of the possible destinations in the right dropbox, and last, click on the search button to obtain information about the route."
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



# Elementos del layout


banner = html.Div([html.Div(html.H1('Routes', style={'color': 'white'}),style={'text-align': 'center', 'max-width': '1140px', 'margin-right': 'auto','margin-left': 'auto'})],
                 style={'background-image': "url(/assets/rutas/Banner_routes2.jpg)", 'backgroundPosition': 'center center','backgroundSize': 'cover', "height": "30vh", 'padding-top': '75px', 'margin-bottom': '12px'})

subtitulo = html.Div([html.P('On this page, you will be able to obtain information and visualize the routes which communicate the Colombian regions. You can get more information about each graph by entering the upper right button')],
            style={'text-align': 'left','margin-top': '5vh','color':'grey'})




parameter_buttons = html.Div([dbc.Row(popovers["Bar-chart"],justify='end'),
                    dbc.Row([html.Div(html.H5('Parameter selection',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                    dbc.Row([dbc.Col(drop_type,width=2, align='center',style={'padding-right': '0px'}),
                    dbc.Col(input_top,width=1, align='center',style={'padding-right': '0px'}),
                    dbc.Col(calendar2,width=4, align='center',style={'padding-left': '3rem'}),
                    dbc.Col(dbc.Button(id="loading-button", n_clicks=0, children=["Analyze"]),width=2,align='center')],justify="center")]
                    ,style={"height": "10vh",'padding-top': '4px','margin-bottom': '6vh'})


chart_bar = html.Div([dbc.Spinner(children=[dcc.Graph(id="the_graph")], size="lg", color="primary", type="border",fullscreen=False)],
                    style={'margin-top': '3vh'})


routs_map = html.Div([dbc.Row(popovers["Routes-maps"],justify='end'),
                    dbc.Row([dbc.Col(html.Div([dbc.Row([html.Div(html.H5('Routes of interest',style={'color':'gray'}),style={'text-align': 'center'})],justify='center'),
                                            dbc.Row(radio_item_routes_for_map,justify='center')]), width={"size": 3}),
                            dbc.Col(html.Div([dbc.Row([html.Div(html.H5('Route map',style={'color':'gray'}),style={'text-align': 'center'})],justify='center'),
                                                dcc.Graph(id='fig_top_rout')]), width={"size": 4}),
                            dbc.Col(html.Div([dbc.Row([html.Div(html.H5('Information of route',style={'color':'gray'}),style={'text-align': 'center'})],justify='center'),
                                            dbc.Row(id='table1',justify='center')]),width={"size": 5})],justify="center")],style={'margin-top': '5vh'})


parameter_buttons_2 = html.Div([dbc.Row(popovers["Routes-specific"],justify='end'),
                    dbc.Row([html.Div(html.H5('Origin and destination of the route',style={'color':'gray'}),style={'text-align': 'center'})],justify="center"),
                    dbc.Row([dbc.Col(drop_type_origin,width=2, align='center',style={'padding-right': '0px'}),
                    dbc.Col(dcc.Dropdown(id='drop_destination'),width=2, align='center'),
                    dbc.Col(dbc.Button(id="loading-button2", n_clicks=0, children=["Analyze"]),width=2,align='center')],justify="center")]
                    ,style={"height": "10vh",'padding-top': '4px','margin-bottom': '6vh'})


routes_maps_2 = html.Div([dbc.Row([dbc.Col(html.Div([dbc.Row([html.Div(html.H5('Information of route',style={'color':'gray'}),style={'text-align': 'center'})],justify='center'),
                                            dbc.Row(id='table2',justify='center')]),width={"size": 5}),
                        dbc.Col(html.Div([dbc.Row([html.Div(html.H5('Route map',style={'color':'gray'}),style={'text-align': 'center'})],justify='center'),
                                        dbc.Spinner(children=[dcc.Graph(id="fig_scatter")], size="lg", color="primary", type="border",fullscreen=False)]), width={"size": 5})
                        ],justify="center")
                        ])


# ---------------------------------------------------------------
# Creación del layout de la página
layout = html.Div([
    html.Div([banner,
            subtitulo,
            parameter_buttons,
            chart_bar,
            routs_map,
            parameter_buttons_2,
            routes_maps_2,
    footer,
    ])])