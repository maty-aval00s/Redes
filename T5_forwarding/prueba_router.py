import socket
import router
import sys

if len(sys.argv) < 4:
    sys.exit('Uso: python3 prueba_router.py "IP;puerto;TTL" IP_router_inicial puerto_router_inicial < archivo.txt')

ip_destino, puerto_destino, ttl = sys.argv[1].split(";")
puerto_destino = int(puerto_destino)
ttl = int(ttl)
address = (sys.argv[2], int(sys.argv[3]))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for linea in sys.stdin:
    paquete = {"ip": ip_destino,
               "puerto": puerto_destino,
               "ttl": ttl,
               "mensaje": linea.rstrip("\n")}
    sock.sendto(router.create_packet(paquete), address)
sock.close()