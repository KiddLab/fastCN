#!/usr/bin/env python3

import sys
import genutils3
import os

from optparse import  OptionParser

USAGE = """
python extract-chunks.py    --fa <genome fa> --segments < segments file>  --outdir <output dir>

uses samtools cmds to split genome into segments indicated



"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--fa',dest='faFile',help='input genome fasta file name')
parser.add_option('--segments',dest='segmentsFile',help='segments file name')
parser.add_option('--outdir',dest='outDir',help='output directory for segments')

(options,args)=parser.parse_args()


if options.faFile is None:
    parser.error('faFile file name not given')
if options.segmentsFile is None:
    parser.error('segmentsFile file name not given')
if options.outDir is None:
    parser.error('outDir name not given')

###############################################################################

if options.outDir[-1] != '/':
    options.outDir += '/'
    
if os.path.isdir(options.outDir) is False:
    print('***ERRROR!!****')
    print('out path %s does not exist!' % options.outDir)
    print('plase make the directory and try again.')
    sys.exit()
    


inFile = open(options.segmentsFile,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    print(line)
    r = '%s:%s-%s' % (line[0],line[1],line[2])
    outFileName = options.outDir + r + '.fa'
    cmd = 'samtools faidx %s %s > %s' % (options.faFile,r,outFileName)
    print(cmd)
    genutils3.runCMD(cmd)
    
inFile.close()