//
// Sequencing QC
//

//
// MODULE: Load nf-core modules
//
include { FASTQC  } from '../../modules/nf-core/fastqc/main'

//
// MODULE: SeqKit stats
//
params.modules.seqkit_stats.args = [
  params.modules.seqkit_stats.args,
  params.seqkit_stats_options
].findAll().join(' ')

include { SEQKIT_STATS  } from '../../modules/local/seqkit_stats/main'

workflow SEQUENCING_QC {
    take:
        reads

    main:
        //
        // MODULE: Run FastQC
        //
        FASTQC ( reads )
        fastqc_zip = FASTQC.out.zip
        fastqc_version = FASTQC.out.version

        //
        // MODULE: Run SeqKit stats
        //
        SEQKIT_STATS( reads )
        seqkit_stats = SEQKIT_STATS.out.stats
        seqkit_version = SEQKIT_STATS.out.version

    emit:
        fastqc_zip
        fastqc_version
        seqkit_stats
        seqkit_version
}
