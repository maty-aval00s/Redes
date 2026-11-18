import socket
import random
import router
import sys

if len(sys.argv) < 4:
    sys.exit('Uso: python3 prueba_router.py "IP;puerto;TTL" IP_router_inicial puerto_router_inicial < archivo.txt')

campos = sys.argv[1].split(";")
ip_destino = campos[0]
puerto_destino = int(campos[1])
ttl = int(campos[2])
id_fijo = int(campos[3]) if len(campos) > 3 else None
address = (sys.argv[2], int(sys.argv[3]))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for linea in sys.stdin:
    paquete = {"ip": ip_destino,
               "puerto": puerto_destino,
               "ttl": ttl,
               "id": id_fijo if id_fijo is not None else random.randint(0, 2**32 - 1),
               "offset": 0,
               "flag": 0,
               "mensaje": linea.rstrip("\r\n").encode()}
    sock.sendto(router.create_packet(paquete), address)
sock.close()