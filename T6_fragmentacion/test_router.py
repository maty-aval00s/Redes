import random
import router

IP_packet_v1 = router.create_packet({"ip": "127.0.0.1", "puerto": 8885, "ttl": 10,
                                     "id": 7, "offset": 0, "flag": 0,
                                     "mensaje": b"Este es un mensaje de prueba para la fragmentacion"})
MTU = 35

fragment_list = router.fragment_IP_packet(IP_packet_v1, MTU)
print("Fragmentos:", len(fragment_list))

IP_packet_v2 = router.reassemble_IP_packet(fragment_list)
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

# Desordenados
random.shuffle(fragment_list)
print("Desordenados:", router.reassemble_IP_packet(fragment_list) == IP_packet_v1)

# Incompleta: falta uno
print("Falta uno:", router.reassemble_IP_packet(fragment_list[:-1]))

# Un solo fragmento
print("Un fragmento:", router.reassemble_IP_packet([fragment_list[0]]))

# Paquete completo (sin fragmentar)
print("Paquete completo:", router.reassemble_IP_packet([IP_packet_v1]) == IP_packet_v1)