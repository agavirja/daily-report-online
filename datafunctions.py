import streamlit as st
import pandas as pd
import numpy as np
import json
import mysql.connector as sql
from shapely.geometry import  Polygon
from sqlalchemy import create_engine 

# Credenciales
user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
schema   = st.secrets["schema"]
engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

@st.experimental_memo
def propertydata():
    # db_connection       = sql.connect(user=user, password=password, host=host, database=schema)
    data                = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_gestion", engine) 
    datacaracteristicas = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_caracteristicas", engine)
    dataimagenes        = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_img", engine)
    
    vardrop = [x for x in list(data) if x in list(datacaracteristicas)]
    if any([x for x in vardrop if 'id_inmueble' in x]):
        vardrop.remove('id_inmueble')
    if vardrop!=[]:
        datacaracteristicas.drop(columns=vardrop,inplace=True)
    data    = data.merge(datacaracteristicas,on='id_inmueble',how='left',validate='1:1')
    
    vardrop = [x for x in list(data) if x in list(dataimagenes)]
    if any([x for x in vardrop if 'id_inmueble' in x]):
        vardrop.remove('id_inmueble')
    if vardrop!=[]:
        dataimagenes.drop(columns=vardrop,inplace=True)    
    
    data  = data.merge(dataimagenes,on='id_inmueble',how='left',validate='1:1')
    return data

@st.experimental_memo
def propertymanagementdata():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.app_pm_cuentas", engine)
    
    # Gasto del inmueble:
        # Restar del total de gasto (incluye los desembolsos) el valor de la compra
    datapaso  = data.groupby(['id_inmueble','tipo'])['valor'].sum().reset_index()
    datamerge = datapaso[datapaso['tipo']=='PRECIO COMPRA']
    datamerge.rename(columns={'valor':'valorcompra'},inplace=True)
    datamerge['tipo'] = 'GASTO'
    datapaso = datapaso.merge(datamerge,on=['id_inmueble','tipo'],how='left',validate='1:1')
    idd      = datapaso['valorcompra'].isnull()
    datapaso.loc[idd,'valorcompra'] = 0
    datapaso['valor'] = datapaso['valor']-datapaso['valorcompra']
    
        # Restar del total de gasto los ingresos recibidos por el inmueble
    datamerge = data[(data['tipo']=='INGRESO') & (~data['concepto'].isin(['INGRESO 1 (VENTA)','INGRESO 2 (VENTA)','INGRESO 3 (VENTA)','INGRESO 4 (VENTA)','INGRESO 5 (VENTA)','INGRESO 6 (VENTA)','INGRESO  6 (VENTA)','INGRESO ESCRITURAS (VENTA)']))]
    datamerge = datamerge.groupby(['id_inmueble','tipo'])['valor'].sum().reset_index()
    datamerge.rename(columns={'valor':'valoringreso'},inplace=True)
    datamerge['tipo'] = 'GASTO'
    datapaso = datapaso.merge(datamerge[['id_inmueble','tipo','valoringreso']],on=['id_inmueble','tipo'],how='left',validate='1:1')
    idd      = datapaso['valoringreso'].isnull()
    datapaso.loc[idd,'valoringreso'] = 0
    datapaso['valor'] = datapaso['valor']-datapaso['valoringreso']
    datapaso = datapaso[datapaso['tipo']=='GASTO']
    datapaso = datapaso[['id_inmueble','valor']]
    datapaso.columns = ['id_inmueble','gasto']
    
    return data,datapaso

@st.experimental_memo
def followup():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.app_callcenter_callhistory_inbound", engine) 
    return data

@st.experimental_memo
def inspeccion_callsample():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.app_callsample", engine) 
    data['fecha_asignacion_callagent']  = pd.to_datetime(data['fecha_asignacion_callagent'],errors='coerce')
    data['fecha_asignacion_visitagent'] = pd.to_datetime(data['fecha_asignacion_visitagent'],errors='coerce')
    return data

@st.experimental_memo
def inspeccion_visitas():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.app_callsample", engine) 
    data['fecha_asignacion_callagent']  = pd.to_datetime(data['fecha_asignacion_callagent'],errors='coerce')
    data['fecha_asignacion_visitagent'] = pd.to_datetime(data['fecha_asignacion_visitagent'],errors='coerce')

    # Historial de llamadas 
    datacallhistory  = pd.read_sql_query("SELECT * FROM colombia.app_callhistory;", engine) 

    # Caracteristicas
    datacaracteristicas = pd.read_sql_query("SELECT * FROM colombia.app_inspeccion_caracteristicas;", engine) 
    # Fotos
    datafotos    = pd.read_sql_query("SELECT * FROM colombia.app_seguimiento_fotos_visitas", engine)
    # Estado del ambiente 
    dataambiente = pd.read_sql_query("SELECT * FROM colombia.app_inspection_ambiente", engine) 

    grupofotos            = datafotos.groupby('id_unique')['url_foto'].apply('|'.join).reset_index()
    grupofotos.columns    = ['id','url_foto']
    dataambiente          = dataambiente.merge(grupofotos,on='id',how='left',validate='1:1')
    groupambiente         = dataambiente.groupby('id_inmueble').apply(create_json_group).reset_index(name='json')
    groupambiente['json'] = groupambiente['json'].apply(json.dumps)
    datacaracteristicas   = datacaracteristicas.merge(groupambiente,on='id_inmueble',how='outer')

    return data,datacaracteristicas,datacallhistory

@st.experimental_memo
def inspeccion_callhistory():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.app_callhistory", engine)
    data['call_date']  = pd.to_datetime(data['call_date'],errors='coerce')
    return data     
    
@st.experimental_memo
def inspeccion_seguimiento_ofertas():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_ofertas", engine)
    return data  

@st.experimental_memo
def inspeccion_seguimiento_ofertas_merge():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_ofertas", engine)
    idlist        = 'id_inmueble='+' OR id_inmueble='.join(data[data['id_inmueble'].notnull()]['id_inmueble'].astype(int).astype(str).unique())
    datacaracteristicas = pd.read_sql_query(f"SELECT * FROM colombia.app_inspeccion_caracteristicas WHERE {idlist}", engine)
    vardrop = [x for x in list(datacaracteristicas) if x in list(data)]
    vardrop.remove('id_inmueble')
    datacaracteristicas.drop(columns=vardrop,inplace=True)
    data = data.merge(datacaracteristicas,on='id_inmueble',how='left',validate='m:1')
    return data  

@st.experimental_memo
def datadocumentos():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT * FROM colombia.data_stock_inmuebles_documents", engine) 
    return data

@st.experimental_memo
def datarecorridos():
    # db_connection = sql.connect(user=user, password=password, host=host, database=schema)
    data          = pd.read_sql_query("SELECT fecha_recorrido,nombre_conjunto,direccion_formato, direccion_porteria, upzcodigo,scanombre,tipo_negocio,telefono1, telefono2,telefono3, latitud,longitud,url_foto_fachada,url_foto_direccion,status,coddir FROM colombia.app_recorredor_stock_ventanas", engine) 
    return data

@st.experimental_memo
def getdatamarketcoddir(filename,fcoddir):
    data = pd.read_pickle(filename,compression='gzip')
    if fcoddir is not None and fcoddir!="":
        data = data[data['coddir']==fcoddir]
    return data

@st.experimental_memo
def getdatamarketsimilar(filename,inputvar):
    data = pd.read_pickle(filename,compression='gzip')
    idd  = True
    if 'areaconstruida' in inputvar and inputvar['areaconstruida']>0:
        areamin = inputvar['areaconstruida']*0.8
        areamax = inputvar['areaconstruida']*1.2
        idd     = (idd) & (data['areaconstruida']>=areamin)  & (data['areaconstruida']<=areamax)
    if 'habitaciones' in inputvar and inputvar['habitaciones']>0:
        idd     = (idd) & (data['habitaciones']>=inputvar['habitaciones'])
    if 'banos' in inputvar and inputvar['banos']>0:
        idd     = (idd) & (data['banos']>=inputvar['banos'])
    if 'garajes' in inputvar and inputvar['garajes']>0:
        idd     = (idd) & (data['garajes']>=inputvar['garajes'])
    if 'estrato' in inputvar and inputvar['estrato']>0:
        idd     = (idd) & (data['estrato']==inputvar['estrato'])
    data = data[idd]
    return data

@st.experimental_memo
def getdatacatastro(filename):
    data = pd.read_pickle(filename,compression='gzip')
    if 'geometry' in data: del data['geometry']
    return data

def create_json_group(group):
    tipo_ambiente = group['tipo'].tolist()
    tipo_suelo    = group['tipo_suelo'].tolist()
    estado_suelo  = group['estado_suelo'].tolist()
    tipo_pared    = group['tipo_pared'].tolist()
    estado_pared  = group['estado_pared'].tolist()
    url_foto      = group['url_foto'].tolist()
    json_group = [{'tipo_ambiente': tipo_ambiente[i], 'tipo_suelo': tipo_suelo[i] , 'estado_suelo': estado_suelo[i] , 'tipo_pared': tipo_pared[i] , 'estado_pared': estado_pared[i] , 'url_foto': url_foto[i] } for i in range(len(tipo_ambiente))]
    return json_group