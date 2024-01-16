"""
    This file contains the redirection of the pages.
    
"""

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages.home import home
from pages.analysis.terminals import terminals_analysis
from pages.analysis.routes import routes_analysis
from pages.analysis.terminals import terminals_analysis_specific
from pages.Predicciones import Predicciones_rutas
from pages.Predicciones import Predicciones_terminales
from pages.contact import contact
from pages.analitics import analitics

@app.callback(
  Output("page-content", "children"), 
  Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == '/':
        return home.layout
    elif pathname == '/terminals':
        return terminals_analysis.layout
    elif pathname == '/routes':
        return routes_analysis.layout
    elif pathname == '/terminals_specific':
        return terminals_analysis_specific.layout        
    elif pathname == '/contact':
        return contact.layout
    elif pathname == '/analysis':
        return analitics.layout     
    elif pathname == '/terminal_forecasting':
        return Predicciones_terminales.layout
    elif pathname == '/routs_forecasting':
        return Predicciones_rutas.layout
    
    
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )