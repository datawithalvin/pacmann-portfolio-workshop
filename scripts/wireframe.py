# -------- Import libraries ---------
from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# -------- Load dataset ---------
filepath = "../datasets/preprocessed-data.csv"
main_df = pd.read_csv(filepath, parse_dates=["acq_date"])

# -------- Build components ---------

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

mytitle = dcc.Markdown("Dashboard Pemantauan Titik Api di Indonesia")

description = """Dashboard ini menampilkan titik api yang diamati dan terdeteksi oleh Visible Infrared Imaging Radiometer Suite, 
            atau VIIRS, sepanjang tahun 2020 hingga 2023. Instrumen VIIRS terbang pada satelit pengorbit kutub 
            Suomi-NPP dan NOAA-20 dari Joint Polar Satellite System. Instrumen pada satelit pengorbit kutub biasanya mengamati kebakaran 
            liar di lokasi tertentu beberapa kali sehari saat mengorbit Bumi dari kutub ke kutub. VIIRS mendeteksi titik panas dengan resolusi 
            375 meter per piksel, yang berarti dapat mendeteksi kebakaran yang lebih kecil dan berintensitas rendah dibandingkan satelit 
            pengamatan kebakaran lainnya. VIIRS juga menyediakan kemampuan deteksi kebakaran malam hari melalui Day-Night Band-nya, 
            yang dapat mengukur cahaya tampak intensitas rendah yang dipancarkan oleh kebakaran kecil dan baru."""

dropdown = dcc.Dropdown(options=[{"label": str(year), "value": year} for year in main_df["year"].unique()],
                        value=2023,  # initial value displayed when page first loads
                        clearable=False)

app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3(mytitle),
                html.Label("Pilih Tahun"),
                dropdown,
                html.Hr(),
                html.P(description, style={'text-align': 'justify'}),

            ], width=2),
            dbc.Col([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="barfig1"), width=12, style={"height": "50%"})
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="barfig2"), width=12, style={"height": "50%"})
                ]),
            ], width=3),
            dbc.Col([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="mapfig"), width=12, style={"height": "70%"})
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure={}, id="linefig"), width=10, style={"height": "30%"}),
                    dbc.Col(dcc.Graph(figure={}, id="barfig3"), width=2, style={"height": "30%"})
                ]),
            ], width=5)
        ]),
    ],
    fluid=True)

# -------- Run app ---------
if __name__ == '__main__':
    app.run_server(debug=True, port=8054)

   
