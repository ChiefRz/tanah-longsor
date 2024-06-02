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

alt.themes.enable("dark")

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
    df_selected_year_sorted = all_peta[all_peta.TAHUN == selected_year].sort_values(by="KEJADIAN", ascending=False)

#######################
# Plots

# Choropleth map
def make_choropleth(input_df, input_id, input_column):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column,
                               range_color=(0, max(df_peta_selected_year.KEJADIAN)),
                               labels={'KEJADIAN':'BANYAK KEJADIAN'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

#######################
# Dashboard Main Panel
col = st.columns((5, 2), gap='medium')

with col[0]:
    st.markdown('#### Total Population')

    fig, ax = plt.subplots(figsize=(9, 8))
    df_peta_selected_year.plot(column='KEJADIAN', cmap='Wistia', legend=True, legend_kwds={"label": 'Banyaknya Kejadian', "orientation": "horizontal"}, ax=ax)
    
    ax.set_title(f'Peta Sebaran Tanah Longsor Kab. Semarang pada Tahun {selected_year}')
    ax.set_axis_off()
    plt.show()
    st.pyplot(fig)

with col[1]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("KECAMATAN", "KEJADIAN"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "KECAMATAN": st.column_config.TextColumn(
                        "KECAMATAN",
                    ),
                    "KEJADIAN": st.column_config.ProgressColumn(
                        "KEJADIAN",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.KEJADIAN),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
            - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
