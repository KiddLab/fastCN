import sys
import genutils3
import os

from optparse import  OptionParser

USAGE = """
extract-50mers.py --fai <.fai file> --fa <fasta file> --outdir <out dir for kmer files>

prints out 50mers with step of 5.



"""
###############################################################################
parser = OptionParser(USAGE)

parser.add_option('--fai',dest='faiFileName',help='fai file name')
parser.add_option('--fa',dest='fastaFileName',help='genome fasta file name')
parser.add_option('--outdir',dest='outDirName',help='out dir name')


(options,args)=parser.parse_args()
if options.faiFileName is None:
    parser.error('faiFileName file name not given')
if options.fastaFileName is None:
    parser.error('fastaFileName file name not given')
if options.outDirName is None:
    parser.error('outDirName  not given')


###############################################################################

if options.outDirName[-1] != '/':
    options.outDirName += '/'
if os.path.isdir(options.outDirName) is False:
    print('ERROR!!!!')
    print(options.outDirName,'is not a dir that exists!')
    sys.exit()
    

chromLens = genutils3.read_chrom_len(options.faiFileName)

#print(chromLens)
print('Read in %i seq lens' % len(chromLens))
chromSeqs = genutils3.read_fasta_file_to_dict(options.fastaFileName)

print('Read in %i seqs' % len(chromSeqs))


k = 50
step = 5


for cName in chromLens:
    cLen = chromLens[cName]
    print('Doing...',cName,cLen)
    kOut = '%s/%s.kmer.50.5.fa' % (options.outDirName,cName)
    print(kOut)
    outFile = open(kOut,'w')
    b = 0
    e = b + k
    while e <= cLen:
        seq = chromSeqs[cName]['seq'][b:e]
        sName = cName + '_' + str(b) + '_' + str(e)
        if 'N' not in seq:  # skip 'N'
            outFile.write('>%s\n%s\n' % (sName,seq))
        b = b + step
        e = b + k
    outFile.close()
outFile.close()
