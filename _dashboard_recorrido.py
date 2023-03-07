import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import copy
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from datafunctions import datarecorridos
from html_scripts import boxkpi,boxnumberpercentage
from coddir import coddir

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def dashboard_recorrido():
    
    data = datarecorridos()
    st.write('---')
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Gestión Recorridos</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        totalventanas = len(data)
        html          = boxkpi(totalventanas,'Total Ventanas')
        html_struct   = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)

    with col2:
        barriosunicos = len(data['scanombre'].unique())
        html          = boxkpi(barriosunicos,'Barrios Unicos')
        html_struct   = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)

    with col3:            
        barriosunicos = len(data['nombre_conjunto'].unique())
        html          = boxkpi(barriosunicos,'Edificios Unicos')
        html_struct   = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)            

    with col4:            
        enventa       = sum(data['tipo_negocio'].astype(str).str.lower().str.contains('venta'))
        html          = boxkpi(enventa,'En Venta')
        html_struct   = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)            

    with col5:            
        enarriendo    = sum(data['tipo_negocio'].astype(str).str.lower().str.contains('arriendo'))
        html          = boxkpi(enarriendo,'En Arriendo')
        html_struct   = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)       

    st.write('---')
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Gestión Call Center Inbound</h1></div>', unsafe_allow_html=True)

    df          = data[['fecha_recorrido']]
    df          = df[df['fecha_recorrido'].notnull()]
    df['count'] = 1
    df.columns  = ['fecha','count']
    df          = df.set_index(['fecha'])
    df          = df.groupby(pd.Grouper(freq='M'))['count'].count().reset_index()
    
    if df.empty is False:
        fig = px.bar(df, x='fecha', y='count',text='count')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis_title='',
            yaxis_title='',
            legend_title_text=None,
            #width=800, 
            #height=500
        )        
        st.plotly_chart(fig, theme="streamlit",use_container_width=True)