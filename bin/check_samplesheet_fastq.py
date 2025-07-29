#!/usr/bin/env python

import copy
import json
import os
import csv
import sys
import errno
import argparse
from validate_samplesheet import validate_all_samples

def parse_args(args=None):
    Description = "Reformat QUANTS samplesheet file and check its contents."
    Epilog = "Example usage: python check_samplesheet.py <FILE_IN> <FILE_OUT>"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("FILE_IN", help="Input samplesheet file.")
    parser.add_argument("PARAMS_IN", help="Input Params file.")
    parser.add_argument("FILE_OUT", help="Output file.")
    return parser.parse_args(args)


def make_dir(path):
    if len(path) > 0:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise exception


def print_error(error, context="Line", context_str=""):
    error_str = "ERROR: Please check samplesheet -> {}".format(error)
    if context != "" and context_str != "":
        error_str = "ERROR: Please check samplesheet -> {}\n{}: '{}'".format(
            error, context.strip(), context_str.strip()
        )
    print(error_str)
    sys.exit(1)


def validate_headers(fieldnames: list, REQUIRED_HEADERS: list, OPTIONAL_HEADERS: list) -> list:

    HEADERS = []

    if not fieldnames:
        raise ValueError("ERROR: samplesheet file doesn't contain any fields.")

    # Check required headers
    missing_required = [col for col in REQUIRED_HEADERS if col not in fieldnames]
    if missing_required:
        raise ValueError(f"ERROR: samplesheet missing required headers: {', '.join(missing_required)}")

    HEADERS = REQUIRED_HEADERS + OPTIONAL_HEADERS
    # Check if all optional headers are present
    missing_optional = [col for col in OPTIONAL_HEADERS if col not in fieldnames]

    if missing_optional:
        print(f"WARNING: samplesheet missing optional headers: {', '.join(missing_optional)} \n"
                "These will be taken from params.json file")

    HEADERS = list(filter(lambda item: item not in missing_optional, HEADERS))

    return HEADERS


def check_samplesheet(file_in, params_in, file_out):
    """
    This function checks that the samplesheet follows the following structure:

    sample,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform
    SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,SAMPLE_PE_RUN1_2.fastq.gz,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_PE,SAMPLE_PE_RUN2_1.fastq.gz,SAMPLE_PE_RUN2_2.fastq.gz,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,
    """
    
    with open(params_in) as f:
        params = json.load(f)

    sample_mapping_dict = {}

    with open(file_in, "r") as f_in:
        f_reads = csv.DictReader(f_in)

        f_reads_ln = list(f_reads)

        # Check headers
        MIN_COLS = 2

        REQUIRED_HEADERS = [
            "sample",
            "fastq_1",
            "fastq_2"
        ]

        OPTIONAL_HEADERS = [
            "oligo_library",
            "adapter_path",
            "primer_start",
            "primer_end",
            "append_start",
            "append_end",
            "read_transform"
        ]

        headers = [header for header in f_reads.fieldnames if header.strip()]

        HEADERS = validate_headers(headers, REQUIRED_HEADERS, OPTIONAL_HEADERS)
        
        validating_samples = copy.deepcopy(f_reads_ln)
        
        validate_all_samples(validating_samples, params)
        
        # Check sample entries
        for line in f_reads_ln:
            
            lspl = [val for val in line.values() if val and val.strip()]

            for val in line.values():
                if val is None:
                    print_error(
                    "Inconsistent number of columns!",
                    "Line",
                    ",".join(str(v) if v is not None else "" for v in line.values()),
                )

            num_cols = len([x for x in lspl if x])

            if num_cols < MIN_COLS:
                print_error(
                    "Invalid number of populated columns (minimum = {})!".format(
                        MIN_COLS
                    ),
                    "Line",
                    ",".join(str(v) if v is not None else "" for v in line.values()),
                )

            # Check sample name entries
            sample = line.get("sample")
            sample = sample.replace(" ", "_")
            if not sample:
                print_error(
                    "Sample entry has not been specified!",
                    "Line",
                     ",".join(str(v) if v is not None else "" for v in line.values())
                )

            # Check FastQ file extension
            for fastq in [line.get("fastq_1"), line.get("fastq_2")]:
                if fastq:
                    if fastq.find(" ") != -1:
                        print_error("FastQ file contains spaces!",
                                    "Line",
                                     ",".join(str(v) if v is not None else "" for v in line.values())
                                )
                    if not fastq.endswith(".fastq.gz") and not fastq.endswith(".fq.gz"):
                        print_error(
                            "FastQ file does not have extension '.fastq.gz' or '.fq.gz'!",
                            "Line",
                            ",".join(str(v) if v is not None else "" for v in line.values()),
                        )

            # Auto-detect paired-end/single-end
            sample_info = []  ## [single_end, fastq_1, fastq_2]

            fastq_1 = line.get("fastq_1")
            fastq_2 = line.get("fastq_2")

            # Get rest of the info from file read line and skip sample to avoid duplication in the file out.
            # Example: [fastq_1,fastq_2,oligo_library,adapter_path,LibAmpF,LibAmpR,read_transform]
            rest_info = [line.get(h) for h in HEADERS if h != "sample"]

            if sample and fastq_1 and fastq_2:  ## Paired-end short reads
                sample_info = ["0", *rest_info]
            elif sample and fastq_1 and not fastq_2:  ## Single-end short reads
                sample_info = ["1", *rest_info]
            else:
                print_error("Invalid combination of columns provided!",
                            "Line",
                            ",".join(str(v) if v is not None else "" for v in line.values())
                        )

            # Create sample mapping dictionary = { sample: [ single_end, fastq_1, fastq_2 ] }
            if sample not in sample_mapping_dict:
                sample_mapping_dict[sample] = [sample_info]
            else:
                if sample_info in sample_mapping_dict[sample]:
                    print_error("Samplesheet contains duplicate rows!",
                                "Line",
                                ",".join(str(v) if v is not None else "" for v in line.values())
                            )
                else:
                    sample_mapping_dict[sample].append(sample_info)

    # Write validated samplesheet with appropriate columns
    if len(sample_mapping_dict) > 0:
        out_dir = os.path.dirname(file_out)
        make_dir(out_dir)
        with open(file_out, "w") as f_out:
            csv_writer = csv.writer(f_out)

            # Add column "single_end" in output csv file headers
            HEADERS.insert(1, "single_end")
            csv_writer.writerow(HEADERS)

            for sample in sorted(sample_mapping_dict.keys()):

                # Check that multiple runs of the same sample are of the same datatype
                if not all(
                    x[0] == sample_mapping_dict[sample][0][0]
                    for x in sample_mapping_dict[sample]
                ):
                    print_error(
                        "Multiple runs of a sample must be of the same datatype!",
                        "Sample: {}".format(sample),
                    )
                ## VAOFFORD: Removed _T1 suffix to sample name
                for idx,val in enumerate(sample_mapping_dict[sample]):
                    row_to_write = [sample] + val
                    csv_writer.writerow(row_to_write)
    else:
        print_error("No entries to process!", "Samplesheet: {}".format(file_in))


def main(args=None):
    args = parse_args(args)
    check_samplesheet(args.FILE_IN, args.PARAMS_IN, args.FILE_OUT)


if __name__ == "__main__":
    sys.exit(main())
