import socket
import struct




HOST = ''
PORT = 8080
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((HOST, PORT))
while True:
	vet = []
	msg, cliente = udp.recvfrom(65535)
	for a in msg:
		vet.append(a)
	pol = vet[0]
	x = vet[1]
	y = vet[2]
	ts = (vet[3] << 24) | (vet[4] << 16) | (vet[5] << 8) | (vet[6] << 0)
	print("pol: ", pol)
	print("x: ", x)
	print("y: ", y)
	print("ts: ", ts)
	break


udp.close()
