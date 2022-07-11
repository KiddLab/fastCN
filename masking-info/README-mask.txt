5 August 2020

To run fastCN we need a masked genome.  The genome should be masked
for common repeats (RepeatMasker), tandem repeats (TRF), and regions based on the NCBI
WindowMasker/DUST algorithm. We also additionally mask out 50mers that are have at least 20
hits in the genome. 

Here is how we run these tools on our cluster.  I am using the Tasha_CanFam4 genome as 
an example.

To make things more efficient, we divide the genome into segments based on the location of gaps.

1. Divide genome into segments

1.1 get the locations of the gaps:
get-gaps-bed.py \
--in /home/jmkidd/links/kidd-lab/genomes/tasha/ref/Tasha_CanFam4.fa \
--out Tasha_CanFam4.gaps.bed

1.2 determine where to split the genome.
We want to divide the genome up into several hundred 'chunks' based on where the gaps are.
This is done by splitting at gaps of a certains size.  Some genomes contain many thousands of
short gaps, we do not want to split at those.  The size may need to be adjusted to yield
a few hundred segments to split.

 python3 write-chunk-coords.py \
 --fai /home/jmkidd/links/kidd-lab/genomes/tasha/ref/Tasha_CanFam4.fa.fai \
 --gaps Tasha_CanFam4.gaps.bed \
 --out Tasha_CanFam4.gap-segments.txt \
 --mingap 100

1.3 Divide genome into sub sequences based on the determined segments
mkdir chunk-segments
 
python3 extract-chunks.py \
--fa /home/jmkidd/links/kidd-lab/genomes/tasha/ref/Tasha_CanFam4.fa \
--segments Tasha_CanFam4.gap-segments.txt \
--outdir chunk-segments/


2. Run RepeatMasker on each chunk

2.1 Write cmd for each segment using the script write-rm.py
This will have to be edited to point to the correct directory and to include
the correct RepeatMasker cmds (such as the species).

For this example, it is:

[jmkidd@gl3153 mask-repeats]$ head Tasha_CanFam4.repeatmasker.cmds
RepeatMasker -species dog -e ncbi chunk-segments/chrX:43901771-43908773.fa
RepeatMasker -species dog -e ncbi chunk-segments/chr15:17832796-64389122.fa

2.2 Each of these commands show then be run.  This can be done using the appropriate
cmds on your compute cluster.

2.3 combine the RepeatMasker output into single, and convert to bed format.

python combine-rm.py --fai /home/jmkidd/links/kidd-lab/genomes/tasha/ref/Tasha_CanFam4.fa.fai \
--segments Tasha_CanFam4.gap-segments.txt --rmdir chunk-segments/ --out Tasha_CanFam4.combined-RM.out

python convert-RM-to-bed.py   --rmfile Tasha_CanFam4.combined-RM.out --bed Tasha_CanFam4.combined-RM.out.bed

3. run tandem repeats finder

3.1 write trf cmds for each chunk

as before, you will have to edit the write-trf.py script to point to the right directories.
mkdir trfDir
write-trf.py

3.2 run the trf cmds for each segment using your cluster.  The cmds are in trfDir/trfchunks.cmds

3.3 combine the trf output into a single file, convert to bed format, and merge together

python combine-trf.py --segments Tasha_CanFam4.gap-segments.txt --trfdir trfDir/ --out Tasha_CanFam4.trf.dat

python trf-to-bed.py --trf Tasha_CanFam4.trf.dat --bed Tasha_CanFam4.trf.bed

sort and merge bed file

sortBed -i Tasha_CanFam4.trf.bed | mergeBed -i stdin > Tasha_CanFam4.trf.merge.bed

You can check the length of masked regions using bed-length.py

[jmkidd@gl-login1 mask-repeats]$ bed-length.py -f Tasha_CanFam4.trf.merge.bed
Tasha_CanFam4.trf.merge.bed 44866605

4. Run WindowMasker/DUST

4.1 This uses the NCBI tools to also mask repetitive sequences in a window-based manner

On our cluster we use:
module load ncbi-blast/2.10.0

and run nt wo steps:

windowmasker -mem 10000 -mk_counts  -in ref/Tasha_CanFam4.fa -out wm_counts

windowmasker -ustat wm_counts -dust true -in ref/Tasha_CanFam4.fa   -out Tasha_CanFam4.sddust.out

4.2 Convert output to bed format

python convert-dustout-to-bed.py --sddust Tasha_CanFam4.sddust.out --bed Tasha_CanFam4.sddust.out.bed

5. Make genome version with RepeatMasker, TRF, and WindowMasker/DUST regions masked out

5.1 combine masking information

cat ../Tasha_CanFam4.combined-RM.out.bed ../Tasha_CanFam4.trf.bed ../Tasha_CanFam4.sddust.out.bed \
| grep -v '#chrom' | cut -f 1,2,3 > combined.RMandTRFandDust.bed

sortBed -i combined.RMandTRFandDust.bed > combined.RMandTRFandDust.bed.sort

mergeBed -i combined.RMandTRFandDust.bed.sort > combined.RMandTRFandDust.bed.sort.merge

# check size of masked regions
bed-length.py -f combined.RMandTRFandDust.bed.sort.merge

[jmkidd@gl-login1 make-mrsfast-masked]$ bed-length.py -f combined.RMandTRFandDust.bed.sort.merge
combined.RMandTRFandDust.bed.sort.merge 1181247082

5.2 make masked version of the genome

mkdir RMandTRFandDustmasked

maskFastaFromBed -fi ../ref/Tasha_CanFam4.fa \
-fo RMandTRFandDustmasked/Tasha_CanFam4.fa \
-bed combined.RMandTRFandDust.bed.sort.merge


5.3 make mrsfast index to use when searching for the 50mers

module load mrsfast/3.4.1
mrsfast --index RMandTRFandDustmasked/Tasha_CanFam4.fa

samtools faidx RMandTRFandDustmasked/Tasha_CanFam4.fa

6. Search for 50mers to mask

6.1 extract 50mers from masked genome to search

mkdir k50-search
mkdir k50-search/k50fasta

python k50-search/extract-50mers.py \
--fai RMandTRFandDustmasked/Tasha_CanFam4.fa.fai \
--fa RMandTRFandDustmasked/Tasha_CanFam4.fa \
--outdir k50-search/k50fasta


6.2 Next we will search each of the 50mers against the masked genome
using mrsFAST. 

Write the cmds to search:
python write-mrsfast-ksearch-cmds.py \
--fa ../RMandTRFandDustmasked/Tasha_CanFam4.fa \
--kdir k50fasta/ \
--out mrsfast.ksearch.cmds

then run all the cmds in mrsfast.ksearch.cmds, with proper memory, etc for the mrsfast jobs
this searches hits for each 50mer within edit distance of 2. These searches should be pretty fast
 due to the length of the 50mers and the use of masked genome.

6.3 Count the hits for each kmer

python count-kmer-maps.py --kdir k50fasta/


6.4 Select kmer with >=20 hits

python select-50.py --kdir k50fasta/ --out k50.selge20.bed

6.5 Merge together the set of  kmer coordinates

sortBed -i k50.selge20.bed | mergeBed -i stdin > k50.selge20.bed.merge

Check the length
[jmkidd@gl-login1 k50-search]$ bed-length.py -f k50.selge20.bed.merge
k50.selge20.bed.merge 95135

Here there are not that many masked. But they are found many times and for most applications
we get better performance if we mask them out.  If there are specific regions of the genome
of interest with high copy number in the assembly, you may alter this step.

7. Make genome version with all segments masked and prepare for fastCN GC_control_gen

7.1 add masking of overrepresented kmer

mkdir RMandTRFandDustandK50-masked

maskFastaFromBed -fi RMandTRFandDustmasked/Tasha_CanFam4.fa \
-fo RMandTRFandDustandK50-masked/Tasha_CanFam4.fa \
-bed k50-search/k50.selge20.bed.merge

samtools faidx RMandTRFandDustandK50-masked/Tasha_CanFam4.fa 

This is the masked version of the genome that should be used for the mrsFAST

7.2 Setup mrsFAST index of masked genome

module load mrsfast/3.4.1
mrsfast --index RMandTRFandDustandK50-masked/Tasha_CanFam4.fa

7.3 Determine masked regions for use in GC_control_gen

get-gaps-bed.py  --in RMandTRFandDustandK50-masked/Tasha_CanFam4.fa --out RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed

Check the length. This is the total amount masked in the genome. It is a pretty big fraction!
bed-length.py -f RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed
RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed 1181398476


Now, need to add 36bp due to masking shadow effect

slopBed -b 36 -i RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed -g RMandTRFandDustandK50-masked/Tasha_CanFam4.fa.fai \
>  RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed.slop36

sortBed -faidx RMandTRFandDustandK50-masked/Tasha_CanFam4.fa.fai -i RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed.slop36 \
 > RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed.slop36.sorted

mergeBed -i RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed.slop36.sorted > RMandTRFandDustandK50-masked/Tasha_CanFam4.gaps.bed.slop36.sorted.merge

This file, Tasha_CanFam4.gaps.bed.slop36.sorted.merge, is needed for the masked input in the fastCN GC_control_gen step.

