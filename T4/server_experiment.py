
from socketTCP import SocketTCP

mensaje = ("0123456789" * 120).encode()

servidor = SocketTCP(debug=False)
servidor.bind(("localhost", 8000))
conexion, _ = servidor.accept()
conexion.timeout = 0.5

for i in range(5):
    recibido = conexion.recv_using_go_back_n(len(mensaje))
    print(f"Corrida {i+1}:", "OK" if recibido == mensaje else "ERROR")