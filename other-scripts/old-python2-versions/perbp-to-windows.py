#!/usr/bin/env python2

import struct
import array
import sys
import subprocess
import signal
import os
import numpy as np
from optparse import  OptionParser

###############################################################################
# Helper function to run commands, handle return values and print to log file
def runCMD(cmd):
    val = subprocess.Popen(cmd, shell=True).wait()
    if val == 0:
        pass
    else:
        print 'command failed'
        print cmd
        sys.exit(1)
#####################################################################
def open_gzip_read(fileName):
    gc = 'gunzip -c ' + fileName
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # To deal with fact that might close file before reading all
    try:
        inFile = os.popen(gc, 'r')
    except:
        print "ERROR!! Couldn't open the file " + fileName + " using gunzip -c\n"
        sys.stdout.flush()
        sys.exit(1)
    return inFile
#####################################################################



USAGE = """
python perbp-to-windows.py --depth <depth file .gz> --out <output file>
                           --chromlen <*.fai> --windows <windows file>

note that depth file (output of fastCN) is assumed to be gzipped

order and length of chroms in --chromlen should match genome used for fastCN
windows are typically 3kb of non-masked sequence


"""
parser = OptionParser(USAGE)
parser.add_option('--depth',dest='depth', help = 'per bp depth file name')
parser.add_option('--out',dest='out', help = 'output for deth per window')
parser.add_option('--chromlen',dest='chromLen', help = '.fai of genome mapped')
parser.add_option('--windows',dest='windows', help = 'windows to output depth in')

(options, args) = parser.parse_args()

if options.depth is None:
    parser.error('per bp depthnot given')
if options.out is None:
    parser.error('output for depth  name not given')
if options.chromLen is None:
    parser.error('chromLen  not given')
if options.windows is None:
    parser.error('windows  not given')




options.depth
options.out
print 'Doing:'
print options.depth
print options.out


windowsFile = options.windows
chromLenandOrder = options.chromLen


######
#setup chrom lens
print 'Begining read in of depth from gzipped file....'
sys.stdout.flush()
runCMD('date')
print options.depth
print chromLenandOrder
    
    
chromStarts = {}
inFile = open(chromLenandOrder,'r')
totBp = 0
startBp = 0
for line in inFile:
    line = line.rstrip()
    line = line.split()
    cName = line[0]
    cLen = int(line[1])
    chromStarts[cName] = startBp
    startBp += cLen
inFile.close()
print 'totBp is',startBp


print 'Read in depth array...',options.depth
sys.stdout.flush()
    
inpipe = open_gzip_read(options.depth)
depthArray = np.fromfile(inpipe  , dtype = np.float16, count=startBp )
inpipe.close()
print 'Size:',depthArray.size
    
print 'DONE read in of depth file'
sys.stdout.flush()
    

print 'Convert inf to 65504.0 ...'
sys.stdout.flush()

# change value of Inf to 65504, the max value of float16
depthArray[depthArray == np.inf] = 65504.0




    
print 'Starting window output...'
sys.stdout.flush()

inFile = open(windowsFile,'r')
outFile = open(options.out,'w')
prevC = '?'
chromStart = -1
    
nw = 0
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = line[0]
    b = int(line[1])
    e = int(line[2])
    nc = int(line[3])
    if c != prevC:
        chromStart = chromStarts[c]
        prevC = c
    nb = b + chromStart
    ne = e + chromStart

    dSlice = depthArray[nb:ne]
    totD = dSlice[dSlice >= 0.0].astype(np.float64).sum()
    nc2 = int(dSlice[dSlice >= 0.0].size)
#    if nc2 != nc:
#        print line,nc2
    if nc2 == 0:
        m = -1
    else:
        m = totD/nc2
    outFile.write('%s\t%i\t%i\t%f\n' % (c,b,e,m))
inFile.close()
outFile.close()
runCMD('date')
print 'DONE with window output'
sys.stdout.flush()    





