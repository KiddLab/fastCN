#!/usr/bin/env python3
# Author: Jeffrey M Kidd
# bed-length.py
# Returns total length of intervals in in a UCSC (0-based style) bed file

import sys
from optparse import  OptionParser

USAGE = """USAGE:python bed-length.py -f <bed file> 

Reads a UCSC style bed file and reports total interval size.  Assumes that intervals are 
non-redundant. Can loop over multiple files at once."""

parser = OptionParser(USAGE)
parser.add_option("-f",dest="bedFile",help="name of bed file to be processed")
(options,args)=parser.parse_args()


if options.bedFile is None:
    parser.error('bedFile file not given')
    
#############################################################################
# Done with options parsing

toDo = []
toDo.append(options.bedFile)
for f in args:
    toDo.append(f)
    
for f in toDo:
    tot = 0
    myFile = open(f,'r')
    for line in myFile:
        line = line.rstrip()
        line = line.split()
        tot += (int(line[2]) - int(line[1]))
    print(f,tot)
    myFile.close()


