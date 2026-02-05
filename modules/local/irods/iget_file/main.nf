// NOTE: params.irods_iget_cmd is intended for testing only (nf-test).
// In production, leave unset to use the real `iget`.

process IRODS_IGET_FILE {
    tag "$meta.id"
    label 'process_low'

    input:
        tuple val(meta), val(irods_path)

    output:
        tuple val(meta), path("${file(irods_path).getName()}")         , emit: file
        tuple val(meta), path("${file(irods_path).getName()}.md5")     , emit: md5
        path "versions.yml"                                            , emit: versions

    when:
        task.ext.when == null || task.ext.when

    script:
        def iget_cmd = params.irods_iget_cmd ?: 'iget'
        def local_filename = file(irods_path).getName()

        """
        set -euo pipefail

        command -v ${iget_cmd} >/dev/null 2>&1 || { echo "ERROR: ${iget_cmd} not found (iRODS iCommands required)"; exit 127; }

        echo "IRODS path: ${irods_path}"
        echo "Downloading to: ${local_filename}"

        ${iget_cmd} -K -f -v "${irods_path}" "${local_filename}"
        md5sum "${local_filename}" > "${local_filename}.md5"

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            iget: "unknown"
        END_VERSIONS
        """
}
