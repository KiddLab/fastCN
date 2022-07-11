import sys
import os
import glob

from optparse import  OptionParser

USAGE = """
write-mrsfast-ksearch-cmds.py --kdir <dir of kmer fasta files> --fa <fasta> --out <out file for cmds>

writes out cmds for mrsfast



"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--fa',dest='fastaFileName',help='genome fasta file name')
parser.add_option('--kdir',dest='kdirName',help='kmer output dir')
parser.add_option('--out',dest='outName',help='out file name')


(options,args)=parser.parse_args()
if options.kdirName is None:
    parser.error('kdirName  not given')
if options.fastaFileName is None:
    parser.error('fastaFileName file name not given')
if options.outName is None:
    parser.error('outName not given')


###############################################################################
if options.kdirName[-1] != '/':
    options.kdirName += '/'



fileList = glob.glob(options.kdirName + '*fa')
print('Found %i fastas' % len(fileList))

outFile = open(options.outName,'w')

for faFile in fileList:
    outSAM = faFile + '.mrsfast' # automatically adds .sam.gz
    cmd = 'mrsfast '
    cmd += ' --search ' + options.fastaFileName + ' ' 
    cmd += ' --seq ' + faFile
    cmd += ' --disable-nohits --mem 12 --threads 1 -e 2 --outcomp -o ' + outSAM
    cmd += '\n'
    outFile.write(cmd)

outFile.close()
