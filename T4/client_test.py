# CLIENT
from socketTCP import SocketTCP
client_socketTCP = SocketTCP()
client_socketTCP.connect(("localhost", 8000))
# test 1
message = "Mensje de len=16".encode()
client_socketTCP.send_using_go_back_n(message)
# test 2
message = "Mensaje de largo 19".encode()
client_socketTCP.send_using_go_back_n(message)
# test 3
message = "Mensaje de largo 19".encode()
client_socketTCP.send_using_go_back_n(message)

# CLIENT
largo = "Este es un mensaje bastante largo para probar que la ventana de Go-Back-N avanza correctamente varias veces.".encode() * 3
# test 4
client_socketTCP.send_using_go_back_n(largo)
# test 5
client_socketTCP.send_using_go_back_n(largo)