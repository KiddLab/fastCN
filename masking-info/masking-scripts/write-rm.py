import glob

# EDIT SCRIPT TO HAVE RIGHT FILES

outFile = open('Tasha_CanFam4.repeatmasker.cmds','w')
fl = glob.glob('chunk-segments/*fa')
print('have %i fl' % len(fl))

for f in fl:
    # EDIT to have write species
    cmd = 'RepeatMasker -species dog -e ncbi ' + f + '\n'
    outFile.write(cmd)
outFile.close()