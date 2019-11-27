import serial
import time
conexao = serial.Serial('/dev/ttyUSB0', 9600) # Configuração da conexão
def pisca(tempo=1):
    while True:
        conexao.write(bytes([1])) # Escreve 1 no arduino (LED acende)
        time.sleep(tempo) # Aguarda n segundos
        conexao.write(bytes([2])) # Escreve 2 no arduino (LED apaga)
        time.sleep(tempo) # Aguarda n segundos
if __name__ == '__main__': # Executa a função
    pisca()
