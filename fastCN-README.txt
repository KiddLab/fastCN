Usage of mrsFAST pipeline
Copyright Feichen Shen
2016-7-1

1. Generate GC control file
You'll need the followings files:
	1)Original Genome in one fasta
	2)Excluded region in bed format and same chromosome order as above
	3)Masked region in bed format, same order as well
	4)The fasta index .fai from file 1)
Run the command to get a control region.
./GC_control_gen Original_genome.fa Excluded.bed Masked.bed 400 genome_GC.bin

2.Run actual mrsFAST and pipe data into SAM_GC_correction
You'll need 2 files related to reference genome:
	1)Genome fasta index in .fai
	2)GC control region binary from step 1.
... | SAM_GC_correction genome_masked.fa.fai genome_GC.bin /dev/fd/0 Sample_prefix
It will generate Sample_prefix.bin, Sample_prefix.png and Sample_prefix.txt.
The first file is the corrected depth in half float (IEEE 754-2008) representation. Masked region is -1.0


To compile, run:
g++ -o GC_control_gen GC_control_gen.cc 
g++ -o SAM_GC_correction SAM_GC_correction.cc 
g++ depth_combine.c -O2 -flax-vector-conversions -o depth_combine



