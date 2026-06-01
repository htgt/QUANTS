# infer_library_orientations.py

Infer library orientation from experimental primers, FASTQ reads, and template library sequences.

## Requirements

This script requires a Python environment with Biopython installed:

```bash
pip install biopython
```

## Usage

```bash
python infer_library_orientations.py \
       --name NAME \
       --expt_forward_primer EXPT_FORWARD_PRIMER \
       --expt_reverse_primer EXPT_REVERSE_PRIMER \
       --valiant_meta VALIANT_META \
       --fastq_1 FASTQ_1 \
       [--max_reads MAX_READS] \
       [--output OUTPUT]
```

## Inputs

Required:

- `--name`: Sample name
- `--expt_forward_primer`: Experimental forward primer sequence
- `--expt_reverse_primer`: Experimental reverse primer sequence
- `--valiant_meta`: Path to valiant metadata file
- `--fastq_1`: Path to FASTQ read file

Optional:

- `--max_reads`: Maximum number of reads to process (default: `100`)
- `--output`: Output TSV path (default: `library_orientations.tsv`)

## Output

A TSV file containing:

| Column | Description |
|---------|-------------|
| `name` | Sample name |
| `primer_start` | Primer sequence to trim from the start of reads. |
| `primer_end` | Primer sequence to trim from the end of reads.|
| `append_start` |  Sequence to append to the start of reads before alignment. |
| `append_end` | Sequence to append to the end of reads before alignment. |

## Example

```bash
python infer_library_orientations.py \
    --name sample1 \
    --expt_forward_primer ACTGACTGACTG \
    --expt_reverse_primer CAGTCAGTCAGT \
    --valiant_meta library_meta.tsv \
    --fastq_1 sample1.fastq.gz
```