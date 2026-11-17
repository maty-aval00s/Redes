import socket
import router
import sys
if len(sys.argv) < 7:
    sys.exit("Uso: python3 cliente.py IP_router_final puerto_router_final mensaje IP_envío puerto_envío TTL")
ip_router_final = sys.argv[1]
puerto_router_final = int(sys.argv[2])
mensaje = sys.argv[3]
ip_envio = sys.argv[4]
puerto_envio = int(sys.argv[5])
ttl = int(sys.argv[6])

data = {"ip": ip_router_final,
        "puerto": puerto_router_final,
        "ttl": ttl,
        "mensaje": mensaje}

address = (ip_envio, puerto_envio)
packet = router.create_packet(data)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(packet, address)
sock.close()



