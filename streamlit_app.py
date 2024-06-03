#######################
# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import geopandas as gpd
import pyproj

#######################
# Page configuration
st.set_page_config(
    page_title="Tanah Longsor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

#######################
# Load data

all_rekap = pd.read_csv('all_data/all_rekap.csv')
all_peta = gpd.read_file('all_data/all_peta.shp')

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

def process_timeseries(df):
    ts = df_rekap_selected_year.resample(rule='M' , on='TANGGAL_KEJADIAN').agg({
        "NO": "nunique"
    })
    ts.index = ts.index.strftime('%B')
    ts = ts.reset_index()
    ts.rename(columns={
        "TANGGAL_KEJADIAN": "Bulan", "NO": "Jumlah Kejadian Bencana"
    }, inplace=True)
    return ts
    
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

    fig = px.choropleth(df_peta_selected_year, geojson=df_peta_selected_year.geometry, locations='id', color='KEJADIAN', 
                               color_continuous_scale='Reds',
                               range_color=(0, max(df_peta_selected_year.KEJADIAN)),
                               labels={'KEJADIAN':'KEJADIAN'}
                              )
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    
    fig.update_geos(fitbounds="locations", visible=True)
    fig.show()

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        ts["TANGGAL_KEJADIAN"],
        ts["Jumlah Kejadian Bencana"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
    
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
    
