import sys, time
from socketTCP import SocketTCP

cc_on = sys.argv[1] == "cc"          
mensaje = ("0123456789" * 120).encode()  # 1200 bytes

cliente = SocketTCP(debug=False)
cliente.timeout = 0.5
cliente.set_congestion_control(cc_on)
cliente.connect(("localhost", 8000))

for i in range(5):
    t0 = time.time()
    cliente.send_using_go_back_n(mensaje)
    t1 = time.time()
    print(f"Corrida {i+1}: {t1 - t0:.2f} s, {cliente.number_of_sent_segments} segmentos")