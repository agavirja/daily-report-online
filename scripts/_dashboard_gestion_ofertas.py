import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
from bs4 import BeautifulSoup
from datetime import datetime


import sys
sys.path.insert(0, '/scripts')
from html_scripts import boxkpi,boxnumberpercentage
from datafunctions import inspeccion_callsample,inspeccion_callhistory,inspeccion_seguimiento_ofertas

# px.colors.named_colorscales()
# color_continuous_scale=px.colors.sequential.Viridis / invers: px.colors.sequential.Viridis[::-1]
# color_discrete_sequence=px.colors.qualitative.Vivid

def dashboard_gestion_ofertas(comercial=None,modulo_gestion_lead=True,modulo_seguimiento_ofertas=True,modulo_inconsistencias=True):
    
    data                  = inspeccion_callsample()
    datacallhistory       = inspeccion_callhistory()
    dataseguimientofertas = inspeccion_seguimiento_ofertas()
    
    if modulo_gestion_lead:
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Gestión de Inmuebles de Oportunidad</h1></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            totalregistros     = len(data['id_inmueble'].unique())
            sinasignacion_call = len(data[data['fecha_asignacion_callagent'].isnull()]['id_inmueble'].unique())
            html               = boxnumberpercentage(totalregistros,f'({sinasignacion_call} sin asignar)','Total oportundiades')
            html_struct        = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col2:
            asignacion_call     = len(data[data['fecha_asignacion_callagent'].notnull()]['id_inmueble'].unique())
            por_asignacion_call = asignacion_call/totalregistros
            por_asignacion_call = "{:.1%}".format(por_asignacion_call)
            html          = boxnumberpercentage(asignacion_call,f'({por_asignacion_call})','Llamada asignada')
            html_struct   = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col3:
            asignacion_visit     = len(data[data['fecha_asignacion_visitagent'].notnull()]['id_inmueble'].unique())
            por_asignacion_visit = asignacion_visit/asignacion_call
            por_asignacion_visit = "{:.1%}".format(por_asignacion_visit)
            html          = boxnumberpercentage(asignacion_visit,f'({por_asignacion_visit})','Visita asignada')
            html_struct   = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)   

        with col4:
            estado_pendiente     = len(data[data['finalizado'].str.lower()=='pendiente']['id_inmueble'].unique())
            por_estado_pendiente = estado_pendiente/asignacion_visit
            por_estado_pendiente = "{:.1%}".format(por_estado_pendiente)
            html          = boxnumberpercentage(estado_pendiente,f'({por_estado_pendiente})','Pendiente de visita')
            html_struct   = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True) 
            
        with col5:
            estado_finalizado     = len(data[data['finalizado'].str.lower()=='finalizado']['id_inmueble'].unique())
            por_estado_finalizado = estado_finalizado/asignacion_visit
            por_estado_finalizado = "{:.1%}".format(por_estado_finalizado)
            html          = boxnumberpercentage(estado_finalizado,f'({por_estado_finalizado})','Visita Finalizada')
            html_struct   = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True) 

        datacallhistory                = datacallhistory[datacallhistory['id_inmueble'].notnull()]
        datacallhistory['call_status'] = datacallhistory['call_status'].replace(['NÚMERO EQUIVOCADO','DESISTE COMERCIALIZACIÓN','NO HAY COMUNICACIÓN'],['NUMERO EQUIVOCADO','DESISTE COMERCIALIZACION','NO CONTESTA'])
        datacallhistory['order']       = datacallhistory['call_status'].replace(['EFECTIVA', 'NUMERO EQUIVOCADO', 'NO CUMPLE CON REQUISITOS','DESISTE COMERCIALIZACION','VENDIDO', 'ARRENDADO', 'NO NEGOCIABLE', 'HACER SEGUIMIENTO', 'NO CONTESTA'],[1,2,3,4,5,6,7,8,9])
        datacallhistory                = datacallhistory[datacallhistory['order'].notnull()]
        datacallhistory                = datacallhistory.sort_values(by='order',ascending=True).drop_duplicates(subset='id_inmueble',keep='first')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Llamadas contestadas</h1></div>', unsafe_allow_html=True)
            df          = datacallhistory[['call_status']]
            df          = df[df['call_status'].notnull()]
            df['count'] = 1
            df          = df.groupby('call_status')['count'].count().reset_index()
            df.columns  = ['call_status','count']
            df          = df.sort_values(by='count',ascending=False)
            df['colors'] = px.colors.sequential.Viridis[0:len(df)]
            
            if df.empty is False:
                # color_continuous_scale=px.colors.sequential.Viridis / invers: px.colors.sequential.Viridis[::-1]
                # color_discrete_sequence=px.colors.qualitative.Vivid
                fig = px.bar(df, x='call_status', y='count', text='count', color='count',color_continuous_scale=px.colors.sequential.RdBu)
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
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Fuente del Lead</h1></div>', unsafe_allow_html=True)
            df          = data[['procedencia']]
            df          = df[df['procedencia'].notnull()]
            df['count'] = 1
            df          = df.groupby('procedencia')['count'].count().reset_index()
            df.columns  = ['procedencia','count']
            df          = df.sort_values(by='count',ascending=False)
            
            if df.empty is False:
                fig = px.bar(df, x='procedencia', y='count', text='count',color='count',color_continuous_scale=px.colors.sequential.RdBu)
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
                
        with col3:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Visitas realizadas</h1></div>', unsafe_allow_html=True)
            df          = data[['fecha_asignacion_visitagent','finalizado','id_inmueble']]
            df          = df[df['finalizado'].str.lower()=='finalizado'].drop_duplicates(subset='id_inmueble',keep='first')
            df['count'] = 1
            df          = df[['fecha_asignacion_visitagent','count']]
            df.columns  = ['fecha','count']
            df          = df.set_index(['fecha'])
            g           = df[['count']].groupby(pd.Grouper(freq='M'))
            g           = pd.concat([g.sum()], axis=1).reset_index()
            g['fecha']  = g['fecha'].apply(lambda x: x.strftime("%b-%y"))

            if g.empty is False:
                fig = px.bar(g, x='fecha', y='count', text='count',  color_discrete_sequence=['#2166ac'])
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_title='',
                    yaxis_title='',
                    legend_title_text=None,
                    autosize=True,
                    #xaxis={'tickangle': -90},
                    #width=800, 
                    #height=500
                )            
                st.plotly_chart(fig, theme="streamlit",use_container_width=True)                
        
    if modulo_seguimiento_ofertas:
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Seguimiento de Ofertas Realizadas</h1></div>', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            estado_finalizado = len(data[data['finalizado'].str.lower()=='finalizado']['id_inmueble'].unique())
            html              = boxnumberpercentage(estado_finalizado,'&nbsp;','# Visitas')
            html_struct       = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col2:
            totalofertas       = len(dataseguimientofertas[dataseguimientofertas['estado'].notnull()])
            por_totalofertas   = totalofertas/estado_finalizado
            por_totalofertas   = "{:.1%}".format(por_totalofertas)
            html               = boxnumberpercentage(totalofertas,f'({por_totalofertas})','Total ofertas realizadas')
            html_struct        = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col3:
            rechazadas         = sum(dataseguimientofertas['estado'].str.lower()=='rechazada')
            por_rechazadas     = rechazadas/totalofertas
            por_rechazadas     = "{:.1%}".format(por_rechazadas)
            html               = boxnumberpercentage(rechazadas,f'({por_rechazadas})','Ofertas rechazadas')
            html_struct        = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col4:
            aceptadas          = sum(dataseguimientofertas['estado'].str.lower()=='comprado')
            por_aceptadas      = aceptadas/totalofertas
            por_aceptadas      = "{:.1%}".format(por_aceptadas)
            html               = boxnumberpercentage(aceptadas,f'({por_aceptadas})','Ofertas aceptadas')
            html_struct        = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

        with col5:
            pendientes          = sum(dataseguimientofertas['estado'].str.lower().str.contains('pendiente'))
            por_pendientes      = pendientes/totalofertas
            por_pendientes      = "{:.1%}".format(por_pendientes)
            html               = boxnumberpercentage(pendientes,f'({por_pendientes})','Pendientes de respuesta')
            html_struct        = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Estado de las ofertas</h1></div>', unsafe_allow_html=True)
            df          = dataseguimientofertas[['fecha_oferta','estado']]
            df['count'] = 1
            df.columns  = ['fecha','estado','count']
            df          = df.set_index(['fecha'])
            g           = df.groupby([pd.Grouper(freq='M'),'estado'])
            g           = pd.concat([g.sum()], axis=1).reset_index()
            g           = g[g['count']>0]
            g['fecha']  = g['fecha'].apply(lambda x: x.strftime("%b-%y"))

            if g.empty is False:
                fig = px.bar(g, x='fecha', y='count', text='count', barmode='group', color='estado')
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_title='',
                    yaxis_title='',
                    legend_title_text=None,
                    autosize=True,
                    legend=dict(
                        orientation="h",
                        entrywidth=70,
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1),
                    #xaxis={'tickangle': -90},
                    #width=800, 
                    #height=500
                )            
                st.plotly_chart(fig, theme="streamlit",use_container_width=True)         

        with col2:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Asesor</h1></div>', unsafe_allow_html=True)
            df          = dataseguimientofertas[['asesor']]
            df          = df[df['asesor'].notnull()]
            df['count'] = 1
            df          = df.groupby('asesor')['count'].count().reset_index()
            df.columns  = ['asesor','count']
            df          = df.sort_values(by='count',ascending=False)
            
            if df.empty is False:
                fig = px.bar(df, x='asesor', y='count', text='count', color='count',color_continuous_scale=px.colors.sequential.RdBu)
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

        with col3:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Data de Ofertas Pendientes</h1></div>', unsafe_allow_html=True)
            datapaso = dataseguimientofertas[dataseguimientofertas['estado'].str.lower().str.contains('pendiente')][['id', 'id_inmueble', 'asesor', 'direccion', 'nombre_conjunto', 'areaconstruida', 'habitaciones', 'banos', 'garajes', 'piso', 'depositos', 'url', 'valoradministracion', 'precio_publicacion', 'precio_maximo', 'precio_oferta', 'fecha_oferta', 'precio_compra', 'observaciones', 'estado']]
            for i in ['areaconstruida', 'habitaciones', 'banos', 'garajes', 'piso', 'depositos']:
                datapaso[i] = pd.to_numeric(datapaso[i],errors='coerce')
                idd = datapaso[i]>=0
                if sum(idd)>0:
                    datapaso.loc[idd,i] = datapaso.loc[idd,i].astype(int).astype(str)
            for i in ['valoradministracion', 'precio_publicacion', 'precio_maximo', 'precio_oferta', 'fecha_oferta', 'precio_compra']:
                datapaso[i] = pd.to_numeric(datapaso[i],errors='coerce')
                idd = datapaso[i]>=0
                if sum(idd)>0:
                    datapaso.loc[idd,i] = datapaso.loc[idd,i].apply(lambda x: f"${x:,.0f}")       
            datapaso.index = range(len(datapaso))                     
            st.dataframe(datapaso)