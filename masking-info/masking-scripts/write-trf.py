import glob

# NOTE !!!
#edit dirs as needed
outFile = open('trfDir/trfchunks.cmds','w')
fl = glob.glob('/home/jmkidd/links/kidd-lab/jmkidd-projects/tasha/mask-repeats/chunk-segments/*fa')
print('have %i fl' % len(fl))

for f in fl:
    cmd = 'trf %s 2 7 7 80 10 50 500 -h -d \n' % f
    outFile.write(cmd)
#    break
outFile.close()

