#!/usr/bin/env python3

import sys

from optparse import  OptionParser

USAGE = """
convert-dustout-to-bed.py  --sddust <sddust file> --bed <output file>s

convert output of SDDust to bed format

"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--sddust',dest='sddustFile',help='sddustFile file name')
parser.add_option('--bed',dest='bedFileName',help='bed file name')


(options,args)=parser.parse_args()
if options.sddustFile is None:
    parser.error('sddustFile file name not given')
if options.bedFileName is None:
    parser.error('bedFileName file name not given')
###############################################################################


inFile = open(options.sddustFile,'r')
outFile = open(options.bedFileName,'w')
for line in inFile:
    line = line.rstrip()
    if line[0] == '>':
        name = line[1:]
    else:
        line = line.split()
        b = int(line[0])
        e = int(line[2])
        outFile.write('%s\t%i\t%i\n' % (name,b,e+1))

inFile.close()
outFile.close()
