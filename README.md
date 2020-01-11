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
python3, various standard python modules, g++, mrsfast, samtools

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

## Step 3 Setup fastCN GC-normalization files

The basic command layout is:
```./GC_control_gen Original_genome.fa Excluded.bed Masked.bed 400 genome_GC.bin```

The 400 indicates a window size of 400 bp for determining GC percentage for normalization.
The command will create a file GRCh38_BSM_WMDUST/ref/GRCh38_BSM_WMDUST.GC_control.bin


Sample cmd:
```
fastCN/GC_control_gen \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST_unmasked.fa \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST.exclude.bed.sort2 \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST.gaps.bed.slop36.sorted.merged.sort2 \
400 \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST.GC_control.bin
```

Note that the file GRCh38_BSM_WMDUST/ref/GRCh38_BSM.fa is the unmasked genome. This way
GC values in repeats are considered properly.

## Step 4 Build mrsfast index for mapping
We have tested with mrsfast v. 3.3.9, but newer versions will work as well. 
An index should be build from the masked genome.

```
cd GRCh38_BSM_WMDUST/ref-WMDUST-masked/
mrsfast --index GRCh38_BSM_WMDUST_masked.fa
```


## Step 5 Download a small fastq set from 1000 Genomes for testing

```
cd ..
mkdir fastq
cd fastq
wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR062/SRR062559/SRR062559_1.fastq.gz
wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR062/SRR062559/SRR062559_2.fastq.gz
```

## Step 6 Mapping
Now we are ready to do the mapping and postprocessing.  Here, we'll break it down
into individual steps. Steps can be easily combined with a Python or other driver
script to streamline the procedure for multiple samples.  If you have multiple libraries/runs/lanes
for a sample, it is best to run them separately and then combine the GC normalized depth files. Other scripts
in the repository can be used to combine the files.

Here, we will split the reads into 36bp chunks and map them to the masked
reference genome using mrsfast.  Other python scripts included can be used to process
BAM files.  This example uses 8 threads and 16G of memory in the mrsfast step.

```
cd ..
mkdir mapping

python fastCN/extract-from-fastq36-pair.py --in1 fastq/SRR062559_1.fastq.gz --in2 fastq/SRR062559_2.fastq.gz  |  \
mrsfast --search GRCh38_BSM_WMDUST/ref-WMDUST-masked/GRCh38_BSM_WMDUST_masked.fa \
 --seq /dev/fd/0 --disable-nohits --mem 16 --threads 8 -e 2 --outcomp -o mapping/SRR062559
```

This will make the file `mapping/SRR062559.sam.gz`

## Step 7 Perform GC correction and make per-bp depth file.

The GC correction step uses a python utility `smooth_GC_mrsfast.py` for curve fitting. 
Check that this program is found in your path:
```
which smooth_GC_mrsfast.py
```

Then make a directory for output and execute  `SAM_GC_correction`:

```
mkdir binary
zcat mapping/SRR062559.sam.gz | \
fastCN/SAM_GC_correction  \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST_unmasked.fa.fai \
GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST.GC_control.bin \
/dev/fd/0 \
binary/SRR062559
```

The resulting binary depth file should be gziped for future processing and to make files smaller and 

`gzip binary/SRR062559.bin`

This should also make a plot of the depth vs GC and a curve of correction factors used. In the example,
there is a mean depth of ~1.25 and a smooth correction curve.

Here is a sample image

![SRR062559.png](sample-output/binary/SRR062559.png)

## Step 8: Convert per bp corrected depth to depth in windows
The file binary/SRR062559.bin.gz is a half-float representation of the per-bp  GC corrected depth.
We can convert to mean values in 3kb windows using the associated python script.

```
mkdir windows

python fastCN/perbp-to-windows.py \
--depth binary/SRR062559.bin.gz \
--out windows/SRR062559.depth.3kb.bed \
--chromlen GRCh38_BSM_WMDUST/ref-WMDUST/GRCh38_BSM_WMDUST_unmasked.fa.fai \
--windows GRCh38_BSM_WMDUST/windows-WMDUST/GRCh38_BSM_WMDUST.3kb.bed
```

## Step 9 convert windows of depth to windows of copy-number based on defined control regions

```
python fastCN/depth-to-cn.py \
--in windows/SRR062559.depth.3kb.bed \
--autocontrol GRCh38_BSM_WMDUST/windows-WMDUST/GRCh38_BSM_WMDUST.3kb.autoControl.bed \
--chrX GRCh38_BSM_WMDUST/windows-WMDUST/GRCh38_BSM_WMDUST.3kb.chrXnonParControl.bed
```

The file windows/SRR062559.depth.3kb.bed.CN.bed has per window estimated copy numbers
windows/SRR062559.depth.3kb.bed.stats has the mean and std depth for autosomes and X.
The two png files show the distributions.

![zscore](sample-output/windows/SRR062559.depth.3kb.bed.stats.zscore.hist.png)
![dept-hist](sample-output/windows/sample-output/windows/SRR062559.depth.3kb.bed.stats.hist.png)






