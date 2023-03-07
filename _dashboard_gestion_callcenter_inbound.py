import streamlit as st
import pandas as pd
import re
import plotly.express as px
from bs4 import BeautifulSoup
from datetime import datetime

from html_scripts import boxkpi,boxnumberpercentage
from datafunctions import propertydata,followup

def phonenumber(x):
    try: return re.sub('[^0-9]','',str(x))
    except: return None
    
@st.experimental_memo
def datacallcenter(id_inmueble=None):
    datafollowup = followup()
    datafollowup = datafollowup[datafollowup['id_inmueble'].notnull()]
    if id_inmueble is not None:
        datafollowup = datafollowup[datafollowup['id_inmueble']==id_inmueble]
    datafollowup['contact_number'] = datafollowup['contact_number'].apply(lambda x: phonenumber(x))    
    return datafollowup

    
#---------------------------------------------------------------------#
# Gestion del inmueble

def dashboard_gestion_callcenter_inbound(id_inmueble=None,modulo_callcenter=True,modulo_callcenter_fallas=True):
    
    data         = propertydata()
    datafollowup = datacallcenter(id_inmueble)
    if datafollowup.empty is False:
        if modulo_callcenter:
            st.write('---')
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Gestión Call Center Inbound</h1></div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                totalllamadas = len(datafollowup)
                #html          = boxkpi(totalllamadas,'Total llamadas')
                html          = boxnumberpercentage(totalllamadas,'&nbsp;','Total llamadas')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)
    
            with col2:
                telunicos     = len(datafollowup['contact_number'].unique())
                por_telunicos = telunicos/totalllamadas
                por_telunicos = "{:.1%}".format(por_telunicos)
                html          = boxnumberpercentage(telunicos,f'({por_telunicos})','Total llamadas de números unicos')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)
    
            with col3:            
                datafollowup['fecha'] = pd.to_datetime(datafollowup['date_visit'],errors='coerce')
                visitasagendadas      = sum(datafollowup['fecha'].notnull())
                por_visitasagendadas  = visitasagendadas/telunicos
                por_visitasagendadas  = "{:.1%}".format(por_visitasagendadas)
                html        = boxnumberpercentage(visitasagendadas,f'({por_visitasagendadas})','Total visitas agendadas')
                html_struct = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)            
    
            with col4:
                visitascheck     = sum(datafollowup['visit_check']==1)
                por_visitascheck = visitascheck/visitasagendadas
                por_visitascheck = "{:.1%}".format(por_visitascheck)
                html        = boxnumberpercentage(visitascheck,f'({por_visitascheck})','Total visitas realizadas')
                html_struct = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)            
        
            if id_inmueble is None:
                col1, col2, col3 = st.columns(3)
            else:
                col1, col2 = st.columns(2)
                
            with col1:
                st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;"># Llamadas y visitas</h1></div>', unsafe_allow_html=True)
                
                df          = datafollowup[['call_date','contact_number']].drop_duplicates(subset='contact_number',keep='first')
                df          = df[['call_date']]
                df['count'] = 1
                df.columns  = ['fecha','valor']
                df['fecha'] = pd.to_datetime(df['fecha'],errors='coerce')
                df          = df.set_index(['fecha'])
                bplot           = df[['valor']].groupby(pd.Grouper(freq='M'))
                bplot           = pd.concat([bplot.sum()], axis=1).reset_index()
                bplot.columns   = ['fecha','valor']
                bplot['fecha']  = bplot['fecha'].apply(lambda x: x.strftime("%b-%y"))
                bplot           = bplot[bplot['valor']>0]
                bplot['grupo']  = 'Llamadas'
                
                df               = datafollowup[['date_visit','visit_check']]
                df['date_visit'] = pd.to_datetime(df['date_visit'],errors='coerce')
                df               = df[df['visit_check']==1]
                df.columns       = ['fecha','valor']
                df               = df.set_index(['fecha'])
                g                = df[['valor']].groupby(pd.Grouper(freq='M'))
                g                = pd.concat([g.sum()], axis=1).reset_index()
                g.columns        = ['fecha','valor']
                g['fecha']       = g['fecha'].apply(lambda x: x.strftime("%b-%y"))
                g                = g[g['valor']>0]
                g['grupo']       = 'Visitas'
                bplot            = bplot.append(g)
                
                if bplot.empty is False:
                    fig = px.bar(bplot, x='fecha', y='valor', barmode='group',color='grupo', text='valor', color_discrete_sequence=['#2166ac','#d6604d'])
                    fig.update_traces(texttemplate='%{text:.0s}', textposition='outside')
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
                st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Fuente de las llamadas</h1></div>', unsafe_allow_html=True)
                df          = datafollowup[['fuente_llamada']]
                df          = df[df['fuente_llamada'].notnull()]
                df['count'] = 1
                df          = df.groupby('fuente_llamada')['count'].count().reset_index()
                df.columns  = ['fuente','count']
                df          = df.sort_values(by='count',ascending=False)
                
                if df.empty is False:
                    fig = px.bar(df, x='fuente', y='count', text='count', color='count',color_continuous_scale=px.colors.sequential.RdBu)
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        xaxis_title='',
                        yaxis_title='',
                        legend_title_text=None,
                        showlegend=False,
                        coloraxis_showscale=False,
                        #width=800, 
                        #height=500
                    )            
                    st.plotly_chart(fig, theme="streamlit",use_container_width=True)
                    
            if id_inmueble is None:
                with col3:
                    st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Llamadas y visitas por inmuebles disponibles</h1></div>', unsafe_allow_html=True)
    
                    idd = (data['estado_venta']=='VENDIDO') | (data['estado_venta'].isnull())
                    if sum(~idd)>0:
                        vectorids   = data[~idd]['id_inmueble'].unique()
                        df          = datafollowup[['id_inmueble']]
                        df          = df[df['id_inmueble'].isin(vectorids)]
                        df          = df[df['id_inmueble'].notnull()]
                        df['count'] = 1
                        df          = df.groupby('id_inmueble')['count'].count().reset_index()
                        df.columns  = ['id_inmueble','count']
                        df          = df.sort_values(by='id_inmueble',ascending=True)
                        df['id_inmueble'] = df['id_inmueble'].astype(int).astype(str)
                        df['grupo']       = 'Llamadas'
                        
                        dfappend          = datafollowup[['id_inmueble','visit_check']]
                        dfappend          = dfappend[dfappend['visit_check']==1]
                        dfappend          = dfappend[['id_inmueble']]
                        dfappend          = dfappend[dfappend['id_inmueble'].isin(vectorids)]
                        dfappend          = dfappend[dfappend['id_inmueble'].notnull()]
                        dfappend['count'] = 1
                        dfappend          = dfappend.groupby('id_inmueble')['count'].count().reset_index()
                        dfappend.columns  = ['id_inmueble','count']
                        dfappend          = dfappend.sort_values(by='id_inmueble',ascending=True)
                        dfappend['id_inmueble'] = dfappend['id_inmueble'].astype(int).astype(str)
                        dfappend['grupo']       = 'Visitas'
                        
                        df = df.append(dfappend)
                        
                        if df.empty is False:
                            fig = px.bar(df, x='id_inmueble', y='count', barmode='group',color='grupo', text='count',color_discrete_sequence=['#2166ac','#d6604d'])
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
                 
        if modulo_callcenter_fallas:
            st.write('---')
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Inconsistencias Call Center</h1></div>', unsafe_allow_html=True)
    
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                sinfuente     = sum(datafollowup['fuente_llamada'].isnull()) + sum(datafollowup['fuente_llamada']=='')
                html          = boxkpi(sinfuente,'# Registros sin fuente de llamada')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)
    
            with col2:
                sinnombre     = sum(datafollowup['nombre_cliente'].isnull()) + sum(datafollowup['nombre_cliente']=='')
                html          = boxkpi(sinnombre,'# Registros sin nombre del cliente')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)
    
            with col3:            
                idd           = datafollowup['contact_number'].apply(lambda x: re.sub('[^0-9]','',str(x))=='')
                html          = boxkpi(sum(idd),'# Registros sin telefono')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)          
    
            with col4:
                idd              = ((datafollowup['visit_check']==0) | (datafollowup['visit_check'].isnull())) & (datafollowup['date_visit']<datetime.now().strftime("%Y-%m-%d"))
                html          = boxkpi(sum(idd),'# Visitas agendadas sin visita realizada')
                html_struct   = BeautifulSoup(html, 'html.parser')
                st.markdown(html_struct, unsafe_allow_html=True)           
            