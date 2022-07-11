
#!/usr/bin/env python3

import sys

from optparse import  OptionParser

USAGE = """
python combine-trf.py   --segments < segments file> --trfdir <dir where trf out .dat files are> --out <out file name>

combine the split trf files into a single file

"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--segments',dest='segmentsFile',help='segmentsFile file name')
parser.add_option('--trfdir',dest='trfdir',help='dir for trf output')
parser.add_option('--out',dest='outFile',help='output file name for combined trf data')

(options,args)=parser.parse_args()

if options.segmentsFile is None:
    parser.error('segmentsFile file name not given')
if options.trfdir is None:
    parser.error('trfdir file name not given')
if options.outFile is None:
    parser.error('outFile file name not given')

###############################################################################



chunks = []
inFile = open(options.segmentsFile,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = '%s:%s-%s' % (line[0],line[1],line[2])
    line.append(c)
    chunks.append(line)
inFile.close()
print('Read in %i chunks ' % len(chunks))

outFile = open(options.outFile,'w')


#setup initial
for c in chunks:
    print(c)
    offSet = int(c[1]) - 1
    print('offset is ',offSet)
    
    outFileName = '%s/%s.fa.2.7.7.80.10.50.500.dat' % (options.trfdir,c[3])
    print(outFileName)
    inFile = open(outFileName,'r')
    i = 0
    while True:
        line = inFile.readline()
        i += 1
        if line == '':
            break
        if i <=15:
            continue
        line = line.rstrip()
        line = line.split()
        nl = [c[0],str(int(line[0]) + offSet),str(int(line[1]) + offSet)]
        nl = '\t'.join(nl) + '\n'
        outFile.write(nl)    
    inFile.close()
outFile.close()