import sys
from types import SimpleNamespace

COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"


def print_error(message):
    print(f"{COLOR_RED}{message}{COLOR_RESET}", file=sys.stderr)
    sys.exit(1)


def print_warning(message):
    print(f"{COLOR_YELLOW}{message}{COLOR_RESET}")


def print_success(message):
    print(f"{COLOR_GREEN}{message}{COLOR_RESET}")


def get_row_truth_table(row):
    
    truth_table = {
        "row_identifier":  row.get('row_identifier', 'N/A'),
        "sample": row.get('sample', 'Unknown Sample'),
        "append_start": row.get('append_start', '') or False,
        "append_end": row.get('append_end', '') or False
    }
    
    return SimpleNamespace(**truth_table)


def get_params_truth_table(params):

    truth_table = {
        "append_start": params.get('append_start', '') or False,
        "append_end": params.get('append_end', '') or False,
        "read_modification": params.get('read_modification', '') or False
    }
    
    return SimpleNamespace(**truth_table)


def validate_params(params={}, errors=[]):
    """
    Validates global parameters and appends any error messages to the errors list.
    """
    params_error = []

    if params:
        if params.append_start or params.append_end:
            sub_str = 'append_start can no longer be set globally, it should be set in the samplesheet.' if params.append_start else (
                      'append_end can no longer be set globally, it should be set in the samplesheet.' if params.append_end else "")
            params_error.append(sub_str)
        
    
    if params_error:
        errors.extend([f"{err} " for err in params_error])
        return False 

    return True 


def validate_row(row={}, params={}, errors=[]):
    """
    Validates a single row of the samplesheet and appends any error messages to the errors list.
    """
    row_errors = [] 
        
    if row:
        if params.read_modification and (not row.append_start or not row.append_end):
                # TODO: Check append_start and append_end logic
                sub_str = 'append_start must be set if append_end is set in the samplesheet.' if not row.append_start else (
                            'append_end must be set if append_start is set in the samplesheet.' if not row.append_end else "")
                    
                str = f"If read_modification is set to True, {sub_str}"
                row_errors.append(str)

        if not params.read_modification and (row.append_start or row.append_end):
                str = f"If read_modification is set to False, then append_start and append_end should not be in the samplesheet"
                row_errors.append(str)
        
        if params.read_modification and (type(row.append_start) == 'str' or type(row.append_end) == 'str'):
                str = f"If read_modification is set to True, {'append_start' if not row.append_start else 'append_end'} must be set of valid values."
                row_errors.append(str)

    if row_errors:
        errors.extend([f"Row{row.row_identifier} : Sample-{row.sample} : {err}" for err in row_errors])
        return False 

    return True 


def validate_all_samples(samplesheet_data, params):
    """
    Processes all rows in the samplesheet, collecting all validation errors.
    """
    all_validation_errors = []
    has_critical_errors = False
    
    processed_params = get_params_truth_table(params)
    
    valid_params = validate_params(processed_params, all_validation_errors)
    
    if not valid_params:
        display_report(all_validation_errors)

    for i, row in enumerate(samplesheet_data, start=1):
        
        if 'row_identifier' not in row:
            row['row_identifier'] = i
        
        processed_row = get_row_truth_table(row)
        valid_rows = validate_row(processed_row, processed_params, all_validation_errors)

    if not valid_rows:
        display_report(all_validation_errors)
    else:
        print_success("\nSamplesheet validated successfully!.")
        return True 


def display_report(all_validation_errors):
    if all_validation_errors:
        for error_msg in all_validation_errors:
            print_warning(f"WARNING: {error_msg}")
            print_warning("\nWarnings were found. Please review them, as changes will be required to proceed successfully.")
        
        sys.exit(1) 
