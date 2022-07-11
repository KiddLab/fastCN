
#!/usr/bin/env python3

import sys

from optparse import  OptionParser

USAGE = """
python combine-trf.py  --fai <genome .fai file> --segments < segments file> --rmdir <dir where trf out .dat files are> --out <out file name>

combine the split trf files into a single file

"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--fai',dest='faiFile',help='genome .fai file name')
parser.add_option('--segments',dest='segmentsFile',help='segmentsFile file name')
parser.add_option('--rmdir',dest='rmDir',help='dir for repeat masker output')
parser.add_option('--out',dest='outFile',help='output file name for combined repeat masker data')

(options,args)=parser.parse_args()


if options.faiFile is None:
    parser.error('faiFile file name not given')
if options.segmentsFile is None:
    parser.error('segmentsFile file name not given')
if options.rmDir is None:
    parser.error('rmDir file name not given')
if options.outFile is None:
    parser.error('outFile file name not given')

###############################################################################



import sys
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


# get chrom sizes
chromSizes = {}

inFile = open(options.faiFile,'r')
for line in inFile:
   line = line.rstrip()
   line = line.split()
   c = line[0]
   s = int(line[1])
   chromSizes[c] = s
inFile.close()



#setup initial
c = chunks[0]
outFileName = '%s/%s.fa.out' % (options.rmDir,c[3])
inFile = open(outFileName,'r')
for i in range(3):
    line = inFile.readline()
    outFile.write(line)
inFile.close()

for c in chunks:
    print(c)
    chromSize = chromSizes[c[0]]
    print('chrom size',chromSize)
    offSet = int(c[1]) - 1
    print('offset is ',offSet)
    
    outFileName = '%s/%s.fa.out' % (options.rmDir,c[3])
    print(outFileName)
    inFile = open(outFileName,'r')
    i = 0
    while True:
        line = inFile.readline()
        i += 1
        if line == '':
            break
        if i <=3:
            continue
        line = line.rstrip()
        line = line.split()
        
        line[4] = c[0]
        line[5] = str(int(line[5]) + offSet)
        line[6] = str(int(line[6]) + offSet)
        bpLeft = chromSize - int(line[6])
        line[7] = '(%i)' % bpLeft
        nl = ' '.join(line) + '\n'
        outFile.write(nl)    
    inFile.close()    


outFile.close()