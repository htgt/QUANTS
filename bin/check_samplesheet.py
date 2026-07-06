#!/usr/bin/env python

import copy
import json
import os
import csv
import sys
import errno
import argparse

from validate_samplesheet_rows import get_params, get_row, validate_row, display_validation_report

REQUIRED_HEADERS = ["sample"]
OPTIONAL_HEADERS = [
        "group_id",
        "oligo_library",
        "adapter_path",
        "primer_start",
        "primer_end",
        "append_start",
        "append_end",
        "read_transform",
        "expt_forward_primer",
        "expt_reverse_primer"
  ]
MIN_NUMBER_OF_POPULATED_COLS = 2
VALID_FILE_EXTENSIONS = {
        "fastq": (".fastq.gz", ".fq.gz"),
        "cram": (".cram",)
    }

def parse_args(args=None):
    Description = "Reformat QUANTS samplesheet file and check its contents."
    Epilog = "Example usage: python check_samplesheet.py <FILE_IN> <PARAMS_IN> <FILE_OUT>"

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


def validate_headers(fieldnames: list = [],
                     file_type: str = "",
                     row_headers: list = [],
                     is_params: bool = False) -> list:
    if file_type == "fastq":
        REQUIRED_HEADERS.extend(["fastq_1", "fastq_2"])
    elif file_type == "cram":
        REQUIRED_HEADERS.extend(["cram_path"])

    if is_params:
        if not row_headers:
            print("No row to validate headers.")
            sys.exit(1)

        headers_to_check = REQUIRED_HEADERS + OPTIONAL_HEADERS

        invalid_headers = [header for header in row_headers if header and header not in headers_to_check]

        if invalid_headers:
            if not [unnamed_col for unnamed_col in invalid_headers if "unnamed_col" in unnamed_col]:
                raise ValueError(f"ERROR: Check for invalid headers in the samplesheet: {', '.join(invalid_headers)}")
            raise ValueError(f"ERROR: Check in the samplesheet if there are any extra commas before or after headers. For example: sample,,fastq_1,fastq_2,")

    else:
        if not fieldnames:
            raise ValueError("ERROR: samplesheet file doesn't contain any fields.")

        # Check required headers
        missing_required = [col for col in REQUIRED_HEADERS if col not in fieldnames]
        if missing_required:
            raise ValueError(f"ERROR: samplesheet missing required headers: {', '.join(missing_required)}")

        # Check if all optional headers are present
        all_headers = REQUIRED_HEADERS + OPTIONAL_HEADERS
        missing_optional = [col for col in OPTIONAL_HEADERS if col not in fieldnames]
        if missing_optional:
            print(f"WARNING: samplesheet missing optional headers: {', '.join(missing_optional)}")

        valid_headers = [header for header in all_headers if header not in missing_optional]

        return valid_headers


def check_sequencing_fields(input_type: str,
                            line: dict,
                            single_end: bool) -> None:
    """
    Validate sequencing input fields and file paths.
    """

    files_to_check = []

    # Check file path presence
    if input_type == "fastq":
        fastq_1 = line.get("fastq_1")
        fastq_2 = line.get("fastq_2")

        if not fastq_1:
            print_error("fastq_1 file path missing!",
                        "Line",
                        ",".join(str(v) if v is not None else "" for v in line.values()))

        files_to_check.append(fastq_1)

        if single_end:
            if fastq_2:
                print_error("fastq_2 provided but single_end is set globally to True!",
                             "Line",
                             ",".join(str(v) if v is not None else "" for v in line.values()))

        else:
            if not fastq_2:
                print_error("fastq_2 file path missing but single_end is set globally to False!",
                            "Line",
                            ",".join(str(v) if v is not None else "" for v in line.values()))

            files_to_check.append(fastq_2)

    elif input_type == "cram":
        cram_path = line.get("cram_path")

        if not cram_path:
            print_error("cram_path file path missing!",
                        "Line",
                        ",".join(str(v) if v is not None else "" for v in line.values()))

        files_to_check.append(cram_path)

    # Check file path contains no spaces and right extension
    valid_extensions = VALID_FILE_EXTENSIONS.get(input_type)

    for file in files_to_check:
        if " " in file:
            print_error(f"{input_type.upper()} file path contains spaces!",
                        "Line",
                        ",".join(str(v) if v is not None else "" for v in line.values()))

        if not file.endswith(valid_extensions):
            print_error(f"{input_type.upper()} file extension can only be {' or '.join(valid_extensions)}!",
                        "Line",
                        ",".join(str(v) if v is not None else "" for v in line.values()))


def validate_all_samples(samplesheet_data: list[dict],
                         params: dict,
                         file_type: str):
    """
    Processes all rows in the samplesheet, collecting all validation warnings and errors.
    """

    all_validation_warnings = []
    all_validation_errors = []

    processed_params = get_params(params)

    for i, row in enumerate(samplesheet_data, start=2):

        # checks for additional columns or extra commas
        validate_headers(row_headers = list(row.keys()),
                         file_type = file_type,
                          is_params = True)

        if 'row_identifier' not in row:
            row['row_identifier'] = i

        processed_row = get_row(row)
        row_warnings, row_errors = validate_row(processed_row, processed_params)

        all_validation_warnings.extend(row_warnings)
        all_validation_errors.extend(row_errors)

    if any(all_validation_warnings) or any(all_validation_errors):
        display_validation_report(all_validation_warnings,
                                  all_validation_errors)


def check_samplesheet(file_in, params_in, file_out):
    """
    This function checks that the samplesheet follows the following structure (with FASTQ as file type):
    sample,fastq_1,fastq_2,group_id,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform
    SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,SAMPLE_PE_RUN1_2.fastq.gz,AAAA,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_PE,SAMPLE_PE_RUN2_1.fastq.gz,SAMPLE_PE_RUN2_2.fastq.gz,AAAA,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,,BBBB,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,
    Or, alternatively (with CRAM as file type):
    sample,cram_path,group_id,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform
    SAMPLE_PE,SAMPLE_PE_RUN1_1.cram,AAAA,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_PE,SAMPLE_PE_RUN2_1.cram,AAAA,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement
    SAMPLE_SE,SAMPLE_SE_RUN1_1.cram,BBBB,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,
    """

    with open(params_in) as f:
        params = json.load(f)

    sample_mapping_dict = {}

    with open(file_in, "r") as f_in:
        f_reads = csv.DictReader(f_in)

        # Check headers
        f_reads.fieldnames = [
                    name if name.strip() else f"unnamed_col_{i}"
                    for i, name in enumerate(f_reads.fieldnames, start=1)
                ]

        headers = [header.strip() for header in f_reads.fieldnames if header]

        valid_headers = validate_headers(fieldnames = headers, file_type = params['input_type'])

        # For dealing with printed message if header row contains fewer columns than the other rows
        flatten_row = lambda values: (
                str(x)
                for v in values
                for x in (v if isinstance(v, list) else [v])
                if x is not None
            )

        group_id = []

        header_len = len(headers)

        f_reads_ln = list(f_reads)

        # Check sample entries
        for line in f_reads_ln:
            line_len = len([v for v in line.values() if v is not None])

            # check if number of headers matches number of row values
            if header_len != line_len:
                print_error(
                    f"Inconsistent number of columns: The header row has {header_len} columns, but a data row has {line_len} columns.",
                    "Line",
                    ",".join(flatten_row(line.values())),
                )

            # Check number of populated columns
            lspl = [val for val in line.values() if val and val.strip()]

            num_cols = len([x for x in lspl if x])

            if num_cols < MIN_NUMBER_OF_POPULATED_COLS:
                print_error(
                    "Invalid number of populated columns (minimum = {})!".format(
                        MIN_NUMBER_OF_POPULATED_COLS
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

            # Get group_id for later check
            group_id += [line.get("group_id")]

            # Check file extension
            single_end = int(params['single_end'])
            check_sequencing_fields(input_type = params['input_type'],
                                    line = line,
                                    single_end = single_end)

            # Get sample info
            # Get rest of the info from file read line and skip sample to avoid duplication in the file out.
            # Example: [fastq_1,fastq_2,oligo_library,adapter_path,LibAmpF,LibAmpR,read_transform]
            sample_info = []
            rest_info = [line.get(h) for h in valid_headers if h != "sample"]
            sample_info = [single_end, *rest_info]

            # Create sample mapping dictionary = { sample: [ single_end, fastq_1, fastq_2 ] } or { sample: [ single_end, cram_path ] }
            if sample not in sample_mapping_dict:
                sample_mapping_dict[sample] = [sample_info]
            else:
                if sample_info in sample_mapping_dict[sample]:
                    print_error("Samplesheet contains duplicate rows!",
                                "Line",
                                ",".join(str(v) if v is not None else "" for v in line.values()))
                else:
                    sample_mapping_dict[sample].append(sample_info)

        # Check each sample row in relation to global params
        validating_samples = copy.deepcopy(f_reads_ln)
        validate_all_samples(samplesheet_data = validating_samples,
                             params = params,
                             file_type = params['input_type'])

    # Check group_id column
    if not any(group_id):
        print(f"WARNING: Samplesheet group_id column not found or entirely empty. Results will not be grouped in the output directory")
    elif not all(group_id):
        raise ValueError(f"ERROR: Please ensure that all samples have values for group_id in the samplesheet, or remove the group_id column")

    # Write validated samplesheet with appropriate columns
    if len(sample_mapping_dict) > 0:
        out_dir = os.path.dirname(file_out)
        make_dir(out_dir)
        with open(file_out, "w") as f_out:
            csv_writer = csv.writer(f_out)

            # Add column "single_end" in output csv file headers
            valid_headers.insert(1, "single_end")
            csv_writer.writerow(valid_headers)

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
