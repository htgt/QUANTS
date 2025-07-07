//
// Read filtering
//

params.options = [:]
def modules = params.modules.clone()

//
// MODULE: SeqKit seq
//
include { SEQKIT_SEQ  } from '../../modules/local/seqkit_seq/main'
workflow READ_FILTERING {
    take:
        reads

    main:
        ch_filtered_reads = Channel.empty()
        if (params.read_filtering) {
            //
            // MODULE: Run SeqKit seq
            //
            ch_reads = reads.map { meta, reads ->
                return [meta, reads, "filtered", params.seqkit_seq_options]
            }
            SEQKIT_SEQ ( ch_reads )
            ch_filtered_reads = SEQKIT_SEQ.out.reads
        }
    emit:
        reads = ch_filtered_reads
        versions = SEQKIT_SEQ.out.version
}
