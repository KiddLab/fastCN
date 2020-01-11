#!/usr/bin/env python

import sys
import os
import signal
import gzip

from optparse import OptionParser


USAGE = """
 extract-from-fastq36.py --in <fastq.gz file>

"""
parser = OptionParser(USAGE)
parser.add_option('--in',dest='inFASTQ', help = 'input fastq.gz file')

#parser.add_option('--out',dest='outBase', help = 'output base prefix')


(options, args) = parser.parse_args()

if options.inFASTQ is None:
    parser.error('input inFASTQ not given')

###############################################################################

#########################################################################################
def determine_parts_all(seq):
    targetLen = 36
    seqLen = len(seq)
    if seqLen < targetLen:
        return []        
    numParts = seqLen/targetLen
    delta = seqLen - (numParts * targetLen)
    delta = delta >> 1
    start = delta
    res = []
    for i in range(numParts):
        end = start + targetLen
        res.append([start,end])
        start = end
    return res    
#########################################################################################



try:
    inFile = gzip.open(options.inFASTQ,'rt')
except:
    print("ERROR!! Could not open the file " + options.inFASTQ + " using gzip.open \n")
    sys.exit(1)


#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # To deal with fact that might close file before reading all

#num = 0
while True:
    line1 = inFile.readline().rstrip()
    if line1 == '':
        break
    line2 = inFile.readline().rstrip()
    line3 = inFile.readline().rstrip()
    line4 = inFile.readline().rstrip()
    name = line1[1:]
    name = name.split()[0]
    seq = line2
    qual = line4
    parts = determine_parts_all(seq)
    for i in range(len(parts)):
        s = seq[parts[i][0]:parts[i][1]]
        q = qual[parts[i][0]:parts[i][1]]
        n = name + '_' + str(i)
        sys.stdout.write('@%s\n%s\n+\n%s\n' % (n,s,q))
#        num += 1
#    if num > 100:
#        break
    
inFile.close()
