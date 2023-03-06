import streamlit as st
import copy

import sys
sys.path.insert(0, '/scripts')
from datafunctions import propertydata
from currency import currencyoptions,getcurrency
from _dashboard_gestion_callcenter_inbound import dashboard_gestion_callcenter_inbound
from _dashboard_gestion_ofertas import dashboard_gestion_ofertas
from _dashboard_property_management import dashboard_property_management
from _dashboard_recorrido import dashboard_recorrido

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

# Gestion call center
if id_inmueble=='Todos': id_inmueble = None
dashboard_gestion_callcenter_inbound(id_inmueble=id_inmueble)

# Gestion operativa
dashboard_gestion_ofertas()

# Property Management 
dashboard_property_management(id_inmueble=id_inmueble,currency=currency,currencycal=currencycal)


# Recorrido
dashboard_recorrido()
