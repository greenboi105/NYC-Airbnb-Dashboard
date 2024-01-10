from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Bootstrap stylesheet file
BS = 'https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/cyborg/bootstrap.min.css'
app = Dash(__name__, external_stylesheets=[BS])
app.title = "NYC Airbnb Analytics"

# How heroku determines what to execute
server = app.server

# Generate API key for maps
API_KEY = 'pk.eyJ1IjoiZ3JlZW5ib2kxMDUiLCJhIjoiY2xlMGo4aGZ0MDlyNTN2cWtlYnAyeTduNCJ9.22dna4Wm_VmFU1OKBXCFgQ'
px.set_mapbox_access_token(API_KEY)

# Load data into CSV - we do so using pandas ability to read from a hosted raw CSV file
url = 'https://raw.githubusercontent.com/greenboi105/python_nyc/main/AB_NYC_2019.csv'

# The original dataset
airbnb = pd.read_csv(url)

# Filtering for only prices where the price is below 500 (this is done to remove extreme outliers)
prices = airbnb[airbnb['price'] < 500]

# Determine the boroughs of NYC 
regions = prices["neighbourhood_group"].sort_values().unique()

# Processing to filter only the DataFrame with the most active host IDs
top_host = airbnb.host_id.value_counts().head(10)
top_host_df=pd.DataFrame(top_host)
top_host_df.reset_index(inplace=True)
top_host_df.rename(columns={'host_id':'Host_ID', 'count':'P_Count'}, inplace=True)

avg_availability = airbnb.groupby(['neighbourhood_group'])['availability_365'].mean()
avg_availability_df = pd.DataFrame(avg_availability).reset_index()

# Plots
neighbourhood_distribution = px.scatter_mapbox(prices, lon='longitude', lat='latitude', color='price', template="plotly_dark", title="Prices in the Five Boroughs", height=700, color_continuous_scale="portland").update(layout=dict(title=dict(x=0.5)))

neighbourhood_group = px.scatter_mapbox(airbnb, lon='longitude', lat='latitude', color='availability_365', title="Availability in The Five Boroughs", template="plotly_dark", height=700, color_continuous_scale="delta", labels=dict(availability_365="Days Available Per Year")).update(layout=dict(title=dict(x=0.5)))

neighbourhood_pricing = px.box(airbnb, x="room_type", y="price", color="neighbourhood_group", title="Room Type and Neighbourhood Pricing", template="plotly_dark", height=700).update(layout=dict(title=dict(x=0.5)))

price_distribution = px.histogram(prices, x="price", title="Distribution of Airbnb Prices in NYC", color="neighbourhood_group", marginal='box', template="plotly_dark", height=700).update(layout=dict(title=dict(x=0.5)))

availability_plot = px.bar(avg_availability_df, color="neighbourhood_group", x="neighbourhood_group", y="availability_365", template="plotly_dark")

colors = {
    'background': '#111111',
    'text': '#5A5A5A'
}

prompt_description = """
    Analysis of factors influencing prices of Airbnb rentals in New York City. New York City is one of the most global cities in the world, and attracts tenants from all corners of the globe.
"""

"""
The structure of the app is a tree - this is where we display the plots generated from Plotly using Dash.

We have the original heading text, then the figures with which we want to display information.
"""

app.layout = html.Div(children=[
    html.Div(
        children=[
    
        html.H1(children='New York City Airbnb Prices', style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

        html.H4(children='Analysis of NYC Airbnb Prices: Designed by Jerry Y. 💻', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        html.P(children=prompt_description, style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        ], className="header",
    ),

    dcc.Graph(
        id='price-chart',
        figure=neighbourhood_distribution
    ),

    dcc.Graph(
        id='neighourhood-rooms',
        figure=neighbourhood_group
    ),

    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Region", className="menu-location"),
                    dcc.Dropdown(
                        id="region-filter",
                        options= ["Any"] + [str(region) for region in regions],
                        value="Any",
                    ),
                ]
            )
        ],
        className="menu",
        ),

    dcc.Graph(
        id='apartment-distribution',
    ),

    dcc.Graph(
        id="neighbourhood_roomtype",
        figure=neighbourhood_pricing
    ),

    dcc.Graph(
        id="price-distribution",
        figure=price_distribution
    ),

    dcc.Graph(
        id="availability-plot",
        figure=availability_plot
    )
])

@app.callback(
    Output("apartment-distribution", "figure"),
    Input("region-filter", "value"),
)

def update_charts(region):
    """
    Function to update chart based on filtering on borough selected using dropdown menu.
    """
    if region == "Any": return px.scatter(airbnb, x='longitude', y='latitude', color='room_type', title="Airbnb Distribution in NYC", template="plotly_dark", height=700).update(layout=dict(title=dict(x=0.5))).update_yaxes(scaleanchor="x", scaleratio=1,)

    filtered_data = airbnb[airbnb['neighbourhood_group'] == region]

    region_plot = px.scatter(filtered_data, x='longitude', y='latitude', color='room_type', title="Airbnb Distribution in NYC", template="plotly_dark", height=700).update(layout=dict(title=dict(x=0.5))).update_yaxes(scaleanchor="x", scaleratio=1,)

    return region_plot

if __name__ == '__main__':
    app.run_server(debug=True)

    