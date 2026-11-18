import socket
import time
import router

def fragmentar(id_paquete, mensaje, mtu):
    paquete = router.create_packet({"ip": "127.0.0.1", "puerto": 8885, "ttl": 10,
                                    "id": id_paquete, "offset": 0, "flag": 0,
                                    "mensaje": mensaje.encode()})
    return router.fragment_IP_packet(paquete, mtu)

A = fragmentar(111, "Mensaje A: primero de dos paquetes fragmentados", 35)
B = fragmentar(222, "Mensaje B: segundo paquete con otro ID distinto", 35)
print("Fragmentos A:", len(A), "| Fragmentos B:", len(B))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destino = ("127.0.0.1", 8885)

def enviar(nombre, fragmentos):
    print(f"--- {nombre} ---")
    for f in fragmentos:
        sock.sendto(f, destino)
        time.sleep(0.1)
    time.sleep(0.5)

enviar("1. A en orden", A)
enviar("2. B en desorden", [B[2], B[0], B[3], B[1]])
intercalados = [x for par in zip(A, B) for x in par]
enviar("3. A y B intercalados", intercalados)