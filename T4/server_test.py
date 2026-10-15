# SERVER
from socketTCP import SocketTCP
server_socketTCP = SocketTCP()
server_socketTCP.bind(("localhost",8000))
connection_socketTCP, new_address = server_socketTCP.accept()

# test 1
buff_size = 16
full_message = connection_socketTCP.recv_using_go_back_n(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

# test 2
buff_size = 19
full_message = connection_socketTCP.recv_using_go_back_n(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

# test 3
buff_size = 14
message_part_1 = connection_socketTCP.recv_using_go_back_n(buff_size)
message_part_2 = connection_socketTCP.recv_using_go_back_n(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
else: print("Test 3: Failed")

# SERVER
# test 4: mensaje largo (más de 8 segmentos, la ventana tiene que avanzar)
largo = "Este es un mensaje bastante largo para probar que la ventana de Go-Back-N avanza correctamente varias veces.".encode() * 3
full_message = connection_socketTCP.recv_using_go_back_n(len(largo))
print("Test 4:", "Passed" if full_message == largo else "Failed")

# test 5: mensaje largo leído en varios recv con buffer chico
recibido = b""
while len(recibido) < len(largo):
    recibido += connection_socketTCP.recv_using_go_back_n(50)
print("Test 5:", "Passed" if recibido == largo else "Failed")