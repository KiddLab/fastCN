# fastCN

A pipeline for the fast estimation of copy-number based on read depth using
the multi-mapper mrsFAST.

If you are interested in generating paralog specific copy-number estimates
consider QuicK-mer2, accessible at: https://github.com/KiddLab/QuicK-mer2

The basic functionality of fastCN is described in [fastCN-README.txt](fastCN-README.txt)


For more information, and to reference the algorithm, please cite [our paper](https://bmcbiol.biomedcentral.com/articles/10.1186/s12915-018-0535-2) :


Pendleton AL, Shen F, Taravella AM, Emery S, Veeramah KR, Boyko AR, Kidd JM.
Comparison of village dog and wolf genomes highlights the role of the neural
crest in dog domestication. BMC Biol. 2018 Jun 28;16(1):64. doi: 10.1186/s12915-018-0535-2. PMID:29950181

# Tutorial for setting up and testing the fastCN pipeline.

Requirements:
python3, various standard python modules, g++, mrsfast version 3.4 (or newer), samtools

## Step 1 Download and compile fastCN core programs

Setup a directory to download and work from.  Clone the repository and compile the required core program components.
There may be some compiler warnings.

```
git clone https://github.com/KiddLab/fastCN.git 

cd fastCN
g++ -o GC_control_gen GC_control_gen.cc 
g++ -o SAM_GC_correction SAM_GC_correction.cc 
```

The fastCN directory needs to be in your path so that the correction script can find required
utilities. You can add the directory to your path temporarily using 

```
export PATH=$PWD:$PATH
```

## Step 2 Download prebuilt reference files and masked genome bed file

Pre-computed masking information is available for some commonly used reference genes in https://kiddlabshare.med.umich.edu/fastCN-references/

For this tutorial we will use a version of the human GRCh38 genome assembly. 

Download it to a directory and unpack it. First, change you directory to be outside of the fastCN git repository. Then:

```
wget https://kiddlabshare.med.umich.edu/fastCN-references/GRCh38_BSM_WMDUST.tar.gz
tar -xvzf GRCh38_BSM_WMDUST.tar.gz
rm GRCh38_BSM_WMDUST.tgz
```

This directory contains several files to use with the fastCN pipeline.  The genome reference
is a version of GRCh38 that does not include alternative or HLA haplotypes.  Masking has occurred
already for regions identified by RepeatMasker, TRF, WMDUST, and overrepresented 50mers.

There are three directories.

`GRCh38_BSM_WMDUST/ref-WMDUST` contains files describing the genome masking. This includes an unmasked 
version of the reference, a file giving the masking locations plus 36bp flanks, and a bed file of regions
to exclude during normalization.

`GRCh38_BSM_WMDUST/ref-WMDUST-masked/` contains the genome reference with repeated segments masked out.
Mapping will occur against this version, otherwise a large number of alignments to repeats will occur.

`GRCh38_BSM_WMDUST/windows-WMDUST/` contains several files needed for normalization and processing.
Included are windows containing 1kb and 3kb of masked sequence, as well as regions that are not used in
copy-number correction.

