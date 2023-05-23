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
import json
import mysql.connector as sql
from bs4 import BeautifulSoup
from shapely.geometry import Polygon,Point
from datetime import datetime


from currency import currencyoptions,getcurrency
from datafunctions import propertydata,propertymanagementdata,followup,inspeccion_callsample,inspeccion_callhistory,inspeccion_seguimiento_ofertas,datadocumentos


@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


# https://altair-viz.github.io/gallery/index.html

st.set_page_config(layout="wide")

def id_inmueble_change():
    if st.session_state.id_inmueble=='Todos':
        st.session_state.direccion       = 'Todos'
        st.session_state.nombre_conjunto = 'Todos'
    else: 
        st.session_state.direccion       = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['direccion'].iloc[0]
        st.session_state.nombre_conjunto = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['nombre_conjunto'].iloc[0]

def direccion_change():
    if st.session_state.direccion=='Todos':
        st.session_state.id_inmueble     = 'Todos'
        st.session_state.nombre_conjunto = 'Todos'
    else:
        st.session_state.id_inmueble     = st.session_state.data[st.session_state.data['direccion']==st.session_state.direccion]['id_inmueble'].iloc[0]
        st.session_state.nombre_conjunto = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['nombre_conjunto'].iloc[0]
        
def nombre_conjunto_change():
    if st.session_state.nombre_conjunto=='Todos':
        st.session_state.id_inmueble = 'Todos'
        st.session_state.direccion   = 'Todos'
    else:
        st.session_state.id_inmueble = st.session_state.data[st.session_state.data['nombre_conjunto']==st.session_state.nombre_conjunto]['id_inmueble'].iloc[0]
        st.session_state.direccion   = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['direccion'].iloc[0]
   
    
data = propertydata()
data = data.sort_values(by='id_inmueble',ascending=True)

formato = {'id_inmueble':'Todos','direccion':'Todos','nombre_conjunto':'Todos','gestion_angulo':0}
for key,value in formato.items():
    if key not in st.session_state: 
        st.session_state[key] = value
        
if 'data' not in st.session_state: 
    st.session_state.data = copy.deepcopy(data)
    
col1, col2, col3, col4,col5 = st.columns([1,1,2,2,1])
with col1:
    currency    = st.selectbox('Moneda', options=currencyoptions())
    currencycal = getcurrency(currency)
    
with col2:
    id_inmueble = st.selectbox('ID', options=['Todos']+list(data['id_inmueble']),key='id_inmueble',on_change=id_inmueble_change)
with col3:
    direccion = st.selectbox('Direccion', options=['Todos']+list(data['direccion']),key='direccion',on_change=direccion_change)
with col4:
    nombre_conjunto = st.selectbox('Nombre del conjunto', options=['Todos']+list(data['nombre_conjunto']),key='nombre_conjunto',on_change=nombre_conjunto_change)

with col5:
    st.markdown('<div>&nbsp</div>', unsafe_allow_html=True)
    if st.button('Actualizar información'):
        st.experimental_memo.clear()
        st.experimental_rerun()     

if id_inmueble=='Todos': id_inmueble = None

#-----------------------------------------------------------------------------#
# Data Stock Inmuebles
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Stock Inmuebles</h1></div>', unsafe_allow_html=True)
if id_inmueble is not None: data = data[data['id_inmueble']==id_inmueble]
data      = data.sort_values(by='id_inmueble',ascending=True)
vardelete = ['id_inmueble_pricing', 'coddir', 'oferta_actual', 'precio_renta', 'ano_compra_compra', 'url', 'mes_compra_compra', 'pagos', 'pagos_pendientes', 'porcentaje_comision', 'id', 'codigo_img_property_data', 'setu_ccnct', 'secu_ccnct', 'scacodigo', 'scanombre', 'barmanpre', 'tiempodeconstruido', 'conjunto_valorventamt2_mediana', 'conjunto_valorventa', 'conjunto_nobs', 'market_valorventamt2_mediana', 'market_valorventa', 'market_nobs', 'sell_forecast_model_valorestimado', 'sell_forecast_model_valorestimado_mt2', 'rent_forecast_model_valorestimado', 'rent_forecast_model_valorestimado_mt2', 'ph', 'avaluocatastral', 'impuestopredial']
vardelete = [x for x in vardelete if x in list(data)]
data.drop(columns=vardelete,inplace=True)
data.index = range(len(data))
dataexport = copy.deepcopy(data)

for i in ['id_inmueble','habitaciones', 'banos', 'garajes', 'depositos', 'estrato', 'piso', 'antiguedad', 'ascensores', 'numerodeniveles', 'conjunto_unidades', 'antiguedad_min', 'antiguedad_max', 'total_parqueaderos', 'total_depositos', 'numero_sotanos']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].astype(int).astype(str)
            
for i in [ 'areaconstruida','areaprivada',]:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: str(round(x,1)))
            
for i in ['precio_lista_oferta_inicial', 'precio_compra', 'precio_lista_venta', 'precio_venta', 'valoradministracion']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: f"${x:,.0f}")
  
for i in ['fecha_oferta_compra', 'fecha_promesa_compra', 'fecha_compra', 'fecha_oferta_venta', 'fecha_promesa_venta', 'fecha_escritura_venta']:
    if i in data:
        data[i] = pd.to_datetime(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: x.strftime('%Y-%m-%d'))
             
data.fillna('',inplace=True)
            
varrename  = {'direccion': 'Direccion', 'nombre_conjunto': 'Nombre del Conjunto', 'estado': 'Estado', 'asesor_compra': 'Asesor del Compra', 'precio_lista_oferta_inicial': 'Precio Oferta Inicial', 'fecha_oferta_compra': 'Fecha oferta para Compra', 'fecha_promesa_compra': 'Fecha promesa para Compra', 'fecha_compra': 'Fecha de Compra', 'precio_compra': 'Precio de Compra', 'presupuesto_remodelacion': 'Presupuesto de Remodelacion', 'estado_compra': 'Estado de Compra', 'asesor_venta': 'Asesor de Venta', 'precio_lista_venta': 'Precio lista para Venta', 'precio_venta': 'Precio de Venta', 'fecha_oferta_venta': 'Fecha oferta para Venta', 'fecha_promesa_venta': 'Fecha promesa para Venta', 'fecha_escritura_venta': 'Fecha escritura para Venta', 'estado_venta': 'Estado de Venta', 'codigo_domus': 'Codigo Domus', 'url_domus': 'Url Domus', 'codigo_fr': 'Codigo Fr', 'url_fr': 'Url Fr', 'codigo_m2': 'Codigo M2', 'url_m2': 'Url M2', 'codigo_cc': 'Codigo Cc', 'url_cc': 'Url Cc', 'codigo_meli': 'Codigo Meli', 'url_meli': 'Url Meli', 'codigo_whatsapp': 'Codigo Whatsapp', 'url_whatsapp': 'Url Whatsapp', 'tipoinmueble': 'Tipo de inmueble', 'ciudad': 'Ciudad', 'areaconstruida': 'Area construida', 'areaprivada': 'Area privada', 'habitaciones': 'Habitaciones', 'banos': 'Baños', 'garajes': 'Garajes', 'depositos': 'Depositos', 'estrato': 'Estrato', 'piso': 'Piso', 'antiguedad': 'Antiguedad', 'ascensores': 'Ascensores', 'numerodeniveles': 'Numero de niveles', 'valoradministracion': 'Valor administracion', 'latitud': 'Latitud', 'longitud': 'Longitud', 'conjunto_unidades': 'Unidades en el Conjunto', 'antiguedad_min': 'Antiguedad Minima', 'antiguedad_max': 'Antiguedad Maxima', 'dpto_ccdgo': 'Codigo del departamento', 'mpio_ccdgo': 'Codigo del municipio', 'localidad': 'Localidad', 'upz': 'Upz', 'barriocatastral': 'Barriocatastral', 'barriocomun': 'Barriocomun', 'chip': 'Chip', 'matricula': 'Matricula', 'cedula_catastral': 'Cedula Catastral', 'total_parqueaderos': 'Total de Parqueaderos del edificio o conjunto', 'total_depositos': 'Total de Depositos del edificio o conjunto', 'numero_sotanos': 'Numero de Sotanos', 'porteria': 'Porteria', 'circuito_cerrado': 'Circuito del Cerrado', 'lobby': 'Lobby', 'salon_comunal': 'Salon del Comunal', 'parque_infantil': 'Parque del Infantil', 'terraza': 'Terraza', 'sauna': 'Sauna', 'turco': 'Turco', 'jacuzzi': 'Jacuzzi', 'cancha_multiple': 'Cancha del Multiple', 'cancha_baloncesto': 'Cancha del Baloncesto', 'cancha_voleibol': 'Cancha del Voleibol', 'cancha_futbol': 'Cancha del Futbol', 'cancha_tenis': 'Cancha del Tenis', 'cancha_squash': 'Cancha del Squash', 'salon_juegos': 'Salon del Juegos', 'gimnasio': 'Gimnasio', 'zona_bbq': 'Zona del Bbq', 'sala_cine': 'Sala del Cine', 'piscina': 'Piscina'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(data)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_inmuebles.csv",
       "text/csv",
       key='data_inmuebles'
    )

#-----------------------------------------------------------------------------#
# Data Documentos
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Documentos de los inmuebles</h1></div>', unsafe_allow_html=True)
data = datadocumentos()
if id_inmueble is not None: data = data[data['id_inmueble']==id_inmueble]
data      = data.sort_values(by='id_inmueble',ascending=True)

datafinal = pd.DataFrame()
for i in data['id_inmueble']:
    datapaso = pd.DataFrame()
    for j in ['venta_relevantfiles', 'venta_allfiles', 'compra_allfiles']:
        try: datapaso = datapaso.append(json.loads(data[data['id_inmueble']==i]['venta_relevantfiles'].iloc[0]))
        except: pass
    datapaso['id_inmueble'] = i
    datafinal = pd.concat([datafinal,datapaso])

#datafinal = datafinal[['id_inmueble','filename', 'filedate', 'urldocument']]
datafinal.index = range(len(datafinal))
dataexport = copy.deepcopy(datafinal)

data.fillna('',inplace=True)
            
varrename  = {'filename':'Nombre del archivo', 'filedate':'Fecha del archivo', 'urldocument':'Link del documento'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(datafinal)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_documentos.csv",
       "text/csv",
       key='data_documentos'
    )
    

#-----------------------------------------------------------------------------#
# Data Property Management
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Property Management</h1></div>', unsafe_allow_html=True)
data,datapaso = propertymanagementdata()
if id_inmueble is not None: data = data[data['id_inmueble']==id_inmueble]
data      = data.sort_values(by=['id_inmueble','tipo','concepto'],ascending=True)
data       = data[['id_inmueble', 'direccion', 'nombre_edificio', 'tipo', 'concepto', 'valor', 'fecha_pago']]
data.index = range(len(data))
dataexport = copy.deepcopy(data)

data['id_inmueble'] = pd.to_numeric(data['id_inmueble'],errors='coerce')
idd = data['id_inmueble'].notnull()
if sum(idd)>0:
    data.loc[idd,'id_inmueble'] = data.loc[idd,'id_inmueble'].astype(int).astype(str)
    
data['valor'] = pd.to_numeric(data['valor'],errors='coerce')
idd           = data['valor'].notnull()
if sum(idd)>0:
    data.loc[idd,'valor'] = data.loc[idd,'valor'].apply(lambda x: f"${x:,.0f}")
          
data['fecha_pago'] = pd.to_datetime(data['fecha_pago'],errors='coerce')
idd                = data['fecha_pago'].notnull()
if sum(idd)>0:
    data.loc[idd,'fecha_pago'] = data.loc[idd,'fecha_pago'].apply(lambda x: x.strftime('%Y-%m-%d'))
    
data.fillna('',inplace=True)
            
varrename  = {'direccion': 'Direccion', 'nombre_conjunto': 'Nombre del Conjunto', 'tipo':'Tipo', 'concepto':'Concepto', 'valor':'Valor Pagado', 'fecha_pago':'Fecha de pago'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(data)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_property_management.csv",
       "text/csv",
       key='data_property_management'
    )
    
    
    
#-----------------------------------------------------------------------------#
# Data Call Center Inbound
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Data Call Center Inbound</h1></div>', unsafe_allow_html=True)
data = followup()
if id_inmueble is not None: data = data[data['id_inmueble']==id_inmueble]   
data      = data.sort_values(by=['call_date'],ascending=True)
data      = data[['id_inmueble','call_date',  'fuente_llamada', 'nombre_cliente', 'contact_number', 'interesado', 'observaciones', 'date_visit', 'visit_check', 'final_status']]
data.index = range(len(data))
dataexport = copy.deepcopy(data)

for i in ['id_inmueble','interesado','visit_check']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].astype(int).astype(str)

for i in ['call_date', 'date_visit']:
    if i in data:
        data[i] = pd.to_datetime(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: x.strftime('%Y-%m-%d'))
        if sum(~idd)>0:
            data.loc[~idd,i] = ''
            
data.fillna('',inplace=True)
            
varrename  = {'call_date':'Fecha llamada entrante',  'fuente_llamada':'Fuente de la llamada', 'nombre_cliente':'Nombre del cliente', 'contact_number':'Numero de contacto', 'interesado':'Interesado', 'observaciones':'Observaciones', 'date_visit':'Fecha de la visita', 'visit_check':'Visita realizada', 'final_status':'Estatus Final'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(data)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_callcenter_inbound.csv",
       "text/csv",
       key='data_callcenter_inbound'
    )
    
#-----------------------------------------------------------------------------#
# Data Seguimiento Ofertas
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Seguimiento Ofertas Realizadas</h1></div>', unsafe_allow_html=True)
data       = inspeccion_seguimiento_ofertas()
data.index = range(len(data))
dataexport = copy.deepcopy(data)

for i in ['id_inmueble', 'habitaciones', 'banos', 'garajes', 'depositos', 'piso']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].astype(int).astype(str)
            
for i in [ 'areaconstruida']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: str(round(x,1)))
            
for i in ['precio_publicacion', 'precio_maximo', 'precio_oferta', 'precio_compra', 'contraoferta1', 'contraoferta2', 'contraoferta3', 'remodelacion_pisos', 'remodelacion_pintura', 'remodelacion_banos', 'remodelacion_cocina', 'remodelacion_puertas', 'remodelacion_otros', 'remodelacion_total', 'valoradministracion']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: f"${x:,.0f}")
  
for i in ['fecha_oferta', 'fecha_oferta', 'fecha_cambio_estado', 'fecha_registro']:
    if i in data:
        data[i] = pd.to_datetime(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: x.strftime('%Y-%m-%d'))
             
data.fillna('',inplace=True)
            
varrename  = {'asesor': 'Asesor', 'direccion': 'Direccion', 'nombre_conjunto': 'Nombre del Conjunto', 'areaconstruida': 'Area construida', 'habitaciones': 'Habitaciones', 'banos': 'Banos', 'garajes': 'Garajes', 'piso': 'Piso', 'depositos': 'Depositos', 'url': 'Url', 'valoradministracion': 'Valor administracion', 'precio_publicacion': 'Precio de Publicacion', 'precio_maximo': 'Precio Maximo', 'precio_oferta': 'Precio de Oferta', 'fecha_oferta': 'Fecha de Oferta', 'precio_compra': 'Precio de Compra', 'observaciones': 'Observaciones', 'estado': 'Estado', 'fecha_cambio_estado': 'Fecha de Cambio de Estado', 'fecha_registro': 'Fecha de Registro', 'asumir_gastos_notariales': 'Asumir Gastos Notariales', 'asumir_comision_compra': 'Asumir Comision Compra', 'contraoferta1': 'Contraoferta 1', 'contraoferta2': 'Contraoferta 2', 'contraoferta3': 'Contraoferta 3', 'remodelacion_pisos': 'Remodelacion de Pisos', 'remodelacion_pintura': 'Remodelacion de Pintura', 'remodelacion_banos': 'Remodelacion de Banos', 'remodelacion_cocina': 'Remodelacion de Cocina', 'remodelacion_puertas': 'Remodelacion de Puertas', 'remodelacion_otros': 'Remodelacion de Otros', 'remodelacion_total': 'Remodelacion de Total', 'motivo_venta': 'Motivo de Venta', 'tipo_persona_oferta': 'Tipo de Persona de Oferta', 'num_propietarios': 'Num de Propietarios', 'tipouso': 'Tipouso', 'formapago': 'Formapago', 'preaprobado': 'Preaprobado', 'id_data_cliente_perfil': 'Id Data Cliente Perfil'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(data)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_seguimiento_ofertas.csv",
       "text/csv",
       key='data_seguimiento_ofertas'
    )
    
#-----------------------------------------------------------------------------#
# Data APP Insepccion - Seguimiento Oportunidades
st.write('---')
st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Seguimiento Oportunidades (App Inspeccion)</h1></div>', unsafe_allow_html=True)
data       = inspeccion_callsample()
data.index = range(len(data))
dataexport = copy.deepcopy(data)

for i in ['id_inmueble', 'habitaciones', 'banos', 'garajes', 'estrato', 'antiguedad','disponible','negociable', 'precio_negociable']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].astype(int).astype(str)
            
for i in [ 'areaconstruida']:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: str(round(x,1)))
            
for i in ['valorventa','valormt2','valorarriendo','valoradministracion','precio_maximo_compra','actual_price',]:
    if i in data:
        data[i] = pd.to_numeric(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: f"${x:,.0f}")
  
for i in ['fecha_creacion','fecha_asignacion_callagent','fecha_asignacion_visitagent',]:
    if i in data:
        data[i] = pd.to_datetime(data[i],errors='coerce')
        idd     = data[i].notnull()
        if sum(idd)>0:
            data.loc[idd,i] = data.loc[idd,i].apply(lambda x: x.strftime('%Y-%m-%d'))
             
data.fillna('',inplace=True)
            
varrename  = {'direccion': 'Direccion', 'nombre_conjunto': 'Nombre del Conjunto', 'estado': 'Estado', 'asesor_compra': 'Asesor del Compra', 'precio_lista_oferta_inicial': 'Precio Oferta Inicial', 'fecha_oferta_compra': 'Fecha oferta para Compra', 'fecha_promesa_compra': 'Fecha promesa para Compra', 'fecha_compra': 'Fecha de Compra', 'precio_compra': 'Precio de Compra', 'presupuesto_remodelacion': 'Presupuesto de Remodelacion', 'estado_compra': 'Estado de Compra', 'asesor_venta': 'Asesor de Venta', 'precio_lista_venta': 'Precio lista para Venta', 'precio_venta': 'Precio de Venta', 'fecha_oferta_venta': 'Fecha oferta para Venta', 'fecha_promesa_venta': 'Fecha promesa para Venta', 'fecha_escritura_venta': 'Fecha escritura para Venta', 'estado_venta': 'Estado de Venta', 'codigo_domus': 'Codigo Domus', 'url_domus': 'Url Domus', 'codigo_fr': 'Codigo Fr', 'url_fr': 'Url Fr', 'codigo_m2': 'Codigo M2', 'url_m2': 'Url M2', 'codigo_cc': 'Codigo Cc', 'url_cc': 'Url Cc', 'codigo_meli': 'Codigo Meli', 'url_meli': 'Url Meli', 'codigo_whatsapp': 'Codigo Whatsapp', 'url_whatsapp': 'Url Whatsapp', 'tipoinmueble': 'Tipo de inmueble', 'ciudad': 'Ciudad', 'areaconstruida': 'Area construida', 'areaprivada': 'Area privada', 'habitaciones': 'Habitaciones', 'banos': 'Baños', 'garajes': 'Garajes', 'depositos': 'Depositos', 'estrato': 'Estrato', 'piso': 'Piso', 'antiguedad': 'Antiguedad', 'ascensores': 'Ascensores', 'numerodeniveles': 'Numero de niveles', 'valoradministracion': 'Valor administracion', 'latitud': 'Latitud', 'longitud': 'Longitud', 'conjunto_unidades': 'Unidades en el Conjunto', 'antiguedad_min': 'Antiguedad Minima', 'antiguedad_max': 'Antiguedad Maxima', 'dpto_ccdgo': 'Codigo del departamento', 'mpio_ccdgo': 'Codigo del municipio', 'localidad': 'Localidad', 'upz': 'Upz', 'barriocatastral': 'Barriocatastral', 'barriocomun': 'Barriocomun', 'chip': 'Chip', 'matricula': 'Matricula', 'cedula_catastral': 'Cedula Catastral', 'total_parqueaderos': 'Total de Parqueaderos del edificio o conjunto', 'total_depositos': 'Total de Depositos del edificio o conjunto', 'numero_sotanos': 'Numero de Sotanos', 'porteria': 'Porteria', 'circuito_cerrado': 'Circuito del Cerrado', 'lobby': 'Lobby', 'salon_comunal': 'Salon del Comunal', 'parque_infantil': 'Parque del Infantil', 'terraza': 'Terraza', 'sauna': 'Sauna', 'turco': 'Turco', 'jacuzzi': 'Jacuzzi', 'cancha_multiple': 'Cancha del Multiple', 'cancha_baloncesto': 'Cancha del Baloncesto', 'cancha_voleibol': 'Cancha del Voleibol', 'cancha_futbol': 'Cancha del Futbol', 'cancha_tenis': 'Cancha del Tenis', 'cancha_squash': 'Cancha del Squash', 'salon_juegos': 'Salon del Juegos', 'gimnasio': 'Gimnasio', 'zona_bbq': 'Zona del Bbq', 'sala_cine': 'Sala del Cine', 'piscina': 'Piscina'}
data.rename(columns=varrename,inplace=True)
dataexport.rename(columns=varrename,inplace=True)

st.dataframe(data)

col1,col2 = st.columns([1,5])
with col1:
    csv = convert_df(dataexport)
    st.download_button(
       "download",
       csv,
       "data_seguimiento_oportunidades.csv",
       "text/csv",
       key='data_seguimiento_oportunidades'
    )
