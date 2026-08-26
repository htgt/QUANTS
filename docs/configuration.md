# QUANTS: Configuration

**Note:**
- Use full paths where file paths are required
- Check for deprecated parameters before configuring [here](#deprecated-parameters).
- All of these parameters can be fed through a params.json file instead, using `-params-file params.json`.

## Input/output options

```console
--input                               [string]  Path to comma-separated file containing information about the samples in the experiment.
--single_end                          [boolean] Define whether data is single-end instead of paired-end.
--outdir                              [string]  Path to the output directory where the results will be saved. [default: ./results]
--multiqc_title                       [string]  MultiQC report title. Printed as page header, used for filename if not otherwise specified.
--input_type                          [string]  Type of input data. Options are `fastq` (default) or `cram`.
```

## Quality control

```console
--raw_sequencing_qc                   [boolean] Define whether the pipeline should run sequencing QC for raw input data.
--read_merging_qc                     [boolean] Define whether the pipeline should run sequencing QC for merged reads (only suitable for paired-end data with read merging enabled).
--adapter_trimming_qc                 [boolean] Define whether the pipeline should run sequencing QC for adapter trimmed reads (only suitable when adapter trimming enabled).
--primer_trimming_qc                  [boolean] Define whether the pipeline should run sequencing QC for primer trimmed reads (only suitable when primer trimming enabled).
--read_filtering_qc                   [boolean] Define whether the pipeline should run sequencing QC for filtered reads (only suitable when read filtering enabled).
--seqkit_stats_options                [string]  Define options for SeqKit stats (only suitable when at least one qc is enabled).
```

## Read merging options

```console
--read_merging                        [string]  Define whether the pipeline should merge reads (only suitable for paired-end data).
--seqprep_options                     [string]  Define options for SeqPrep (only suitable for pair-end data with SeqPrep enabled).
--flash2_options                      [string]  Define options for FLASH2 (only suitable for pair-end data with FLASH2 enabled).
```

## Read trimming options

```console
--adapter_trimming                    [string]  Define whether the pipeline should trim adapters from reads.
--primer_trimming                     [string]  Define whether the pipeline should trim primers from reads.
```

## Read filtering options

```console
--read_filtering                      [string]  Define whether the pipeline should filter reads (only suitable when input is single-end or read merging is enabled).
--seqkit_seq_options                  [string]  Define options for SeqKit seq (only suitable when read_filtering enabled).
```

## Read modification options

```console
--read_modification                   [boolean] Define whether to add string and qualities to read (e.g. adding a perfect primer to the read).
--append_quality                      [integer] Define quality value to read quality (this should be a single character), else set to null.
```

## Quantification options

```console   
--quantification                      [string]  Define whether the pipeline should run quantification.
--transform_library                   [boolean] Define whether the pipeline should transform the oligo library (only suitable when quantification is enabled).  
--pyquest_library_convertor_options   [string]  Define options for pyquest library convertor.
```

## Downsampling options

```console
--downsampling                        [boolean] Define whether the pipeline should downsample the input data
--downsampling_size                   [integer] Number of counts to downsample the input data to
--downsampling_seed                   [integer] Optional seed to give to the downsampler. 100 by default
```

## Useful core options

```console
-config
    Add the specified file to configuration set
-name
    Assign a mnemonic name to the a pipeline run
-params-file
    Load script parameters from a JSON/YAML file
-profile
    Choose a configuration profile
-resume
    Execute the script using the cached results, useful to continue executions that was stopped by an error
-w, -work-dir
    Directory where intermediate result files are stored
```

## [BETA] Inferring library orientation options

The --infer_library_orientations parameter and its associated functionality are available in QUANTS.

**Please note** that this functionality is currently in **beta** and should be used with caution. The parameter currently defaults to `False`

```
--infer_library_orientations          [boolean] Define whether the pipeline should infer library orientations.
```

## Deprecated Parameters

With the release of QUANTS version 4.0.0.0, the following parameters can no longer be set globally and must now be specified in the samplesheet for each individual sample:

| Column         | Description                                                                                                                |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| `adapter_cutadapt_options` | Now set as `adapter_path` in samplesheet. |
| `primer_cutadapt_options`  | Now set as `primer_start` and `primer_end` in samplesheet. |
| `append_start`             | Set as `append_start` in samplesheet. |
| `append_end`               | Set as `append_end` in samplesheet. |
| `oligo_library`            | Set as `oligo_library` in samplesheet. |
| `read_transform`           | Set as `read_transform` in samplesheet. |

