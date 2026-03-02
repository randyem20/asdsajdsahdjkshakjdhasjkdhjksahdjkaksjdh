import socket
import threading
import json
import logging

import os

# Configuración básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '0.0.0.0'  # Escuchar en todas las interfaces disponibles
# Render pasa el puerto a través de una variable de entorno llamada PORT. 
# Si no la encuentra, usa el 8888 por defecto para pruebas locales.
PORT = int(os.environ.get("PORT", 8888))

clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """
    Envía un mensaje a todos los clientes conectados, 
    excepto al que lo envió (si se especifica).
    """
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    # Siempre añadimos un salto de línea para asegurar que el receptor pueda leer línea por línea
                    client.sendall((message + '\n').encode('utf-8'))
                except Exception as e:
                    logging.error(f"Error al enviar mensaje a un cliente: {e}")
                    remove_client(client)

def remove_client(client_socket):
    """
    Elimina un cliente de la lista de conexiones activas.
    """
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
            try:
                client_socket.close()
            except:
                pass
            logging.info("Cliente desconectado.")

def handle_client(client_socket, address):
    """
    Maneja la conexión con un cliente individual.
    """
    logging.info(f"Nueva conexión desde {address}")
    with clients_lock:
        clients.append(client_socket)
    
    # Notificar a todos que alguien se ha conectado
    join_msg = json.dumps({"type": "system", "content": f"Un usuario desde {address[0]} se ha unido."})
    broadcast(join_msg, client_socket)

    # Buffer para leer mensajes parciales
    buffer = ""
    
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            
            buffer += data.decode('utf-8', errors='ignore')
            
            # Procesar mensajes línea por línea
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if line:
                    logging.info(f"Recibido [{address}]: {line[:50]}...") # Logueamos un extracto  por seguridad/privacidad
                    # Reenviar el mensaje exacto a los demás (broadcast puro)
                    broadcast(line, client_socket)

    except ConnectionResetError:
        logging.warning(f"Conexión reseteada por {address}")
    except Exception as e:
        logging.error(f"Error procesando cliente {address}: {e}")
    finally:
        remove_client(client_socket)
        # Notificar a todos que alguien se desconectó
        leave_msg = json.dumps({"type": "system", "content": f"El usuario {address[0]} se ha desconectado."})
        broadcast(leave_msg)

def start_server():
    """
    Inicia el servidor en el HOST y PORT especificados.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar el socket inmediatamente al reiniciar el script
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"--- FoxyBrowserMax Chat API Server Iniciado ---")
        logging.info(f"Escuchando en HOST: {HOST} | PORT: {PORT}")
        logging.info("Esperando conexiones de usuarios...")
        
        while True:
            try:
                client_socket, address = server.accept()
                thread = threading.Thread(target=handle_client, args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except Exception as e:
                logging.error(f"Error al aceptar conexión: {e}")
                
    except Exception as e:
        logging.critical(f"No se pudo iniciar el servidor en {HOST}:{PORT}. Error: {e}")
    finally:
        server.close()
        logging.info("Servidor cerrado.")

if __name__ == "__main__":
    start_server()
