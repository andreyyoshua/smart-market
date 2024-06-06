import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

st.header("You can explore more data from all provinces in indonesia here", divider="rainbow")
st.text("")

compiled_data = pd.read_csv('market_potential.csv')
st.dataframe(compiled_data)


chart_data = pd.DataFrame(
   np.random.randn(1000, 2) / [10, 10] + [0.0150345, 119.707791],
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
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
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