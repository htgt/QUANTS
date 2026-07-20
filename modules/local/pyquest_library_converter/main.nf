// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

options        = initOptions(params.modules.pyquest_library_converter ?: [:])

process TRANSFORM_LIBRARY_FOR_PYQUEST {
    label 'process_medium'

    // TODO: Review using getSoftwareName(task.process) instead of 'pyquest'
    //      in saveAs for consistency with other modules.
    //      getSoftwareName(task.process) currently returns 'transform'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename ->
                    saveFiles(
                        filename:filename,
                        options:options,
                        publish_dir: meta.group_id ? "${meta.group_id}/pyquest"
                                                   : "pyquest",
                        meta:meta,
                        publish_by_meta:['id']
                    ) 
                }

    conda params.enable_conda ? 'conda-forge::python=3.12.7' : ''
    container "docker.io/python:3.12.7"

    input:
        tuple val(meta), path(oligo_library)

    output:
        tuple val(meta), path("*.pyquest.tsv"), emit: oligo_library

    script:
        def software = getSoftwareName(task.process)
        def input    = oligo_library
        // File currently being re-processed/overwritten in publish_dir if already present
        def output   = input.getName().split("\\.")[0] + '.pyquest.tsv'

    """
    ${projectDir}/bin/pyquest_library_converter/pyquest_library_converter.py \\
        $input \\
        $output \\
        $options.args
    """
}
