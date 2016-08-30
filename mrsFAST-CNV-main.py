#!/usr/bin/env python

import subprocess
import threading
import sys
import time
import os
import argparse
import glob

parser = argparse.ArgumentParser(description='mrsFAST CNV pipeline')
parser.add_argument('-o',help="Output file prefix or folder")
parser.add_argument('input',help="File path to input fastq file")
parser.add_argument('reference',help="Directory containing the mrsFAST-ultra reference .fa.\nCorresponding index files should also be supplied.")
args = parser.parse_args()

sample_path = args.input
data_path = args.kmer
if data_path[-1]=='/':
    prefix = data_path.split('/')[-2]
else:
    prefix = data_path.split('/')[-1]
    
if os.path.exists(data_path):
    globfile=glob.glob(data_path+"/"+prefix+"_uniq.bc")
    if len(globfile) == 1:
        bloom_counter = globfile[0]
    globfile=glob.glob(data_path+"/*.bed")
    if len(globfile) == 1:
        bedfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_GC.bin")
    if len(globfile) == 1:
        GCfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_CN2.bin")
    if len(globfile) == 1:
        CNfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_kmer.bed")
    if len(globfile) == 1:
        uniqkmer = globfile[0]

if args.o != None:
    output = args.o
else:
    if args.B:
        output = sample_path.replace('.bam','')
    else:
        output = sample_path.replace(".fastq.gz","").replace("*","")