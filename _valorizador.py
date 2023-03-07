import streamlit as st
import re
import copy
import folium
import string
import random
import pandas as pd
import numpy as np
import mysql.connector as sql
import geopandas as gpd
from shapely.geometry import  Point,Polygon
from streamlit_folium import st_folium
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

from forecast_pricing_comercial import forecast_pricing_comercial
from datafunctions import propertydata,getdatamarketcoddir,getdatamarketsimilar

@st.experimental_memo
def getpolygon(metros,lat,lng):
    grados   = np.arange(-180, 190, 10)
    Clat     = ((metros/1000.0)/6371.0)*180/np.pi
    Clng     = Clat/np.cos(lat*np.pi/180.0)
    theta    = np.pi*grados/180.0
    longitud = lng + Clng*np.cos(theta)
    latitud  = lat + Clat*np.sin(theta)
    return Polygon([[x, y] for x,y in zip(longitud,latitud)])

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def valorizador(id_inmueble,inputvar={},currency='COP',currencycal=1):
    
    if id_inmueble is not None:
        data        = propertydata()
        data        = data[data['id_inmueble']==id_inmueble]
        datanalisis = data[['ciudad', 'scacodigo', 'tipoinmueble', 'direccion', 'nombre_conjunto', 'areaconstruida', 'habitaciones', 'banos', 'garajes', 'estrato', 'piso', 'antiguedad', 'ascensores', 'numerodeniveles', 'coddir', 'latitud', 'longitud']]
        
        datanalisis["nombre_edificio"] = copy.deepcopy(datanalisis["nombre_conjunto"])
        datanalisis["num_piso"]        = copy.deepcopy(datanalisis["piso"])
        datanalisis["anos_antiguedad"] = data["antiguedad_min"].apply(lambda x: datetime.now().year-x)
        datanalisis["num_ascensores"]  = copy.deepcopy(datanalisis["ascensores"])
        datanalisis["metros"]  = 400
        
        inputvar = datanalisis.to_dict(orient='records')[0]

    if 'dataexport' not in st.session_state: 
        st.session_state.dataexport = pd.DataFrame()
    #---------------------------------------------------------------------#
    # Forecast
    with st.spinner():
        if inputvar!={}:
            inputvar["tiponegocio"]          = 'Venta'
            inputvar["forecast_venta"]       = forecast_pricing_comercial(inputvar)/currencycal
            inputvar["forecast_ventamt2"]    = inputvar["forecast_venta"]/inputvar['areaconstruida']
            inputvar["tiponegocio"]          = 'Arriendo'
            inputvar["forecast_arriendo"]    = forecast_pricing_comercial(inputvar)/currencycal
            inputvar["forecast_arriendomt2"] = inputvar["forecast_arriendo"]/inputvar['areaconstruida']
            
            inputvar["forecast_ventastr"]       = ''
            inputvar["forecast_ventamt2str"]    = ''
            inputvar["forecast_arriendostr"]    = ''
            inputvar["forecast_arriendomt2str"] = ''

            if currency=='COP':
                try:
                    inputvar["forecast_ventastr"]    = f'${round(inputvar["forecast_venta"] / 1000)* 1000:,.0f}'
                    inputvar["forecast_ventamt2str"] = f'${round(inputvar["forecast_ventamt2"] / 1000)* 1000 :,.0f} mt\u00B2'
                except:  pass
                try: 
                    inputvar["forecast_arriendostr"]    = f'${round(inputvar["forecast_arriendo"] / 1000)* 1000:,.0f}'
                    inputvar["forecast_arriendomt2str"] = f'${round(inputvar["forecast_arriendomt2"] / 1000)* 1000:,.0f} mt\u00B2'
                except: pass
            else:
                try:
                    inputvar["forecast_ventastr"]    = f'${round(inputvar["forecast_venta"]):,.0f}'
                    inputvar["forecast_ventamt2str"] = f'${round(inputvar["forecast_ventamt2"]):,.0f} mt\u00B2'
                except:  pass
                try: 
                    inputvar["forecast_arriendostr"]    = f'${round(inputvar["forecast_arriendo"]):,.0f}'
                    inputvar["forecast_arriendomt2str"] = f'${round(inputvar["forecast_arriendomt2"]):,.0f} mt\u00B2'
                except: pass
                
    #-----------------------------------------------------------------------------#
    # Resultados
    col1, col2, col3 = st.columns(3)
    with col1:
        tiponegocio = st.selectbox('Tipo de negocio',options=['Venta','Arriendo'])
    with col2:
        filtro      = st.selectbox('Filtro por:', options=['Sin filtrar','Menor precio','Mayor precio','Menor área','Mayor área','Menor habitaciones','Mayor habitaciones'])
    with col3: 
        st.text('Descargar data de mercado')
        csv = convert_df(st.session_state.dataexport)
        st.download_button(
           "download",
           csv,
           f"archivo_inmueble_{id_inmueble}.csv",
           "text/csv",
           key='download-forecast'
        ) 
            
    col1, col2, col3 = st.columns([2,3,3])
    with col1:
        with st.spinner():
            if inputvar!={} and (('forecast_ventastr' in inputvar and inputvar['forecast_ventastr']!='') or ('forecast_arriendostr' in inputvar and inputvar['forecast_arriendostr']!='')):
                
                formato = [{"name":"Valor de venta estimado","value":inputvar['forecast_ventastr']},
                           {"name":"Valor de venta estimado por mt\u00B2","value":inputvar['forecast_ventamt2str']},
                           {"name":"Valor de arriendo estimado","value":inputvar['forecast_arriendostr']},
                           {"name":"Valor de arriendo estimado por mt\u00B2","value":inputvar['forecast_arriendomt2str']},
                           ]
            
                html = ""
                for i in formato:
                    if i["value"] is not None and i["value"]!='':
                        html += f"""
                            <tr>
                                <td><b>{i["name"]}</b> {currency}</td>
                                <td><b>{i["value"]}</b> {currency}</td>
                            </tr>
                        """
                
                style = """
                <style>
                        #tblStocks {
                          font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                          border-collapse: collapse;
                          width: 100%;
                        }
                        #tblStocks td, #tblStocks th {
                          border: 1px solid #ddd;
                          padding: 8px;
                        }
                        #tblStocks tr:nth-child(even){background-color: #f2f2f2;}
                        #tblStocks tr:hover {background-color: #ddd;}
                        #tblStocks th {
                            padding-top: 12px;
                            padding-bottom: 12px;
                            text-align: center;
                            background-color: #294c67;;
                            color: white;
                          }
                        .tabla {
                          margin-bottom: 50px;
                        }  
                </style>
                """
                texto = f"""
                <html>
                {style}
                <body>
                    <table id="tblStocks" cellpadding="0" cellspacing="50" class="tabla">
                    <tr>
                        <th colspan="2">Precio de referencia</th>
                    </tr>
                    {html}
                    </table>
                </body>
                </html>
                """       
                texto = BeautifulSoup(texto, 'html.parser')
                st.markdown(texto, unsafe_allow_html=True)  
                
    with col2:
        fcoddir   = inputvar['coddir']
        latitud   = inputvar['latitud']
        longitud  = inputvar['longitud']
        
        if 'venta' in tiponegocio.lower():
            filename    = 'data/data_market_venta_bogota'
            vardep      = 'valorventa'
            varforecast = 'forecast_venta'
        
        if 'arriendo' in tiponegocio.lower():
            filename    = 'data/data_market_arriendo_bogota'
            vardep      = 'valorarriendo'
            varforecast = 'forecast_arriendo'
        
        datacomparables = getdatamarketcoddir(filename,fcoddir)
        datasimilares   = getdatamarketsimilar(filename,inputvar) 
        
        datacomparables[vardep] = datacomparables[vardep]/currencycal
        datasimilares[vardep]   = datasimilares[vardep]/currencycal
        
        if datacomparables.empty is False:
            datacomparables['tipobusqueda'] = '<p1>Mismo Edificio</p1>'
        if datasimilares.empty is False:
            poly                      = getpolygon(inputvar['metros'],latitud,longitud)
            datasimilares['geometry'] = datasimilares.apply(lambda x: Point(x['longitud'],x['latitud']),axis=1)
            datasimilares             = gpd.GeoDataFrame(datasimilares, geometry='geometry')
            idd                       = datasimilares['geometry'].apply(lambda x: poly.contains(x))
            datasimilares             = datasimilares[idd]
            idd                       = datasimilares['coddir']==fcoddir
            datasimilares             = datasimilares[~idd]

            idd           = (datasimilares[vardep]>=(inputvar[varforecast]*0.8)) & (datasimilares[vardep]<=(inputvar[varforecast]*1.2))
            datasimilares = datasimilares[idd]
            datasimilares = datasimilares.sort_values(by=vardep,ascending=True)
            datasimilares['tipobusqueda'] = '<p2>Similares en la zona</p2>'
            datacomparables               = datacomparables.append(datasimilares)
        
        if datacomparables.empty is False:
            datacomparables = datacomparables[['code','direccion','tiponegocio','areaconstruida','habitaciones','banos','garajes','estrato','imagen_principal','valorventa','valorarriendo','tipobusqueda','latitud','longitud','fuente','url']]
            datacomparables = datacomparables[(datacomparables['areaconstruida']>=inputvar['areaconstruida']*0.85) & (datacomparables['areaconstruida']<=inputvar['areaconstruida']*1.15)]
    
            if filtro=='Menor precio':
                datacomparables = datacomparables.sort_values(by=[vardep],ascending=True)
            if filtro=='Mayor precio':
                datacomparables = datacomparables.sort_values(by=[vardep],ascending=False)
            if filtro=='Menor área':
                datacomparables = datacomparables.sort_values(by=['areaconstruida'],ascending=True)
            if filtro=='Mayor área':
                datacomparables = datacomparables.sort_values(by=['areaconstruida'],ascending=False)
            if filtro=='Menor habitaciones':
                datacomparables = datacomparables.sort_values(by=['habitaciones'],ascending=True)
            if filtro=='Mayor habitaciones':
                datacomparables = datacomparables.sort_values(by=['habitaciones'],ascending=False)
            
    with col3:
        if datacomparables.empty is False:
            datapaso         = datacomparables[['direccion',vardep,'areaconstruida','habitaciones','banos','garajes','estrato','fuente','url']]
            st.session_state.dataexport = copy.deepcopy(datapaso)
            datapaso[vardep] = datapaso[vardep].apply(lambda x: f'${x:,.0f} {currency}')
            for i in ['areaconstruida','habitaciones','banos','garajes','estrato']:
                datapaso[i] = pd.to_numeric(datapaso[i],errors='coerce')
                idd = datapaso[i]>=0
                if sum(idd)>0:
                    datapaso.loc[idd,i] = datapaso.loc[idd,i].astype(int).astype(str)
            datapaso.index = range(len(datapaso))
            st.dataframe(datapaso)
        
    if datacomparables.empty is False:

        m1 = folium.Map(location=[latitud, longitud], zoom_start=15,tiles="cartodbpositron")
        img_style = '''
                <style>               
                    .property-image{
                      flex: 1;
                    }
                    img{
                        width:200px;
                        height:120px;
                        object-fit: cover;
                        margin-bottom: 2px; 
                    }
                </style>
                '''
        for i, inmueble in datacomparables.iterrows():
            if isinstance(inmueble['imagen_principal'], str) and len(inmueble['imagen_principal'])>20: imagen_principal =  inmueble['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
            propertyinfo = f'<strong>{inmueble["areaconstruida"]}</strong> mt<sup>2</sup> | <strong>{int(inmueble["habitaciones"])}</strong> hab | <strong>{int(inmueble["banos"])}</strong> baños | <strong>{int(inmueble["garajes"])}</strong> pq'
            url_export   = f"http://localhost:8501/Ficha?idcodigo={inmueble['code']}&tiponegocio={tiponegocio}"
            if isinstance(inmueble['direccion'], str): direccion = inmueble['direccion'][0:35]
            else: direccion = ''
            string_popup = f'''              
              <!DOCTYPE html>
              <html>
                <head>
                  {img_style}
                </head>
                <body>
                    <div>
                    <a href="{url_export}" target="_blank">
                    <div class="property-image">
                        <img src="{imagen_principal}"  alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                    </div>
                    </a>
                    <b> Direccion: {inmueble['direccion']}</b><br>
                    <b> Precio: ${inmueble[vardep]:,.0f}</b>{currency}<br>
                    <b> Área: {inmueble['areaconstruida']}</b><br>
                    <b> Habitaciones: {int(inmueble['habitaciones'])}</b><br>
                    <b> Baños: {int(inmueble['banos'])}</b><br>
                    <b> Garajes: {int(inmueble['garajes'])}</b><br>
                    </div>
                </body>
              </html>
              '''
            folium.Marker(location=[inmueble["latitud"], inmueble["longitud"]], popup=string_popup).add_to(m1)
        folium.Marker(location=[latitud, longitud], icon=folium.Icon(color='green', icon='fa-circle', prefix='fa')).add_to(m1)
        with col2:
            st_map = st_folium(m1,width=800,height=350)
                
        imagenes = ''
        for i, inmueble in datacomparables.iterrows():
            if isinstance(inmueble['imagen_principal'], str) and len(inmueble['imagen_principal'])>20: imagen_principal =  inmueble['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
            propertyinfo = f'<strong>{inmueble["areaconstruida"]}</strong> mt<sup>2</sup> | <strong>{int(inmueble["habitaciones"])}</strong> hab | <strong>{int(inmueble["banos"])}</strong> baños | <strong>{int(inmueble["garajes"])}</strong> pq'
            url_export   = f"http://localhost:8501/Ficha?idcodigo={inmueble['code']}&tiponegocio={tiponegocio}"
            if isinstance(inmueble['direccion'], str): direccion = inmueble['direccion'][0:35]
            else: direccion = ''
            imagenes += f'''    
              <div class="propiedad">
                <a href="{url_export}" target="_blank">
                <div class="imagen">
                  <img src="{imagen_principal}">
                </div>
                </a>
                <div class="caracteristicas">
                  <h3>${inmueble[vardep]:,.0f} {currency}</h3>
                  <p>{direccion}</p>
                  <p>{propertyinfo}</p>
                  {inmueble['tipobusqueda']}
                </div>
              </div>
              '''
            
        style = """
            <style>
              .contenedor-propiedades {
                overflow-x: scroll;
                white-space: nowrap;
                margin-bottom: 40px;
                margin-top: 30px;
              }
              
              .propiedad {
                display: inline-block;
                vertical-align: top;
                margin-right: 20px;
                text-align: center;
                width: 300px;
              }
              
              .imagen {
                height: 200px;
                margin-bottom: 10px;
                overflow: hidden;
              }
              
              .imagen img {
                display: block;
                height: 100%;
                width: 100%;
                object-fit: cover;
              }
              
              .caracteristicas {
                background-color: #f2f2f2;
                padding: 4px;
                text-align: left;
              }
              
              .caracteristicas h3 {
                font-size: 18px;
                margin-top: 0;
              }
              .caracteristicas p {
                font-size: 14px;
                margin-top: 0;
              }
              .caracteristicas p1 {
                font-size: 12px;
                text-align: left;
                width:40%;
                padding: 8px;
                background-color: #294c67;
                color: #ffffff;
                margin-top: 0;
              }
              .caracteristicas p2 {
                font-size: 12px;
                text-align: left;
                width:40%;
                padding: 8px;
                background-color: #008f39;
                color: #ffffff;
                margin-top: 0;
              } 
            </style>
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            {style}
          </head>
          <body>
            <div class="contenedor-propiedades">
            {imagenes}
            </div>
          </body>
        </html>
        """
        texto = BeautifulSoup(html, 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)
