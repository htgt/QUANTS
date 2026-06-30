# QUANTS: Input

## Samplesheet

You will need to create a samplesheet with information about the samples you would like to analyse before running the pipeline.

Use the `input` parameter to specify its location.

```console
--input '[path to samplesheet file]'
```

The samplesheet has to be a **comma-separated** file. 
If working with FASTQ files, you will need a minimum of three columns with headers `sample,fastq_1,fastq_2`. If working with CRAM files, you will need a minimum of two columns with headers `sample,cram_path`. The samplesheet can also contain sample-specific parameters (see example below).

### Minimum samplesheet example

Example of a samplesheet with FASTQ files (note `fastq_2` column header required even if data is single-end):

```csv
sample,fastq_1,fastq_2
S01_D4_R1,S01_D4_R1.fastq.gz,
S02_D4_R2,S02_D4_R2.fastq.gz,
S03_D7_R1,S03_D7_R1.fastq.gz,
S04_D7_R2,S04_D7_R2.fastq.gz,
```

Example of a samplesheet with CRAM files:

```csv
sample,cram_path
S01_D4_R1,S01_D4_R1_merged.cram,
S02_D4_R2,S02_D4_R2_merged.cram,
S03_D7_R1,S03_D7_R1_merged.cram,
S04_D7_R2,S04_D7_R2_merged.cram,
```

### Valid samplesheet fields

Valid samplesheet fields are in the table below:

| Column         | Description                                                                                                                |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| `sample`       | (Required) Custom sample name. Spaces in sample names are automatically converted to underscores (`_`).        |
| `fastq_1`      | (Required if using FASTQ as input type) Full path to a FASTQ file. File has to be gzipped and have the extension ".fastq.gz" or ".fq.gz". If using FASTQ data, `input_type` must be set as `"fastq"`. |
| `fastq_2`      | (Required if using FASTQ as input type) Full path to a FASTQ file (for paired-end sequencing). File has to be gzipped and have the extension ".fastq.gz" or ".fq.gz". Note this field can be left empty when data is single-end data. |
| `cram_path`    | (Required if using CRAM as input type) Full path to a CRAM file for Illumina short reads. File has to have the extension ".cram". If using CRAM data, `input_type` must be set as `"cram"`. |
| `group_id`     | (Optional) Custom group ID to group samples together in the output directory. Note: This currently only works when the data is single-end.                                                 |
| `oligo_library`| (Optional) Path to an oligo library file. Required if `quantification` is enabled in global parameters.                                   |
| `append_start` | (Optional) Sequence to append to the start of reads before alignment. Required if `read_modification` is enabled in global parameters.                                     |
| `append_end`   | (Optional) Sequence to append to the end of reads before alignment. Required if `read_modification` is enabled in global parameters.                                      |
| `primer_start` | (Optional) Primer sequence to trim from the start of reads. Required if `primer_trimming` is set in global parameters.                                     |
| `primer_end`   | (Optional) Primer sequence to trim from the end of reads. Required if `primer_trimming` is set in global parameters.                                       |
| `read_transform`| (Optional) Define this to `reverse`, `complement` or `reverse_complement` if transformation is required, else leave empty. |
| `adapter_path` | (Optional) Path to a FASTA file containing adapter sequences to trim from reads. Required if `adapter_trimming` is set in global parameters.                                   |
| `expt_forward_primer` | (Optional) Sequence of the forward primer used in the experiment. This will replace `primer_start`, but this change is currently under development. This is accepted in the samplesheet but not used in the pipeline currently.                                    |
| `expt_reverse_primer` | (Optional) Sequence of the reverse primer used in the experiment. This will replace `primer_end`, but this change is currently under development. This is accepted in the samplesheet but not used in the pipeline currently.                                  |

Note that the sample-specific parameters are in relation to the global params (see [configurations](configuration.md#quants-configuration)). Samplesheet fields must be consistent with the global parameters (see configuration), i.e., fields may vary depending on global parameter settings. For example, the samplesheet can only include `oligo_library` values if the global quantification parameter is set to `"pyquest"`.

### Example of samplesheet (compatible with QUANTS release 4.x.x.x)

Note the example below contains FASTQ files, but sample-specific parameters can be added to CRAM samplesheets in the same way.

This is the format which should be used for any current production runs.

```csv
sample,group_id,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform
S01_D4_R1,AAAA,S01_D4_R1_1.fastq.gz,S01_D4_R1_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,CAGC,GCAAG,CTTGC,GCTG,reverse_complement
S02_D4_R2,AAAA,S02_D4_R2_1.fastq.gz,S02_D4_R2_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,CAGC,GCAAG,CTTGC,GCTG,reverse_complement
S03_D7_R1,AAAA,S03_D7_R1_1.fastq.gz,S03_D7_R1_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,CAGC,GCAAG,CTTGC,GCTG,reverse_complement
S04_D7_R2,AAAA,S04_D7_R2_1.fastq.gz,S04_D7_R2_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,CAGC,GCAAG,CTTGC,GCTG,reverse_complement
S05_D4_R1,BBBB,S05_D4_R1_1.fastq.gz,S05_D4_R1_2.fastq.gz,/path/to/meta2.csv,path/to/adaptors.fa,CGTT,CGTAT,ATACG,AACG,reverse_complement
S06_D7_R1,BBBB,S06_D7_R1_1.fastq.gz,S06_D7_R1_2.fastq.gz,/path/to/meta2.csv,path/to/adaptors.fa,CGTT,CGTAT,ATACG,AACG,reverse_complement

```

### [BETA/UNDER DEVELOPMENT] Example of samplesheet with all available fields (interim format)

Note that this is an interim format intended for use when `infer_library_orientations` is globally set to `True`. The corresponding functionality is still under development and does not yet work as expected; future updates will integrate the module required to infer library orientations into QUANTS.

Any values provided in `expt_forward_primer` and `expt_reverse_primer` will not be used in the pipeline at the moment.

```csv
sample,group_id,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform,expt_forward_primer,expt_reverse_primer
S01_D4_R1,AAAA,S01_D4_R1_1.fastq.gz,S01_D4_R1_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,,,,,,GCTG,CTTGC
S02_D4_R2,AAAA,S02_D4_R2_1.fastq.gz,S02_D4_R2_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,,,,,,GCTG,CTTGC
S03_D7_R1,AAAA,S03_D7_R1_1.fastq.gz,S03_D7_R1_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,,,,,,GCTG,CTTGC
S04_D7_R2,AAAA,S04_D7_R2_1.fastq.gz,S04_D7_R2_2.fastq.gz,/path/to/meta1.csv,path/to/adaptors.fa,,,,,,GCTG,CTTGC
S05_D4_R1,BBBB,S05_D4_R1_1.fastq.gz,S05_D4_R1_2.fastq.gz,/path/to/meta2.csv,path/to/adaptors.fa,,,,,,AACG,ATACG
S06_D7_R1,BBBB,S06_D7_R1_1.fastq.gz,S06_D7_R1_2.fastq.gz,/path/to/meta2.csv,path/to/adaptors.fa,,,,,,AACG,ATACG

```

```

### Other inputs

Other input files also needed to run QUANTS are:
- Sequencing files (FASTQ or CRAM) specified in the samplesheet.
- FASTA file with adapters, if `adapter_path` set in samplesheet.
- Oligo library file if `oligo_library` set in samplesheet. Note that information on the required library format for [pyQUEST](https://github.com/cancerit/pyQUEST) can be found [here](https://github.com/cancerit/pyQUEST#library) along with other usage details.
