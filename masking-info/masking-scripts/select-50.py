import sys
import os
import glob
import gzip

from optparse import  OptionParser

USAGE = """
select-50.py --kdir <dir of kmer fasta files> --out <out file name>

counts kmer mapping positions


"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--kdir',dest='kdirName',help='kmer output dir')
parser.add_option('--out',dest='outName',help='outName for k with counts >= 20')


(options,args)=parser.parse_args()
if options.kdirName is None:
    parser.error('kdirName  not given')
if options.outName is None:
    parser.error('outName  not given')



###############################################################################
if options.kdirName[-1] != '/':
    options.kdirName += '/'


fileList = glob.glob(options.kdirName + '*.counts')

print('have %i count files to process' % len(fileList))


outFile = open( options.outName,'w')
for fn in fileList:
    print(fn)
    inFile = open(fn,'r')
    for line in inFile:
        line = line.rstrip()
        line = line.split()
        n = line[0]
        num = int(line[2])
        if num >= 20:
            c = n.split('_')
            e = c[-1]
            b = c[-2]
            chrom = '_'.join(c[0:-2])
            outFile.write('%s\t%s\t%s\n' % (chrom,b,e))    
    inFile.close()
outFile.close()

