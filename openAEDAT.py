import struct
import os
import numpy as np
from matplotlib import pyplot as plt, image as im
import pandas as pd
from scipy import ndimage, signal, ndimage
import sys
import cv2
from PIL import ImageDraw, Image

V2 = "aedat"  # Formato do arquivo (.AEDAT)
def loadaerdat(datafile='path.aedat', length=0, version=V2, debug=1, camera='DVS128'):
    """    
    load AER data file and parse these properties of AE events:
    - timestamps (in us), 
    - x,y-position [0..127]
    - polarity (0/1)

    @param datafile - path to the file to read
    @param length - how many bytes(B) should be read; default 0=whole file
    @param version - which file format version is used: "aedat" = v2, "dat" = v1 (old)
    @param debug - 0 = silent, 1 (default) = print summary, >=2 = print all debug
    @param camera='DVS128' or 'DAVIS240'
    @return (ts, xpos, ypos, pol) 4-tuple of lists containing data of all events;
    """
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

T, X, Y, P = loadaerdat('TrackingCopo.aedat')



'''
t, x, y, p = openAEDAT.loadaerdat('TrackingCopo.aedat')
t = (t - t[0]).astype(float)/100000
t = torch.from_numpy(t)
x = torch.from_numpy(x)
y = torch.from_numpy(y)
p = torch.from_numpy(p)
'''

a = tuple(map(tuple, np.ones((126,126),dtype=int)))
a = (a,a,a,a)
a = (a,a,a,a,a,a,a,a,a,a,a,a,a,a,a)
a = (a,a)
a = tuple([a])*100

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














def bounding_boxe(x,y, e_ini=0, e_fin=1000, m=0.01):
    gap = e_fin - e_ini
    Hx, Hy = [], []
    x, y = x[e_ini:e_fin], y[e_ini:e_fin]
    x, y = signal.medfilt(x), signal.medfilt(y)
    for i in range(128):
        Hx.append(len(x[x==i]))
        Hy.append(len(y[y==i]))
    Hx = np.array(Hx)
    Hy = np.array(Hy)
    P1, P2 = [0,0], [0,0]
    P1[0] = np.where(Hx > gap*m)[0][0]
    P1[1] = np.where(Hy > gap*m)[0][0]
    P2[0] = np.where(Hx > gap*m)[0][-1]
    P2[1] = np.where(Hy > gap*m)[0][-1]
    
    return np.array(P1), np.array(P2)

def particula(x, y, e_ini=0, e_fin=1000, limiar=30):
    x = X[e_ini:e_fin].copy()
    y = Y[e_ini:e_fin].copy()
    xy1 = list(zip(x,y))
    xy2 = xy1.copy()
    lc = []
    listaDif = lambda a,b: True if len(set(a) - set(b)) != len(set(a)) else False 
    while len(xy2) > 0:
        l = []
        e = xy2[0]
        l.append(e)
        xy2.remove(xy2[0])
        p1, p2, p3, p4, p6, p7, p8, p9 = (e[0]-1, e[1]-1), (e[0]-1, e[1]  ), (e[0]-1, e[1]+1), \
                                         (e[0]  , e[1]-1),                   (e[0]  , e[1]+1), \
                                         (e[0]+1, e[1]-1), (e[0]+1, e[1]  ), (e[0]+1, e[1]+1)
        if p1 in xy1:
            try:            xy2.remove(p1)
            except: pass
            l.append(p1)
        if p2 in xy1:
            try:            xy2.remove(p2)
            except: pass
            l.append(p2)
        if p3 in xy1: 
            try:            xy2.remove(p3)
            except: pass
            l.append(p3)
        if p4 in xy1: 
            try:            xy2.remove(p4)
            except: pass
            l.append(p4)
        if p6 in xy1: 
            try:            xy2.remove(p6)
            except: pass
            l.append(p6)
        if p7 in xy1: 
            try:            xy2.remove(p7)
            except: pass
            l.append(p7)
        if p8 in xy1: 
            try:            xy2.remove(p8)
            except: pass
            l.append(p8)
        if p9 in xy1: 
            try:            xy2.remove(p9)
            except: pass
            l.append(p9)
        lc.append(l)

    flag = False
    i, j = 0, 1
    lp = lc.copy()

    while i < len(lp):    
        if j < len(lp):
            if  j != i:
                if listaDif(lp[i],lp[j]) == True:
                    lp[i].extend(lp[j])
                    lp[i] = list(set(lp[i]))
                    lp.remove(lp[j])
                    if j < i:   i -= 1
                else:
                    j += 1
            else:
                j += 1
        else:
            i += 1
            j = 0
    m = []
    for i in range(len(lp)):
        lp[i] = list(set(lp[i]))
        m.append(len(lp[i]))
    part = list(zip(m,lp))
    part2 = []
    for i in range(len(part)):
        if part[i][0] >= limiar:
            part2.append(part[i])

    centro = []
    pMax, pMin = [], []
    for i in part2:
        p1, p2 = [], []
        cX, cY = 0, 0
        for j in i[1]:
            p1.append(j[0])
            p2.append(j[1])
        cX, cY = sum(p1)/i[0], sum(p2)/i[0]   
        centro.append((cX,cY))
        pMax.append((max(p1), max(p2)))
        pMin.append((min(p1), min(p2)))

    return centro, pMax, pMin


def create_images(fps=100, t=T, x=X, y=Y, p=P, lim='part'):
    '''
    Divide a quantidade de eventos totais em varias imagens. Salva as imagens na pasta imagens.
    '''
    time = (t[-1]-t[0])/1000000
    frames = fps*time
    events = int(len(t)/frames)
    i, f = 0, events
    frame = 0
    matrices = []
    while frame < frames:
        m = matrix_active(x, y, p, i, f, matrixType=1)
        im.imsave('imagens\\img'+str(frame)+'.png', m, cmap='gray')
        image = Image.open('imagens\\img'+str(frame)+'.png')
        draw = ImageDraw.Draw(image)
        # Tracking de objetos:
        # Por Partículas
        if lim == 'part':
            c, pMax, pMin = particula(e_ini=i, e_fin=f)
            for j in range(len(c)):
                draw.ellipse([pMin[j][0], pMin[j][1], pMax[j][0],pMax[j][1]], 
                             outline=(0,255,0))

        # Por Histograma            
        elif lim == 'hist':
            p1, p2 = bounding_boxe(e_ini=i, e_fin=f, m=0.025)
            draw.rectangle([p1[0],p1[1], p2[0], p2[1]], outline=(255,0,0,255))
        
        if saveImage: 
        	#image = ndimage.rotate(image,180)
        	im.imsave('imagens\\img'+str(frame)+'.png', image)
    	i += events
    	f += events
    	frame += 1
    	matrices.append(image)
    	return matrices



# Chama a função para criar os frames 
#create_images(lim='hist')


# Cria um vídeo no formato .avi juntando todos os frames.
#image_folder = 'imagens'
#video_name = 'imagens\\video.avi'
#images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
#frame = cv2.imread(os.path.join(image_folder, images[0]))
#height, width, layers = frame.shape
#video = cv2.VideoWriter(video_name, -1, 34, (width,height))
#for image in images:
#    video.write(cv2.imread(os.path.join(image_folder, image)))
#cv2.destroyAllWindows()
#video.release()

