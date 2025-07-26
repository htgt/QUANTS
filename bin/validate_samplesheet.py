import sys


def print_warning(msg):
    context  = f"WARNING: {msg}"
    print(context)

def print_info(info):
    context  = f"INFO: {info}"
    print(context)



def validate_samplesheet(row, params):
    
    
    if params["read_modification"]:
        # append_start and append_end is set for all values in samplesheet and append_start and append_end must not be set in params
        if (row["append_start"] and row["append_end"] and params["append_start"] and params["append_end"]):
            print_info("append_start and append_end is set globally")
            sys.exit(1)
    
    if not params["read_modification"] and row["append_start"] and row["append_start"]:
        print_warning("read_modification is not set globally, but append_start and append_end set in samplesheet")
        sys.exit(1)
