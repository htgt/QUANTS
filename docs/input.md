# QUANTS: Input

## Samplesheet

You will need to create a samplesheet with information about the samples you would like to analyse before running the pipeline.

Use the `input` parameter to specify its location.

```console
--input '[path to samplesheet file]'
```

The samplesheet has to be a **comma-separated** file with a minimum of 3 columns (`sample, fastq_1, fastq_2`) and a header row as shown in the examples below. The samplesheet can also contain sample-specific parameters (see example below).

### Minimum samplesheet example

```csv
sample,fastq_1,fastq_2
S01_D4_R1,S01_D4_R1.fastq.gz,
S02_D4_R2,S02_D4_R2.fastq.gz,
S03_D7_R1,S03_D7_R1.fastq.gz,
S04_D7_R2,S04_D7_R2.fastq.gz,
```

### Example of complete samplesheet with all available fields

```csv
sample,group_id,fastq_1,fastq_2,oligo_library,append_start,append_end,primer_start,primer_end,read_transform,adapter_path
S01_D4_R1,AAAA,S01_D4_R1_1.fastq.gz,S01_D4_R1_2.fastq.gz,/path/to/meta1.csv,CTTGC,GCTG,CAGC,GCAAG,reverse_complement,path/to/adaptors.fa
S02_D4_R2,AAAA,S02_D4_R2_1.fastq.gz,S02_D4_R2_2.fastq.gz,/path/to/meta1.csv,CTTGC,GCTG,CAGC,GCAAG,reverse_complement,path/to/adaptors.fa
S03_D7_R1,AAAA,S03_D7_R1_1.fastq.gz,S03_D7_R1_2.fastq.gz,/path/to/meta1.csv,CTTGC,GCTG,CAGC,GCAAG,reverse_complement,path/to/adaptors.fa
S04_D7_R2,AAAA,S04_D7_R2_1.fastq.gz,S04_D7_R2_2.fastq.gz,/path/to/meta1.csv,CTTGC,GCTG,CAGC,GCAAG,reverse_complement,path/to/adaptors.fa
S05_D4_R1,BBBB,S05_D4_R1_1.fastq.gz,S05_D4_R1_2.fastq.gz,/path/to/meta2.csv,ATACG,AACG,CGTT,CGTAT,reverse_complement,path/to/adaptors.fa
S06_D7_R1,BBBB,S06_D7_R1_1.fastq.gz,S06_D7_R1_2.fastq.gz,/path/to/meta2.csv,ATACG,AACG,CGTT,CGTAT,reverse_complement,path/to/adaptors.fa

```

The sample-specific parameters are in relation to the global params (see [configurations](configuration.md#quants-configuration)). Samplesheet fields must be consistent with the global parameters (see configuration), i.e., fields may vary depending on global parameter settings. For example, the samplesheet can only include `oligo_library` values if the global quantification parameter is set to `"pyquest"`. 


Available samplesheet fields are in the table below:

| Column         | Description                                                                                                                |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| `sample`       | Custom sample name. Spaces in sample names are automatically converted to underscores (`_`). Samplesheet must contain this field.                               |
| `fastq_1`      | Full path to a FASTQ file for Illumina short reads 1. File has to be gzipped and have the extension ".fastq.gz" or ".fq.gz". Samplesheet must contain this field. |
| `fastq_2`      | Full path to a FASTQ file for Illumina short reads 2 (for paired-end sequencing). File has to be gzipped and have the extension ".fastq.gz" or ".fq.gz". Samplesheet must contain this field (but can be left empty). |
| `group_id`     | (Optional) Custom group ID to group samples together in the output directory. Note: This currently only works when the data is single-end.                                                 |
| `oligo_library`| (Optional) Path to an oligo library file. Required if `quantification` is enabled in global parameters.                                   |
| `append_start` | (Optional) Sequence to append to the start of reads before alignment. Required if `read_modification` is enabled in global parameters.                                     |
| `append_end`   | (Optional) Sequence to append to the end of reads before alignment. Required if `read_modification` is enabled in global parameters.                                      |
| `primer_start` | (Optional) Primer sequence to trim from the start of reads. Required if `primer_trimming` is set in global parameters.                                     |
| `primer_end`   | (Optional) Primer sequence to trim from the end of reads. Required if `primer_trimming` is set in global parameters.                                       |
| `read_transform`| (Optional) Define this to `reverse`, `complement` or `reverse_complement` if transformation is required, else leave empty. |
| `adapter_path` | (Optional) Path to a FASTA file containing adapter sequences to trim from reads. Required if `adapter_trimming` is set in global parameters.                                   |


### Other inputs

Other input files also needed to run QUANTS are:
- FASTQ files specified in the samplesheet.
- FASTA file with adapters, if `adapter_path` set in samplesheet.
- Oligo library file if `oligo_library` set in samplesheet. Note that Information on the required library format for pyQUEST can be found here along with other usage details.
