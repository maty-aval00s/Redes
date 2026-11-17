import sys
import socket




def create_packet(parsed_IP_packet):
    ip_packet = parsed_IP_packet["ip"]
    puerto_packet = parsed_IP_packet["puerto"]
    ttl_packet = parsed_IP_packet["ttl"]
    mensaje_packet = parsed_IP_packet["mensaje"]
    abcd = ip_packet.split(".")
    abcd = [int(x) for x in abcd]
    bytes_ip = bytes(abcd)
    bytes_puerto = puerto_packet.to_bytes(2, "big")
    bytes_ttl = ttl_packet.to_bytes(1, "big")
    bytes_mensaje = mensaje_packet.encode()
    return bytes_ip + bytes_puerto + bytes_ttl + bytes_mensaje

def parse_packet(IP_packet: bytes):
    ip_bytes = IP_packet[0:4]
    puerto_bytes = IP_packet[4:6]
    ttl = IP_packet[6]
    mensaje_bytes = IP_packet[7:]
    ip = [str(b) for b in ip_bytes]
    ip = ".".join(ip)
    puerto = int.from_bytes(puerto_bytes, "big")
    mensaje = mensaje_bytes.decode()
    packet = {"ip": ip,
              "puerto": puerto,
              "ttl": ttl,
              "mensaje": mensaje
              }
    return packet

def check_routes(routes_file_name: str, destination_address: tuple[str, int], rr_state:dict):
    destination_ip= destination_address[0]
    destination_p= destination_address[1]
    candidatas = []
    area= None
    with open(routes_file_name, "r") as file:
        for linea in file:
            campos = linea.split()
            if not campos:
                continue
            red = campos[0]
            p_ini = int(campos[1])
            p_fin = int(campos[2])
            ip_sig = campos[3]
            p_sig = int(campos[4])
            if (p_ini <= destination_p and destination_p <= p_fin):
                if area is None:
                    area = (red, p_ini, p_fin)
                if (red, p_ini, p_fin) == area:
                    candidatas.append((ip_sig, p_sig))
    
    if not candidatas:   
        return None
    contador = rr_state.get(area, 0)
    next_hop = candidatas[contador % len(candidatas)]
    rr_state[area] = contador + 1
    return next_hop
            
    

if __name__ =="__main__":
    if len(sys.argv) < 4:
        sys.exit("Uso: python3 router.py IP puerto rutas.txt")
    router_IP = sys.argv[1]
    router_puerto = int(sys.argv[2])
    router_rutas = sys.argv[3]

    escucha = (router_IP, router_puerto)

    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_router.bind(escucha)
    rr_state = {}
    while True:
        data = socket_router.recv(1024)
        paquete = parse_packet(data)
        if paquete["ttl"] <= 0:
            print(f"Se recibió paquete {paquete} con TTL 0")
            continue
        destination_address = (paquete["ip"], paquete["puerto"])
        if escucha == destination_address:
            print(paquete["mensaje"])
        else:
            next_hop = check_routes(router_rutas, destination_address, rr_state)
            if next_hop is None:
                print(f"No hay rutas hacia {destination_address} para paquete {paquete}")
            else:
                paquete["ttl"] -= 1
                print(f"Redirigiendo paquete {paquete} con destino final {destination_address} desde {escucha} hacia {next_hop}")
                socket_router.sendto(create_packet(paquete), next_hop)
    




