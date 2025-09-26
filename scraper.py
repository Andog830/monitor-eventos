import requests
from bs4 import BeautifulSoup
import json
import os

token = os.getenv('TELEGRAM_TOKEN')


def scraping_tuboleta():
    try:
        # URL de búsqueda específica (cambia por tu búsqueda real)
        url = "https://www.tuboleta.com/es/resultados-de-busqueda?s=Fucks+News"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todos los contenedores de eventos
            eventos = soup.find_all('a', class_='content-link-container text-black text-decoration-none d-flex flex-column h-100')
            
            info_evento = []

            for i in eventos:
                info_evento.append([i.find('div', class_='content-date lh-sm text-blue text-sm-start text-md-end d-flex flex-column p-0'), i.find('div', class_='fs-8 fs-md-7 text-uppercase fw-bold mb-1'), i.find_all('div', class_='fs-8 fs-md-7 text-grey')])

            eventos_programados = {}

            for evento in info_evento:
                try:
                    # Extraer los elementos del evento
                    fecha_container = evento[0]  # Primer elemento: contenedor de fecha
                    nombre_container = evento[1]  # Segundo elemento: contenedor de nombre
                    info_container = evento[2]    # Tercer elemento: lista con lugar y ciudad
                    
                    # Extraer el nombre del evento
                    nombre_tag = nombre_container.find('span')
                    nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
                    
                    # Extraer lugar y ciudad
                    lugar_tag = info_container[0].find('span') if len(info_container) > 0 else None
                    ciudad_tag = info_container[1].find('span') if len(info_container) > 1 else None
                    
                    lugar = lugar_tag.text.strip() if lugar_tag else "Lugar no disponible"
                    ciudad = ciudad_tag.text.strip() if ciudad_tag else "Ciudad no disponible"
                    
                    # Extraer la fecha (usamos la versión móvil que es más completa)
                    fecha_mobile = fecha_container.find('span', class_='fs-7 fw-bold d-block d-md-none')
                    fecha_desktop_dia = fecha_container.find('span', class_='fs-5 fw-bold d-none d-md-block')
                    fecha_desktop_mes = fecha_container.find('span', class_='fs-8 fw-bold d-none d-md-block')
                    fecha_desktop_dia_semana = fecha_container.find('span', class_='fs-8 d-none d-md-block')
                    
                    if fecha_mobile:
                        # Formato: "30 Sep" - le agregamos el día de la semana
                        fecha_texto = fecha_mobile.text.strip()
                        if fecha_desktop_dia_semana:
                            dia_semana = fecha_desktop_dia_semana.text.strip()
                            fecha = f"{dia_semana} {fecha_texto}"
                        else:
                            fecha = fecha_texto
                    elif fecha_desktop_dia and fecha_desktop_mes and fecha_desktop_dia_semana:
                        # Construir desde los elementos desktop
                        dia = fecha_desktop_dia.text.strip()
                        mes = fecha_desktop_mes.text.strip()
                        dia_semana = fecha_desktop_dia_semana.text.strip()
                        fecha = f"{dia_semana} {dia} {mes}"
                    else:
                        fecha = "Fecha no disponible"
                    
                    # Agregar al diccionario
                    eventos_programados[nombre] = {
                        'ciudad': ciudad,
                        'lugar': lugar,
                        'fecha': fecha
                    }
                    
                except Exception as e:
                    print(f"⚠️ Error procesando evento: {e}")
                    continue
            
            return eventos_programados
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return []

def verificador(eventos_dict):
    with open('eventos.json', 'r', encoding='utf-8') as f: #{'FUCKS NEWS NOTICREO - B/MANGA': {'ciudad': 'Bucaramanga', 'lugar': 'Auditorio Luis A. Calvo', 'fecha': 'Mar 30 Sep'}, 'FUCKS NEWS NOTICREO - CHÍA': {'ciudad': 'Chía', 'lugar': 'Teatro Jorge Arango Tamayo - Chia', 'fecha': 'Lun 6 Oct'}}
        eventos_existentes = json.load(f)
    lista_ex = list(eventos_existentes.keys())
    lista_nuevos = list(eventos_dict.keys())

    for i in lista_ex:
        lista_nuevos.remove(i)

    if lista_nuevos:
        nuevos = {}
        for k in lista_nuevos:
            eventos_existentes[k] = eventos_dict[k]
            nuevos[k] = eventos_dict[k]
        with open('eventos.json', 'w', encoding='utf-8') as f:
                json.dump(eventos_existentes, f, ensure_ascii=False, indent=4)
        return nuevos
    else:
        return

def notificador(eventos_nuevos):
    #{'FUCKS NEWS NOTICREO - B/MANGA': {'ciudad': 'Bucaramanga', 'lugar': 'Auditorio Luis A. Calvo', 'fecha': 'Mar 30 Sep'}, 'FUCKS NEWS NOTICREO - CHÍA': {'ciudad': 'Chía', 'lugar': 'Teatro Jorge Arango Tamayo - Chia', 'fecha': 'Lun 6 Oct'},'FUCKS NEWS NOTICREO - BOGOTÁ': {'ciudad': 'Bogotá', 'lugar': 'Teatro Jorge Elíecer Gaitán', 'fecha': 'Mar 28 Oct'},'FUCKS NEWS NOTICREO - BERLIN': {'ciudad': 'Berlín', 'lugar': 'Olympiastadion', 'fecha': 'Lun 24 Nov'}})
    chats_id = [os.getenv('TELEGRAM_CHAT_BELEN'), os.getenv('TELEGRAM_CHAT_FELIPE')]
    if eventos_nuevos:
          chat = f"https://api.telegram.org/bot{token}/sendMessage"
          for evento in eventos_nuevos:
              mensaje = f"""<b>¡ATENCIÓN! NUEVA FECHA DE FUCKS NEWS</b>

Hace menos de 10 minutos se publicó una nueva fecha de Fucks News en el portal Tuboleta.com:

<b>{evento}</b>
<b>Ciudad:</b> {eventos_nuevos[evento]['ciudad']}
<b>Lugar:</b> {eventos_nuevos[evento]['lugar']}
<b>Fecha:</b> {eventos_nuevos[evento]['fecha']}

APÚRENSE A COMPRAR LAS BOLETAS ANTES DE QUE HAGAN LA PUBLICACIÓN EN INSTAGRAM

https://www.tuboleta.com/es/resultados-de-busqueda?s=Fucks+News"""
              for id in chats_id:
                payload = {
                    'chat_id': id,
                    'text': mensaje,
                    'parse_mode': 'HTML'
                }
                try:
                    response = requests.post(chat, json=payload)
                    if response.status_code == 200:
                        print("✅ Mensaje enviado a Telegram")
                    else:
                        print(f"❌ Error: {response.text}")
                        return False
                except Exception as e:
                    print(f"❌ Error de conexión: {e}")
                    return False
    else:
        print('No hay eventos nuevos')

if __name__ == "__main__":
    notificador(verificador(scraping_tuboleta()))
