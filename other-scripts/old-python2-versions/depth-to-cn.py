#!/usr/bin/env python2


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
from optparse import OptionParser

###############################################################################
def windowToKey(a):
    k = a[0] + ':' + str(a[1]) + '-' + str(a[2])
    return k
###############################################################################
def isAutoOrPar(c,p):
    if c != 'chrX':
        return True
    if p <= 6650000:
        return True
    return False        
###############################################################################
def isPar(c,p):
    if c != 'chrX':
        return False
    if p <= 6650000:
        return True
    return False        
###############################################################################
def calc_stats(windowFile,autoControlWindows,XnonParControlWindows):
    res = {}
    res['windowList'] = []
    aDepths = []
    xDepths = []
    inFile = open(windowFile,'r')
    for line in inFile:
        line = line.rstrip()
        line = line.split('\t')
        res['windowList'].append(line)
        k = windowToKey(line)
        d = float(line[3])
        if k in autoControlWindows:
            aDepths.append(d)
        if k in XnonParControlWindows:
            xDepths.append(d)    
    inFile.close()

    
    res['aMed'] = np.median(aDepths)
    res['aDepths'] = aDepths
    cutoff = 3.0*res['aMed']  
    res['aDepthsRestricted'] = [i for i in aDepths if i <= cutoff]
    res['xMed'] = np.median(xDepths)
    res['xDepths'] = xDepths
    cutoff = 3.0*res['xMed'] 
    res['xDepthsRestricted'] = [i for i in xDepths if i <= cutoff]
    
    res['aMean'] = np.mean(res['aDepths'])
    res['aSTD'] = np.std(res['aDepths'])
    res['xMean'] = np.mean(res['xDepths'])
    res['xSTD'] = np.std(res['xDepths'])
    
    res['aMeanRestricted'] = np.mean(res['aDepthsRestricted'])
    res['aSTDRestricted'] = np.std(res['aDepthsRestricted'])
    res['xMeanRestricted'] = np.mean(res['xDepthsRestricted'])
    res['xSTDRestricted'] = np.std(res['xDepthsRestricted'])        
    res['resStr'] = '%f\t%f\t%f\t%f' % (res['aMeanRestricted'],res['aSTDRestricted'],res['xMeanRestricted'],res['xSTDRestricted'])
    return res
###############################################################################

USAGE = """
python2 depth-to-cn.py  --in <fastCN window bed> --autocontrol <autosomes control windows>  --chrX <chrX windows for plotting> 

converts  fastCN 3kb window counts to normalized depth
makes plots and stats table


"""
parser = OptionParser(USAGE)
parser.add_option('--in',dest='inFile', help = 'input window depth bed file')
parser.add_option('--autocontrol',dest='autoControl', help = 'autosome control windows')
parser.add_option('--chrX',dest='chrXWindows', help = 'chrXWindows')



(options, args) = parser.parse_args()

if options.inFile is None:
    parser.error('input file not given')
if options.autoControl is None:
    parser.error('autoControl file not given')
if options.chrXWindows is None:
    parser.error('chrXWindows file not given')



###############################################################################



# Read in control window files...

autoControl = options.autoControl
chrXControl = options.chrXWindows



autoControlWindows = {}
XnonParControlWindows = {}

inFile = open(autoControl,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    k = windowToKey(line)
    autoControlWindows[k] = 1    
inFile.close()

inFile = open(chrXControl,'r')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    if isPar(line[0],int(line[1])) is False:
        k = windowToKey(line)
        XnonParControlWindows[k] = 1    
inFile.close()

print 'Have %i auto control and %i X NONPAR windows' % (len(autoControlWindows), len(XnonParControlWindows))


my_dpi = 100
fn = options.inFile
print 'doing',fn


sn = fn.split('/')[-1].split('.')[0]
print sn

statsFile = fn + '.stats'

res = calc_stats(fn,autoControlWindows,XnonParControlWindows)

# make histogram plot
histPlotFile = statsFile + '.hist.png'
plt.figure(figsize=(400/my_dpi, 300/my_dpi), dpi=my_dpi)
(n,b,p) = plt.hist(res['aDepthsRestricted'],bins=50,label='Autos',normed=True)
plt.hist(res['xDepthsRestricted'],bins=b,label='X-nonPAR',normed=True)
plt.legend()    
plt.title(sn)
plt.xlabel('Control Window Depth')
plt.tight_layout()
plt.savefig(histPlotFile,dpi=my_dpi)
plt.close()




autoZScore = statsFile + '.autoXPAR.zscore.bed' 
xZScore = statsFile + '.XNONPAR.zscore.bed'     
res['autoZ'] = []
res['xZ'] = []
outX = open(xZScore,'w')
outAuto = open(autoZScore,'w')    
for w in res['windowList']:
    d = float(w[3])
    c = w[0]
    p = int(w[1])
    if c in ['chrM','chrY_nonPAB']:
        continue
    if c == 'chrX' and isPar(c,p) is False:
        m = (d - res['xMeanRestricted'])/res['xSTDRestricted']
        nl = [w[0],w[1],w[2],str(m)]
        nl = '\t'.join(nl) + '\n'
        outX.write(nl)
        res['xZ'].append(m)               
    else:
        m = (d - res['aMeanRestricted'])/res['aSTDRestricted']
        nl = [w[0],w[1],w[2],str(m)]
        nl = '\t'.join(nl) + '\n'
        outAuto.write(nl)
        res['autoZ'].append(m)
                    
outX.close()
outAuto.close()

zhistPlotFile = statsFile + '.zscore.hist.png'
#    plt.figure(figsize=(6,4))
plt.figure(figsize=(400/my_dpi, 300/my_dpi), dpi=my_dpi)

plt.hist(res['autoZ'],bins=np.arange(-6,10,.2),label='Autos',normed=True)
plt.hist(res['xZ'],bins=np.arange(-6,10,.2),label='X-nonPAR',normed=True)
plt.legend()    
plt.title(sn)
plt.xlabel('Z Score')
plt.tight_layout()
plt.savefig(zhistPlotFile,dpi=my_dpi)
plt.close()


outF = open(statsFile,'w')
nl = '%s\t%s\n' % (sn,res['resStr'])
outF.write(nl)
outF.close()

print 'Converting to copy number'

inFile = open(statsFile,'r')
l = inFile.readline()
inFile.close()
l = l.rstrip()
l = l.split()
m = float(l[1])
print m
cnFile = fn + '.CN.bed'
inFile = open(fn,'r')
outFile = open(cnFile,'w')
for line in inFile:
    line = line.rstrip()
    line = line.split()
    d = float(line[3])
    c = 2.0*(d/m)
    line[3] = str(c)
    nl = '\t'.join(line) + '\n'
    outFile.write(nl)
inFile.close()
outFile.close()





