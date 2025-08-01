import re
import sys
from types import SimpleNamespace


COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"


VALID_BASES_PATTERN = re.compile(r"^[ATCG]+$", re.IGNORECASE)


def print_error(message):
    print(f"{COLOR_RED}{message}{COLOR_RESET}", file=sys.stderr)


def print_info(message):
    print(f"{COLOR_YELLOW}{message}{COLOR_RESET}")


def print_success(message):
    print(f"{COLOR_GREEN}{message}{COLOR_RESET}")


def get_params(params):

    params_obj = {
        "append_start": params.get('append_start', '') or False,
        "append_end": params.get('append_end', '') or False,
        "read_modification": params.get('read_modification', '') or False,
        "adapter_trimming": params.get('adapter_trimming', '') or False,
        "primer_trimming": params.get('primer_trimming', '') or False,
    }

    return SimpleNamespace(**params_obj)


def get_row(row):

    row_obj = {
        "row_identifier":  row.get('row_identifier', 'N/A'),
        "sample": row.get('sample', 'Unknown Sample'),
        "append_start": row.get('append_start', '') or False,
        "append_end": row.get('append_end', '') or False,
        "adapter_path": row.get('adapter_path', '') or False,
        "primer_start": row.get('primer_start', '') or False,
        "primer_end": row.get('primer_end', '') or False
    }

    return SimpleNamespace(**row_obj)


def validate_row(row={}, params={}, errors=[]):
    """
    Validates a single row of the samplesheet and appends any error messages to the errors list.
    """
    row_errors = [] 

    if not row:
        print_error("No row found to validate.")
        sys.exit(1)

    # When read_modification is True
    if params.read_modification:

        # Check if string is provided in the samplesheet for append_start or append_end.
        if not row.append_start and not row.append_end:
            msg = "If read_modification is set, a string must be provided for either append_start or append_end."
            row_errors.append(msg)

        # Check if append_start and append_end must be a non-empty valid string.
        match_append = lambda seq: seq if not bool(VALID_BASES_PATTERN.match(str(seq))) else ''

        if match_append(row.append_start) or match_append(row.append_end):
            msg = "If read_modification is set to True, values for append_start and append_end must be valid strings."
            row_errors.append(msg)

    # Check if read_modification is False.
    if not params.read_modification:
        # append_start or append_end must not be in the samplesheet.
        if row.append_start or row.append_end:
            msg = "If read_modification is set to False, then append_start or append_end should not be in the samplesheet"
            row_errors.append(msg)


    # Check if adapter_trimming set and adapter_path is not empty
    if params.adapter_trimming == "cutadapt" and not row.adapter_path:
        msg = "If adapter_trimming is set globally, then adapter_path must be set in the samplesheet."
        row_errors.append(msg)

    # Check if adapter_trimming set and adapter_path is not empty
    if not params.adapter_trimming and row.adapter_path:
        msg = "If adapter_trimming is not set globally, then adpater_path must be kept empty."
        row_errors.append(msg)
    
    # Check if primer_trimming set, then both primer_start and primer_end must in the samplesheet
    if params.primer_trimming == "cutadapt":
        if not (row.primer_start and row.primer_end):
            msg = "If primer_trimming is set globally, then both primer_start and primer_end must be in the samplesheet."
            row_errors.append(msg)
        
        # Check if primer_start and primer_end must be a non-empty valid string.
        match_primer = lambda seq: seq if not bool(VALID_BASES_PATTERN.match(str(seq))) else ''

        if match_primer(row.primer_start) or match_primer(row.primer_end):
            msg = "Values for primer_start and primer_end must be valid strings."
            row_errors.append(msg)
    
    # Check if primer_trimming is not set, then both primer_start and primer_end must not be in the samplehseet.
    if not params.primer_trimming:
        if row.primer_start or row.primer_end:
            msg = "If primer_trimming is not set globally, then both primer_start and primer_end must be kept empty."
            row_errors.append(msg)
    

    if row_errors:
        errors.extend([f"Row{row.row_identifier} : Sample-{row.sample} : {err}" for err in row_errors])
        return False


def validate_all_samples(samplesheet_data, params):
    """
    Processes all rows in the samplesheet, collecting all validation errors.
    """
    all_validation_errors = []

    processed_params = get_params(params)

    for i, row in enumerate(samplesheet_data, start=1):
        
        from check_samplesheet_fastq import validate_headers
        
        validate_headers(
                            row_headers = list(row.keys()), 
                            processed_params = processed_params, 
                            is_params = True
                        )

        if 'row_identifier' not in row:
            row['row_identifier'] = i
        
        processed_row = get_row(row)
        valid_row = validate_row(processed_row, processed_params, all_validation_errors)

    if not valid_row and all_validation_errors:
        display_validation_report(all_validation_errors)
    else:
        print_success("\nSamplesheet validated successfully!.")
        return True 


def display_validation_report(all_validation_errors):

    for error_msg in all_validation_errors:
        print_error(f"ERROR: {error_msg}")

    sys.exit(1) 
