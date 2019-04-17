#!/usr/bin/env python2
import sys
import os
import signal

from optparse import OptionParser


USAGE = """
 extract-from-bam.py --in <BAM file>  
                     --rg <read group ID extract, leave blank if all >
                     --reference <reference fasta file, needed for CRAM support>

            

"""
parser = OptionParser(USAGE)
parser.add_option('--in',dest='inBAM', help = 'input BAM file')
parser.add_option('--rg',dest='rgID', help = 'read group ID to exctract')
parser.add_option('--reference',dest='referenceFile', help = 'reference file needed for CRAM support')

#parser.add_option('--out',dest='outBase', help = 'output base prefix')


(options, args) = parser.parse_args()

if options.inBAM is None:
    parser.error('input BAM not given')

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


if options.rgID is None:
    cmd = 'samtools view -F 3840 '
    if options.referenceFile is not None:
        cmd += ' -T %s ' % options.referenceFile
    cmd += options.inBAM
else:
    cmd = 'samtools view -F 3840 '
    if options.referenceFile is not None:
        cmd += ' -T %s ' % options.referenceFile
    cmd += '-r '+ options.rgID + ' ' 
    cmd += options.inBAM

try:
    inFile = os.popen(cmd, 'r')
except:
    print "ERROR!! Could not open the file " + options.inBAM + " using samtools view \n"
    sys.exit(1)


#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # To deal with fact that might close file before reading all

#num = 0
for line in inFile:
    line = line.rstrip()
    line = line.split()
    name = line[0]
    seq = line[9]
    qual = line[10]    
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
