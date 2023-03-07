import streamlit as st
import copy
import json
import pandas as pd
from bs4 import BeautifulSoup

from _valorizador import valorizador
from datafunctions import inspeccion_visitas,getdatacatastro
from coddir import coddir
from html_scripts import table1


def splitimg(x,pos):
    try: return x.split('|')[pos].strip()
    except: return None
    
@st.experimental_memo
def json2dataframe(id_inmueble,datajson):
    dataimg = pd.DataFrame(datajson)
    if dataimg.empty is False:
        dataimg['img0'] = dataimg['url_foto'].apply(lambda x: splitimg(x,0))
        dataimg['img1'] = dataimg['url_foto'].apply(lambda x: splitimg(x,1))
        dataimg['img2'] = dataimg['url_foto'].apply(lambda x: splitimg(x,2))
        dataimg['img3'] = dataimg['url_foto'].apply(lambda x: splitimg(x,3))
        dataimg['img4'] = dataimg['url_foto'].apply(lambda x: splitimg(x,4))
        dataimg['img5'] = dataimg['url_foto'].apply(lambda x: splitimg(x,5))
        del dataimg['url_foto']
        dataimg = pd.melt(dataimg, id_vars=['tipo_ambiente','tipo_suelo','estado_suelo','tipo_pared','estado_pared'], value_vars=['img0','img1','img2','img3','img4','img5'], var_name='img')
        dataimg = dataimg[dataimg['value'].notnull()]
        dataimg.fillna("", inplace = True) 
        if 'img' in dataimg: del dataimg['img']
        dataimg.rename(columns={'value':'img'},inplace=True)
    return dataimg
        
def dashboard_comite(id_inmueble,currency='COP',currencycal=1):
    #id_inmueble = 1695
    if id_inmueble is not None: 
        data,datacaracteristicas,datacallhistory = inspeccion_visitas()

        filename     = 'data/data_catastro_completo_conjunto'
        datacatastro = getdatacatastro(filename)
    
        data                = data[data['id_inmueble']==id_inmueble]
        datatotal           = copy.deepcopy(data)
        datatotal['coddir'] = datatotal['direccion'].apply(lambda x: coddir(x))
        datacaracteristicas = datacaracteristicas[datacaracteristicas['id_inmueble']==id_inmueble]
        datacallhistory     = datacallhistory[datacallhistory['id_inmueble']==id_inmueble]
        datacatastro        = datacatastro[datacatastro['coddir']==coddir(datacaracteristicas['direccion'].iloc[0])]
        
        if len(datacaracteristicas)==1:
            varkeep   = ['id_inmueble']+[x for x in data if x not in datacaracteristicas]
            datatotal = data[varkeep].merge(datacaracteristicas,on='id_inmueble',how='left',validate='1:1')
            datatotal['coddir'] = datatotal['direccion'].apply(lambda x: coddir(x))
            
        if len(datacatastro)==1:
            varkeep = ['coddir']+[x for x in datacatastro if x not in datatotal]
            datatotal = datatotal.merge(datacatastro[varkeep],on='coddir',how='left',validate='1:1')
        
        var2value = ['ciudad', 'zona','upznombre','barrio', 'direccion', 'nombre_conjunto', 'fecha_creacion', 'callagent', 'fecha_asignacion_visitagent', 'visitagent', 'url', 'procedencia', 'valorventa', 'valoradministracion', 'areaconstruida', 'habitaciones', 'banos', 'garajes', 'antiguedad', 'piso', 'niveles', 'ascensor', 'tipo_vista', 'descripcion_estado', 'vetustez_min', 'vetustez_max', 'maxpiso', 'unidades', '50 o menos mt2', '50 a 100 mt2', '100 a 150 mt2', '150 a 200 mt2', '200 a 300 mt2', 'ascensor', 'sotanos', 'porteria', 'zona_verde', 'zona_bbq', 'gimnasio', 'chanchas_multiples', 'zona_ninos', 'vigilancia_247', 'sala_juegos', 'salon_comunal', 'piscina']
        for i in var2value:
            if i not in datatotal:
                datatotal[i] = None
                
        #---------------------------------------------------------------------#
        # Caracteristicas       
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Descripción del inmueble</h1></div>', unsafe_allow_html=True)
    
        col1, col2 = st.columns(2)
        with col1:
            #st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Detalles del inmueble</h1></div>', unsafe_allow_html=True)
            formato = [ 
                        {"name":"Ciudad","value":datatotal['ciudad'].iloc[0]}, 
                        {"name":"Zona","value":datatotal['zona'].iloc[0]}, 
                        {"name":"UPZ","value":datatotal['upznombre'].iloc[0]}, 
                        {"name":"Barrio","value":datatotal['barrio'].iloc[0]}, 
                        {"name":"Direccion","value":datatotal['direccion'].iloc[0]}, 
                        {"name":"Nombre del conjunto","value":datatotal['nombre_conjunto'].iloc[0]}, 
                        {"name":"Fecha creacion lead","value":datatotal['fecha_creacion'].iloc[0].strftime('%Y-%m-%d')},      
                        {"name":"Quien realizó la llamada","value":datatotal['callagent'].iloc[0]}, 
                        {"name":"Fecha de la visita","value":datatotal['fecha_asignacion_visitagent'].iloc[0].strftime('%Y-%m-%d')}, 
                        {"name":"Quien realizó la visita","value":datatotal['visitagent'].iloc[0]}, 
                        {"name":"Publicacion","value":f'''<a href="{datatotal['url'].iloc[0]}" class="button">Link</a>''' }, 
                        {"name":"Procedencia","value":datatotal['procedencia'].iloc[0]},
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
            texto = BeautifulSoup(table1(html,'Detalles del inmueble'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True) 
   
        
        with col2:
            #st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Detalles del inmueble</h1></div>', unsafe_allow_html=True)
            valorventa          = None
            valoradministracion = None
            if 'valorventa' in datatotal and datatotal['valorventa'].iloc[0] is not None: 
                valorventa = f"${datatotal['valorventa'].iloc[0]:,.0f} {currency}" 
            if 'valoradministracion' in datatotal and datatotal['valoradministracion'].iloc[0] is not None: 
                valoradministracion = f"${datatotal['valoradministracion'].iloc[0]:,.0f} {currency}"
            for i in ['habitaciones','banos','garajes','antiguedad','piso','niveles','ascensor']:
                if i in datatotal:
                    try: datatotal[i] = datatotal[i].astype(int)
                    except: pass
                
            formato = [ 
                        {"name":"Valor de oferta inicial","value":valorventa},
                        {"name":"Administracion","value":valoradministracion}, 
                        {"name":"Área construida","value":datatotal['areaconstruida'].iloc[0]}, 
                        {"name":"Habitaciones","value":datatotal['habitaciones'].iloc[0]}, 
                        {"name":"Baños","value":datatotal['banos'].iloc[0]}, 
                        {"name":"Garajes","value":datatotal['garajes'].iloc[0]}, 
                        {"name":"Antiguedad","value":datatotal['antiguedad'].iloc[0]}, 
                        {"name":"Piso","value":datatotal['piso'].iloc[0]}, 
                        {"name":"Niveles","value":datatotal['niveles'].iloc[0]}, 
                        {"name":"Ascensores","value":datatotal['ascensor'].iloc[0]}, 
                        {"name":"Tipo de vista","value":datatotal['tipo_vista'].iloc[0]}, 
                        {"name":"Descripción","value":datatotal['descripcion_estado'].iloc[0]}, 
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
            texto = BeautifulSoup(table1(html,'Caracteristicas generales'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)         
        
    
        #---------------------------------------------------------------------#
        # Valorizador
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Estudio de Mercado</h1></div>', unsafe_allow_html=True)

        # if scacodigo not in inputvar:
        if 'antiguedad' in datatotal: datatotal['anos_antiguedad'] = copy.deepcopy(datatotal['antiguedad'])
        if 'nombre_conjunto' in datatotal: datatotal['nombre_edificio'] = copy.deepcopy(datatotal['nombre_conjunto'])
        if 'niveles' in datatotal: datatotal['numerodeniveles'] = copy.deepcopy(datatotal['niveles'])
        if 'ascensor' in datatotal: 
            datatotal['num_ascensores'] = copy.deepcopy(datatotal['ascensor'])
            datatotal['ascensores']     = copy.deepcopy(datatotal['ascensor'])
        if 'piso' in datatotal: datatotal['num_piso'] = copy.deepcopy(datatotal['piso'])
        if 'tipoinmueble' not in datatotal: datatotal['tipoinmueble'] = 'Apartamento'
    
        inputvar_var = ['ciudad', 'scacodigo', 'tipoinmueble', 'direccion', 'nombre_conjunto', 'areaconstruida', 'habitaciones', 'banos', 'garajes', 'estrato', 'piso', 'antiguedad', 'ascensores', 'numerodeniveles', 'coddir', 'latitud', 'longitud', 'nombre_edificio', 'num_piso', 'anos_antiguedad', 'num_ascensores', 'metros']
        varkeep = [x for x in inputvar_var if x in datatotal]
        
        inputvar = datatotal[varkeep].iloc[0].to_dict()
        if 'metros' not in inputvar: inputvar['metros'] = 300
        
        valorizador(id_inmueble=None,inputvar=inputvar,currency=currency,currencycal=currencycal)
 
    
        #---------------------------------------------------------------------#
        # Informacion del edificio       
        st.write('---')
        st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Caracteristicas del edificio</h1></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            
            formato = [ 
                        {"name":"Antiguedad Minima","value":datatotal['vetustez_min'].iloc[0]}, 
                        {"name":"Antiguedad Maxima","value":datatotal['vetustez_max'].iloc[0]}, 
                        {"name":"Pisos del edificio","value":datatotal['maxpiso'].iloc[0]}, 
                        {"name":"Unidades","value":datatotal['unidades'].iloc[0]}, 
                        {"name":"50 o menos mt2","value":datatotal['50 o menos mt2'].iloc[0]}, 
                        {"name":"50 a 100 mt2","value":datatotal['50 a 100 mt2'].iloc[0]},      
                        {"name":"100 a 150 mt2","value":datatotal['100 a 150 mt2'].iloc[0]},
                        {"name":"150 a 200 mt2","value":datatotal['150 a 200 mt2'].iloc[0]},  
                        {"name":"200 a 300 mt2","value":datatotal['200 a 300 mt2'].iloc[0]},
                        {"name":"Ascensor","value":datatotal['ascensor'].iloc[0]},
                        {"name":"Sotanos","value":datatotal['sotanos'].iloc[0]}
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
            texto = BeautifulSoup(table1(html,'Caracteristicas del edificio'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True) 
   
        
        with col2:
            #st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Detalles del inmueble</h1></div>', unsafe_allow_html=True)
            formato = [ 
                        {"name":"Porteria","value":datatotal['porteria'].iloc[0]}, 
                        {"name":"Zona Verde","value":datatotal['zona_verde'].iloc[0]}, 
                        {"name":"Zona BBQ","value":datatotal['zona_bbq'].iloc[0]}, 
                        {"name":"GYM","value":datatotal['gimnasio'].iloc[0]}, 
                        {"name":"Canchas Multiples","value":datatotal['chanchas_multiples'].iloc[0]}, 
                        {"name":"Zona de ninos","value":datatotal['zona_ninos'].iloc[0]}, 
                        {"name":"Vigilancia","value":datatotal['vigilancia_247'].iloc[0]}, 
                        {"name":"Sala de juegos","value":datatotal['sala_juegos'].iloc[0]}, 
                        {"name":"Salon comunal","value":datatotal['salon_comunal'].iloc[0]}, 
                        {"name":"Piscina","value":datatotal['piscina'].iloc[0]}, 
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
            texto = BeautifulSoup(table1(html,'Amenities'), 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)             
            
            
        #---------------------------------------------------------------------#
        # Imagenes      
       
        if 'json' in datatotal:
            st.write('---')
            st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Fotos del inmueble (visita)</h1></div>', unsafe_allow_html=True)

            datajson = json.loads(datatotal['json'].iloc[0])
            dataimg  = json2dataframe(id_inmueble,datajson)
            css_format = """
                <style>
                  .property-card-left {
                    width: 100%;
                     /* height: 1600px; */
                     /* overflow-y: scroll; */
                    text-align: center;
                    display: inline-block;
                    margin: 0px auto;
                  }

                  .property-block {
                    width:32%;
                    background-color: white;
                    border: 1px solid gray;
                    box-shadow: 2px 2px 2px gray;
                    padding: 3px;
                    margin-bottom: 10px; 
              	    display: inline-block;
              	    float: left;
                    margin-right: 10px; 
                  }

                  .property {
                    border: 1px solid gray;
                    box-shadow: 2px 2px 2px gray;
                    padding: 10px;
                    margin-bottom: 10px;
                  }
                  
                  .property-image{
                    flex: 1;
                  }
                  .property-info{
                    flex: 1;
                  }
                  
                  .price-info {
                    font-family: 'Comic Sans MS', cursive;
                    font-size: 24px;
                    margin-bottom: 1px;
                  }
             
                  .admon-info {
                    font-family: 'Comic Sans MS', cursive;
                    font-size: 12px;
                    margin-bottom: 5px;
                  }
                  
                  .caracteristicas-info {
                    font-size: 16px;
                    margin-bottom: 2px;
                  }

                  img{
                    max-width: 100%;
                    width: 100%;
                    height:250px;
                    object-fit: cover;
                    margin-bottom: 10px; 
                  }
                </style>
            """

            imagenes = ''
            dataimg  = dataimg.sort_values(by='tipo_ambiente', ascending=True)
            for i, inmueble in dataimg.iterrows():

                if isinstance(inmueble['img'], str) and len(inmueble['img'])>20: imagen_principal =  inmueble['img']
                else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
                tipo_ambiente = inmueble['tipo_ambiente']
                tipo_suelo    = inmueble['tipo_suelo']
                estado_suelo  = inmueble['estado_suelo']
                tipo_pared    = inmueble['tipo_pared']
                estado_pared  = inmueble['estado_pared']
                imagenes += f'''
                      <div class="property-block">
                        <div class="property-image">
                          <img src="{imagen_principal}" alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                        </div>
                        <p class="caracteristicas-info">Ambiente: {tipo_ambiente}</p>
                        <p class="caracteristicas-info">Tipo de suelo: {tipo_suelo}</p>
                        <p class="caracteristicas-info">Estado del suelo: {estado_suelo}</p>
                        <p class="caracteristicas-info">Tipo de pared: {tipo_pared}</p>
                        <p class="caracteristicas-info">Estado de la pared: {estado_pared}</p>
                      </div>
                      '''
            texto = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                  {css_format}
                  </head>
                  <body>
                <div class="property-card-left">
                {imagenes}
                </div>
                  </body>
                </html>
                """
            texto = BeautifulSoup(texto, 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)
               