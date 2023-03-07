import streamlit as st
import copy

from datafunctions import propertydata
from currency import currencyoptions,getcurrency
from _dashboard_property import dashboard_property

# https://altair-viz.github.io/gallery/index.html
# https://plotly.streamlit.app/
# https://plotly.com/python/

st.set_page_config(layout="wide")

def id_inmueble_change():
    st.session_state.direccion       = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['direccion'].iloc[0]
    st.session_state.nombre_conjunto = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['nombre_conjunto'].iloc[0]
        
def direccion_change():
    st.session_state.id_inmueble     = st.session_state.data[st.session_state.data['direccion']==st.session_state.direccion]['id_inmueble'].iloc[0]
    st.session_state.nombre_conjunto = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['nombre_conjunto'].iloc[0]
        
def nombre_conjunto_change():
    st.session_state.id_inmueble = st.session_state.data[st.session_state.data['nombre_conjunto']==st.session_state.nombre_conjunto]['id_inmueble'].iloc[0]
    st.session_state.direccion   = st.session_state.data[st.session_state.data['id_inmueble']==st.session_state.id_inmueble]['direccion'].iloc[0]
   
@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


data = propertydata()
data = data.sort_values(by='id_inmueble',ascending=True)

formato = {'id_inmueble':data['id_inmueble'].iloc[0],'direccion':data['direccion'].iloc[0],'nombre_conjunto':data['nombre_conjunto'].iloc[0],'gestion_angulo':0}
for key,value in formato.items():
    if key not in st.session_state: 
        st.session_state[key] = value
        
if 'data' not in st.session_state: 
    st.session_state.data = copy.deepcopy(data)
    
col1, col2, col3, col4, col5 = st.columns([1,1,2,2,1])
with col1:
    currency    = st.selectbox('Moneda', options=currencyoptions())
    currencycal = getcurrency(currency)
    
with col2:
    id_inmueble = st.selectbox('ID', options=data['id_inmueble'],key='id_inmueble',on_change=id_inmueble_change)
with col3:
    direccion = st.selectbox('Direccion', options=data['direccion'],key='direccion',on_change=direccion_change)
with col4:
    nombre_conjunto = st.selectbox('Nombre del conjunto', options=data['nombre_conjunto'],key='nombre_conjunto',on_change=nombre_conjunto_change)

with col5:
    st.markdown('<div>&nbsp</div>', unsafe_allow_html=True)
    if st.button('Actualizar información'):
        st.experimental_memo.clear()
        st.experimental_rerun()    
        
dashboard_property(st.session_state.id_inmueble,currency=currency,currencycal=currencycal)