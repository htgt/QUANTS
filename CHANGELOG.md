# QUANTS: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0.0 - [January 2022]

Initial release of QUANTS, created with the [nf-core](https://nf-co.re/) template.

## 1.1.0.0 - [6th February 2022]

* Rename from nf-core-sge to QUANTS
* Fix SeqPrep->QC file assignment bug
* Add initial documentation

## 1.2.0.0 [30th March 2022]

* Restructure flow of data (technical debt)
* Add subflow for read transform (rev comp, rev, comp)
* Add support for CRAM input
* Remove separate library-independent quantification
* Replace library-dependent quantification with counting unqiue reads + merge with library (pyCROQUET)

## 1.2.1.0 [4th April 2022]

* Allow sample names to start with numeric in post-processing R script

## 1.2.1.1 (9th September 2022)

* Remove meta id tag from pyCROQUET module

## 2.0.0.0 (27th June 2023)

* Replace pyCROQUET with pyQUEST version 1.0
* Add script for converting VaLiAnT meta file (or other CSV/TSV) into pyQUEST-formatted library (not integrated into workflow)

## 3.0.0.0 - [21st August 2023]

* Split read trimming into two stages
    * Adapter trimming - removes user-defined adapter sequences and takes forward both trimmed and untrimmed reads
    * Primer trimming - removes user-defined primer sequences and takes forward only trimmed reads
* Add a read modification process which can append user-defined sequences to trimmed reads
* Add library transformer to allow users to provide libraries in a different format (e.g. the meta CSV from VaLiAnT) and convert it for use with pyQUEST

## 3.0.0.1 - [12th September 2023]

* Primer trimming - bugfix to ensure cutadapt splits reads into trimmed and untrimmed files

## 3.0.0.2 - [11th October 2023]

* Collation of cutadapt JSON results into single JSON file
* Collation of SeqKit statistics results into a single TSV file
* Update version of pyQUEST to version 1.1.0
    * Improved handling of 0-length reads
    * Ability to extract top 50 library-independent counts as FASTA
## 3.0.0.3 - [24th January 2024]

* Hotfix to force COLLATE_CUTADAPT_JSONS to run on 1 cpu

## 3.0.0.4 - [7th November 2024]

* Replace containers which use licensed conda packages
* Remove galaxy depot

## 3.1.0.0 - [26th March 2025]

* Add downsampling step using modified seqtk/sample module
* Replace Python containers which use licensed conda packages

## 4.0.0.0 - [11th August 2025]

* Sample-specific parameter options deprecated from global params
* Read sample-specific parameters from samplesheet and pass to downstream processes
* Extend samplesheet validation in bin/check_samplesheet_fastq.py, and add bin/validate_samplesheet.py script
* Add grouping column group_id to samplesheet
* Aggregate output directories by group_id
* Add memory scaling and error strategy for downsampling
* Extend error codes for overall error strategy

## 4.1.0.0 - [19th June 2026]

### Added
* Support for paired-end samples to be processed through the pipeline
* Memory scaling for downsampling step
* GitLab CI pipeline with a linting step
* Validation for input files containing cram paths
* Script to summarise the execution trace

### Changed
* CPU, memory, and time set per process
* Updated html report produced when pipeline run
* Overview QUANTS diagrams updated
