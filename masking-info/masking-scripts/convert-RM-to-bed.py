#!/usr/bin/env python3

import sys

from optparse import  OptionParser

USAGE = """
python convert-RM-to-bed.py   --rmfile <rm file name> --bed <bed file name>

combine the split trf files into a single file

"""
###############################################################################
parser = OptionParser(USAGE)


parser.add_option('--rmfile',dest='rmFile',help='combined repeat masker file')
parser.add_option('--bed',dest='bedFile',help='repeat masker bed file')

(options,args)=parser.parse_args()

if options.rmFile is None:
    parser.error('rmFile file name not given')
if options.bedFile is None:
    parser.error('bedFile file name not given')

###############################################################################



# convert RM out format to bed format

inFile = open(options.rmFile,'r')
outFile = open(options.bedFile,'w')

header = ['#chrom','begin','end','repName','repClass','Divergence','Del','Ins','Dir','RepCoords']
nl = '\t'.join(header) + '\n'
outFile.write(nl)

for line in inFile:
    line = line.rstrip()
    if line=='':
        continue
    line = line.split()
    if line[0] == 'SW' or line[0] == 'score':
        continue

    chr = line[4]
    b = int(line[5])
    e = int(line[6])
    b = b - 1
    divr = float(line[1])
    dels = float(line[2])
    ins = float(line[3])
    repName = line[9]
    dir = line[8]
    repClass = line[10]
    repPos = line[11] + ',' + line[12] + ',' + line[13]
    
    nl = [chr,b,e,repName,repClass,divr,dels,ins,dir,repPos]
    nl = [str(i) for i in nl]
    nl = '\t'.join(nl) + '\n'
    outFile.write(nl)
    
    
    

inFile.close()
