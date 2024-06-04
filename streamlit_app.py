#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

#######################
# Page configuration
st.set_page_config(
    page_title="Tanah Longsor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

#######################
# Load data

all_rekap = pd.read_csv('all_data/all_rekap.csv')
all_peta = gpd.read_file('all_data/all_peta.geojson')

#######################
# Sidebar
with st.sidebar:
    st.image('asset/bpbd_kab_semarang.png')
    st.title('Tanah Longsor Dashboard')
    
    year_list = list(all_rekap.TAHUN.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_rekap_selected_year = all_rekap[all_rekap.TAHUN == selected_year]
    df_peta_selected_year = all_peta[all_peta.TAHUN == selected_year]
    
    
######################
# Function

def make_choropleth(input_df, input_js, input_id, input_columne):
    choropleth = px.choropleth(input_df, geojson=input_js,
                               locations=input_id,
                               color=input_columne,
                               color_continuous_scale='Reds',
                               range_color=(0, max(df_peta_selected_year.KEJADIAN)),
                               labels={'KEJADIAN':'KEJADIAN'},
                               hover_data='KECAMATAN'
                               )
    choropleth.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    choropleth.update_geos(fitbounds="locations", visible=True)
    return choropleth

def tren(input_df):
    df_rekap_selected_year.set_index(df_rekap_selected_year.TANGGAL_KEJADIAN, inplace=True)
    rekap_ts = input_df.resample(rule='M', on=df_rekap_selected_year.TANGGAL_KEJADIAN).agg({
        "NO": "nunique"
    })
    rekap_ts.index = rekap_ts.index.strftime('%B') #mengubah format order date menjadi Tahun-Bulan
    rekap_ts = rekap_ts.reset_index()
    rekap_ts.rename(columns={"TANGGAL_KEJADIAN": "Bulan", "NO": "Jumlah Kejadian Bencana"}, inplace=True)

    tren, ax = plt.subplots(figsize=(13, 5))
    ax.plot(
        rekap_ts["Bulan"],
        rekap_ts["Jumlah Kejadian Bencana"],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )
    ax.set_title(f'Jumlah Kejadian Tanah Longsor Kab. Semarang Tahun {selected_year}', loc="center", fontsize=20)
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    return tren


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby('KECAMATAN')['NO'].count().reset_index(name='JUMLAH_KEJADIAN')
    return sum_order_items_df

sum_order_items_df = create_sum_order_items_df(df_rekap_selected_year)
df_selected_year_sorted = sum_order_items_df.sort_values(by="JUMLAH_KEJADIAN", ascending=False)
#######################
# Dashboard Main Panel
col = st.columns((5, 2), gap='medium')

with col[0]:
    st.markdown(f' #### Peta Sebaran Tanah Longsor Kab. Semarang pada Tahun {selected_year}')
    
    choropleth = make_choropleth(df_peta_selected_year, df_peta_selected_year.geometry, df_peta_selected_year.index, 'KEJADIAN')
    st.plotly_chart(choropleth, use_container_width=True)
    
    tren = tren(df_rekap_selected_year)
    st.pyplot(tren)

with col[1]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("KECAMATAN", "JUMLAH_KEJADIAN"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "KECAMATAN": st.column_config.TextColumn(
                        "KECAMATAN",
                    ),
                    "JUMLAH_KEJADIAN": st.column_config.ProgressColumn(
                        "JUMLAH_KEJADIAN",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.JUMLAH_KEJADIAN),
                     )}
                 )
    st.write(df_peta_selected_year.head())
