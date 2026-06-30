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
        "append_start"              : params.get('append_start', '') or False,
        "append_end"                : params.get('append_end', '') or False,
        "read_modification"         : params.get('read_modification', '') or False,
        "adapter_trimming"          : params.get('adapter_trimming', '') or False,
        "primer_trimming"           : params.get('primer_trimming', '') or False,
        "quantification"            : params.get('quantification', '') or False,
        "infer_library_orientations": params.get('infer_library_orientations', '') or False,

    }

    return SimpleNamespace(**params_obj)


def is_valid_sequence(seq):
    """Used to check whether primer and adapter fields contain valid strings"""
    return bool(VALID_BASES_PATTERN.match(str(seq)))


def get_row(row):

    row_obj = {
        "row_identifier"     : row.get('row_identifier', 'N/A'),
        "sample"             : row.get('sample', 'Unknown Sample'),
        "append_start"       : row.get('append_start', 'noCol'),
        "append_end"         : row.get('append_end', 'noCol'),
        "adapter_path"       : row.get('adapter_path', 'noCol'),
        "primer_start"       : row.get('primer_start', 'noCol'),
        "primer_end"         : row.get('primer_end', 'noCol'),
        "oligo_library"      : row.get('oligo_library', 'noCol'),
        "read_transform"     : row.get('read_transform', ''),
        "group_id"           : row.get('group_id', ''),
        "expt_forward_primer": row.get('expt_forward_primer', 'noCol'),
        "expt_reverse_primer": row.get('expt_reverse_primer', 'noCol')
    }

    return SimpleNamespace(**row_obj)


def validate_row(row={}, params={}):
    """
    Validates a single row of the samplesheet and returns any error messages.
    """
    row_errors = []

    if not row:
        print_error("No row found to validate.")
        sys.exit(1)

    # When infer_library_orientations is True:
    # Note this check needs to be at the top given current structure
    if params.infer_library_orientations:

        # Both expt_forward_primer and expt_reverse_primer are needed
        if row.expt_forward_primer == "noCol" or row.expt_reverse_primer == "noCol":
            msg = ("If infer_library_orientations is set globally, the samplesheet must include both the "
                   "expt_forward_primer and expt_reverse_primer columns.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if len(row.expt_forward_primer) == 0:
            msg = "expt_forward_primer should not be empty in the samplesheet."
            row_errors.append(msg)

        if len(row.expt_reverse_primer) == 0:
            msg = "expt_reverse_primer should not be empty in the samplesheet."
            row_errors.append(msg)

        if row.expt_forward_primer and not is_valid_sequence(row.expt_forward_primer):
            msg = "expt_forward_primer is not a valid string."
            row_errors.append(msg)

        if row.expt_reverse_primer and not is_valid_sequence(row.expt_reverse_primer):
            msg = "expt_reverse_primer is not a valid string."
            row_errors.append(msg)

        # oligo_library is needed
        if row.oligo_library == "noCol":
            msg = ("If infer_library_orientations is set globally, the oligo_library "
                   "column must exist in the samplesheet.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if len(row.oligo_library) == 0:
            msg = "If infer_library_orientations is set globally, then oligo_library must be set in the samplesheet."
            row_errors.append(msg)

        # Both append_start and append_end must be empty
        if (row.append_start != "noCol" and not len(row.append_start) == 0):
            msg = ("If infer_library_orientations is set globally to False, the append_start column should not be in "
                   "the samplesheet or be empty.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if (row.append_end != "noCol" and not len(row.append_end) == 0):
            msg = ("If infer_library_orientations is set globally to False, the append_end column should not be in "
                   "the samplesheet or be empty.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        # read_transform must be empty
        if (row.read_transform != "noCol" and not len(row.read_transform) == 0):
            msg = ("If infer_library_orientations is set globally, the read_transform column should not be in the "
                   "samplesheet or be empty.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

    # When read_modification is True (and infer_library_orientations is False)
    if params.read_modification and not params.infer_library_orientations:

        # Check if string is provided in the samplesheet for append_start or append_end.
        if row.append_start == "noCol" and row.append_end == "noCol":
            msg = ("If read_modification is set globally and infer_library_orientations is set to False, the "
                   "samplesheet must include the append_start and/or append_end column")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if row.append_end == "noCol":

            if len(row.append_start) == 0:
                msg = "append_start must be set in the samplesheet."
                row_errors.append(msg)
            elif row.append_start != "noCol" and not is_valid_sequence(row.append_start):
                msg = "append_start must be a valid string in the samplesheet."
                row_errors.append(msg)

        elif row.append_start == "noCol":

            if len(row.append_end) == 0:
                msg = "append_end must be set in the samplesheet."
                row_errors.append(msg)
            elif row.append_end != "noCol" and not is_valid_sequence(row.append_end):
                msg = "append_end must be a valid string in the samplesheet."
                row_errors.append(msg)

        else:
            if (row.append_start and not is_valid_sequence(row.append_start)):
                msg = "Value for append_start must be valid strings in the samplesheet."
                row_errors.append(msg)

            if (row.append_end and not is_valid_sequence(row.append_end)):
                msg = "Value for append_end must be valid strings in the samplesheet."
                row_errors.append(msg)

            # Check if valid not-empty string is provided in the samplesheet for append_start or append_end.
            if len(row.append_start) == 0 and len(row.append_end) == 0:
                msg = "append_start or append_end must be set in the samplesheet."
                row_errors.append(msg)

    # Check if read_modification is False.
    if not params.read_modification:

        # append_start or append_end must not be in the samplesheet.
        if (row.append_start != "noCol" and not len(row.append_start) == 0):
            msg = "If read_modification is set globally to False, append_start column should not be in the samplesheet or be empty."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if (row.append_end != "noCol" and not len(row.append_end) == 0):
            msg = "If read_modification is set globally to False, append_end column should not be in the samplesheet or be empty."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

    # Check if adapter_trimming set and adapter_path is not empty or no column.
    if params.adapter_trimming == "cutadapt":

        if row.adapter_path == "noCol":
            msg = "If adapter_trimming is set globally, then adapter_path column must exist in the samplesheet."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if len(row.adapter_path) == 0:
            msg = "If adapter_trimming is set globally, then valid adapter_path must be set in the samplesheet."
            row_errors.append(msg)

    # Check if adapter_trimming is not set and adapter_path must be empty
    if not params.adapter_trimming and row.adapter_path != "noCol" and not len(row.adapter_path) == 0:
        msg = "If adapter_trimming is not set globally, then adpater_path column must not exist in the samplesheet or be empty."
        print_error(f"ERROR: {msg}")
        sys.exit(1)

    # If primer_trimming set (and infer_library_orientations off), then both primer_start and primer_end must in the
    # samplesheet
    if params.primer_trimming == "cutadapt" and not params.infer_library_orientations:

        if row.primer_start == "noCol" or row.primer_end == "noCol":
            msg = ("If primer_trimming is set globally and infer_library_orientations is globally set to False, the "
                   "samplesheet must include both the primer_start and primer_end columns.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if len(row.primer_start) == 0:
            msg = "primer_start should not be empty in the samplesheet."
            row_errors.append(msg)

        if len(row.primer_end) == 0:
            msg = "primer_end should not be empty in the samplesheet."
            row_errors.append(msg)

        if (row.primer_start and not is_valid_sequence(row.primer_start)):
            msg = "Values for primer_start must be provided as valid strings in the samplesheet."
            row_errors.append(msg)
        if (row.primer_end and not is_valid_sequence(row.primer_end)):
            msg = "Values for primer_end must be provided as valid strings in the samplesheet."
            row_errors.append(msg)

    # Check if primer_trimming is not set, then both primer_start and primer_end must not be in the samplesheet.
    if not params.primer_trimming:

        if row.primer_start != "noCol" and not len(row.primer_start) == 0:
            msg = "If primer_trimming is not set globally, then primer_start column must not exist in the samplesheet or be empty."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if row.primer_end != "noCol" and not len(row.primer_end) == 0:
            msg = "If primer_trimming is not set globally, then primer_end column must not exist in the samplesheet or be empty."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

    # Check if quantification is set, then oligo_library must be in the samplesheet.
    if params.quantification == 'pyquest':

        if row.oligo_library == "noCol":
            msg = "If quantification is set globally, then oligo_library column must exist in the samplesheet."
            print_error(f"ERROR: {msg}")
            sys.exit(1)

        if len(row.oligo_library) == 0:
            msg = "If quantification is set globally, then oligo_library must be set in the samplesheet."
            row_errors.append(msg)

    # Check if quantification is not set, then oligo_library must not be in the samplesheet.
    if not params.quantification and not params.infer_library_orientations:

        if row.oligo_library != "noCol" and not len(row.oligo_library) == 0:
            msg = ("If quantification and infer_library_orientations are globally set to False, then the oligo_library "
                   "column must not exist in the samplesheet or be empty.")
            print_error(f"ERROR: {msg}")
            sys.exit(1)

    # Check if read_transform is set in the samplesheet with valid value.
    read_transformation_options = ['reverse', 'complement', 'reverse_complement']
    if row.read_transform:

        if row.read_transform not in read_transformation_options and row.read_transform:
            msg = f"If read_transform is set, options must be one of: {', '.join(read_transformation_options)}."
            row_errors.append(msg)

    if row.group_id and not row.group_id.isalnum():
        msg = "group_id must be alphanumeric!"
        row_errors.append(msg)

    if row_errors:
        return ([f"Row {row.row_identifier} : Sample-{row.sample} : {err}" for err in row_errors])

    return row_errors


def display_validation_report(all_validation_errors):

    for error_msg in all_validation_errors:
        if error_msg:
            print_error(f"ERROR: {error_msg}")

    sys.exit(1)
