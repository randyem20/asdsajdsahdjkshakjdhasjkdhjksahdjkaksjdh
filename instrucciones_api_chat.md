# Instrucciones de la API de Chat FoxyBrowserMax

Esta carpeta contiene el servidor necesario para establecer una sala de chat grupal y compartir sitios en tiempo real con otros usuarios de FoxyBrowserMax.

## ¿Qué es esto?
Es un pequeño servidor escrito en Python puro (usa Sockets y JSON) sin dependencias externas complejas. Sirve de puente (relay) entre diferentes instancias de `respaldo.py` u otras herramientas de tu ecosistema.

## ¿Cómo iniciar el Servidor?
1. Abre una consola (CMD o PowerShell) en esta carpeta (`chat_api`).
2. Ejecuta el comando:
   ```bash
   python server.py
   ```
3. Verás un mensaje en la consola indicando que el servidor está "Escuchando en HOST: 0.0.0.0 | PORT: 8888".

## ¿Cómo conectarse desde otras computadoras (Red Local o Internet)?
- El servidor escucha en el puerto `8888` por defecto.
- **Red Local (LAN):** Los usuarios de tu misma red (misma casa/oficina) solo necesitan saber la IP Privada del ordenador que corre `server.py` (ej: `192.168.1.50`). En FoxyBrowserMax, pondrán esa IP para conectarse.
- **Internet Público:** 
  - Si quieres que gente desde otras partes del mundo se conecte, debes **Abrir el puerto 8888** en tu Router de Internet, dirigiendo el tráfico hacia la IP de la computadora que corre el `server.py`.
  - Los usuarios deberán ingresar tu **IP Pública** para conectarse.
  - Alternativa profesional: Puedes subir esta carpeta `chat_api` a un VPS (Servidor Privado Virtual) como AWS, DigitalOcean o Linode, y correr el servidor allí. Su IP pública estará siempre accesible y encendida.

🚨 **Nota Importante sobre Streamlit Community Cloud (share.streamlit.io):**
Este servidor de chat funciona bajo el protocolo **"Socket TCP Puro"** (en el puerto 8888) y no como una página web estándar (HTTP). Por lo tanto, **servicios como Streamlit Cloud NO PUEDEN alojar este script**, ya que están diseñados única y exclusivamente para aplicaciones web. Para alojar este servidor en internet de forma gratuita o barata, debes usar servicios que expongan "Puertos TCP" directos, como:
- **Render.com** o **Railway.app** (mediante Docker para exponer puertos TCP).
- **Ngrok** o **Localtonet** (para exponer el puerto 8888 de tu propia computadora a internet fácilmente y gratis).
## Formato de Mensajes (Para desarrolladores)
El servidor retransmite todo el texto que le llega, asumiendo que es una línea JSON válida. 

### Compartir un mensaje de texto normal
Desde los clientes się envía:
```json
{
  "type": "msg",
  "username": "TuNombre",
  "content": "Hola equipo, he agregado nuevos proxies."
}
```

### Compartir Sitios (URLs)
Para avisar a otros clientes que agreguen un sitio, desde el cliente se envía:
```json
{
  "type": "site",
  "username": "TuNombre",
  "url": "https://tiendaejemplo.com/checkout",
  "gateway": "Shopify Payments",
  "store_type": "Found"
}
```
*Cuando las demás instancias reciben esto, lo procesarán para agregarlo silenciosamente o avisar al usuario.*
