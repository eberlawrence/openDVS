'''
Biomedical Engineering Lab (BioLab)- Federal University of Uberlandia (UFU)
Eber Lawrence Souza - email: eberlawrence@hotmail.com
'''


import os
import sys
import struct
import numpy as np


def loadAERDAT(datafile='', length=0, debug=1):

    camera = ''
    aeLen = 8  # 1 AE event takes 8 bytes
    readMode = '>II'  # struct.unpack(), 2x ulong, 4B + 4B
    td = 0.000001  # timestep is 1us

    k, p = 0, 0  # line number,  pointer (position on bytes)

    # Check the Python version.
    if sys.version[0] == '3':
        value = 35 # if value >= 3 read the header as binary.
    else:
        value = '#' # if value < 3 read the header as string.

    aerdatafh = open(datafile, 'rb')
    statinfo = os.stat(datafile)
    if length == 0:
        length = statinfo.st_size # Define 'length' = file length
        print("file size", length)

    # Read the header
    lt = aerdatafh.readline()
    while lt and lt[0] == value:
        p += len(lt)
        k += 1
        if k == 10:
            camera = str(lt).split('.')[-1][0 : 6]
            print("Camera used: ", camera)
        lt = aerdatafh.readline()
        if debug >= 2:
            print(str(lt))
        continue

    if(camera == 'DVS128'):
        xmask = 0x00fe  # Bin -> 0000 0000 1111 1110 || Dec -> 254
        xshift = 1
        ymask = 0x7f00  # Bin -> 0111 1111 0000 0000 || Dec -> 32512
        yshift = 8
        pmask = 0x1     # Bin -> 0000 0000 0000 0001 || Dec -> 1
        pshift = 0
    else:
        raise ValueError("Unsupported camera: %s" % (camera))

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
    t, x, y, p = np.array(timestamps), np.array(xaddr), np.array(yaddr), np.array(pol)
    return t - t[0], x, y, p
