nextflow.enable.dsl=2

include { IRODS_IGET_FILE } from './modules/local/irods/iget_file/main'

workflow {
    Channel.of( [ [id:'dummy_sample'], '/seq/10754/10754_1#20.cram' ] ) | IRODS_IGET_FILE
    IRODS_IGET_FILE.out.file.view()
}
