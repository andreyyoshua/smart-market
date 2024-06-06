import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import geopandas as gpd
import requests

st.header("You can explore more data from all provinces in indonesia here", divider="rainbow")
st.text("")

compiled_data = pd.read_csv('market_potential.csv')
st.dataframe(compiled_data)

geometries_df = pd.read_csv('geometries_2.csv')
geometries_df = geometries_df.T
geometries_df.columns = ['geometry']
geometries_df['geometry'] = gpd.GeoSeries.from_wkt(geometries_df['geometry'])
gdf = gpd.GeoDataFrame(geometries_df, geometry='geometry')
gdf["name"] = gdf.index
coords = []
for col in gdf["geometry"].centroid:
    coords.append([col.y, col.x])

# chart_data = pd.DataFrame(
#    np.random.randn(1000, 2) / [10, 10] + [0.0150345, 119.707791],
#    columns=['lat', 'lon']
# )
chart_data = pd.DataFrame(
   coords,
   columns=['lat', 'lon']
)
# chart_data

selected_province = st.selectbox(
    "Select data you want to see on map",
    compiled_data.columns[1:]
)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=0.0150345,
        longitude=119.707791,
        zoom=3.3,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=chart_data,
           get_position='[lon, lat]',
            auto_highlight=True,
            elevation_scale=100,
            radius=20000,
            pickable=True,
            elevation_range=[0, 3000],
            extruded=True,
            coverage=1
        #    radius=200,
        #    elevation_scale=4,
        #    elevation_range=[0, 1000],
        #    pickable=True,
        #    extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))