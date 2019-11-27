import os
import cv2
import sys
import struct
import numpy as np
from scipy import  signal


V2 = "aedat"  # Formato do arquivo (.AEDAT)
def loadaerdat(datafile='path.aedat', length=0, version=V2, debug=1, camera='DVS128'):
    # constants
    aeLen = 8  # 1 AE event takes 8 bytes
    readMode = '>II'  # struct.unpack(), 2x ulong, 4B+4B
    td = 0.000001  # timestep is 1us
    if(camera == 'DVS128'):
        xmask = 0x00fe  # Bin -> 0000 0000 1111 1110 || Dec -> 254
        xshift = 1
        ymask = 0x7f00  # Bin -> 0111 1111 0000 0000 || Dec -> 32512
        yshift = 8
        pmask = 0x1     # Bin -> 0000 0000 0000 0001 || Dec -> 1
        pshift = 0
    else:
        raise ValueError("Unsupported camera: %s" % (camera))

    aerdatafh = open(datafile, 'rb')
    k = 0  # line number
    p = 0  # pointer, position on bytes
    statinfo = os.stat(datafile)
    if length == 0:
        length = statinfo.st_size # Define 'length' = Tamanho do arquivo

    print("file size", length)
    
    # Verifica a versão do Python. 
    if sys.version[0] == '3':
        value = 35 # Se for >= 3 le o cabeçalho em binário.
    else:
        value = '#' # Se for < 3 le o cabeçalho como string.

    # header
    lt = aerdatafh.readline()
    while lt and lt[0] == value:
        p += len(lt)
        k += 1
        lt = aerdatafh.readline() 
        if debug >= 2:
            print(str(lt))
        continue
    
    # variables to parse
    timestamps = []
    xaddr = []
    yaddr = []
    pol = []
    
    # read data-part of file
    aerdatafh.seek(p)
    s = aerdatafh.read(aeLen)
    p += aeLen
    
    print(xmask, xshift, ymask, yshift, pmask, pshift)    
    while p < length:
        addr, ts = struct.unpack(readMode, s)
        # parse event type
        if(camera == 'DVS128'):     
            x_addr = (addr & xmask) >> xshift # Endereço x -> bits de 1-7
            y_addr = (addr & ymask) >> yshift # Endereço y -> bits de 8-14
            a_pol = (addr & pmask) >> pshift  # Endereço polaridade -> bit 0            
            if debug >= 3: 
                print("ts->", ts) 
                print("x-> ", x_addr)
                print("y-> ", y_addr)
                print("pol->", a_pol)

            timestamps.append(ts)
            xaddr.append(x_addr)
            yaddr.append(y_addr)
            pol.append(a_pol)
                  
        aerdatafh.seek(p)
        s = aerdatafh.read(aeLen)
        p += aeLen        

    if debug > 0:
        try:
            print("read %i (~ %.2fM) AE events, duration= %.2fs" % (len(timestamps), len(timestamps) / float(10 ** 6), (timestamps[-1] - timestamps[0]) * td))
            n = 5
            print("showing first %i:" % (n))
            print("timestamps: %s \nX-addr: %s\nY-addr: %s\npolarity: %s" % (timestamps[0:n], xaddr[0:n], yaddr[0:n], pol[0:n]))
        except:
            print("failed to print statistics")

    return np.array(timestamps), np.array(xaddr), np.array(yaddr), np.array(pol)


def matrix_active(x, y, pol, e_ini=0, e_fin=1000, filtro=None, matrixType=1):
    '''
    Gera uma imagem somando todos os eventos dentro do intervalo de tI e tF.
    '''
    x, y, pol = x[e_ini:e_fin], y[e_ini:e_fin], pol[e_ini:e_fin] # recebe um intervalo indicando a quantidade de eventos
    matrix = np.zeros([128, 128]) # Cria uma matriz de zeros 128x128 onde serão inseridos os eventos
    pol = (pol - 0.5) # Os eventos no array de Polaridade passam a ser -0.5 ou 0.5
    if(len(x) == len(y)): # Verifica se o tamanho dos arrays são iguais   
        for i in range(len(x)):
            matrix[y[i], x[i]] += pol[i] # insere os eventos dentro da matriz de zeros
    else:
        print("error x,y missmatch")
    
    if matrixType == 1:
        idx = 0
        for i in matrix: # Limita os eventos em -0.5 ou 0.5
            for j, v in enumerate(i):
                if v > 0.5:
                    matrix[idx][j] = 0.5
                if v < -0.5:
                    matrix[idx][j] = -0.5
            idx += 1
        matrix = (matrix * 256) + 128 # Normaliza a matriz para 8bits -> 0 - 255

    if matrixType == 2:
        idx = 0
        for i in matrix: # Limita os eventos em -0.5 ou 0.5
            for j, v in enumerate(i):
                if v > 0.5:
                    matrix[idx][j] = 0.5
                if v <= -0.5:
                    matrix[idx][j] = 0.5
            idx += 1
        matrix = (matrix * 510) # Normaliza a matriz para 8bits -> 0 - 255

    if filtro == 'mediana':
        matrix = signal.medfilt(matrix)
    elif filtro == 'media':
        kernel = np.ones((3,3),np.float32)/9
        matrix = cv2.filter2D(matrix,-1,kernel)
    else:
        pass
    return matrix

