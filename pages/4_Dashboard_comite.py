import streamlit as st
import copy


from datafunctions import inspeccion_callsample
from currency import currencyoptions,getcurrency
from _dashboard_comite import dashboard_comite



st.set_page_config(layout="wide")

data = inspeccion_callsample()

col1, col2, col3, col4,col5 = st.columns([1,1,2,2,1])
with col1:
    currency    = st.selectbox('Moneda', options=currencyoptions())
    currencycal = getcurrency(currency)
    
with col2:
    id_inmueble = st.selectbox('ID', options=data['id_inmueble'],key='id_inmueble')
with col5:
    st.markdown('<div>&nbsp</div>', unsafe_allow_html=True)
    if st.button('Actualizar información'):
        st.experimental_memo.clear()
        st.experimental_rerun()     
        
# Dashboard Comite
dashboard_comite(id_inmueble)

