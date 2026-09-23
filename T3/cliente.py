import socket
import sys 
from socketTCP import SocketTCP

TROZOS_SIZE = 16

def obtener_destino():
    host = sys.argv[1]
    puerto = int(sys.argv[2]) 
    return host, puerto 

# def leer_archivo():
#     ruta_archivo = input("Ruta:")
#     with open(ruta_archivo, "rb") as f:
#         datos = f.read()
#     return datos 

# def trocear_datos( datos, size):
#     trozos = []
#     for i in range (0, len(datos), size):
#         trozo = datos[i: i+size]
#         trozos.append(trozo)
#     return trozos 

# def enviar_archivo( sock, destino , trozos): 
#     seq = 0
#     for trozo in trozos:
#         segmento = SocketTCP.create_segment(seq,0,0,0,trozo)
#         sock.sendto(segmento, destino)
#         seq += len(trozo)
#     return 


    


if __name__ == "__main__":
    host, puerto = obtener_destino()
    # datos = leer_archivo()
    # trozos = trocear_datos(datos, TROZOS_SIZE )
    # cliente_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # enviar_archivo( cliente_udp, (host, puerto), trozos)
    # cliente_udp.close()

    # client_socketTCP = SocketTCP()
    # client_socketTCP.connect(("localhost", 8000))
    # CLIENT
    # client_socketTCP = SocketTCP()
    # client_socketTCP.connect(("localhost", 8000))
    # # test 1
    # message = "Mensje de len=16".encode()
    # client_socketTCP.send(message)
    # # test 2
    # message = "Mensaje de largo 19".encode()
    # client_socketTCP.send(message)
    # # test 3
    # message = "Mensaje de largo 19".encode()
    # client_socketTCP.send(message)
    # client_socketTCP.close()
    
    contenido = sys.stdin.read()
    mensaje = contenido.encode()
    cliente = SocketTCP(debug=True)
    cliente.connect((host, puerto))
    
    cliente.send(mensaje)
    cliente.close()