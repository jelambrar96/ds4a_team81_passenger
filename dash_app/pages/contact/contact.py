""""This file render contacts page, 
this page contains information about developer of this projects
and url lo mail and linkedin

Keyword arguments:
argument -- description
Return: return_description
"""

# dash dependences
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.P import P

# import footer component
from pages.footer import footer

# email and linkedin icon
linkedin_icon = html.Span(["", html.I(className="fa fa-linkedin")])
email_icon = html.Span(["", html.I(className="fas fa-envelope")])

# info about each developer
contact_images = ["assets/contact/victor.jpeg","assets/contact/jelambrar.jpg","assets/contact/andres.jpeg","assets/contact/juan.jpeg","assets/contact/julian.jpeg"]
contact_names = ["Victor González","Jorge Lambraño","Andrés Díaz","Juan Echeverri","Julian Espejo"]
contact_titles = ['MSc. Probability and Statistics','Electronic Engineer','Systems & Computer Engineering Student',"Computer Science's Student",'PhD Student in Logistics and SCM']

contact_linkedin = ["http://www.linkedin.com/in/victor-glz",
                    "https://www.linkedin.com/in/jorge-lambra%C3%B1o-a64662157/",
                    "https://www.linkedin.com/in/andiazo/",
                    "https://www.linkedin.com/in/juan-david-echeverri-villada-533965196/",
                    "https://www.linkedin.com/in/julian-alberto-espejo-diaz-087563129/"]

contact_email = [f'mailto:{email}' for email in ["gonzalezvmruiz@gmail.com",
                                                 "jelambrar@gmail.com",
                                                 "andresdavid220@gmail.com",
                                                 "juanda20202@hotmail.com",
                                                 "julianes123@gmail.com"]]

# create cards
# we are using a for in a line
# y = [ for item in list]
contact_cards = [dbc.Card(
        [
            dbc.CardImg(src=image, top=True, className= 'border border-light rounded-circle', style = {'color':'grey','border-width':'5px'}),
            dbc.CardBody(
                [
                    html.H4(name, className="card-title ml", style = {'text-align':'center'}),
                    html.H5(title, className="card-title ml", style = {'color':'grey','font-size': '1em','text-align':'center'}),
                    html.Div([
                        dbc.Row([
                            dbc.Button(linkedin_icon, href=linkedin, target="_blank", className = "btn btn-dark btn-circle btn-md mr-2"),
                            dbc.Button(email_icon, href=email, target="_blank", className = "btn btn-dark btn-circle btn-md ml-2")
                        ], justify = 'center'),
                    ])
                ]
            ),
        ],
        style={"width": "18rem"},
    )
for image,name,title,linkedin,email in zip(contact_images,contact_names,contact_titles,contact_linkedin,contact_email)]


# set cards on two columns and add footer
cards_layout =  html.Div([
                dbc.Row([dbc.Col(contact_cards[0],width = 4),dbc.Col(contact_cards[4],width = 4),dbc.Col(contact_cards[2],width = 4)], justify = 'center'),
                dbc.Row([dbc.Col(contact_cards[3],width = 4),dbc.Col(contact_cards[1],width = 4)], justify = 'center')
                ])
layout = html.Div([
                html.H1('Contact',
                    style={'text-align':'center'}),
                cards_layout,
                footer
                ]
                )



