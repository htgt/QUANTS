//
// Read transformation - complement
//

params.options = [:]

//
// MODULE: SeqKit seq
//

include { SEQKIT_SEQ  } from '../../modules/local/seqkit_seq/main'

workflow READ_TRANSFORM {
    take:
        reads

    main:
        ch_transform_reads = Channel.empty()

        def modules = params.modules.clone()
        def seqkit_seq_options = modules['seqkit_seq']

        //
        // MODULE: Run SeqKit seq
        //
        ch_transform_reads = reads.map { meta, reads ->
            def transform_type = meta.read_transform ?: params.read_transform
            def suffix = transform_type
            def seqkit_seq_option = seqkit_seq_options.clone()


            // Set seqkit_opts based on tranform_type
            if (transform_type.contains('complement')) {
                seqkit_seq_option.args += " -p"
            }
            if (transform_type.contains('reverse')) {
                 seqkit_seq_option.args += " -r"
            }

            return [meta, reads, suffix, seqkit_seq_option]
        }

        SEQKIT_SEQ ( ch_transform_reads )
        ch_transform_reads = SEQKIT_SEQ.out.reads
    emit:
        reads = ch_transform_reads
        versions = SEQKIT_SEQ.out.version
}
