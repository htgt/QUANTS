// Import generic module functions
include { saveFiles } from './functions'

params.options = [:]

process SAMPLESHEET_CHECK_FASTQ {
    tag "$samplesheet"
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:'pipeline_info', meta:[:], publish_by_meta:[]) }

    container "docker.io/python:3.12.7"

    input:
    path samplesheet
    path extracted_params

    output:
    path '*.csv'

    script: // This script is bundled with the pipeline, in QUANTS/bin/

        """
        check_samplesheet_fastq.py \\
            $samplesheet \\
            $extracted_params \\
            samplesheet.valid.csv
        """
}

process SAMPLESHEET_CHECK_CRAM {
    tag "$samplesheet"
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:'pipeline_info', meta:[:], publish_by_meta:[]) }

    container "docker.io/python:3.12.7"

    input:
    path samplesheet
    path extracted_params

    output:
    path '*.csv'

    script: // This script is bundled with the pipeline, in QUANTS/bin/

        """
        check_samplesheet_cram.py \\
            $samplesheet \\
            $extracted_params \\
            samplesheet.valid.csv
        """
}

process EXTRACT_PARAMS {

    output:
    path "extracted_params.json"

    script:
    def jsonText = groovy.json.JsonOutput.toJson([
                single_end                          : params.single_end,
                input_type                          : params.input_type,
                append_start                        : params.append_start,
                append_end                          : params.append_end,
                oligo_library                       : params.oligo_library,
                adapter_trimming                    : params.adapter_trimming,
                primer_trimming                     : params.primer_trimming,
                read_modification                   : params.read_modification,
                read_transform                      : params.read_transform,
                quantification                      : params.quantification,
            ])

    """
    echo '${jsonText.replace("'", "\\'")}' > extracted_params.json
    """
}
