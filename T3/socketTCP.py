import socket
import struct 
import random
import time

FORMATO_HEADER = '!IBBB'  # ! = network byte order, I = seq (4 bytes), B,B,B = syn, ack, fin (1 byte c/u)
HEADER_SIZE = struct.calcsize(FORMATO_HEADER)  # calcula el tamaño en bytes automáticamente

class SocketTCP:

    def __init__(self, debug = False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destino = None
        self.seq = 0
        self.estado = "NO CONECTADO"
        self.timeout = 1
        self.seq_otro_lado = None 
        self.bytes_faltantes = 0
        self.sobrante = b""
        self.debug = debug
 


    @staticmethod
    def create_segment(seq, syn, ack, fin, data):
        header = struct.pack(FORMATO_HEADER, seq, syn, ack, fin)
        return header + data

    @staticmethod
    def parse_segment(segmento):
        header_bytes = segmento[0:HEADER_SIZE]
        data = segmento[HEADER_SIZE:]
        seq , syn , ack, fin = struct.unpack(FORMATO_HEADER, header_bytes)

        return { "seq": seq , 
                "syn": syn,
                "ack":ack,
                "fin":fin,
                "data": data
                }

    def bind(self, address):
        self.sock.bind(address)
        self.estado = "ESCUCHANDO"
        return 

    def connect(self, address):
        self.destino = address
        self.seq = random.randint (0,100 )
        self.sock.settimeout(self.timeout)
        segmento_syn = self.create_segment( self.seq, 1,0,0, b"" )
        self.estado = "CONECTANDO"
        conectado = False
        while not conectado:
            self.sock.sendto(segmento_syn,self.destino)
            try:
                respuesta , direccion_server = self.sock.recvfrom(HEADER_SIZE+16)
                self.destino = direccion_server
                respuesta_parseada = SocketTCP.parse_segment(respuesta)
                if respuesta_parseada["syn"] == 1 and respuesta_parseada["ack"] == 1:

                    self.seq_otro_lado = respuesta_parseada["seq"]
                    segmento_ack= SocketTCP.create_segment(self.seq, 0,1,0,b"")
                    self.sock.sendto(segmento_ack, self.destino)
                    conectado = True
            except socket.timeout:
                if self.debug:
                    print(f"[Modo Debug] connect : timeout esperando SYN-ACK reenviando SYN (seq= {self.seq})")

        self.estado = "CONECTADO"
        return 

    def accept(self):
        segmento, direccion_cliente = self.sock.recvfrom(HEADER_SIZE + 16)
        segmento_parseado = SocketTCP.parse_segment(segmento)
        seq_cliente = segmento_parseado["seq"]

        new_socket = SocketTCP(debug=self.debug)
        new_socket.bind((self.sock.getsockname()[0], 0))
        new_socket.seq = random.randint(0, 100)
        new_socket.seq_otro_lado = seq_cliente
        new_socket.destino = direccion_cliente
        new_socket.sock.settimeout(new_socket.timeout)

        segmento_synack = SocketTCP.create_segment(new_socket.seq, 1, 1, 0, b"")
        new_socket.estado = "CONECTANDO"
        conectado = False
        
        while not conectado:
            new_socket.sock.sendto(segmento_synack, direccion_cliente)
            try:
                respuesta, _ = new_socket.sock.recvfrom(HEADER_SIZE + 16)
                respuesta_parseada = SocketTCP.parse_segment(respuesta)
                if respuesta_parseada["ack"] == 1:
                    conectado = True
            except socket.timeout:
                if self.debug:
                    print(f"[Modo debug] accept: timeout esperando ACK final reenviando SYN-ACK (seq = {new_socket.seq})") 
        new_socket.estado = "CONECTADO"
        nueva_direccion = new_socket.sock.getsockname()
        return new_socket, nueva_direccion

    def send(self, message):
        trozos = []
        for i in range (0, len(message), 16):
            trozo = message[i: i+16]
            trozos.append(trozo)
        largo_mensaje = len(message)
        segmento_largo_msg = struct.pack('!I', largo_mensaje)
        mensaje_completo = [segmento_largo_msg] + trozos

        self.sock.settimeout(self.timeout)
        for data in mensaje_completo:
            segmento = SocketTCP.create_segment(self.seq,0,0,0,data)
            confirmado = False
            while not confirmado:
                self.sock.sendto(segmento, self.destino)
                try:
                    respuesta, _ = self.sock.recvfrom(HEADER_SIZE+16 )
                    respuesta_parseada = SocketTCP.parse_segment(respuesta)
                    if respuesta_parseada["syn"] == 1 and respuesta_parseada["ack"]==1:
                        if self.debug:
                            print(f"[Modo debug] send: SYN-ACK duplicado recibido, reenviando ACK del handshake")
                        ack_handshake = SocketTCP.create_segment(self.seq,0,1,0,b"")
                        self.sock.sendto(ack_handshake,self.destino) 
                    elif respuesta_parseada["ack"] == 1 and respuesta_parseada["seq"] == self.seq + len(data):
                        confirmado = True
                        self.seq += len(data)
                except socket.timeout:
                    if self.debug:
                        print(f"[Modo debug] send: timeout esperando ACK, reenviando segmento (seq={self.seq})")

    def recv(self, buffsize):
        self.sock.settimeout(self.timeout)
        mensaje_recibido = b""
        if self.bytes_faltantes == 0:
            largo_recibido = False
            while not largo_recibido:
                try:
                    segmento, _ = self.sock.recvfrom(HEADER_SIZE + 16)
                    segmento_parseado = SocketTCP.parse_segment(segmento)
                    if segmento_parseado["seq"] == self.seq_otro_lado:
                        largo_msg = struct.unpack('!I', segmento_parseado["data"])[0]
                        self.bytes_faltantes = largo_msg
                        self.seq_otro_lado += len(segmento_parseado["data"])
                        ack = SocketTCP.create_segment(self.seq_otro_lado, 0, 1, 0, b"")
                        self.sock.sendto(ack, self.destino)
                        largo_recibido = True
                    else:
                        ack_repetido = SocketTCP.create_segment(self.seq_otro_lado, 0, 1, 0, b"")
                        self.sock.sendto(ack_repetido, self.destino)
                except socket.timeout:
                    if self.debug:
                        print(f"[Modo debug] recv: timeout esperando segmento de largo_msg, reintentando")
        total_restante = len(self.sobrante) + self.bytes_faltantes
        datos_a_recibir = min(total_restante, buffsize)
        if self.sobrante:
            mensaje_recibido += self.sobrante
            self.sobrante = b""
        while len(mensaje_recibido) < datos_a_recibir:
            try:
                segmento, _ = self.sock.recvfrom(HEADER_SIZE + 16)
                segmento_parseado = SocketTCP.parse_segment(segmento)
                if segmento_parseado["seq"] == self.seq_otro_lado:
                    mensaje_recibido += segmento_parseado["data"]
                    self.seq_otro_lado += len(segmento_parseado["data"])
                    self.bytes_faltantes -= len(segmento_parseado["data"])
                else:
                    if self.debug: 
                        print(f"[Modo debug] recv: segmento duplicado/fuera de orden (seq={segmento_parseado['seq']}, esperado={self.seq_otro_lado}), reenviando ACK sin consumir")
                ack = SocketTCP.create_segment(self.seq_otro_lado, 0, 1, 0, b"")
                self.sock.sendto(ack, self.destino)
            except socket.timeout:
                if self.debug:
                    print(f"[Modo debug] recv: timeout esperando segmento de datos, reintentando")

        if len(mensaje_recibido) > datos_a_recibir:
            sobrante_nuevo = mensaje_recibido[datos_a_recibir:]
            mensaje_recibido = mensaje_recibido[:datos_a_recibir]
            self.sobrante = sobrante_nuevo

        return mensaje_recibido

    def close(self):
        self.sock.settimeout(self.timeout)
        fin = SocketTCP.create_segment(self.seq, 0, 0, 1, b"")
        intentos = 0
        cerrado_con_confirmacion = False
        while intentos < 3 and not cerrado_con_confirmacion:
            self.sock.sendto(fin, self.destino)
            try:
                respuesta, _ = self.sock.recvfrom(HEADER_SIZE + 16)
                respuesta_parseada = SocketTCP.parse_segment(respuesta)
                if respuesta_parseada["ack"] == 1 and respuesta_parseada["fin"] == 1:
                    cerrado_con_confirmacion = True
            except socket.timeout:
                intentos += 1
                if self.debug:
                    print(f"[Modo debug] close: timeout esperando FIN+ACK (intento {intentos}/3), reenviando FIN")

        if cerrado_con_confirmacion:
            self.seq += 1
            ack_final = SocketTCP.create_segment(self.seq, 0, 1, 0, b"")
            for i in range(3):
                self.sock.sendto(ack_final, self.destino)
                time.sleep(self.timeout)
            self.seq += 1

        self.estado = "CERRADO"
        self.sock.close()

    def recv_close(self):
        self.sock.settimeout(None)
        segmento, _ = self.sock.recvfrom(HEADER_SIZE + 16)
        segmento_parseado = SocketTCP.parse_segment(segmento)
        if segmento_parseado["fin"] == 1:
            seq_z = segmento_parseado["seq"]
            finack = SocketTCP.create_segment(seq_z + 1, 0, 1, 1, b"")
            self.sock.sendto(finack, self.destino)
            self.sock.settimeout(self.timeout)
            intentos = 0
            recibido = False
            while intentos < 3 and not recibido:
                try:
                    respuesta_final, _ = self.sock.recvfrom(HEADER_SIZE + 16)
                    respuesta_final_parseada = SocketTCP.parse_segment(respuesta_final)
                    if respuesta_final_parseada["ack"] == 1:
                        recibido = True
                except socket.timeout:
                    intentos += 1
                    if self.debug:
                        print(f"[Modo debug] recv_close: timeout esperando ACK final (intento {intentos}/3)")
            self.estado = "CERRADO"
            self.sock.close()

