import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
import time
import base64

st.set_page_config(
    page_title="Hello",
    page_icon="🤖",
    layout='wide'
)

def construct_df_from_datacontent(url):
    data = requests.get(url).json()
    
    vervar = sorted(data["vervar"], key=lambda x: x['val'])
    val = data["var"][0]["val"]
    turvar = data["turvar"]
    tahun = data["tahun"]
    turtahun = data["turtahun"]
    
    datacontent = data["datacontent"]
    label = data['var'][0]['label']
    columns = [f"{tv['label'] + ' ' if tv['val'] != 0 else ''}{t['label']}{' ' + tt['label'] if tt['val'] != 0 else ''}" for tv in turvar for t in tahun for tt in turtahun]
    
    # Construct { 'label': 'Province', 'index': 0, 'values': [] } as much as vervar
    d = [{'label': v['label'], 'index': v_idx, 'values': []} for (v_idx, v) in enumerate(vervar)]
    
    for (v_idx, v) in enumerate(vervar):
        for tv in turvar:
            for t in tahun:
                for tt in turtahun:
                    # 9999   1451 0     115   0
                    # vervar+val+turvar+tahun+turtahun
                    key = str(v["val"]) + str(val) + str(tv["val"]) + str(t["val"]) + str(tt["val"])
                    
                    next(x for x in d if x['index'] == v_idx)['values'].append(datacontent[key] if key in datacontent else None)
    
    
    values = [x['values'] for x in d]
    indices = [x['label'] for x in d]
    df = pd.DataFrame(values, index=indices, columns=columns)
    
    # columns_without_tahunan = [x for x in columns if "Tahunan" not in x]
    # df = df[columns_without_tahunan].T
    df = df.T
    return df


compiled_data = pd.read_csv('clustered_market_potential.csv')
# compiled_data

st.write("# Welcome to BusinessVision AI! 👋🤖")
LOGO_IMAGE = "biissa.png"
st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        # font-weight:700 !important;
        # font-size:50px !important;
        # color: #f9a01b !important;
        # padding-top: 75px !important;
        margin-right: 8px;
    }
    .logo-img {
        # float:right;
        width: 60px;
        height: 30px
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <div class="container">
        <p class="logo-text">By</p>
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
    </div>
    """,
    unsafe_allow_html=True
)


st.text("")
st.text("")


geometries_df = pd.read_csv('geometries_2.csv')
geometries_df = geometries_df.T
geometries_df.columns = ['geometry']
geometries_df['geometry'] = gpd.GeoSeries.from_wkt(geometries_df['geometry'])


gdf = gpd.GeoDataFrame(geometries_df, geometry='geometry', crs="4326")
gdf["name"] = gdf.index
colors = []
cluster_to_colors = []
for province in gdf['name']:
    row = compiled_data[compiled_data['Provinsi'] == province.upper()]
    colors.append(row['color'].iloc[0])
    if any(x["cluster"] == int(row['Cluster'].iloc[0].replace('Cluster ', '')) for x in cluster_to_colors) is False:
        cluster_to_colors.append({
            "cluster": int(row['Cluster'].iloc[0].replace('Cluster ', '')),
            "color": row['color'].iloc[0]
        })
gdf["color"] = colors
gdf.reset_index(drop=True, inplace=True)


has_finished = False

'We can help you to be succeed in your business'
'To start, let us know more about your preference'

with st.form("my_form"):
    selected_province = st.selectbox(
        "Please choose your preference area to start your business",
        gdf['name']
    )

    business_per_sectors = construct_df_from_datacontent("https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/447/key/452454d38b732ad01300c6c6c35183e1")
    business_per_sectors.columns = [''.join([i for i in x if not i.isdigit()]).strip() for x in business_per_sectors.columns]

    selected_industry = st.selectbox('What industry do you prefer', business_per_sectors.columns[0:-1])

    if st.form_submit_button("Submit"):
        selected_province_data = compiled_data[compiled_data.columns[:-1]]
        selected_province_data = selected_province_data[selected_province_data["Provinsi"] == selected_province.upper()]


        t = st.empty()
        text = f"""Your option to start {selected_industry} business at {selected_province} is a good choice. With
        """
        selected_data = selected_province_data[[
            "Income Average per hour",
            "GDP",
            "SD / Sederajat",
            "Digital Wallet Adoption Rate",
            "SMP / Sederajat",
            "Micro Business",
            "Population Density (per KM)",
            "Jumlah Bencana Alam",
            "Household Consumptions",
            "Pasar Tradisional"
        ]]
        for col in selected_data:
            text += f"\n{selected_data[col][selected_data.index[0]]} {col},"
        text = text[:-1]
        text += f"\n\nIt's a good place to start your {selected_industry} business at {selected_province}"

        for i in range(len(text) + 1):
            t.text("%s..." % text[0:i])
            time.sleep(0.005)

        "See below for the specific data"
        selected_province_data.reset_index(drop=True, inplace=True)
        selected_province_data

        st.caption("Based on 2023 Data: BPS, Kementerian Keuangan, Kemenhub")

        st.text("")
        st.text("")
        st.text("")
        st.write("If you're still open for other area, here's i can show you the other best area where your business can start")

        # st.button("Get your business? Let's Start", type="primary")
        if selected_province is not None:
            m = folium.Map(location=[-2.8971724, 119.1074087], zoom_start=4.3)
            g = folium.GeoJson(
                gdf,
                style_function=lambda x: {
                    'fillColor': x["properties"]["color"],
                    "color": "black",
                    "fillOpacity": 0.4,
                    "weight": 1,
                }
                # tooltip=tooltip,
                # popup=popup,
            ).add_to(m)

            st_data = st_folium(m, width=1000, height=500)

            cluster_to_colors = sorted(cluster_to_colors, key=lambda x: x['cluster'])
            cluster_to_potentials = {
                4: 'Very Low Potential ',
                3: 'Low Potential',
                2: 'Very High Potential',
                1: 'High potential',
                0: 'Medium Potential'
            }
            for cluster_to_color in cluster_to_colors:
                st.components.v1.html(
                    f"""
                    <div style="display:flex; flex-direction:row">
                        <div style="background-color:white;width:20px; height:20px; margin-right:8px;">
                            <div style="background-color:{cluster_to_color["color"]}; opacity:0.5; width:20px; height:20px;">
                        
                            </div>
                        </div>
                        <div style="color:white;">
                            {cluster_to_potentials[cluster_to_color["cluster"]]} Area
                        </div>
                    </div>
                    """,
                    height=27
                )
        # st.page_link("pages/explore.py", label="Want to explore more? Let's go")
        # st.page_link("pages/kyc.py", label="Get your business? Let's Start")

        # from pycaret.regression import *

        # model = load_model("../first_predictive_model")
        # predict_model(model, data=compiled_data)
        has_finished = True

        
# def scroll_to_top():
#     js = '''
#     <script>
#         var body = window.parent.document.querySelector(".main");
#         console.log(body);
#         body.scrollTop = 0;
#     </script>
#     '''

#     st.components.v1.html(js)
# if has_finished:
#     st.button("Next", on_click=scroll_to_top)