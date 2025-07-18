//
// Primer/QC trimming
//

params.options = [:]
//
// MODULE: cutadapt
//
include { CUTADAPT as CUTADAPT_PRIMER  } from '../../modules/local/cutadapt/main'

workflow PRIMER_TRIMMING {
    take:
        reads

    main:
        ch_trimmed_reads = Channel.empty()

        def modules = params.modules.clone()
        def primer_options = modules['cutadapt_primer']

        ch_reads = reads.map { meta, reads ->
            def primer_option = primer_options.clone()
            primer_option.args += " " + ((meta.primer_start && meta.primer_end) ? "-g '${meta.primer_start}...${meta.primer_end}' -m 1" : params.primer_cutadapt_options)
            return [meta, reads, primer_option]
        }

        if (params.primer_trimming == "cutadapt") {
            //
            // MODULE: Run cutadapt
            //

            CUTADAPT_PRIMER ( ch_reads )
            ch_trimmed_reads = CUTADAPT_PRIMER.out.reads
            ch_trimmed_stats = CUTADAPT_PRIMER.out.json
        }
    emit:
        reads = ch_trimmed_reads
        stats = ch_trimmed_stats
        versions = CUTADAPT_PRIMER.out.version
}
