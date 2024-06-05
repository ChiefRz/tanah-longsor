#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px

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
                                      hover_name='KECAMATAN',
                               )
    choropleth.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350,  # Add annotations to the layout
    )
    choropleth.update_geos(fitbounds="locations", visible=True)
    return choropleth
    
def tren(input):
    # Kelompokkan data berdasarkan bulan per bulan
    input["TANGGAL_KEJADIAN"] = pd.to_datetime(input["TANGGAL_KEJADIAN"])
    data_bulan = input.groupby(input["TANGGAL_KEJADIAN"].dt.month)
    
    # Hitung jumlah kejadian bencana yang unik pada kolom NO setiap bulan
    jumlah_kejadian = data_bulan["NO"].nunique()
    
    # Ubah format indeks menjadi nama bulan
    nama_bulan = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    jumlah_kejadian.index = [nama_bulan[i-1] for i in jumlah_kejadian.index]
    jumlah_kejadian = jumlah_kejadian.reindex(nama_bulan, fill_value=0)

    # Ubah indeks menjadi kolom biasa dan membuat indeks baru
    jumlah_kejadian = jumlah_kejadian.reset_index()
    jumlah_kejadian = jumlah_kejadian.rename(columns={"index": "Bulan", "NO": "Jumlah Kejadian Bencana"})
    
    tren = px.line(jumlah_kejadian, x='Bulan', y='Jumlah Kejadian Bencana', markers=True)
    return tren
    

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby('KECAMATAN')['NO'].count().reset_index(name='JUMLAH_KEJADIAN')
    return sum_order_items_df

def generate_chart(input):
    rekap_lapor = input.groupby(by="PELAPOR").NO.nunique().reset_index()
    rekap_lapor.rename(columns={
        "NO": "Jumlah Kejadian Bencana"
    }, inplace=True)
    
    fig = px.pie(rekap_lapor, values='Jumlah Kejadian Bencana', names='PELAPOR', hole=.3)
    fig.update_layout(legend=dict(orientation="h"))
    return fig

def musim(input_df):
    rekap_musim = input_df.groupby(by="MUSIM").NO.nunique().reset_index()
    rekap_musim.rename(columns={
         "NO": "Jumlah Kejadian Bencana"
         }, inplace=True)
    
    fig = px.bar(rekap_musim, y='Jumlah Kejadian Bencana', x='MUSIM', text_auto='.2s',
            title="Controlled text sizes, positions and angles")
    rekap_musim.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    return fig


sum_order_items_df = create_sum_order_items_df(df_rekap_selected_year)
df_selected_year_sorted = sum_order_items_df.sort_values(by="JUMLAH_KEJADIAN", ascending=False)
#######################
# Dashboard Main Panel
col = st.columns((5, 2), gap='medium')

with col[0]:
    st.markdown(f' #### Peta Sebaran Tanah Longsor Kab. Semarang pada Tahun {selected_year}')
    
    choropleth = make_choropleth(df_peta_selected_year, df_peta_selected_year.geometry, df_peta_selected_year.index, 'KEJADIAN')
    st.plotly_chart(choropleth, use_container_width=True)

    st.markdown(f' #### Jumlah Kejadian Tanah Longsor Kab. Semarang Tahun {selected_year}')
    
    tren = tren(df_rekap_selected_year)
    st.plotly_chart(tren, use_container_width=True)

with col[1]:
    st.markdown('#### Kecamatan Paling Sering Terjadi Bencana')

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
    
    st.markdown('##### Proporsi Pelaporan')
    fig = generate_chart(df_rekap_selected_year)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('##### Rekap Bencana Berdasarkan Musim')
    fig = musim(df_rekap_selected_year)
    st.plotly_chart(fig, use_container_width=True)
