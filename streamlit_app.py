#######################
# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import geopandas as gpd

#######################
# Page configuration
st.set_page_config(
    page_title="Tanah Longsor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

#######################
# Load data

all_rekap = pd.read_csv('dashboard/all_rekap.csv')
all_peta = gpd.read_file('dashboard/all_peta.shp')

#######################
# Sidebar
with st.sidebar:
    st.title('Tanah Longsor Dashboard')
    
    year_list = list(all_rekap.TAHUN.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_rekap_selected_year = all_rekap[all_rekap.TAHUN == selected_year]
    df_peta_selected_year = all_peta[all_peta.TAHUN == selected_year]
    
    
######################
# Function

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby('KECAMATAN')['NO'].count().reset_index(name='TANAH LONGSOR')
    return sum_order_items_df

sum_order_items_df = create_sum_order_items_df(df_rekap_selected_year)
df_selected_year_sorted = sum_order_items_df.sort_values(by="TANAH LONGSOR", ascending=False)
#######################
# Dashboard Main Panel
col = st.columns((5, 2), gap='medium')

with col[0]:
    st.markdown(f' #### Peta Sebaran Tanah Longsor Kab. Semarang pada Tahun {selected_year}')

    fig, ax = plt.subplots(figsize=(9, 8))
    df_peta_selected_year.plot(column='KEJADIAN', cmap='Wistia', legend=True, legend_kwds={"label": 'Banyaknya Kejadian', "orientation": "horizontal"}, ax=ax)
    ax.set_axis_off()
    plt.show()
    st.pyplot(fig)

with col[1]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("KECAMATAN", "TANAH LONGSOR"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "KECAMATAN": st.column_config.TextColumn(
                        "KECAMATAN",
                    ),
                    "TANAH LONGSOR": st.column_config.ProgressColumn(
                        "TANAH LONGSOR",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.KEJADIAN),
                     )}
                 )
    
