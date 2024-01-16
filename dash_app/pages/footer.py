""" 
footer.py contains logos of mintic ds41 and u-movil
"""

# load dependences
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

 #create cards with logos
card_mintic = dbc.Card([
    dbc.CardBody([
        dbc.CardImg(src="assets/logos/cropped-UMOVIL-balls-text.png",
                    top=True, style={"width": "12rem", "height": "5rem", "padding": "1rem", "border": "0px"}),
    ])
])
card_ds4a = dbc.Card([
    dbc.CardBody([
        dbc.CardImg(src="assets/logos/logo_ds1.svg", top=True,
                    style={"width": "12rem", "height": "5rem","padding": "1rem"}),
    ])
])
card_umovil = dbc.Card([
    dbc.CardBody([
        dbc.CardImg(src="assets/logos/logo_mintic.png", top=True,
                    style={"width": "12rem", "height": "5rem","padding": "1rem"}),
    ])
])

# create footer componen and add cards
footer = html.Div([
    html.Hr(),
    dbc.Row([
        dbc.Col(card_mintic),
        dbc.Col(card_ds4a),
        dbc.Col(card_umovil),
    ]),
],
style={"margin": "2rem", "bottom": 0}
)
