//
// Adapter/QC trimming
//

params.options = [:]
//
// MODULE: cutadapt
//
include { CUTADAPT as CUTADAPT_ADAPTER  } from '../../modules/local/cutadapt/main'

// For switching to the nf-core Cutadapt module
// include { CUTADAPT as CUTADAPT_ADAPTER  } from '../../modules/nf-core/cutadapt/main'

workflow ADAPTER_TRIMMING {
    take:
        reads

    main:
        ch_trimmed_reads = Channel.empty()

        def modules = params.modules.clone()
        def adapter_options = modules['cutadapt_adapter']

        ch_reads = reads.map { meta, reads ->
            def adapter_option = adapter_options.clone()
            adapter_option.args += " " + "-a \"file:${meta.adapter_path}\""
            return [meta, reads, adapter_option]
        }

        if (params.adapter_trimming == "cutadapt") {
            //
            // MODULE: Run cutadapt
            //

            CUTADAPT_ADAPTER ( ch_reads )
            ch_trimmed_reads = CUTADAPT_ADAPTER.out.reads
            ch_trimmed_stats = CUTADAPT_ADAPTER.out.json
        }
    emit:
        reads = ch_trimmed_reads
        stats = ch_trimmed_stats
        versions = CUTADAPT_ADAPTER.out.version
}
