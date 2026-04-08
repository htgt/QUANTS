process SEQTK_SAMPLE {
    tag "$meta.id"
    label 'process_single_seqtk'

    container "quay.io/biocontainers/seqtk:1.4--he4a0461_1"

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*.fq.gz")   , emit: reads
    path "versions.yml"                , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def prefix = task.ext.prefix ?: "${meta.id}"
    def sample_size = params.downsampling_size
    def seed = params.downsampling_seed
    def single_end = meta.single_end.toString().toBoolean()
    def read_files = reads instanceof List ? reads : [reads]
    if ( !sample_size ) {
        error "SEQTK/SAMPLE must have a sample_size value included"
    }
    if (!single_end && read_files.size() != 2) {
        error "SEQTK/SAMPLE expected exactly 2 input FASTQs for paired-end data"
    }
    def commands = read_files.withIndex().collect { read, idx ->
        def suffix = single_end ? '' : "_${idx + 1}"
        """\
        seqtk \\
            sample \\
            -s$seed \\
            "$read" \\
            $sample_size \\
            | gzip --no-name > ${prefix}_downsampled${suffix}.fq.gz
        """.stripIndent().trim()
    }.join('\n\n')
    """
    ${commands}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        seqtk: \$(echo \$(seqtk 2>&1) | sed 's/^.*Version: //; s/ .*\$//')
    END_VERSIONS
    """

    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    def single_end = meta.single_end.toString().toBoolean()
    def stub_outputs = single_end ? ["${prefix}_downsampled.fq.gz"] : ["${prefix}_downsampled_1.fq.gz", "${prefix}_downsampled_2.fq.gz"]
    def stub_commands = stub_outputs.collect { output_file -> "echo \"\" | gzip > ${output_file}" }.join('\n')

    """
    ${stub_commands}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        seqtk: \$(echo \$(seqtk 2>&1) | sed 's/^.*Version: //; s/ .*\$//')
    END_VERSIONS
    """

}
