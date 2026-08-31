import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE, RR , A
import dnslib
from collections import deque , Counter ##librería nativa de python 
IP_VM = "10.0.2.15"
puerto = 8000
buffsize = 4096
address = (IP_VM, puerto)
root_ip = "198.41.0.4"

def parsear_msg(msg):
    msg_parseado = DNSRecord.parse(msg)
    resultado = {
        "qname": msg_parseado.get_q().get_qname(),
        "ancount": msg_parseado.header.a ,
        "nscount": msg_parseado.header.auth,
        "arcount": msg_parseado.header.ar ,
        "answer": msg_parseado.rr,
        "authority": msg_parseado.auth,
        "additional": msg_parseado.ar       

    }
    return resultado

def resolver(mensaje_consulta: bytes, ip_addr=root_ip, nombre_server= ".") -> bytes:
    #enviar query a (ip_addr,53) y esperar respuesta 
    consulta_parseada = parsear_msg(mensaje_consulta)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f'(debug) Consultando \'{consulta_parseada["qname"]}\' a \'{nombre_server}\' con dirección IP \'{ip_addr}\'' )
    sock.sendto(mensaje_consulta, (ip_addr,53))
    respuesta, _ = sock.recvfrom(buffsize)
    sock.close()

    resultado = parsear_msg(respuesta)

    #si llega una respuesta directa (b)
    if resultado["ancount"] > 0:
        for registro in resultado["answer"]:
            if QTYPE.get(registro.rtype) == "A":
                return respuesta 
    elif resultado["nscount"] >0: #caso c
        ip_en_additional = None
        nombre_ns_additional = None
        for registro in resultado["additional"]:
            if QTYPE.get(registro.rtype) == "A": #caso c.1
                ip_en_additional = str(registro.rdata)
                nombre_ns_additional = str(registro.rname)
                break
        if ip_en_additional is not None:
            return resolver(mensaje_consulta, ip_en_additional, nombre_ns_additional)
        else: #caso c.2
            nombre_ns = None
            for registro in resultado["authority"]:
                if isinstance(registro.rdata, dnslib.dns.NS):
                    nombre_ns = str(registro.rdata)
                    break
            query_ns_bytes = DNSRecord.question(nombre_ns).pack()
            respuesta_ns = resolver(query_ns_bytes)
            respuesta_parseada = parsear_msg(respuesta_ns)
            ip_respuesta = str(respuesta_parseada["answer"][0].rdata)
            return resolver(mensaje_consulta, ip_respuesta, nombre_ns)
        
    return None #caso d
                    

def armar_respuesta_cache(msg_original: bytes, ip: str) -> bytes:
    query = DNSRecord.parse(msg_original)
    query.add_answer(RR(query.q.qname, QTYPE.A, rdata=A(ip)))
    return query.pack()



if __name__ == "__main__":
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.bind(address)
    ultimas_querys = deque(maxlen=20)
    cache = {}

    while True:
        msg , origen = socket_server.recvfrom(buffsize)
        msg_parseado = parsear_msg(msg)
        qname = str(msg_parseado["qname"])
        ultimas_querys.append(qname)
        mas_frecuentes = Counter(ultimas_querys).most_common(3)
        
        respuesta = None
        if qname in cache:
            print(f"(debug) Utilizando caché para '{qname}'")
            respuesta = armar_respuesta_cache(msg, cache[qname])
        else:
            print(f"(debug) '{qname}' no está en caché, resolviendo...")
            respuesta = resolver(msg)
            ip = None
            if respuesta is not None:
                for dominio , cantidad in mas_frecuentes:
                    if dominio == qname:
                        respuesta_parseada= parsear_msg(respuesta)
                        for registro in respuesta_parseada["answer"]:
                            if QTYPE.get(registro.rtype) == "A":
                                ip = str(registro.rdata)
                                cache[qname] = ip
                                break
                        break
                

        if respuesta is not None:
            socket_server.sendto(respuesta, origen)

