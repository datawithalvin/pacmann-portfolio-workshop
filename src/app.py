# -------- Import libraries ---------
from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# -------- Load dataset ---------
filepath = "datasets/preprocessed-data.csv"
main_df = pd.read_csv(filepath, parse_dates=["acq_date"])

# -------- Build components ---------

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server


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


# -------- Callback (placeholder) ---------
@app.callback(
    Output("barfig1", "figure"),
    Output("barfig2", "figure"),
    Output("mapfig", "figure"),
    Output("linefig", "figure"),
    Output("barfig3", "figure"),
    Input(dropdown, "value")
)
def update_dashboard(selected_year):
    dff = main_df[main_df["year"] == selected_year]

        # Create placeholder figures
    def create_placeholder_figures():
        barfig1 = create_top10_city(dff)
        barfig2 = create_top10_province(dff)
        mapfig = create_density_map(dff)
        linefig = create_line_chart(dff)
        barfig3 = create_bar_chart_confidence(dff)

        return barfig1, barfig2, mapfig, linefig, barfig3
    
    def create_density_map(dataframe):
        # Define hover data
        hover_data = {
            'acq_date': True, 'frp': True, 'province': True,
            'longitude': False, 'latitude': False
        }
        
        # Create density map figure
        fig = px.density_mapbox(
            dataframe, lat='latitude', lon='longitude',
            z='frp', radius=5, center=dict(lat=-2.5, lon=118),
            zoom=3.8, hover_name='regency_city',
            hover_data=hover_data, color_continuous_scale='matter_r',
            mapbox_style='carto-darkmatter', template='plotly_dark'
        )
        
        # Update figure layout
        fig.update_layout(
            width=1000, height=475,
            margin=dict(r=1, t=1, l=1, b=1), plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        
        # Update colorbar location and orientation
        fig.update_coloraxes(
            showscale=True,
            colorbar=dict(
                len=0.3, yanchor='bottom', y=0,
                xanchor='center',
                thickness=10, title='Fire Radiative Power',
                orientation='h', title_side="top")
        )
        
        return fig
    
    def create_top10_city(dataframe):
        grouped = dataframe.groupby(["regency_city"]).agg(
            total_fires = ("frp", "count")
            )

        grouped = grouped.sort_values(by="total_fires", ascending=False).reset_index()
        grouped = grouped.head(10)

        fig = px.bar(grouped, x="total_fires", y="regency_city", orientation="h", text="total_fires",
                        labels={"regency_city":"", "total_fires":"Jumlah Titik Api"}, template="plotly_dark")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        fig.update_layout(autosize=True,width=500,height=475)
        fig.update_layout(title="10 Kabupaten/Kota Dengan Titik Api Terbanyak",title_font_size=14)
        # fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
        # fig.update_yaxes(tickfont_size=8)
        fig.update_traces(marker_color='indianred')
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_xaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    

        return fig
    
    def create_top10_province(dataframe):
        grouped = dataframe.groupby(["province"]).agg(
            total_fires = ("frp", "count")
            )

        grouped = grouped.sort_values(by="total_fires", ascending=False).reset_index()
        grouped = grouped.head(10)

        fig = px.bar(grouped, x="total_fires", y="province", orientation="h", text="total_fires",
                        labels={"province":"", "total_fires":"Jumlah Titik Api"}, template="plotly_dark")

        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        fig.update_layout(autosize=True,width=500,height=400)
        fig.update_layout(title="10 Provinsi Dengan Titik Api Terbanyak",title_font_size=14)
        # fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
        # fig.update_yaxes(tickfont_size=8)
        fig.update_traces(marker_color='indianred')
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_xaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        

        return fig
    
    def create_line_chart(dff):
        line_df = dff

        # Upsample to daily frequency and count the number of fires in each day
        line_df = line_df.resample('D', on='acq_date')['frp'].count()

        fig = px.line(line_df, x=line_df.index, y=line_df.values,
                labels={"y":"<b>Jumlah Titik Api</b>", "acq_date":""},template="plotly_dark")

        fig.update_layout(autosize=True,width=700,height=400)
    #     fig.update_layout(margin={"r":0,"t":1,"l":0,"b":0})
        fig.update_layout(title="Jumlah Titik Api Harian yang Terdeteksi", title_font_size=16)
        fig.update_traces(line_color='indianred')
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_yaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

        return fig
    
    def create_bar_chart_confidence(dff):
        # groupby confidence
        percentage_df = dff.groupby(["confidence"])["frp"].agg("count")
        percentage_df = percentage_df.reset_index()
        percentage_df = percentage_df.rename(columns={"frp":"counts"})
        percentage_df["percent"] = round((percentage_df["counts"] / percentage_df["counts"].sum()) * 100, 2)

        # sort by confidence level
        percentage_df = percentage_df.sort_values(by=['confidence'])

        # build bar chart graph
        fig = px.bar(percentage_df, x='confidence', y='percent', text='percent',
                        color_discrete_sequence=['indianred'],
                        template="plotly_dark")

        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_layout(autosize=True, width=450, height=400)
        fig.update_layout(title="Proporsi Tingkat Confidence Api", title_font_size=14)
        fig.update_xaxes(title='Tingkat Confidence')
        fig.update_yaxes(title='Persentase')
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside', textfont_size=11)

        return fig



    # Create and update the figures based on the selected year
    barfig1, barfig2, mapfig, linefig, barfig3 = create_placeholder_figures()

    return barfig1, barfig2, mapfig, linefig, barfig3

# -------- Run app ---------
if __name__ == '__main__':
    app.run_server(debug=True)

   
