# Splicing Analysis Toolkit (Spanki)
# Example code for an analysis of splicing
# Uses testdata availble from:
# http://www.cbcb.umd.edu/software/spanki/testdata.tar.gz

ECHO "[***************] Starting female spankijunc runs"
spankijunc -m all -o female_rep1 -i testdata/female_r1.bam -g testdata/annotation/genemodels.gtf -f testdata/fasta/myref.fa
spankijunc -m all -o female_rep2 -i testdata/female_r2.bam -g testdata/annotation/genemodels.gtf -f testdata/fasta/myref.fa
ECHO "[***************] Starting male spankijunc runs"
spankijunc -m all -o male_rep1 -i testdata/male_r1.bam -g testdata/annotation/genemodels.gtf -f testdata/fasta/myref.fa
spankijunc -m all -o male_rep2 -i testdata/male_r2.bam -g testdata/annotation/genemodels.gtf -f testdata/fasta/myref.fa

# Note:  If you want all your tables to be symmetrical (have the same number of rows and the same junctions),
# then create a list of junctions (either curated, or a merge of all junctions detected), and run make_curated_jtab
# on each sample. Example:

ECHO "[***************] Making a table of all junctions detected in any sample"
cat female_rep1/juncs.all female_rep2/juncs.all female_rep1/juncs.all female_rep2/juncs.all > all_tables.txt
head -1 female_rep1/juncs.all | awk '{print $1"\t"$4"\t"$7"\t"$8"\t"$9"\t"$14"\t"$15}' > all_juncs.txt 
awk '{if ($1 != "juncid") {print $1"\t"$4"\t"$7"\t"$8"\t"$9"\t"$14"\t"$15}}' all_tables.txt | sort -u >> all_juncs.txt

ECHO "[***************] Getting additional data from the female runs"
make_curated_jtab -o female_rep1_curated -i  testdata/female_r1.bam -jlist all_juncs.txt -jtab female_rep1/juncs.all
make_curated_jtab -o female_rep2_curated -i  testdata/female_r2.bam -jlist all_juncs.txt -jtab female_rep2/juncs.all
ECHO "[***************] Getting additional data from the male runs"
make_curated_jtab -o male_rep1_curated -i  testdata/male_r1.bam -jlist all_juncs.txt -jtab male_rep1/juncs.all
make_curated_jtab -o male_rep2_curated -i  testdata/male_r2.bam -jlist all_juncs.txt -jtab male_rep2/juncs.all

ECHO "[***************] Merging the replicates together"
merge_jtabs female_rep1_curated/juncs.all,female_rep2_curated/juncs.all > female_repsmerged.juncs
merge_jtabs male_rep1_curated/juncs.all,male_rep2_curated/juncs.all > male_repsmerged.juncs

# Alternatively, just merge the tables without the extra step of making the tables symmetrical:
#merge_jtabs female_rep1/juncs.all,female_rep2/juncs.all > female_repsmerged.juncs
#merge_jtabs male_rep1/juncs.all,male_rep2/juncs.all > male_repsmerged.juncs

ECHO "[***************] Parsing events output"
spankisplice -o female_repsmerged_events -j female_repsmerged.juncs -c testdata/female_cuff/isoforms.fpkm_tracking -f testdata/fasta/myref.fa -g testdata/annotation/genemodels.gtf -a testdata/annotation/genemodels_splices.out 
spankisplice -o male_repsmerged_events -j male_repsmerged.juncs -c testdata/male_cuff/isoforms.fpkm_tracking -f testdata/fasta/myref.fa -g testdata/annotation/genemodels.gtf -a testdata/annotation/genemodels_splices.out 

ECHO "[***************] Doing pairwise comparison"
splicecomp -a female_repsmerged_events/events.out -b male_repsmerged_events/events.out -o F_vs_M_splicecomp
junccomp -a female_repsmerged.juncs -b male_repsmerged.juncs -o F_vs_M_junccomp

########################
# Other functions      #
########################

# Annotating a junction set (From a junction table)
annotate_junctions -o female_rep1_annotated_junctab -jtab female_rep1/juncs.all -f ~/data/indexes/dm3_NISTnoUextra.fa -g ~/data/annotation/dmel_BDGP5.39.67_ed.gtf
# Annotating a junction set (From a junction list)
annotate_junctions -o female_rep1_annotated_junclist -jlist female_rep1/juncs.list -f ~/data/indexes/dm3_NISTnoUextra.fa -g ~/data/annotation/dmel_BDGP5.39.67_ed.gtf
# Annotating annotated junctions
annotate_junctions -o annotated_reference_juncs -f ~/data/indexes/dm3_NISTnoUextra.fa -g ~/data/annotation/dmel_BDGP5.39.67_ed.gtf




