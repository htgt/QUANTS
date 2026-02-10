include { local_file_name } from './functions'

// NOTE: params.irods_iget_cmd is intended for testing only (nf-test).
// In production, leave unset to use the real `iget`.

process IRODS_IGET_FILE {
    tag "$meta.id"
    label 'process_low'

    input:
        tuple val(meta), val(irods_path)

    output:
        tuple val(meta), path("${local_file_name(irods_path)}")        , emit: file
        tuple val(meta), path("${local_file_name(irods_path)}.md5")    , emit: md5
        path "versions.yml"                                         , emit: versions

    when:
        task.ext.when == null || task.ext.when

    script:
        def local_filename  = local_file_name(irods_path)

        """
        set -euo pipefail

        command -v iget >/dev/null 2>&1 || { echo "ERROR: iget not found (iRODS iCommands required)"; }

        echo "IRODS path: ${irods_path}"
        echo "Downloading to: ${local_filename}"

        iget -K -f -v "${irods_path}" "${local_filename}"
        md5sum "${local_filename}" > "${local_filename}.md5"

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            irods_client: \$(iget -h 2>&1 | grep "Version" | awk '{print \$3}')
        END_VERSIONS
        """
}
