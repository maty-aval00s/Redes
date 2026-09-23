import socket
from socketTCP import SocketTCP

ESCUCHA = 8000

# def new_socket(host, puerto):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((host,puerto))
#     return sock
# def escuchar(sock):
#     while True:
#         segmento, direccion = sock.recvfrom(1024)
#         info = SocketTCP.parse_segment(segmento)
#         print(f"seq={info['seq']} syn={info['syn']} ack={info['ack']} fin={info['fin']}")
#         print( info["data"].decode())
#     return


if __name__ == "__main__":

    # # SERVER
    server_socketTCP = SocketTCP(debug=True)
    server_socketTCP.bind(("localhost", 8000))
    connection_socketTCP, new_address = server_socketTCP.accept()
    print("Handshake completo. Nueva direccion:", new_address)
    mensaje_completo = connection_socketTCP.recv(10000)
    print(mensaje_completo.decode())
    connection_socketTCP.recv_close()
    print("Conexion cerrada.")
    
    # # test 1
    # buff_size = 16
    # full_message = connection_socketTCP.recv(buff_size)
    # print("Test 1 received:", full_message)
    # if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    # else: print("Test 1: Failed")

    # # test 2
    # buff_size = 19
    # full_message = connection_socketTCP.recv(buff_size)
    # print("Test 2 received:", full_message)
    # if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    # else: print("Test 2: Failed")

    # # test 3
    # buff_size = 14
    # message_part_1 = connection_socketTCP.recv(buff_size)
    # message_part_2 = connection_socketTCP.recv(buff_size)
    # print("Test 3 received:", message_part_1 + message_part_2)
    # if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    # else: print("Test 3: Failed")

    # connection_socketTCP.recv_close()
