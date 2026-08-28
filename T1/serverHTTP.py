import socket 
import sys 
import json

if len(sys.argv) < 2:
    sys.exit(1)

file = sys.argv[1]

with open(file, "r") as f:
    datos_file = json.load(f)


username = datos_file["user"]


IP_VM = "10.0.2.15"


def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)


def parse_HTTP_message(http_message: bytes):
    if not http_message:
        return None
    head , _ , body = http_message.partition(b"\r\n\r\n")   #separamos head de body 
    lineas_head = head.split(b"\r\n")   #obtenemos headers por separado
    start_line = lineas_head[0].decode()  #obtener startline 
    partes_start_line = start_line.split(" ")

    if len(partes_start_line) < 3:
        return None

    if partes_start_line[0].startswith("HTTP/"): #es una respuesta 
        ver = partes_start_line[0]
        estado = partes_start_line[1]
        info_estado = " ".join(partes_start_line[2:]) #en caso de que sea "Not Found" (tiene un espacio)
        metodo = None
        direccion = None
    else:                               #es una solicitud
        metodo = partes_start_line[0]
        direccion = partes_start_line[1]
        ver = partes_start_line[2]
        estado = None
        info_estado = None
   
    headers = {}  #diccionario para almacenar headers

    for line in lineas_head[1:]:  #recorrer las líneas para guardarlas en diccionario.
        if line:  # por si hay una línea vacía
            nombre, _ , valor = line.decode().partition(": ")
            headers[nombre] = valor

    mensaje = {"method": metodo,
               "path": direccion,
               "version": ver,
               "status" : estado,
               "status_info": info_estado,
               "head": headers,
               "body": body}

    return mensaje


def create_HTTP_message(message):
    if message["method"] is not None:  #es request
        start_line = message["method"] + " " + message["path"] + " " + message["version"]

    else:          #es una respuesta 
        start_line = message["version"] + " " + message["status"] + " " +  message["status_info"]

    lineas_headers = []  #lista para almacenar headers

    for nombre, valor in message["head"].items():
        lineas_headers.append(f"{nombre}: {valor}")

    head_completo = start_line + "\r\n" + "\r\n".join(lineas_headers)  #unir todo el head
    return head_completo.encode() + b"\r\n\r\n" + message["body"]  #unir head + body (mensaje final)

def recibir_mensaje_completo(sock, buffsize):
    buffer = b""
    llamadas_recv=0
    # ¿Cómo sé que el HEAD llegó completo?
    # Buscando la secuencia "\r\n\r\n" dentro de lo acumulado en buffer.
    # Mientras no aparezca, seguimos llamando a recv() y acumulando bytes,
    # sin importar cuántas llamadas se necesiten.
    while not contains_end_of_message(buffer, b"\r\n\r\n"):
        # ¿Qué pasa si los headers no caben en mi buffer?
        # buffsize (1024) es solo el límite de cuántos bytes trae cada
        # llamada a recv(), no un límite total. Si el head es más grande,
        # simplemente necesitamos varias llamadas, acumulando en 'buffer'
        # hasta juntar el head completo.
        datos = sock.recv(buffsize)
        llamadas_recv+=1
        if not datos:       # el cliente cerró la conexión antes de completar los headers
            return buffer    
        buffer += datos

    # Ya sabemos que "\r\n\r\n" está en buffer: separamos lo que es head
    # de lo que ya llegó de más (puede venir parte del body junto con
    # la última tanda de headers, ya que recv() no respeta los límites
    # lógicos del mensaje).
    fin_headers = buffer.find(b"\r\n\r\n") + len(b"\r\n\r\n")
    head_bytes = buffer[:fin_headers]
    body_recibido = buffer[fin_headers:]

    # Para saber cuánto body esperar, buscamos Content-Length dentro
    # del head ya completo.
    content_length = 0
    for linea in head_bytes.split(b"\r\n"):
        if linea.lower().startswith(b"content-length:"):
            content_length = int(linea.split(b":")[1].strip())
            break

    # ¿Y el BODY? ¿Cómo sé si llegó el mensaje completo?
    # Content-Length nos dice cuántos bytes de body esperar.
    # Seguimos llamando a recv() y acumulando hasta que body_recibido
    # alcance ese largo; recién ahí el mensaje completo (head + body)
    # está garantizado.
    while len(body_recibido) < content_length:
        chunk = sock.recv(buffsize)
        llamadas_recv+=1
        if not chunk:
            break
        body_recibido += chunk

    print(f"mensaje recibido en {llamadas_recv} llamadas a recv() (buffsize={buffsize})")
    return head_bytes + body_recibido

def bloqueado(host, path_puro, f):
    recurso_completo = host + path_puro
    for entrada in f["blocked"]:
        if entrada == host or entrada == recurso_completo:
            return True
    return False

def extraer_path_puro(path):
    if path.startswith("http://") or path.startswith("https://"):
        resto = path.split("://", 1)[1]      # quita "http://" o "https://"
        idx = resto.find("/")
        return resto[idx:] if idx != -1 else "/"
    return path   # ya viene sin protocolo 


def reemplazar_palabras(body_bytes, forbidden_words):
    texto = body_bytes.decode()
    for entrada in forbidden_words:          
        for palabra, reemplazo in entrada.items():   
            texto = texto.replace(palabra, reemplazo)
    return texto.encode()








if __name__== "__main__":
    buffsize = 30
    new_socket_address = (IP_VM, 8000)
    print("Creando socket de server")
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
    server_socket.listen(3)

    print(' Esperando clientes')
    while True:
        new_socket, new_socket_address = server_socket.accept()
        recv_msg = recibir_mensaje_completo(new_socket, buffsize) 
        mensaje = parse_HTTP_message(recv_msg)
        if mensaje is None or "Host" not in mensaje["head"]:
            new_socket.close()
            continue

        host_header = mensaje["head"]["Host"]
        if ":" in host_header:
            host, puerto = host_header.split(":")
            puerto = int(puerto)
        else:
            host = host_header
            puerto = 80


        if mensaje["path"].endswith("/gatos.png"):
            with open("gatos.png", "rb") as f:
                img_bytes = f.read()
            respuesta = {
                "method": None, "path": None, "version": "HTTP/1.1",
                "status": "200", "status_info": "OK",
                "head": {"Content-Type": "image/png", "Content-Length": str(len(img_bytes))},
                "body": img_bytes
            }
            new_socket.sendall(create_HTTP_message(respuesta))
            new_socket.close()
            continue

        path_puro = extraer_path_puro(mensaje["path"])
        if bloqueado(host, path_puro, datos_file):
            html_403 = "<html><body><h1>403- Sitio bloqueado</h1><img src='/gatos.png'></body></html>"
            body_bytes = html_403.encode()
            respuesta = {
                "method": None, "path": None, "version": "HTTP/1.1",
                "status": "403", "status_info": "Forbidden",
                "head": {"Content-Type": "text/html", "Content-Length": str(len(body_bytes))},
                "body": body_bytes
            }
            new_socket.sendall(create_HTTP_message(respuesta))
            new_socket.close()
            continue

        mensaje["head"]["X-ElQuePregunta"] = username
        mensaje_modificado = create_HTTP_message(mensaje)
        socket_destino = socket.socket(socket.AF_INET, socket.SOCK_STREAM )  
        socket_destino.connect((host, puerto))
        socket_destino.sendall(mensaje_modificado) ## enviar el mensaje recibido por el proxy al server 
        respuesta_server = recibir_mensaje_completo(socket_destino, buffsize)
        respuesta_parseada = parse_HTTP_message(respuesta_server)

        if respuesta_parseada is not None and "forbidden_words" in datos_file:
            nuevo_body = reemplazar_palabras(respuesta_parseada["body"], datos_file["forbidden_words"])
            respuesta_parseada["body"]=nuevo_body
            respuesta_parseada["head"]["Content-Length"] = str(len(nuevo_body))
            respuesta_final = create_HTTP_message(respuesta_parseada)
        else:
            respuesta_final=respuesta_server

        new_socket.sendall(respuesta_final)
        socket_destino.close()



            


        # html = "<html><body><h1>Este es un proxy :) </h1></body></html>"
        # html_bytes = html.encode()
        # respuesta = {"method": None,
        #         "path": None,
        #         "version": "HTTP/1.1",
        #         "status" : "200",
        #         "status_info": "OK",
        #         "head": {"Content-Type":"text/html" , "Content-Length": (str(len(html_bytes))), "X-ElQuePregunta": username},
        #         "body": html_bytes}
        
        # new_socket.sendall(create_HTTP_message(respuesta))

        new_socket.close()
