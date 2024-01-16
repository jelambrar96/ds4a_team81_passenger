"""
layout.py

- this file contains the view structure of all pages-
- contains sidebar, navbar and status-bar
- 
"""

# dependences from dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "1rem",
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#343a40",
    "color": "white",
}

# side bar take this style when is hidden
SIDEBAR_HIDEN = {
    "position": "fixed",
    "top": "1rem",
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#343a40",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "4rem 1rem",
    "background-color": "white",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "4rem 1rem",
    "background-color": "white",
}


# this is a sidebar 
navbar = dbc.NavbarSimple(
    children=[
        dbc.Button("Menu", outline=True, color="light", className="mr-1", id="btn_sidebar"),
    ],
    color="dark",
    dark=True,
    links_left=True,
    fluid=True,
    fixed="top", # this block the sidebar on the top of page
)


# this is the sidebar
sidebar = html.Div(
    [
        html.P("Menu"),
        # each navlink is a link to anoher page
        dbc.Nav(
            [
                dbc.NavLink([html.Span(['',html.I(className="fa fa-home")]),"  Home"], href="/", active="exact"),
                dbc.NavLink([html.Span(['',html.I(className="fa fa-line-chart")]),"  Analytics"], href="/analysis", active="exact"),
                dbc.NavLink("Terminals", href="/terminals", active="exact",style={'padding-left':'2rem'}),
                dbc.NavLink("Specific terminals", href="/terminals_specific", active="exact",style={'padding-left':'2rem'}),
                dbc.NavLink("Routes", href="/routes", active="exact",style={'padding-left':'2rem'}),
                dbc.NavLink("Terminal forecasting", href="/terminal_forecasting", active="exact",style={'padding-left':'2rem'}),
                dbc.NavLink("Routes forecasting", href="/routs_forecasting", active="exact",style={'padding-left':'2rem'}),
                dbc.NavLink([html.Span(['',html.I(className="fa fa-phone")]),"  Contact"], href="/contact", active="exact"), 
            ],
            vertical=True,
            pills=True,
        ),
    html.Div(html.Img(src='/assets/logos/Logo-Driven-by-Data.svg',width="240rem"), style={'padding-top': 30})
    ],
    id="sidebar",
    # apply sidebar style
    style=SIDEBAR_STYLE,
)

content = html.Div(

    id="page-content",
    style=CONTENT_STYLE)

layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)

