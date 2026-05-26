#!/usr/bin/env python3

# Adapted from benchling_utils infer-library-orientations
# Original author: Jamie Billington

__version__ = "1.0.0"

import argparse
import csv
import logging
from pathlib import Path
from orientations import SequenceLibrary, SequenceSample


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Infer library orientation from experimental primers, "
            "FASTQ reads, and template library sequences.\n\n"
            "Inputs:\n"
            "  - name\n"
            "  - Experimental forward and reverse primers\n"
            "  - FASTQ read file\n"
            "  - Template library metadata\n\n"
            "Outputs:\n"
            "  TSV file containing"
            "  - name \n"
            "  - primer_start\n"
            "  - primer_end\n"
            "  - append_start\n"
            "  - append_end"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Sample name",
    )

    parser.add_argument(
        "--expt_forward_primer",
        required=True,
        help="sequence for experiment forward primer"
    )

    parser.add_argument(
        "--expt_reverse_primer",
        required=True,
        help="sequence for experiment reverse primer"
    )

    parser.add_argument(
        "--valiant_meta",
        required=True,
        help="path valiant met file"
    )

    parser.add_argument(
        "--fastq_1",
        required=True,
        help="path to fastq_1"
    )

    parser.add_argument(
        "--max_reads",
        type=int,
        default=100,
        help="Maximum number of reads to process. Default: 100",
    )

    parser.add_argument(
        "--output",
        default="library_orientations.tsv",
        type=Path,
        help="Output TSV path. Default: library_orientations.tsv",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}")

    return parser.parse_args()


def main():
    args = parse_args()

    sample = SequenceSample(
            name=args.name,
            expt_forward_primer=args.expt_forward_primer,
            expt_reverse_primer=args.expt_reverse_primer,
            valiant_meta=Path(args.valiant_meta),
            fastq_1=Path(args.fastq_1),
            max_reads=args.max_reads
    )
    output_file = args.output

    sample_data = SequenceLibrary(sample)

    logging.info("-" * 52)

    logging.info(
        "Detecting orientation for sample: %s",
        sample.name,
    )

    logging.info(
        "Primer vs. Template orientation: %s",
        sample_data.lib_relative_orientation
    )

    logging.info(
        "Primer vs. Reads orientation: %s",
        sample_data.read_relative_orientation
    )

    logging.info(
        "Apply reverse complement to reads: %s",
        sample_data.read_transform
    )

    logging.info("-" * 52)

    primer_forward = sample_data.effective_fwd
    primer_reverse = sample_data.effective_rev
    append_start = sample_data.append_fwd
    append_end = sample_data.append_rev

    if sample_data.read_transform:
        read_transform = "reverse_complement"
    else:
        read_transform = ""

    headers = [
        "name",
        "primer_start",
        "primer_end",
        "append_start",
        "append_end",
        "read_transform"
    ]

    # Write TSV file
    with open(
        output_file,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(headers)
        writer.writerow(
            [
                sample.name,
                primer_forward,
                primer_reverse,
                append_start,
                append_end,
                read_transform
            ]
        )

        logging.info(f"Created {output_file}")


if __name__ == "__main__":
    main()
