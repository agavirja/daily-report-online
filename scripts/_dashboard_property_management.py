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
from datafunctions import propertymanagementdata


   
def dashboard_property_management(id_inmueble=None,currency='COP',currencycal=1,fecha_inicial=None,fecha_final=None,seccion_flujo_pagos=True,seccion_property_management=True):
    
    datapm,datagasto = propertymanagementdata()
    
    # Currency 
    datapm['valor']  = pd.to_numeric(datapm['valor'],errors='coerce')
    datapm['valor']  = datapm['valor']/currencycal
    
    # Filtro por fechas
    datapm.index = range(len(datapm))
    idd          = datapm.index>=0
    if fecha_inicial is not None:
        idd = (idd) & (datapm['fecha_pago']>=fecha_inicial)
    if fecha_final is not None:
        idd = (idd) & (datapm['fecha_pago']<=fecha_final)
    
    datapm = datapm[idd]
    if seccion_flujo_pagos:
        datagasto = datapm[datapm['tipo'].isin(['GASTO','INGRESO'])]
        idd       = datagasto['tipo']=='GASTO'
        datagasto.loc[idd,'valor'] = datagasto.loc[idd,'valor']*(-1)
        if id_inmueble is not None: datagasto = datagasto[datagasto['id_inmueble']==id_inmueble]
        
        if datagasto.empty is False:
            st.write('---')
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-top: 5px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Flujo de Pagos</h1></div>', unsafe_allow_html=True)

            lista                       = list(datagasto['concepto'].unique())
            lista_flujoentrada_ingresos = ['ARRIENDO','PRORRATA (VENTA)']
            lista_flujosaluda_compra    = ['DESEMBOLSO 1 (COMPRA)', 'DESEMBOLSO 2 (COMPRA)', 'DESEMBOLSO 3 (COMPRA)', 'DESEMBOLSO ESCRITURAS (COMPRA)']
            lista_flujoentrada_venta    = ['INGRESO 1 (VENTA)', 'INGRESO 2 (VENTA)', 'INGRESO 3 (VENTA)', 'INGRESO ESCRITURAS (VENTA)']
        
            listaremove                 = lista_flujoentrada_ingresos+lista_flujosaluda_compra+lista_flujoentrada_venta
            lista_flujosalida_gastos    = [x for x in lista if x not in listaremove]
            datagasto['grupo_concepto'] = None
        
            idd = datagasto['concepto'].isin(lista_flujosalida_gastos)
            if sum(idd)>0:
                datagasto.loc[idd,'grupo_concepto'] = 'Flujo de gastos'
        
            idd = datagasto['concepto'].isin(lista_flujoentrada_ingresos)
            if sum(idd)>0:
                datagasto.loc[idd,'grupo_concepto'] = 'Flujo de ingresos'
                
            idd = datagasto['concepto'].isin(lista_flujosaluda_compra)
            if sum(idd)>0:
                datagasto.loc[idd,'grupo_concepto'] = 'Flujo de pagos por compra'
        
            idd = datagasto['concepto'].isin(lista_flujoentrada_venta)
            if sum(idd)>0:
                datagasto.loc[idd,'grupo_concepto'] = 'Flujo de ingresos por venta'
                
            col1, col2  = st.columns(2)
            df          = datagasto[['fecha_pago','grupo_concepto','valor']]
            df.columns  = ['fecha','grupo','valor']
            df          = df.set_index(['fecha'])
            g           = df.groupby([pd.Grouper(freq='M'),'grupo'])
            g           = pd.concat([g.sum()], axis=1).reset_index()
            g['fecha']  = g['fecha'].apply(lambda x: x.strftime("%b-%y"))
    
            with col1:
                if g.empty is False:
                    st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Flujo de desembolsos de compra e ingresos por venta</h1></div>', unsafe_allow_html=True)
                    ddf = g[g['grupo'].isin(['Flujo de pagos por compra','Flujo de ingresos por venta'])]
                    
                    if currency=='COP':
                        ddf['valorstr'] = ddf['valor']/1000000
                        ddf['valorstr'] = ddf['valorstr'].apply(lambda x: f"${x:,.0f} MM")
                    else:
                        ddf['valorstr'] = ddf['valor'].apply(lambda x: f"${x:,.0f} {currency}")
                    
                    if len(ddf)<8:
                        fig = px.bar(ddf, x='fecha', y='valor',barmode='group', color='grupo',text='valorstr',color_discrete_sequence=['#EF553B','#00CC96'])
                        fig.update_traces(textposition='outside')
                    else:
                        fig = px.bar(ddf, x='fecha', y='valor',barmode='group', color='grupo',color_discrete_sequence=['#EF553B','#00CC96'])
                                        
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
                    
            with col2:
                if g.empty is False:
                    st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Flujo de gastos e ingresos mensuales de los inmuebles</h1></div>', unsafe_allow_html=True)
                    ddf = g[g['grupo'].isin(['Flujo de gastos','Flujo de ingresos'])]
                    
                    if currency=='COP':
                        ddf['valorstr'] = ddf['valor']/1000000
                        ddf['valorstr'] = ddf['valorstr'].apply(lambda x: f"${x:,.0f} MM")
                    else:
                        ddf['valorstr'] = ddf['valor'].apply(lambda x: f"${x:,.0f} {currency}")
                    
                    if len(ddf)<8:
                        fig = px.bar(ddf, x='fecha', y='valor',barmode='group', color='grupo', text='valorstr',color_discrete_sequence=['#EF553B','#00CC96'])
                        fig.update_traces(textposition='outside')
                    else:
                        fig = px.bar(ddf, x='fecha', y='valor',barmode='group', color='grupo',color_discrete_sequence=['#EF553B','#00CC96'])
                    
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
                            
                # GRAFICA: TODOS LOS ELEMENTOS EN LA MISMA GRAFICA (LA MEDIDA DE LOS GRANDES DISTORCIONA LA MEDIDA DE LOS GASTOS PEQUEÑOS)
                #if g.empty is False:
                #    fig = px.bar(g, x='fecha', y='valor',barmode='group', color='grupo')
                #    fig.update_layout(
                #        plot_bgcolor='rgba(0, 0, 0, 0)',
                #        paper_bgcolor='rgba(0, 0, 0, 0)',
                #        xaxis_title='',
                #        yaxis_title='',
                #        legend_title_text=None,
                #        autosize=True,
                #        #xaxis={'tickangle': -90},
                #        #width=800, 
                #        #height=500
                #    )            
                #    st.plotly_chart(fig, theme="streamlit",use_container_width=True)      
    if seccion_property_management:
        
        formato = [{'grupo':'COMISION', 'variable':'COMISIÓN (COMPRA)'},
                   {'grupo':'COMISION', 'variable':'COMISIÓN (VENTA)'},
                   {'grupo':'ADMINISTRACION', 'variable':'ADMINISTRACIÓN'},
                   {'grupo':'PUBLICIDAD', 'variable':'PÚBLICACIÓN'},
                   {'grupo':'PUBLICIDAD', 'variable':'PUBLICIDAD'},
                   {'grupo':'SERVICIOS PUBLICOS', 'variable':'ENERGIA'},
                   {'grupo':'SERVICIOS PUBLICOS', 'variable':'ACUEDUCTO Y ALCANTARILLADO'},
                   {'grupo':'SERVICIOS PUBLICOS', 'variable':'GAS'},
                   {'grupo':'SERVICIOS PUBLICOS', 'variable':'ASEO'},
                   {'grupo':'GASTOS TRANSFERENCIA', 'variable':'COSTO CHEQUE'},
                   {'grupo':'GASTOS TRANSFERENCIA', 'variable':'PRORRATA (COMPRA)'},
                   {'grupo':'IMPUESTO', 'variable':'IMPUESTO 4X1000'},
                   {'grupo':'IMPUESTO', 'variable':'PREDIALES'},
                   {'grupo':'IMPUESTO', 'variable':'ICA (VENTA)'},
                   {'grupo':'INGRESOS ADICIONALES', 'variable':'PRORRATA (VENTA)'},
                   {'grupo':'INGRESOS ADICIONALES', 'variable':'ARRIENDO'},
                   {'grupo':'NOTARIALES', 'variable':'AUTENTICACIÓN (COMPRA)'},
                   {'grupo':'NOTARIALES', 'variable':'AUTENTICACIÓN (VENTA)'},
                   {'grupo':'NOTARIALES', 'variable':'BENEFICIENCIA Y REGISTRO'},
                   {'grupo':'NOTARIALES', 'variable':'DERECHOS NOTARIALES (COMPRA)'},
                   {'grupo':'NOTARIALES', 'variable':'DERECHOS NOTARIALES (VENTA)'},
                   {'grupo':'NOTARIALES', 'variable':'DERECHOS NOTARIALES LEVANTAMIENTO HIPOTECA (COMPRA)'},
                   {'grupo':'NOTARIALES', 'variable':'RETENCION EN LA FUENTE (VENDEDOR)'},
                   {'grupo':'NOTARIALES', 'variable':'RETENCION EN LA FUENTE (VENTA)'},
                   {'grupo':'NOTARIALES', 'variable':'RETENCION EN LA FUENTE (COMPRADOR)'},
                   {'grupo':'OTROS GASTOS', 'variable':'OTROS GASTOS (VENTA)'},
                   {'grupo':'OTROS GASTOS', 'variable':'OTROS GASTOS (COMPRA)'},
                   {'grupo':'OTROS GASTOS', 'variable':'CTL'},
                   {'grupo':'REMODELACION', 'variable':'PINTURA'},
                   {'grupo':'REMODELACION', 'variable':'OTROS GASTOS DE ADECUACIÓN'},
                   {'grupo':'REMODELACION', 'variable':'PISOS'},
                   {'grupo':'REMODELACION', 'variable':'BAÑOS'}]
        
        datapaso = pd.DataFrame(formato)
        vector1  = datapaso['variable'].to_list()
        vector2  = datapaso['grupo'].to_list()
        
        datacuentas           = datapm[datapm['tipo'].isin(['GASTO','INGRESO'])]
        lista_concepto_remove = lista_flujosaluda_compra+lista_flujoentrada_venta
        idd = datacuentas['concepto'].isin(lista_concepto_remove)
        if sum(idd)>0:
            datacuentas = datacuentas[~idd]
        datacuentas = datacuentas[datacuentas['concepto'].isin(vector1)]
        if id_inmueble is not None: datacuentas = datacuentas[datacuentas['id_inmueble']==id_inmueble]
        datacuentas['grupo'] = datacuentas['concepto'].replace(vector1,vector2)
        
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Tipo de gasto</h1></div>', unsafe_allow_html=True)
            df = datacuentas[datacuentas['grupo'].notnull()]
            df = df.groupby('grupo')['valor'].sum().reset_index()
            df = df.sort_values(by='valor',ascending=True)
            fig = px.pie(df, values='valor', names='grupo', hole=.3, color_discrete_sequence=px.colors.sequential.RdBu[::-1])
            st.plotly_chart(fig, theme="streamlit",use_container_width=True)  

        with col2:
            st.markdown('<div style="background-color: #f7f7f7; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 14px; text-align: center; color: #3A5AFF;">Property Management</h1></div>', unsafe_allow_html=True)
            df          = datacuentas[datacuentas['grupo'].isin(['ADMINISTRACION','PUBLICIDAD','SERVICIOS PUBLICOS','REMODELACION'])]
            df          = df[['fecha_pago','grupo','valor']]
            df.columns  = ['fecha','grupo','valor']
            df          = df.set_index(['fecha'])
            g           = df.groupby([pd.Grouper(freq='M'),'grupo'])
            g           = pd.concat([g.sum()], axis=1).reset_index()
            g['fecha']  = g['fecha'].apply(lambda x: x.strftime("%b-%y"))
            
            if g.empty is False:
                
                if currency=='COP':
                    g['valorstr'] = g['valor']/1000000
                    g['valorstr'] = g['valorstr'].apply(lambda x: f"${x:,.0f} MM")
                else:
                    g['valorstr'] = g['valor'].apply(lambda x: f"${x:,.0f} {currency}")
                
                if len(ddf)<8:
                    fig = px.bar(g, x='fecha', y='valor', barmode='group', color='grupo', text='valorstr')
                    fig.update_traces(textposition='outside')
                else:
                    fig = px.bar(g, x='fecha', y='valor', barmode='group', color='grupo')

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