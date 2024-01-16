""""sumary_line
This is file render analylics page
This page contains cards and links to analylicals pages. 

Keyword arguments:
argument -- description
Return: return_description
"""


from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.H1 import H1

# call another file of project
from pages.footer import footer

# this is a plus (+) icon to see more button on each card
plus_icon = html.Span(["", html.I(className="fa fa-plus", style={"margin-left": "6px"})])



def create_card(title, href, image_path):
    """"This function create a card with photo, link and title
    
    Keyword arguments: 
    argument -- title of card, link to another page, and path_to_image
    Return: Return a card that exteds from dash_bootstrap_components.Card
    """
    return dbc.Card(
        [
            # locate image
            dbc.CardImg(src=image_path, top=True),
            dbc.CardBody(
                [
                    # title of cards
                    dbc.Row([
                        html.H4(title, className="card-title"),
                    ], justify = 'center'),
                    # button of link
                    dbc.Row([
                        dbc.Button(["See More", plus_icon, ], color="primary", href=href),
                    ], justify = 'center'),
                ]
            ),
        ],
        # set style to card
        style={"width": "20rem", "margin": "1rem"},
    )

# generate all cards
card_bus = create_card("Routes analysis", "/routes", "assets/buses/pexels-chut-foto-996954.jpg")
card_terminal = create_card("Bus terminal analysis", "/terminals", "assets/buses/pexels-polina-kovaleva-7664653.jpg")
card_one_terminal = create_card("Specific terminal analysis", "/terminals_specific", "assets/buses/pexels-quentin-ecrepont-2275290.jpg")

card_passenger_prediction_terminals = create_card("Passenger prediction in terminals", "/terminal_forecasting", "assets/buses/terminal.jpg")
card_passenger_prediction_routes = create_card("Passenger prediction in routes", "/routs_forecasting", "assets/buses/bus-690508_960_720.jpg")
# card_bus = create_card(title, href, image_path)


# this is the structure of analitucs page,
# cards and page components are going to be added here!
layout = html.Div(
    [
        html.Div([
            html.Div(
                html.H1('Analytics',style={'color':'white'}),
                style={'text-align': 'center','max-width': '1140px','margin-right': 'auto','margin-left': 'auto'})
                ],
            style={'background-image': "url(/assets/home/barner_analytics.jpg)",'backgroundPosition': 'center center',
                   'backgroundSize': 'cover',"height": "30vh",'padding-top': '75px','margin-bottom': '12px'}),
        html.Div(
            [
                # one row of three cards
                dbc.Row(
                    [
                        card_terminal,
                        card_one_terminal,
                        card_bus,
                    ],
                    justify = 'center',
                    style={"margin-bottom": "2rem"},
                ),
                # one row of two cards
                dbc.Row(
                    [
                        card_passenger_prediction_terminals,
                        card_passenger_prediction_routes,
                    ], 
                    justify = 'center',
                    style={"margin-bottom": "2rem"},
                ),
            ],
        ),
        # add footer
        footer
    ]
)
