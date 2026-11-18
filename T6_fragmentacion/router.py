import sys
import socket
HEADER_SIZE = 20



def create_packet(parsed_IP_packet):
    ip_packet = parsed_IP_packet["ip"]
    puerto_packet = parsed_IP_packet["puerto"]
    ttl_packet = parsed_IP_packet["ttl"]
    mensaje_packet = parsed_IP_packet["mensaje"]
    id_packet = parsed_IP_packet["id"]
    offset_packet = parsed_IP_packet["offset"]
    flag_packet = parsed_IP_packet["flag"]
    abcd = ip_packet.split(".")
    abcd = [int(x) for x in abcd]
    bytes_ip = bytes(abcd)
    bytes_puerto = puerto_packet.to_bytes(2, "big")
    bytes_ttl = ttl_packet.to_bytes(1, "big")
    bytes_id = id_packet.to_bytes(4, "big")
    bytes_offset = offset_packet.to_bytes(4, "big")
    bytes_size = len(mensaje_packet).to_bytes(4,"big")
    bytes_flag = flag_packet.to_bytes(1,"big")
    return bytes_ip + bytes_puerto + bytes_ttl  + bytes_id + bytes_offset + bytes_size + bytes_flag + mensaje_packet

def parse_packet(IP_packet: bytes):
    ip_bytes = IP_packet[0:4]
    puerto_bytes = IP_packet[4:6]
    ttl = IP_packet[6]
    id_bytes = IP_packet[7:11]
    offset_bytes = IP_packet[11:15]
    size_bytes = IP_packet[15:19]
    flag = IP_packet[19]
    mensaje_bytes = IP_packet[20:]
    ip = [str(b) for b in ip_bytes]
    ip = ".".join(ip)
    puerto = int.from_bytes(puerto_bytes, "big")
    id = int.from_bytes(id_bytes,"big")
    offset = int.from_bytes(offset_bytes,"big")
    size = int.from_bytes(size_bytes,"big")
    mensaje = mensaje_bytes
    packet = {"ip": ip,
              "puerto": puerto,
              "ttl": ttl,
              "id":id,
              "offset": offset,
              "size":size,
              "flag":flag,
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
            mtu = int(campos[5])
            if (p_ini <= destination_p and destination_p <= p_fin):
                if area is None:
                    area = (red, p_ini, p_fin)
                if (red, p_ini, p_fin) == area:
                    candidatas.append(((ip_sig, p_sig), mtu))
    
    if not candidatas:   
        return None
    contador = rr_state.get(area, 0)
    next_hop = candidatas[contador % len(candidatas)][0]
    next_mtu = candidatas[contador % len(candidatas)][1]
    rr_state[area] = contador + 1
    return (next_hop, next_mtu)
            

def fragment_IP_packet(IP_packet: bytes, MTU: int) -> list[bytes]:
    if len(IP_packet) <= MTU:
        return [IP_packet]

    paquete = parse_packet(IP_packet)
    mensaje = paquete["mensaje"]
    trozo = MTU - HEADER_SIZE
    if trozo <= 0:
        raise ValueError(f"MTU {MTU} no alcanza para el header de {HEADER_SIZE} bytes")

    fragmentos = []
    for inicio in range(0, len(mensaje), trozo):
        fragmento = dict(paquete)
        fragmento["mensaje"] = mensaje[inicio:inicio + trozo]
        fragmento["offset"] = paquete["offset"] + inicio
        es_ultimo = inicio + trozo >= len(mensaje)
        fragmento["flag"] = paquete["flag"] if es_ultimo else 1
        fragmentos.append(create_packet(fragmento))
    return fragmentos


def reassemble_IP_packet(fragment_list: list[bytes]) -> bytes | None:
    if not fragment_list:
        return None

    fragmentos = sorted((parse_packet(f) for f in fragment_list),
                        key=lambda p: p["offset"])

    if fragmentos[0]["offset"] != 0:
        return None
    for actual, siguiente in zip(fragmentos, fragmentos[1:]):
        if actual["offset"] + actual["size"] != siguiente["offset"]:
            return None
        if actual["flag"] != 1:
            return None
    if fragmentos[-1]["flag"] != 0:
        return None

    paquete = dict(fragmentos[0])
    paquete["mensaje"] = b"".join(p["mensaje"] for p in fragmentos)
    paquete["offset"] = 0
    paquete["flag"] = 0
    return create_packet(paquete)



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
    fragmentos_recibidos = {}
    while True:
        data = socket_router.recv(1024)
        paquete = parse_packet(data)
        if paquete["ttl"] <= 0:
            print(f"Se recibió paquete {paquete} con TTL 0")
            continue
        destination_address = (paquete["ip"], paquete["puerto"])
        if escucha == destination_address:
            id_paquete = paquete["id"]
            fragmentos_recibidos.setdefault(id_paquete, []).append(data)
            completo = reassemble_IP_packet(fragmentos_recibidos[id_paquete])
            if completo is None:
                print(f"Fragmento offset {paquete['offset']} guardado para ID {id_paquete}, esperando el resto")
            else:
                print(parse_packet(completo)["mensaje"].decode())
                del fragmentos_recibidos[id_paquete]
        else:
            routes = check_routes(router_rutas, destination_address, rr_state)

            if routes is None:
                print(f"No hay rutas hacia {destination_address} para paquete {paquete}")
            else:
                next_hop, next_mtu = routes
                paquete["ttl"] -= 1
                fragmentos = fragment_IP_packet(create_packet(paquete), next_mtu)
                print(f"Redirigiendo paquete {paquete} con destino final {destination_address} desde {escucha} hacia {next_hop} (MTU {next_mtu}, {len(fragmentos)} fragmento(s))")
                for fragmento in fragmentos:
                    socket_router.sendto(fragmento, next_hop)
    




