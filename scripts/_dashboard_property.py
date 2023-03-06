import streamlit as st
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

import sys
sys.path.insert(0, '/scripts')
from html_scripts import table1,table2,timelineproperty,html_estado_propiedad,imgpropertylist
from datafunctions import propertydata,propertymanagementdata,followup,datadocumentos
from _valorizador import valorizador
from _dashboard_gestion_callcenter_inbound import dashboard_gestion_callcenter_inbound
from _dashboard_property_management import dashboard_property_management

# https://altair-viz.github.io/gallery/index.html
# https://plotly.streamlit.app/
# https://plotly.com/python/

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def dashboard_property(id_inmueble,currency='COP',currencycal=1,caracteristicas_section=True,proceso_section=True,unit_economics_sectrion=True,property_management_section=True,gestion_section=True,property_image_section=True,forecast_analisis=True):

    data                        = propertydata()
    data                        = data.sort_values(by='id_inmueble',ascending=True)
    datapm,datagasto            = propertymanagementdata()
    datafollowup                = followup()
    datafollowup                = datafollowup[datafollowup['id_inmueble'].notnull()]
    datafollowup['id_inmueble'] = datafollowup['id_inmueble'].astype(int)
    datapropertydocumentos      = datadocumentos()
    dataproperty                = data[data['id_inmueble']==id_inmueble]
    datapropertydocumentos      = datapropertydocumentos[datapropertydocumentos['id_inmueble']==id_inmueble]
   
    #-------------------------------------------------------------------------#
    # Caracteristicas generales propiedad
    if caracteristicas_section:
        st.write('---')
        st.markdown('<div style="margin-top: 30px;"</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1,2])
        with col1:
            if dataproperty['estado_venta'].iloc[0] is not None and dataproperty['estado_venta'].iloc[0].lower()=='vendido':
                html = html_estado_propiedad('<div class="estadovendido"><span><b>Vendido</b></span></div>')
                st.markdown(BeautifulSoup(html, 'html.parser'), unsafe_allow_html=True)  
            else:
                if dataproperty['estado_compra'].iloc[0] is not None:
                    estado_propiedad = dataproperty['estado_compra'].iloc[0].title()
                    if estado_propiedad.lower()=='comprado': estado_propiedad = 'Disponible'
                    html = html_estado_propiedad(f'<div class="estadonovendido"><span><b>{estado_propiedad}</b></span></div>')
                    st.markdown(BeautifulSoup(html, 'html.parser'), unsafe_allow_html=True)
                    
            if pd.isnull(dataproperty['url_img1'].iloc[0]):
                st.image("https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png",use_column_width ='auto')
            else:
                st.image(dataproperty['url_img1'].iloc[0],use_column_width ='auto')
                
        precio_compra  = dataproperty['precio_compra'].iloc[0]/currencycal
        datacallcenter = datafollowup[datafollowup['id_inmueble']==id_inmueble]
        with col2:      
            columna1 = [{"name":"Ciudad","value":dataproperty['ciudad'].iloc[0]},
                       {"name":"Dirección","value":dataproperty['direccion'].iloc[0]},
                       {"name":"Nombre del edificio","value":dataproperty['nombre_conjunto'].iloc[0]},
                       {"name":"Localidad","value":dataproperty['localidad'].iloc[0]},
                       {"name":"Barrio","value":dataproperty['barriocatastral'].iloc[0]},
                       {"name":"CHIP","value":dataproperty['chip'].iloc[0]},
                       {"name":"Matricula Inmobiliaria","value":dataproperty['matricula'].iloc[0]},
                       {"name":"Cedula catastral","value":dataproperty['cedula_catastral'].iloc[0]},
                       {"name":"Estrato","value":dataproperty['estrato'].iloc[0]},
                       ]
            
            columna2 = [
                        {"name":"Antiguedad","value":dataproperty['antiguedad'].iloc[0]},
                        {"name":"Área construida","value":dataproperty['areaconstruida'].iloc[0]},
                        {"name":"Habitaciones","value":dataproperty['habitaciones'].iloc[0]},
                        {"name":"Baños","value":dataproperty['banos'].iloc[0]},
                        {"name":"Garajes","value":dataproperty['garajes'].iloc[0]},
                        {"name":"Piso","value":dataproperty['piso'].iloc[0]},  
                       ]
        
            lista = []
            try:
                for i in json.loads(datapropertydocumentos['venta_relevantfiles'].iloc[0]):
                    if 'filename' in i and any([x for x in ['ctl','escritura'] if x in i['filename'].lower()]) and any([x for x in ['pago','poder','recibo'] if x in i['filename'].lower()]) is False:
                        lista.append(i['filename'])
            except: pass
                
            # CTL
            filevector = []
            if any([x for x in lista if 'ctl' in x.lower()]) and any([x for x in lista if 'actualizado' in x.lower()]):
                filevector = [x for x in lista if 'ctl' in x.lower() and 'actualizado' in x.lower()]
            elif any([x for x in lista if 'ctl' in x.lower()]) and any([x for x in lista if 'apartamento' in x.lower()]):
                filevector = [x for x in lista if 'ctl' in x.lower() and 'apartamento' in x.lower()]
            elif any([x for x in lista if 'ctl' in x.lower()]) and any([x for x in lista if 'apto' in x.lower()]):
                filevector = [x for x in lista if 'ctl' in x.lower() and 'apto' in x.lower()]            
            if filevector!=[]:
                filevector = pd.DataFrame({'filename':filevector})
                filevector = filevector.sort_values(by='filename',ascending=False)
                for i in json.loads(datapropertydocumentos['venta_relevantfiles'].iloc[0]):
                    if i['filename']==filevector['filename'].iloc[0]:
                        columna2.append({"name":"CTL","value":f'''<a href="{i['urldocument']}" class="button">CTL</a>'''})
                        break
        
            # ESCRITURAS
            filevector = []
            if any([x for x in lista if 'escritura' in x.lower()]) and any([x for x in lista if re.sub('[^0-9]','',x.lower().split('escritura')[-1])!='']):
                filevector = [x for x in lista if 'escritura' in x.lower() and re.sub('[^0-9]','',x.lower().split('escritura')[-1]) in x.lower()]
            elif any([x for x in lista if 'escrituras' in x.lower()]):
                filevector = [x for x in lista if 'escrituras' in x.lower()]
            elif any([x for x in lista if 'escritura' in x.lower()]):
                filevector = [x for x in lista if 'escritura' in x.lower()]       
            if filevector!=[]:
                filevector = pd.DataFrame({'filename':filevector})
                filevector = filevector.sort_values(by='filename',ascending=False)
                for i in json.loads(datapropertydocumentos['venta_relevantfiles'].iloc[0]):
                    if i['filename']==filevector['filename'].iloc[0]:
                        columna2.append({"name":"Escritura","value":f'''<a href="{i['urldocument']}" class="button">Escritura</a>'''})
                        break    
            
            html = ""
            for i in range(max(len(columna1),len(columna2))):
                htmlpaso = ""
                try:
                    if columna1[i]["value"] is not None and columna1[i]["value"]!='':
                        htmlpaso += f"""
                                <td>{columna1[i]["name"]}</td>
                                <td>{columna1[i]["value"]}</td>            
                        """        
                except:
                    htmlpaso += """
                            <td></td>
                            <td></td>            
                    """  
                try:
                    if columna2[i]["value"] is not None and columna2[i]["value"]!='':
                        htmlpaso += f"""
                                <td>{columna2[i]["name"]}</td>
                                <td>{columna2[i]["value"]}</td>            
                        """        
                except:
                        htmlpaso += """
                                <td></td>
                                <td></td>            
                        """  
                html += f"""
                    <tr>
                    {htmlpaso}
                    </tr>
                """
            texto = BeautifulSoup(table2(html,'Caracteristicas'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)  

    #-------------------------------------------------------------------------#
    # Timeline
    if proceso_section:

        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 0px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Línea de Proceso</h1></div>', unsafe_allow_html=True)
        
        formato = {'Oferta de compra':'fecha_oferta_compra','Firma promesa de compra':'fecha_promesa_compra','Escrituras de compra':'fecha_compra', 'Oferta de venta':'fecha_oferta_venta','Firma de promesa venta':'fecha_promesa_venta','Firma escritura de venta':'fecha_escritura_venta'}
        proceso = ""
        for key,value in formato.items():
            try:    
                fechainput = dataproperty[value].iloc[0].strftime('%Y-%m-%d')
                proceso += f"""
                <div class="swiper-slide">
                <div class="timestamp"><span class="date">{fechainput}</span></div>
                <div class="statusdark"><i class="fas fa-check"></i><span>{key}</span></div>
                </div>
                """ 
          
            except: 
                proceso += f"""
                <div class="swiper-slide">
                <div class="timestamp"><span class="date">&nbsp</span></div>
                <div class="statuslight"><span>{key}</span></div>
                </div>
                """
        with st.container():
            texto = BeautifulSoup(timelineproperty(proceso), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)  
             
    #-------------------------------------------------------------------------#
    # Siguientes pasos (firma  de promesa, firma de escritura, etc)
    
    
    #-------------------------------------------------------------------------#
    # Analisis de precios y gastos de la propiedad (property management)
    if unit_economics_sectrion:
        st.write('---')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Unit Economics</h1></div>', unsafe_allow_html=True)
        
            precio_compra = dataproperty['precio_compra'].iloc[0]/currencycal
            totalgasto    = datagasto[datagasto['id_inmueble']==id_inmueble]['gasto'].iloc[0]/currencycal
            try: 
                precio_lista_venta = dataproperty['precio_lista_venta'].iloc[0]/currencycal 
                precio_lista_venta = f"${precio_lista_venta:,.0f} {currency}"
            except: precio_lista_venta = None
            
            if pd.isna(dataproperty['precio_venta'].iloc[0]):
                precio_venta       = None
                retorno_bruto      = None
                retorno_neto       = None
                total_ganancia     = None
            else:
                precio_venta  = dataproperty['precio_venta'].iloc[0]/currencycal
                retorno_bruto = (precio_venta/precio_compra)-1
                retorno_bruto = "{:.1%}".format(retorno_bruto)
                retorno_neto  = ((precio_venta-totalgasto)/precio_compra)-1
                retorno_neto  = "{:.1%}".format(retorno_neto)
                total_ganancia = (precio_venta-precio_compra-totalgasto)
                total_ganancia = f"${total_ganancia:,.0f} {currency}"
                precio_venta  = f"${precio_venta:,.0f} {currency}"
        
            if dataproperty['estado_venta'].iloc[0] is not None and dataproperty['estado_venta'].iloc[0].lower()=='vendido':
                dias = dataproperty['fecha_escritura_venta'].iloc[0]-dataproperty['fecha_compra'].iloc[0]
            else:
                dias = datetime.now()-dataproperty['fecha_compra'].iloc[0]
            dias = dias.days 
        
            formato = [{"name":"Precio de compra","value":f"${precio_compra:,.0f} {currency}"},
                       {"name":"Total gasto","value":f"${totalgasto:,.0f} {currency}"},
                       {"name":"Precio lista para venta","value":precio_lista_venta},
                       {"name":"Precio de venta","value":precio_venta},
                       {"name":"Total ganancia","value":total_ganancia},
                       {"name":"Retorno bruto","value":retorno_bruto},
                       {"name":"Retorno neto","value":retorno_neto},
                       {"name":"Días en el mercado","value":int(dias)}
                       ]
            html = ""
            for i in formato:
                if i["value"] is not None and i["value"]!='':
                    html += f"""
                        <tr>
                            <td><b>{i["name"]}</b></td>
                            <td><b>{i["value"]}</b></td>
                        </tr>
                    """
            texto = BeautifulSoup(table1(html,'Units'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True) 
   
    #-------------------------------------------------------------------------#
    # Property management
    if property_management_section:        
        dashboard_property_management(id_inmueble,currency=currency,currencycal=currencycal)
   
    #-------------------------------------------------------------------------#
    # Gestion Inbound del inmueble
    if gestion_section:
        dashboard_gestion_callcenter_inbound(id_inmueble,modulo_callcenter=True,modulo_callcenter_fallas=False)
           
    #-------------------------------------------------------------------------#
    # Analisis de precios actualziado del edificio, sector,etc
    if forecast_analisis:
        #if st.button('Realizar analisis de precios de mercado'):
        st.write('---')
        with st.spinner():
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 40px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Precios de mercado</h1></div>', unsafe_allow_html=True)
            valorizador(id_inmueble=id_inmueble,currency=currency,currencycal=currencycal)
    
    #-------------------------------------------------------------------------#
    # Modificar variables del inmueble
    
    
    
    #-------------------------------------------------------------------------#
    # Fotos del inmueble
    if property_image_section:
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Fotos de la propiedad</h1></div>', unsafe_allow_html=True)               
        
        imagenes = ''
        for img in ['url_img1', 'url_img2', 'url_img3', 'url_img4', 'url_img5', 'url_img6', 'url_img7', 'url_img8', 'url_img9', 'url_img10', 'url_img11', 'url_img12', 'url_img13', 'url_img14', 'url_img15', 'url_img16', 'url_img17', 'url_img18', 'url_img19', 'url_img20', 'url_img21', 'url_img22', 'url_img23', 'url_img24', 'url_img25'] :
            if isinstance(dataproperty[img].iloc[0], str) and len(dataproperty[img].iloc[0])>20:
                imagenes += f'''
                      <div class="property-block">
                        <div class="property-image">
                          <img src="{dataproperty[img].iloc[0]}" alt="property image" class="mi-imagen">
                        </div>
                      </div>
                      '''
        texto = BeautifulSoup(imgpropertylist(imagenes), 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)