#!/usr/bin/env python3

import sys

from optparse import  OptionParser

USAGE = """
python trf-to-bed.py  --trf <trf file name> --bed <bed file name>

combine the split trf files into a single file

"""
###############################################################################
parser = OptionParser(USAGE)


parser.add_option('--trf',dest='trfFile',help='combined TRF file')
parser.add_option('--bed',dest='bedFile',help='combined bed file')

(options,args)=parser.parse_args()

if options.trfFile is None:
    parser.error('trfFile file name not given')
if options.bedFile is None:
    parser.error('bedFile file name not given')

###############################################################################




inFile = open(options.trfFile,'r')
outFile = open(options.bedFile,'w')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = line[0]
    b = int(line[1])
    e = int(line[2])
    b =b - 1
    outFile.write('%s\t%i\t%i\n' % (c,b,e))
inFile.close()
outFile.close()