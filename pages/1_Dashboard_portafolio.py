import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import altair as alt
import plotly.express as px
import pandas as pd
import numpy as np
import copy
import mysql.connector as sql
from bs4 import BeautifulSoup
from shapely.geometry import Polygon,Point
from datetime import datetime

import sys
sys.path.insert(0, '/scripts')
from html_scripts import boxnumbermoney,boxkpi,table1
from datafunctions import propertydata,propertymanagementdata,followup
from currency import currencyoptions,getcurrency
from _dashboard_property import dashboard_property

# https://altair-viz.github.io/gallery/index.html

st.set_page_config(layout="wide")

data             = propertydata()
datapm,datagasto = propertymanagementdata()
datafollowup     = followup()
datafollowup     = datafollowup[datafollowup['id_inmueble'].notnull()]
datafollowup['id_inmueble'] = datafollowup['id_inmueble'].astype(int)

col1, col2, col3 = st.columns(3)
with col1:
    currency    = st.selectbox('Moneda', options=currencyoptions())
    currencycal = getcurrency(currency)
    
with col3:
    st.markdown('<div>&nbsp</div>', unsafe_allow_html=True)
    if st.button('Actualizar información'):
        st.experimental_memo.clear()
        st.experimental_rerun()  
#-----------------------------------------------------------------------------#
# Estadisticas generales

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Compra</h1></div>', unsafe_allow_html=True)
    idj = data['estado_compra'].notnull()
    for i in data[idj]['estado_compra'].unique():
        idd    = data['estado_compra']==i
        number = sum(idd)
        money  = data[idd]['precio_compra'].sum()/currencycal
        money  = f"${money:,.0f} {currency}"
        add_s  = ''
        if number>1: add_s  = 's'
        label = f'Inmuebles {i.lower()}{add_s}'
        html  = boxnumbermoney(number,money,label)
        html_struct = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)

with col2:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Venta</h1></div>', unsafe_allow_html=True)
    idj = data['estado_venta'].isin(['VENDIDO','POR FIRMAR ESCRITURA'])
    for i in data[idj]['estado_venta'].unique():
        idd    = data['estado_venta']==i
        number = sum(idd)
        money  = data[idd]['precio_venta'].sum()/currencycal
        money  = f"${money:,.0f} {currency}"
        add_s  = ''
        if number>1: add_s  = 's'
        label = f'Inmuebles {i.lower()}{add_s}'
        html  = boxnumbermoney(number,money,label)
        html_struct = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)

with col3:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Cartera</h1></div>', unsafe_allow_html=True)
    idj  = (data['estado_venta'].isin(['VENDIDO','POR FIRMAR ESCRITURA'])) | (data['estado_venta'].isnull()) 
    for i in data[~idj]['estado_venta'].unique():
        idd    = data['estado_venta']==i
        number = sum(idd)
        money  = data[idd]['precio_lista_venta'].sum()/currencycal
        money  = f"${money:,.0f} {currency}"
        add_s  = ''
        if number>1: add_s  = 's'
        label = f'Inmuebles {i.lower()}{add_s}'
        html  = boxnumbermoney(number,money,label)
        html_struct = BeautifulSoup(html, 'html.parser')
        st.markdown(html_struct, unsafe_allow_html=True)


#-----------------------------------------------------------------------------#
# Diagnostico de inmuebles adminsitrados
st.write('---')

frecuenciaq = 'Y'
col1, col2, col3, col4 = st.columns([2,1,1,2])
with col1:
    frecuencia = st.selectbox('Frecuencia', options=['Anual','Mensual'],label_visibility="hidden")
    if frecuencia=='Mensual': frecuenciaq = 'M'
        
with col2:
    fechainicial = st.date_input('fecha_inicial_bar_graph',min(data['fecha_compra'].min(),data['fecha_escritura_venta'].min()),label_visibility="hidden")
    
with col3:
    fechafinal = st.date_input('fecha_inicial_bar_graph',datetime.now(),label_visibility="hidden")

col1,col2,col3 = st.columns(3)
with col1:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Compras y ventas</h1></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Cifras históricas</h1></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Unit Economics</h1></div>', unsafe_allow_html=True)

col1,col2,col3,col4,col5 = st.columns([4,2,2,2,2])
# Compras
datagraph  = pd.DataFrame()
idd        = data['estado_compra']=='COMPRADO'
df         = data[idd][['fecha_compra','precio_compra']]
df.columns = ['fecha','valor']
df         = df[(df['fecha']>=fechainicial.strftime("%Y-%m-%d")) & (df['fecha']<=fechafinal.strftime("%Y-%m-%d"))]    
df         = df.set_index(['fecha'])
g          = df.groupby(pd.Grouper(freq=frecuenciaq))
g          = pd.concat([g.sum(), g.count()], axis=1).reset_index()
g.columns  = ['fecha','valor','conteo']
g['grupo'] = 'Compras'
datagraph  = datagraph.append(g)

# Ventas
idd        = data['estado_venta']=='VENDIDO'
df         = data[idd][['fecha_escritura_venta','precio_venta']]
df.columns = ['fecha','valor']
df         = df[(df['fecha']>=fechainicial.strftime("%Y-%m-%d")) & (df['fecha']<=fechafinal.strftime("%Y-%m-%d"))]    
df         = df.set_index(['fecha'])
g          = df.groupby(pd.Grouper(freq=frecuenciaq))
g          = pd.concat([g.sum(), g.count()], axis=1).reset_index()
g.columns  = ['fecha','valor','conteo']
g['grupo'] = 'Ventas'
datagraph  = datagraph.append(g)
datagraph['valor'] = datagraph['valor']/currencycal

if currency=='COP':
    datagraph['valorstr'] = datagraph['valor']/1000000
    datagraph['valorstr'] = datagraph['valorstr'].apply(lambda x: f"${x:,.0f} MM")
else:
    datagraph['valorstr'] = datagraph['valor'].apply(lambda x: f"${x:,.0f} {currency}")

if frecuencia=='Mensual':
    datagraph['fecha'] = datagraph['fecha'].apply(lambda x: x.strftime("%b-%y"))
elif frecuencia=='Anual':
    datagraph['fecha'] = datagraph['fecha'].apply(lambda x: x.strftime("%Y"))
        
        
col1, col2, col3, col4 = st.columns([4,4,2,2])
with col1:
    fig = px.bar(datagraph[datagraph['conteo']>0], x='fecha', y='conteo', barmode='group',color='grupo', text='conteo', color_discrete_sequence=['#2166ac','#d6604d'])
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

with col2:
    if len(datagraph)<8:
        fig = px.bar(datagraph[datagraph['valor']>0], x='fecha', y='valor', barmode='group',color='grupo', text='valorstr', color_discrete_sequence=['#2166ac','#d6604d'])
        fig.update_traces(textposition='outside')
    else:
        fig = px.bar(datagraph[datagraph['valor']>0], x='fecha', y='valor', barmode='group',color='grupo', color_discrete_sequence=['#2166ac','#d6604d'])

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
    
with col3:
    idd      = data['estado_venta']=='VENDIDO'
    capbruto = data[idd]['precio_venta'].sum()/data[idd]['precio_compra'].sum()-1
    capbruto = "{:.1%}".format(capbruto)
    label    = 'Cap Bruto'
    html     = boxkpi(capbruto,label)
    html_struct = BeautifulSoup(html, 'html.parser')
    st.markdown(html_struct, unsafe_allow_html=True)

with col4:
    idd      = data['estado_venta']=='VENDIDO'
    datapaso = data[idd]
    datapaso = datapaso.merge(datagasto,on='id_inmueble',how='left',validate='1:1')
    datapaso['valor'] = datapaso['precio_venta']-datapaso['gasto']
    capneto  = datapaso['valor'].sum()/datapaso['precio_compra'].sum()-1
    capneto  = "{:.1%}".format(capneto)
    label    = 'Cap Neto'
    html     = boxkpi(capneto,label)
    html_struct = BeautifulSoup(html, 'html.parser')
    st.markdown(html_struct, unsafe_allow_html=True)

with col3:
    idd   = (data['estado_venta']=='VENDIDO') & (data['fecha_escritura_venta'].notnull())
    dias  = data[idd]['fecha_escritura_venta']-data[idd]['fecha_compra']
    dias  = dias.apply(lambda x: x.days)
    dias  = round(dias.mean(),1)
    label = 'Días promedio para venta'
    html  = boxkpi(dias,label)
    html_struct = BeautifulSoup(html, 'html.parser')
    st.markdown(html_struct, unsafe_allow_html=True)    

with col4:
    tir   = 0
    label = 'TIR'
    html  = boxkpi(tir,label)
    html_struct = BeautifulSoup(html, 'html.parser')
    st.markdown(html_struct, unsafe_allow_html=True)    
    


#-----------------------------------------------------------------------------#
# Diagnostico de inmuebles adminsitrados

idd         = (data['estado_venta'].isin(['VENDIDO','POR FIRMAR ESCRITURA'])) | (data['estado_venta'].isnull()) 
datacartera = pd.DataFrame()
if sum(~idd)>0:
    st.write('---')
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Inmuebles en Cartera</h1></div>', unsafe_allow_html=True)

    datacartera = data[~idd]
    datacartera['dias']      = datetime.now()-datacartera['fecha_compra']
    datacartera['dias']      = datacartera['dias'].apply(lambda x: x.days)    
    datacartera['diaslabel'] = pd.cut(datacartera['dias'],[0,60,180,np.inf],labels=['Menor a 60 días','Entre 60 y 180 días','Mayor a 180 días'])
    datagraph                = datacartera['diaslabel'].value_counts().reset_index()
    datagraph['order']       = datagraph['index'].replace(['Menor a 60 días','Entre 60 y 180 días','Mayor a 180 días'],[1,2,3])
    datagraph['colors']      = datagraph['index'].replace(['Menor a 60 días','Entre 60 y 180 días','Mayor a 180 días'],['#2ECC71','#F1C40F','#E74C3C'])
    datagraph = datagraph.sort_values(by='order',ascending=True)
    
    col1, col2 = st.columns([1,2])
    with col1:
        if datagraph.empty is False:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Tiempo en el mercado</h1></div>', unsafe_allow_html=True)
            fig = px.bar(datagraph, x='index', y='diaslabel', text='diaslabel',color='diaslabel',color_continuous_scale=datagraph['colors'])
            fig.update_traces(textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                xaxis_title='',
                yaxis_title='',
                legend_title_text=None,
                autosize=True,
                showlegend=False,
                coloraxis_showscale=False,
                #xaxis={'tickangle': -90},
                #width=800, 
                #height=500
            )            
            st.plotly_chart(fig, theme="streamlit",use_container_width=True)
            
    with col2: 
        st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Data Inmuebles Cartera</h1></div>', unsafe_allow_html=True)
        #https://streamlit-aggrid.readthedocs.io/en/docs/GridOptionsBuilder.html
        df = datacartera[['id_inmueble','diaslabel','dias','direccion','nombre_conjunto']]
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
        gb.configure_selection(selection_mode="single", use_checkbox=True) # "multiple"
        gb.configure_side_bar(filters_panel=False,columns_panel=False)
        gridoptions = gb.build()
        
        response = AgGrid(
            df,
            height=350,
            gridOptions=gridoptions,
            enable_enterprise_modules=False,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            fit_columns_on_grid_load=True,
            header_checkbox_selection_filtered_only=False,
            use_checkbox=True)

    if response['selected_rows']:
        for i in response['selected_rows']:
            dashboard_property(i['id_inmueble'] ,currency,currencycal,proceso_section=False,property_image_section=False,property_management_section=False)
            
            
                        
#-----------------------------------------------------------------------------#
# Caracteristicas del portafolio


# Mapa con los puntos, mapa de calor con los poligonos donde hemos comprado 

# Pie chart de las caracteristcias de los inmuebles

# De los inmuebles que se han vendido rapido, que caracteristcias tienen 
