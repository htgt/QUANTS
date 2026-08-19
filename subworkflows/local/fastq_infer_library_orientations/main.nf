//
// Infer library orientations
//

//
// MODULE: INFERLIBRARYORIENTATIONS
include { INFERLIBRARYORIENTATIONS } from '../../../modules/local/inferlibraryorientations/main.nf'

workflow FASTQ_INFER_LIBRARY_ORIENTATIONS {
    take:
        reads     // channel: [meta, fastq_files]

    main:
        ch_input = reads.map { meta, fastq ->
            tuple(meta, file(meta.oligo_library), fastq)
        }

        INFERLIBRARYORIENTATIONS(ch_input)

        ch_reads_with_tsv = reads
            .map { meta, sample_reads ->
                tuple(meta.id, meta, sample_reads)
            }
            .join(
                INFERLIBRARYORIENTATIONS.out.library_orientations
                    .map { meta, tsv ->
                        tuple(meta.id, tsv)
                    }
            )

        ch_updated_reads = ch_reads_with_tsv.map { id, meta, sample_reads, tsv ->
            // Parse the single-row TSV produced by INFERLIBRARYORIENTATIONS
            def row = tsv.splitCsv(header:true, sep:'\t').first()

            def updated_meta = meta + [
                primer_start   : row.primer_start,
                primer_end     : row.primer_end,
                append_start   : row.append_start,
                append_end     : row.append_end,
                read_transform : row.read_transform
            ]
            tuple(updated_meta, sample_reads)
        }

        emit:
            reads = ch_updated_reads
            // No versions as module emits topics that is
            // not compatible with current version handling in pipeline

}
