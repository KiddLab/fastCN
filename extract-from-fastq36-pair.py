#!/usr/bin/env python2
import sys
import os
import signal
import gzip

from optparse import OptionParser


USAGE = """
 extract-from-fastq36-pair.py --in1 <fq .gz file>  --in2 <fq .gz file>  

"""
parser = OptionParser(USAGE)
parser.add_option('--in1',dest='inFQ1', help = 'input 1 fqFILE .gz')
parser.add_option('--in2',dest='inFQ2', help = 'input 2 fqFILE .gz')



(options, args) = parser.parse_args()

if options.inFQ1 is None:
    parser.error('input inFQ1 not given')
if options.inFQ2 is None:
    parser.error('input inFQ2 not given')


###############################################################################
#########################################################################################
def determine_parts_all(seq):
    targetLen = 36
    seqLen = len(seq)
    if seqLen < targetLen:
        return []        
    numParts = seqLen/targetLen
    delta = seqLen - (numParts * targetLen)
    delta = delta/numParts
    start = delta
    res = []
    for i in range(numParts):
        end = start + targetLen
        res.append([start,end])
        start = end
    return res    
#########################################################################################
def get_4l_record(myFile):
    #fastq style file...
    # '' if last record
    myLine1 = myFile.readline()
    if myLine1 == '':
        return ''
    myLine2 = myFile.readline()
    myLine3 = myFile.readline()
    myLine4 = myFile.readline()
    return [myLine1,myLine2,myLine3,myLine4]
#########################################################################################


try:
    inFile1 = gzip.open(options.inFQ1, 'r')
except:
    print "ERROR!! Could not open the file " + options.inFQ1 + " \n"
    sys.exit(1)

try:
    inFile2 = gzip.open(options.inFQ2, 'r')
except:
    print "ERROR!! Could not open the file " + options.inFQ2 + " \n"
    sys.exit(1)


#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # To deal with fact that might close file before reading all

num = 0
while True:
    ref = get_4l_record(inFile1)
    if ref == '':
        break
    name = ref[0][1:].rstrip()
    seq = ref[1].rstrip()
    qual = ref[3].rstrip()
    parts = determine_parts_all(seq)
    for i in range(len(parts)):
        s = seq[parts[i][0]:parts[i][1]]
        q = qual[parts[i][0]:parts[i][1]]
        n = name + '_' + str(i)
        sys.stdout.write('@%s\n%s\n+\n%s\n' % (n,s,q))
#        num += 1
#    if num > 1:
#        break    
inFile1.close()

num = 0
while True:
    ref = get_4l_record(inFile2)
    if ref == '':
        break
    name = ref[0][1:].rstrip()
    seq = ref[1].rstrip()
    qual = ref[3].rstrip()
    parts = determine_parts_all(seq)
    for i in range(len(parts)):
        s = seq[parts[i][0]:parts[i][1]]
        q = qual[parts[i][0]:parts[i][1]]
        n = name + '_' + str(i)
        sys.stdout.write('@%s\n%s\n+\n%s\n' % (n,s,q))
#        num += 1
#    if num > 1:
#        break    
inFile2.close()

