# python2 program, now changed to python3
# edit windowSize, windowOutName, and maskedBed file to proper files
# sorry -- hard coded in
import struct
import array
import sys
import subprocess
import signal
import os
import numpy as np

###############################################################################
# Helper function to run commands, handle return values and print to log file
def runCMD(cmd):
    val = subprocess.Popen(cmd, shell=True).wait()
    if val == 0:
        pass
    else:
        print('command failed')
        print cmd
        sys.exit(1)
#####################################################################


chromNames = []
nameToLen = {}
chromMask = {}

# sorry -- options are hard coded in here.  
# To do: need to update to take options from the command line.

chromLenandOrder = '../ref/GRCh38_BSM.fa.fai'
maskedBed = '../ref/GRCh38_bsm.gaps.bed.slop36.sorted.merged.sorted2'
windowSize = 1000
windowOutName = 'GRCh38_bsm.1kb.bed'


print('Reading from',chromLenandOrder)
sys.stdout.flush()
runCMD('date')
inFile = open(chromLenandOrder,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = line[0]
    cLen = int(line[1])
    chromNames.append(c)
    nameToLen[c] = cLen
    chromMask[c] = np.zeros(cLen+1,dtype=np.int)
inFile.close()

print('Setup empty arrays')
sys.stdout.flush()
runCMD('date')

print('Setting masked values')
sys.stdout.flush()
runCMD('date')

inFile = open(maskedBed,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = line[0]
    b = int(line[1])
    e = int(line[2])
    b = b + 1 # will work in 1 based coordinates

    for i in range(b,e+1):
        chromMask[c][i] = 1
inFile.close()
print('Masked values set to 1')
sys.stdout.flush()
runCMD('date')

outFile = open(windowOutName,'w')
for c in chromNames:
    cLen = nameToLen[c]
    print c,cLen
    windowStart = 1
    while windowStart <= cLen:
        coveredBp = 0
        if chromMask[c][windowStart] == 0:
            coveredBp += 1
        windowEnd = windowStart + 1
        while (coveredBp  < windowSize) and (windowEnd <= cLen):
            if chromMask[c][windowEnd] == 0:
                coveredBp += 1
            windowEnd += 1
        windowEnd -= 1 # went 1 to far
        outFile.write('%s\t%i\t%i\t%i\n' % (c,windowStart-1,windowEnd,coveredBp))
        windowStart = windowEnd + 1
outFile.close()







