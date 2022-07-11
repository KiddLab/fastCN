import sys
import os
import glob
import gzip

from optparse import  OptionParser

USAGE = """
count-kmer-maps.py --kdir <dir of kmer fasta files> 

counts kmer mapping positions


"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--kdir',dest='kdirName',help='kmer output dir')


(options,args)=parser.parse_args()
if options.kdirName is None:
    parser.error('kdirName  not given')

###############################################################################
if options.kdirName[-1] != '/':
    options.kdirName += '/'
#!/usr/bin/env python


fastaFiles = glob.glob(options.kdirName + '*.fa')

print('have %i fastaFiles to process' % len(fastaFiles))

for kmerFa in fastaFiles:
    print(kmerFa)
    mapFile = kmerFa + '.mrsfast.sam.gz'
    print(mapFile)
    mapFileCounts = mapFile + '.counts'
    print(mapFileCounts)

    print('Init counts matrix')
    
    kmerCounts = {}
    inFile = open(kmerFa,'r')
    while True:
        line1 = inFile.readline()
        if line1 == '':
            break
        line2 = inFile.readline()
        name = line1.rstrip()
        name = name[1:]
        kmerCounts[name] = 0
    inFile.close()


    print('Reading through',mapFile)

    inFile = gzip.open(mapFile,'rt')
    for line in inFile:
        if line[0] == '@':
            continue
        
        line = line.rstrip()
        line = line.split()
        kmerCounts[line[0]] += 1
    inFile.close()

    print('Read in all lines, printing output to',mapFileCounts)

    outFile = open(mapFileCounts,'w')
    inFile = open(kmerFa,'r')
    while True:
        line1 = inFile.readline()
        if line1 == '':
            break
        line2 = inFile.readline()
        seq = line2.rstrip()
        name = line1.rstrip()
        name = name[1:]
        outFile.write('%s\t%s\t%i\n' % (name,seq,kmerCounts[name]))    
    inFile.close()
    outFile.close()



