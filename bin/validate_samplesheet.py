import sys


COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"


def print_error(message):
    print(f"{COLOR_RED} {message}{COLOR_RESET}", file=sys.stderr)
    sys.exit(1)


def print_warning(message):
    print(f"{COLOR_YELLOW} {message}{COLOR_RESET}")


def validate_row(row, params, errors):
    """
    Validates a single row of the samplesheet and appends any error messages to the errors list.
    """
    row_errors = [] 

    if params["read_modification"]:
        if row.get("append_start") and row["append_end"] and params["append_start"] and params["append_end"]:
            row_errors.append("'append_start' and 'append_end' are set both globally (in params) and in the samplesheet for this row. They should not be set in both places.")

    if not params["read_modification"] and row["append_start"] and row["append_end"]:
        row_errors.append("'read_modification' is not enabled globally, but 'append_start' and 'append_end' are set in the samplesheet for this row. These settings will likely be ignored.")
    
    
    if params["quantification"] == "pyquest" and params["oligo_library"] and row["oligo_library"]:
        row_errors.append("When 'quantification' is enabled globally, 'oligo_library' should not be set globally and in samplesheet simultaneously.")
        
    if params["transform_library"] and not params["quantification"]:
        row_errors.append("If transform_library is set to true, quantification must also be set to true.")
    
    if row_errors:
        errors.extend([f"Row {row.get('row_identifier', 'N/A')} : Sample {row["sample"]}: {err}" for err in row_errors])
        return False 
    return True 


def validate_all_samples(samplesheet_data, params):
    """
    Processes all rows in the samplesheet, collecting all validation errors.
    """
    all_validation_errors = []
    has_critical_errors = False

    for i, row in enumerate(samplesheet_data, start=1):
        
        if 'row_identifier' not in row:
            row['row_identifier'] = i

        row_valid = validate_row(row, params, all_validation_errors)
        if not row_valid and "Error:" in "".join(all_validation_errors[-1:]):
             has_critical_errors = True

    if all_validation_errors:
        print_warning("\n--- Samplesheet Validation Report ---")
        for error_msg in all_validation_errors:
            if "Error:" in error_msg:
                print_error(f"ERROR: {error_msg}")
            else:
                print_warning(f"WARNING: {error_msg}")
        
        if has_critical_errors:
            print_error("\nCritical errors were found. Please correct them before proceeding.")
            sys.exit(1) 
        else:
            print_warning("\nWarnings were found. Please review them.")
            print_warning("-------------------------------------")
            sys.exit(1) 
    else:
        print_warning("\nSamplesheet validated successfully!.")
        return True 
