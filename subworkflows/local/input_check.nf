//
// Check input samplesheet and get read channels
//

// TODO: look into better ways for handling CRAM vs FASTQ input types
// For now, reads can also mean CRAM depending on input_type

include { SAMPLESHEET_CHECK; EXTRACT_PARAMS } from '../../modules/local/samplesheet_check'

workflow INPUT_CHECK {
    take:
        samplesheet // file: /path/to/samplesheet.csv

    main:
        // process to extract necessary parameters for samplesheet validation from global params
        extracted_params = EXTRACT_PARAMS()

        if (params.input_type == "fastq") {
            fastq_ch = INPUT_CHECK_FASTQ(samplesheet, extracted_params)
            seq_data = fastq_ch.reads
        }
        else if (params.input_type == "cram") {
            cram_ch = INPUT_CHECK_CRAM(samplesheet, extracted_params)
            seq_data = cram_ch.crams
    }

    emit:
        seq_data
}

workflow INPUT_CHECK_FASTQ {
    take:
    samplesheet // file: /path/to/samplesheet.csv
    extracted_params

    main:
    //TODO: look into doing this as a single step rather than duplicating check loop
    SAMPLESHEET_CHECK ( samplesheet, extracted_params )
        .splitCsv ( header:true, sep:',' )
        .map { create_fastq_channels(it) }
        .set { reads }

    emit:
        reads // channel: [ val(meta), [ reads ] ]
}

// Function to get list of [ meta, [ fastq_1, fastq_2 ] ]
def create_fastq_channels(LinkedHashMap row) {
    def meta = [:]
    meta.id                        = row.sample
    meta.single_end                = row.single_end.toBoolean()
    meta.group_id                  = row.group_id
    meta.read_transform            = row.read_transform
    meta.adapter_path              = row.adapter_path
    meta.primer_start              = row.primer_start
    meta.primer_end                = row.primer_end
    meta.expt_forward_primer       = row.expt_forward_primer
    meta.expt_reverse_primer       = row.expt_reverse_primer
    meta.append_start              = row.append_start
    meta.append_end                = row.append_end
    meta.oligo_library             = row.oligo_library

    def array = []
    if (!file(row.fastq_1).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> Read 1 FASTQ file does not exist!\n${row.fastq_1}"
    }
    if (meta.single_end) {
        array = [ meta, [ file(row.fastq_1) ] ]
    } else {
        if (!file(row.fastq_2).exists()) {
            exit 1, "ERROR: Please check input samplesheet -> Read 2 FASTQ file does not exist!\n${row.fastq_2}"
        }
        array = [ meta, [ file(row.fastq_1), file(row.fastq_2) ] ]
    }
    return array
}

workflow INPUT_CHECK_CRAM {
    take:
    samplesheet // file: /path/to/samplesheet.csv
    extracted_params

    main:
    //TODO: look into doing this as a single step rather than duplicating check loop
    SAMPLESHEET_CHECK ( samplesheet, extracted_params )
        .splitCsv ( header:true, sep:',' )
        .map { create_cram_channels(it) }
        .set { crams }

    emit:
        crams // channel: [ val(meta), [ cram_path ] ]
}

// Function to get list of [ meta, [ cram_path ] ]
def create_cram_channels(LinkedHashMap row) {
    def meta = [:]
    meta.id                        = row.sample
    meta.single_end                = row.single_end.toBoolean()
    meta.group_id                  = row.group_id
    meta.read_transform            = row.read_transform
    meta.adapter_path              = row.adapter_path
    meta.primer_start              = row.primer_start
    meta.primer_end                = row.primer_end
    meta.expt_forward_primer       = row.expt_forward_primer
    meta.expt_reverse_primer       = row.expt_reverse_primer
    meta.append_start              = row.append_start
    meta.append_end                = row.append_end
    meta.oligo_library             = row.oligo_library

    def array = []
    if (!file(row.cram_path).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> CRAM file does not exist!\n${row.cram_path}"
    }
    array = [ meta, [ file(row.cram_path) ] ]
    return array
}
