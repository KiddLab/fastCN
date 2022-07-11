#!/usr/bin/env python3

from optparse import  OptionParser

USAGE = """
python write-chunk-coords.py    --fai <genome fai index> --gaps <gap bed file> --out <output segments file>
                                --mingap <int default=2000>
writes list of genome segments seperated by gaps
for use when splitting up genome into smaller pieces

will not split at gaps that are less than mingap bp long


"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--fai',dest='faiFile',help='input fai file name')
parser.add_option('--gaps',dest='gapsFile',help='gaps bed file name')
parser.add_option('--out',dest='outFile',help='output segments file name')
parser.add_option('--mingap',dest='mingap',type=int,default=2000,help='min gap file size')


(options,args)=parser.parse_args()


if options.faiFile is None:
    parser.error('faiFile file name not given')
if options.gapsFile is None:
    parser.error('gapsFile file name not given')
if options.outFile is None:
    parser.error('outFile file name not given')

###############################################################################

print('minGap len for splitting set to:',options.mingap)
chromLens = {}
gapLists = {}
cNames = []
inFile = open(options.faiFile,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    c = line[0]
    l = int(line[1])
    chromLens[c] = l
    gapLists[c] = []
    cNames.append(c)
inFile.close()

inFile = open(options.gapsFile,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    line[1] = int(line[1])
    line[2] = int(line[2])
    if ((line[2] - line[1]) )< options.mingap: # skip over gaps that are smaller than min gap size
        continue    
    gapLists[line[0]].append(line)
inFile.close()


print('Ready to go!')


outFile = open(options.outFile,'w')
for c in cNames:
     endGap = 0
     cLen = chromLens[c]
     print(c,cLen)
     
     for i in range(len(gapLists[c])):
         print(gapLists[c][i])
         startSegment = endGap + 1
         endSegment = gapLists[c][i][1] 
         print(c,startSegment,endSegment)
         outFile.write('%s\t%i\t%i\n' % (c,startSegment,endSegment))
         endGap = gapLists[c][i][2]
    #now last one
     endSegment = cLen
     startSegment = endGap + 1
     print(c,startSegment,endSegment)
     outFile.write('%s\t%i\t%i\n' % (c,startSegment,endSegment))
               
outFile.close()     