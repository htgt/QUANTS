#!/usr/bin/env nextflow
/*
========================================================================================
    QUANTS
========================================================================================
    GitLab : https://gitlab.internal.sanger.ac.uk/team113_nextflow_pipelines/QUANTS
----------------------------------------------------------------------------------------
*/

nextflow.enable.dsl = 2

// Import nf-schema plugin functions for parameter validation
include { validateParameters; paramsHelp; paramsSummaryLog } from 'plugin/nf-schema'

/*
========================================================================================
    VALIDATE & PRINT PARAMETER SUMMARY
========================================================================================
*/

// Validate input parameters
validateParameters()

WorkflowMain.initialise(workflow, params, log)

/*
========================================================================================
    NAMED WORKFLOW FOR PIPELINE
========================================================================================
*/

include { SGE } from './workflows/sge'

//
// WORKFLOW: Run main QUANTS analysis pipeline
//
workflow NFCORE_QUANTS {
    SGE ()
}

/*
========================================================================================
    RUN ALL WORKFLOWS
========================================================================================
*/

//
// WORKFLOW: Execute a single named workflow for the pipeline
// See: https://github.com/nf-core/rnaseq/issues/619
//
workflow {
    NFCORE_QUANTS ()
}

/*
========================================================================================
    THE END
========================================================================================
*/
