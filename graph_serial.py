#!/usr/bin/python

import sys, serial, argparse
import numpy as np
import glob
from collections import deque
from time import sleep
import struct
import itertools
import subprocess
import time
import datetime
import getopt
import os

#from sklearn.multiclass import OneVsOneClassifier
#from sklearn.multiclass import OneVsRestClassifier
#from sklearn.neural_network import MLPClassifier
#from sklearn.preprocessing import StandardScaler
#from sklearn import preprocessing
#from sklearn import svm

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from pylab import *

nSamples = 500
nChannels = 4

class AnalogPlot:
    def __init__(self, strPort, maxLen):
        self.ser = serial.Serial(strPort, 115200)
        self.maxLen = maxLen
        self.paused = False
        #self.trained = False
        #self.clf = OneVsRestClassifier(MLPClassifier(solver='lbfgs', alpha=1e-1, hidden_layer_sizes=(20,), random_state=1))
        #self.scaler = StandardScaler()
        self.buffers = []
        for i in range(0,nChannels):
            self.buffers.append(deque([0.0]*maxLen, maxlen = maxLen))

    # update plot
    def update(self, frameNum, lines):

        while self.ser.inWaiting() > 50:
            try:
                first_bits = self.ser.read(2)
                while first_bits != '\xBE\xEF':
                    first_bits = self.ser.read(2)
                data = self.ser.read(nChannels*2)
                data_unpacked = struct.unpack(str(nChannels) + 'H', data)

                for i in range(0,nChannels):
                    self.buffers[i].append(data_unpacked[i])
                    lines[i].set_data(range(self.maxLen), self.buffers[i])

                #print data_unpacked

            except KeyboardInterrupt:
                print('exiting')

    def close(self):
        self.ser.write('\xFF')
        self.ser.flush()
        self.ser.close()
        print 'closing analogPlot'

#def saveData():
#    timestr = time.strftime("%Y%m%d-%H%M%S")
#    dirpath = os.path.join(parentPath, timestr)
#    os.mkdir(dirpath)
#    os.chdir(dirpath)
#    trainingLabels = np.array(analogPlot.labels)
#    trainingSet = np.array(analogPlot.features)
#    np.save('labels', trainingLabels)
#    np.save('data', trainingSet)
#
#    os.chdir(parentPath)
#    #exit(0)

def press(event, mesh, analogPlot):
    sys.stdout.flush()
    #if event.key == 't':
    #    analogPlot.trainClassifier()
    if event.key == ' ':
        analogPlot.paused = not analogPlot.paused
        analogPlot.ser.write("\xFF")
    #if event.key == 'w':
    #    saveData()
    #    print 'training data saved'
    if event.key == 'q':
        analogPlot.close()
        exit(0)

def connect_serial():

    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        #ports = glob.glob('/dev/ttyACM*')
        ports = glob.glob('/dev/ttyUSB*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usb*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    if len(result) > 1:
        print 'Too many ports to choose from'
        #exit(0)
    if len(result) < 1:
        print 'No ports found'
        exit(0)
    if len(result) is 1:
        print 'Found serial port: ', result

    return result[0]

def main():

    strPort = connect_serial()

    print 'Connecting to :', strPort,'...'
    global analogPlot
    analogPlot = AnalogPlot(strPort, nSamples)

    # wait for port to open
    while analogPlot.ser.isOpen() == 0:
        print '...'
        sleep(1)
    sleep(2)

    print 'Connected!'

    analogPlot.ser.write("\xFF")
    fig, axarr = plt.subplots(nChannels, sharex=True, sharey=False)
    lines = []
    for ax in axarr:
        lines.append(ax.plot([],[])[0])
        ax.set_xlim([0, nSamples])
        ax.set_ylim([0, 1023])

    fig.canvas.mpl_connect('key_press_event', lambda event: press(event, lines, analogPlot))

    anim = animation.FuncAnimation(fig, analogPlot.update, fargs=(lines,), interval=1)
    plt.show()
    analogPlot.close()

    print('exiting.')

if __name__ == '__main__':
    main()
