//
// Quantification
//

//
// MODULE: pyQUEST
//
include { PYQUEST  } from '../../modules/local/pyquest/main.nf'

//
// MODULE: pyQUEST library transformer
// Script found in modules/local/pyquest_library_converter/bin/pyquest_library_converter
//
params.modules.pyquest_library_converter.args = [
    params.modules.pyquest_library_converter.args,
    params.pyquest_library_converter_options
].findAll().join(' ')

include { TRANSFORM_LIBRARY_FOR_PYQUEST  } from '../../modules/local/pyquest_library_converter/main.nf'

workflow QUANTIFICATION {
    take:
        reads

    main:
        ch_sample_counts = Channel.empty()

        // Channel with meta and oligo library outside of it
        ch_oligo_library = reads.map { meta, reads ->
            def lib = meta.oligo_library
            return [meta, lib]
        }

        if (params.transform_library) {
            //
            // MODULE: Run Python library transformer
            //
            TRANSFORM_LIBRARY_FOR_PYQUEST ( ch_oligo_library )
        }

        if (params.quantification == "pyquest") {
            //
            // MODULE: Run pyQUEST
            //
            if (params.transform_library) {
                PYQUEST ( reads.join(TRANSFORM_LIBRARY_FOR_PYQUEST.out.oligo_library) )
            } else {
                PYQUEST ( reads.join(ch_oligo_library) )
            }

            ch_sample_library_counts = PYQUEST.out.library_counts
            ch_sample_read_counts = PYQUEST.out.read_counts
            ch_sample_stats = PYQUEST.out.stats
            versions = PYQUEST.out.version
        }

    emit:
        library_counts = ch_sample_library_counts
        read_counts = ch_sample_read_counts
        stats = ch_sample_stats
        versions
}
