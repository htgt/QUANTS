//
// Merge paired end reads
//

//
// MODULE: Load FLASH2
//
params.modules.flash2.args = [
    params.modules.flash2.args,
    params.flash2_options
].findAll().join(' ')

include { FLASH2  } from '../../modules/local/flash2/main.nf'

//
// MODULE: Load SEQPREP
//
params.modules.seqprep.args = [
  params.modules.seqprep.args,
  params.seqprep_options
].findAll().join(' ')

include { SEQPREP } from '../../modules/local/seqprep/read_merging/main.nf'

workflow READ_MERGING {
    take:
        reads

    main:
        ch_merged_reads = Channel.empty()
        ch_versions = Channel.empty()

        if (params.read_merging == "flash2") {
            //
            // MODULE: Run FLASH
            //
            FLASH2 ( reads )
            ch_merged_reads = FLASH2.out.reads
            ch_versions = FLASH2.out.version
        }

        if (params.read_merging == "seqprep") {
            //
            // MODULE: Run SeqPrep
            //
            SEQPREP ( reads )
            ch_merged_reads = SEQPREP.out.reads
            ch_versions = SEQPREP.out.version
        }

    emit:
        reads = ch_merged_reads
        versions = ch_versions
}
