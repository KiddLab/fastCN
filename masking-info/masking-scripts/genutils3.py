# commonly used functions
# updated to Python 3

import sys
import subprocess

###############################################################################
def read_fasta_file_to_list(fastaFile):
    myDict = {}
    inFile = open(fastaFile,'r')
    line = inFile.readline()
    line = line.rstrip()
    if line[0] != '>':
        print('ERROR, FILE DOESNNOT START WITH >')
        sys.exit()
    myName = line[1:]
    myDict[myName] = {}
    myDict[myName]['seq'] = ''
    myDict[myName]['seqLen'] = 0    
    mySeq = ''
    while True:
        line = inFile.readline()
        if line == '':
            myDict[myName]['seq'] = mySeq
            myDict[myName]['seqLen'] = len(myDict[myName]['seq'])         
            break
        line = line.rstrip()
        if line[0] == '>':
            myDict[myName]['seq'] = mySeq
            myDict[myName]['seqLen'] = len(myDict[myName]['seq'])         
            myName = line[1:]
            myDict[myName] = {}
            myDict[myName]['seq'] = ''
            myDict[myName]['seqLen'] = 0    
            mySeq = ''
            continue
        mySeq += line
    inFile.close()
    return myDict
###############################################################################
# poor name choice on function when first started.  Keep to save compatability
def read_fasta_file_to_dict(fastaFile):
    return read_fasta_file_to_list(fastaFile)
###############################################################################
###############################################################################
def add_breaks_to_line(seq,n=50):
    myList = []
    myList = [i for i in seq]
    newList = []
    c = 0
    for i in myList:
        newList.append(i)
        c += 1
        if c % n == 0 and c != (len(myList)):
            newList.append('\n')
    myStr = ''.join(newList)
    return myStr    
###############################################################################
# Helper function to run commands,
# doesn't check return or print to log.  Use for 'grep' so that doesn't
# fail if no items found
def runCMDNoFail(cmd):
    val = subprocess.Popen(cmd, shell=True).wait()
###############################################################################
# Helper function to run commands, handle return values and print to log file
def runCMD(cmd):
    val = subprocess.Popen(cmd, shell=True).wait()
    if val == 0:
        pass
    else:
        print('command failed')
        print(cmd)
        sys.exit(1)
###############################################################################
# Helper function to run commands, handle return values and print to log file
def runCMD_output(cmd):
    val = subprocess.Popen(cmd, text=True, shell=True, stdout = subprocess.PIPE)
    resLines = []
    for i in val.stdout:
       i = i.rstrip()
       resLines.append(i)
    return resLines
#############################################################################        
# Helper function to read in information from genome .fai file and return
# a dictionary containing chrom names and lengths
def read_chrom_len(faiFileName):
    chromLens = {}
    inFile = open(faiFileName,'r')
    for line in inFile:
        line = line.rstrip()
        line = line.split()
        chromLens[line[0]] = int(line[1])
    inFile.close()
    return chromLens    
############################################################################# 
###############################################################################
def get_4l_record(myFile):
    #fastq style file...
    # just return sequence len
    # -1 if last record
    myLine1 = myFile.readline()
    if myLine1 == '':
        return ''
    myLine2 = myFile.readline()
    myLine3 = myFile.readline()
    myLine4 = myFile.readline()
    return [myLine1,myLine2,myLine3,myLine4]
###############################################################################
#####################################################################
# assumes line is already list
def parse_blat_psl_line(line):
    blatLine = {}
    blatLine['match'] = int(line[0])
    blatLine['mismatch'] = int(line[1])
    blatLine['repmatch'] = int(line[2])
    blatLine['ncount'] = int(line[3])
    blatLine['qGapCount'] = int(line[4])
    blatLine['qGapBases'] = int(line[5])
    blatLine['tGapCount'] = int(line[6])
    blatLine['tGapBases'] = int(line[7])
    blatLine['strand'] = line[8]
    blatLine['qName'] = line[9]
    blatLine['qSize'] = int(line[10])
    blatLine['qStart'] = int(line[11])
    blatLine['qEnd'] = int(line[12])

    blatLine['tName'] = line[13]
    blatLine['tSize'] = int(line[14])
    blatLine['tStart'] = int(line[15])
    blatLine['tEnd'] = int(line[16])
    
    blatLine['blockCount'] = int(line[17])
    blatLine['blockSizes'] = line[18]
    blatLine['qStarts'] = line[19]
    blatLine['tStarts'] = line[20]
    return blatLine
#####################################################################
def parse_paf_line(line):
    pafLine = {}
    pafLine['qName'] = line[0]
    pafLine['qLen'] = int(line[1])
    pafLine['qStart'] = int(line[2])
    pafLine['qEnd'] = int(line[3])
    pafLine['strand'] = line[4]
    pafLine['tName'] = line[5]
    pafLine['tLen'] = int(line[6])
    pafLine['tStart'] = int(line[7])
    pafLine['tEnd'] = int(line[8])
    pafLine['numMatch'] = int(line[9])
    pafLine['alignBlockLen'] = int(line[10])
    pafLine['mapQ'] = int(line[11])
    return pafLine
##############################################################################
# Returns complement of a bp.  If not ACGT then return same char
def complement(c):
    if c == 'A':
        return 'T'
    if c == 'T':
        return 'A'
    if c == 'C':
        return 'G'
    if c == 'G':
        return 'C'
    if c == 'a':
        return 't'
    if c == 't':
        return 'a'
    if c == 'c':
        return 'g'
    if c == 'g':
        return 'c'
    # If not ACTGactg simply return same character
    return c   
##############################################################################
# Returns the reverse compliment of sequence 
def revcomp(seq):
    c = ''    
    seq = seq[::-1] #reverse
    # Note, this good be greatly sped up using list operations
    seq = [complement(i) for i in seq]
    c = ''.join(seq)
    return c
##############################################################################
#################################################
def get_gc_percentage_interval(genomeFasta,reg):
# genomeFasta must have .fai index
# region is in samtools format chr:start-end, inclusive
    cmd = 'samtools faidx %s %s ' % (genomeFasta,reg)
    res = runCMD_output(cmd)
    totLen = 0
    nucs= ['A','C','G','T','N']
    counts={}
    for i in nucs:
        counts[i] = 0
    for line in res:
        line  = line.rstrip()
        line = line.upper()
        if line[0] == '>':
            continue
        totLen += len(line)
        for i in nucs:
            counts[i] += line.count(i)
    gc = counts['C'] + counts['G']
    acgt = counts['A'] + counts['C'] + counts['G'] + counts['T']
    gc_f = float(gc)/float(acgt)
    return gc_f
#################################################
###############################################################################
def add_breaks_to_line(seq,n=50):
    myList = []
    myList = [i for i in seq]
    newList = []
    c = 0
    for i in myList:
        newList.append(i)
        c += 1
        if c % n == 0 and c != (len(myList)):
            newList.append('\n')
    myStr = ''.join(newList)
    return myStr    
###############################################################################
##############################################################################
def parse_rm_lines_to_dict(fileName):
    myDict = {}
    inFile = open(fileName,'r')
    for line in inFile:
        line = line.rstrip()
        if line == '':
            continue 
        line = line.replace('(','')
        line = line.replace(')','')        
        line = line.split() 
        if line[0] == 'SW' or line[0] == 'score':
            continue
        myHit = {}
        myHit['score'] = int(line[0])
        myHit['dvg'] = float(line[1])
        myHit['queryName'] = line[4]
        myHit['qStart'] = int(line[5])
        myHit['qEnd'] = int(line[6])
        myHit['qLeft'] = int(line[7])
        
        myHit['dir'] = line[8]
        myHit['repeat'] = line[9]
        myHit['family'] = line[10]
        
        myHit['rmStart'] = int(line[11])
        myHit['rmEnd'] = int(line[12])
        myHit['rmLeft'] = int(line[13])
        
        if myHit['dir'] == 'C':
            myHit['rmStart'] = int(line[13])
            myHit['rmEnd'] = int(line[12])
            myHit['rmLeft'] = int(line[11])
            
        myHit['qMatchLen']= myHit['qEnd'] - myHit['qStart'] + 1
        myHit['rmMatchLen']= myHit['rmEnd'] - myHit['rmStart'] + 1
        
           
        
        if myHit['queryName'] not in myDict:
            myDict[myHit['queryName']] = []
        myDict[myHit['queryName']].append(myHit)       
    inFile.close()
    return myDict
##############################################################################   




