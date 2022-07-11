#!/usr/bin/env python3

import genutils3

from optparse import  OptionParser
USAGE = """
python get-gaps-bed.py    --in <fasta in file> --out <bed file>

Loads sequences from fasta and print out bed of 'N' positions


"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--in',dest='inFile',help='input file name')
parser.add_option('--out',dest='outFile',help='output file name')

(options,args)=parser.parse_args()


if options.inFile is None:
    parser.error('input file name not given')
if options.outFile is None:
    parser.error('outFile file name not given')
###############################################################################

fastaDict = genutils3.read_fasta_file_to_list(options.inFile)

print('Read in %i sequences' % len(fastaDict))
outFile = open(options.outFile,'w')
seqsToDo = list(fastaDict.keys())
seqsToDo.sort()
for seqName in seqsToDo:
    print(seqName,fastaDict[seqName]['seqLen'])
    seq = fastaDict[seqName]['seq']
    i = 0
    while i < fastaDict[seqName]['seqLen']:
        while i < fastaDict[seqName]['seqLen'] and seq[i] != 'N':
            i+=1
        #in reg start
        lp = i
        while i < fastaDict[seqName]['seqLen'] and seq[i] == 'N':
            i+=1
        rp = i-1 # got rp
        if lp < fastaDict[seqName]['seqLen']:
            outFile.write('%s\t%i\t%i\n' % (seqName,lp,rp+1))
outFile.close()    