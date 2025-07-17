//
// Read filtering
//

params.options = [:]

//
// MODULE: SeqKit seq
//
include { SEQKIT_SEQ  } from '../../modules/local/seqkit_seq/main'
workflow READ_FILTERING {
    take:
        reads

    main:
        ch_filtered_reads = Channel.empty()

        def modules = params.modules.clone()
        def seqkit_seq_options = modules['seqkit_seq']
        if (params.seqkit_seq_options) {
            seqkit_seq_options.args += " " + params.seqkit_seq_options
        }


        if (params.read_filtering) {
            //
            // MODULE: Run SeqKit seq
            //
            def seqkit_seq_option = seqkit_seq_options.clone()
            ch_reads = reads.map { meta, reads ->
                return [meta, reads, "filtered", seqkit_seq_option]
            }
            SEQKIT_SEQ ( ch_reads )
            ch_filtered_reads = SEQKIT_SEQ.out.reads
        }
    emit:
        reads = ch_filtered_reads
        versions = SEQKIT_SEQ.out.version
}
