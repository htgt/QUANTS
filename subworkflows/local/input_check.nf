//
// Check input samplesheet and get read channels
//

// TODO: look into better ways for handling CRAM vs FASTQ input types
// For now, reads can also mean CRAM depending on input_type

params.options = [:]

include { SAMPLESHEET_CHECK_FASTQ; SAMPLESHEET_CHECK_CRAM } from '../../modules/local/samplesheet_check' addParams( options: params.options )

workflow INPUT_CHECK_FASTQ {
    take:
    samplesheet // file: /path/to/samplesheet.csv

    main:
    //TODO: look into doing this as a single step rather than duplicating check loop

    // process to extract necessary parameters for samplesheet validation from global params
    extracted_params = EXTRACT_PARAMS()

    SAMPLESHEET_CHECK_FASTQ ( samplesheet, extracted_params )
        .splitCsv ( header:true, sep:',' )
        .map { create_fastq_channels(it) }
        .set { reads }
    emit:
        reads // channel: [ val(meta), [ reads ] ]
}

process EXTRACT_PARAMS {

    output:
    path "extracted_params.json"

    script:
    def jsonText = groovy.json.JsonOutput.toJson([
                single_end                          : params.single_end,
                adapter_cutadapt_options            : params.adapter_cutadapt_options,
                primer_cutadapt_options             : params.primer_cutadapt_options,
                append_start                        : params.append_start,
                append_end                          : params.append_end,
                oligo_library                       : params.oligo_library,
                input_type                          : params.input_type,
                raw_sequencing_qc                   : params.raw_sequencing_qc,
                adapter_trimming                    : params.adapter_trimming,
                adapter_trimming_qc                 : params.adapter_trimming_qc,
                primer_trimming                     : params.primer_trimming,
                primer_trimming_qc                  : params.primer_trimming_qc,
                read_modification                   : params.read_modification,
                append_quality                      : params.append_quality,
                transform_library                   : params.transform_library,
                read_transform                      : params.read_transform,
                quantification                      : params.quantification,
                pyquest_library_converter_options   : params.pyquest_library_converter_options
            ])

    """
    echo '${jsonText.replace("'", "\\'")}' > extracted_params.json
    """
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
    meta.append_start              = row.append_start
    meta.append_end                = row.append_end
    meta.oligo_library             = row.oligo_library
    
    def array = []
    if (!file(row.fastq_1).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> Read 1 FastQ file does not exist!\n${row.fastq_1}"
    }
    if (meta.single_end) {
        array = [ meta, [ file(row.fastq_1) ] ]
    } else {
        if (!file(row.fastq_2).exists()) {
            exit 1, "ERROR: Please check input samplesheet -> Read 2 FastQ file does not exist!\n${row.fastq_2}"
        }
        array = [ meta, [ file(row.fastq_1), file(row.fastq_2) ] ]
    }
    return array
}

workflow INPUT_CHECK_CRAM {
    take:
    samplesheet // file: /path/to/samplesheet.csv

    main:
    //TODO: look into doing this as a single step rather than duplicating check loop
    SAMPLESHEET_CHECK_CRAM ( samplesheet )
        .splitCsv ( header:true, sep:',' )
        .map { create_cram_channels(it) }
        .set { crams }
    emit:
        crams // channel: [ val(meta), [ cram_file ] ]
}

// Function to get list of [ meta, [ cram_file ] ]
def create_cram_channels(LinkedHashMap row) {
    def meta = [:]
    meta.id           = row.sample
    meta.single_end   = row.single_end.toBoolean()

    def array = []
    if (!file(row.cram_file).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> CRAM file does not exist!\n${row.cram_file}"
    }
    array = [ meta, [ file(row.cram_file) ] ]
    return array
}
