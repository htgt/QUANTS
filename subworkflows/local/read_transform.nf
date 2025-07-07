//
// Read transformation - complement
//

params.options = [:]
def modules = params.modules.clone()

//
// MODULE: SeqKit seq
//

include { SEQKIT_SEQ  } from '../../modules/local/seqkit_seq/main'

workflow READ_TRANSFORM {
    take:
        reads

    main:
        ch_transform_reads = Channel.empty()
        //
        // MODULE: Run SeqKit seq
        //
        ch_transform_reads = reads.map { meta, reads ->
            def transform_type = meta.read_transform ?: params.read_transform
            def suffix = transform_type
            def seqkit_opts = ""

            // Set seqkit_opts based on tranform_type
            if (transform_type.contains('complement')) {
                seqkit_opts += " -p"
            }
            if (transform_type.contains('reverse')) {
                 seqkit_opts += " -r"
            }

            return [meta, reads, suffix, seqkit_opts]
        }

        SEQKIT_SEQ ( ch_transform_reads )
        ch_transform_reads = SEQKIT_SEQ.out.reads
    emit:
        reads = ch_transform_reads
        versions = SEQKIT_SEQ.out.version
}
