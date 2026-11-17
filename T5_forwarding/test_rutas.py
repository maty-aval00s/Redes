import router

IP_packet_v1 = b'\x7f\x00\x00\x01\x22\xb1\x0ahola'  
parsed_IP_packet = router.parse_packet(IP_packet_v1)
print(parsed_IP_packet)
IP_packet_v2 = router.create_packet(parsed_IP_packet)  
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))