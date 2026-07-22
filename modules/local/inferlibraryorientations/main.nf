process INFERLIBRARYORIENTATIONS {
    tag "$meta.id"
    label 'process_single'

    container "${workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container
        ? 'https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/22/22bee7342faf242ec00cc4b07316a2205d87476961be9d1dba5950db7985e572/data'
        : 'community.wave.seqera.io/library/pip_bio:9e823e800c83a47a'}"


    input:
    tuple val(meta), path(valiant_meta), path(fastq_1)

    output:
    tuple val(meta), path("${meta.id}_library_orientations.tsv"), emit: library_orientations
    tuple( 
        val("${task.process}"),
        val('infer_library_orientations/infer_library_orientations.py'),
        eval("""
            python3 ${projectDir}/bin/infer_library_orientations/infer_library_orientations.py \
             --version | sed 's/infer_library_orientations.py //'
        """),
        emit: versions_infer_library_orientations,
        topic: versions
    )

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"

    """
    python3 ${projectDir}/bin/infer_library_orientations/infer_library_orientations.py \
      --name ${meta.id} \
      --expt_forward_primer ${meta.expt_forward_primer} \
      --expt_reverse_primer ${meta.expt_reverse_primer} \
      --valiant_meta ${valiant_meta} \
      --fastq_1 ${fastq_1} \
      --output ${prefix}_library_orientations.tsv
    """

    stub:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"

    """
    touch ${prefix}_library_orientations.tsv
    """
}

