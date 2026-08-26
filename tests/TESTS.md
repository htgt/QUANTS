# End-to-end pipeline tests

The `test/` directory contains end-to-end tests for the quants pipeline using the nf-test framework.

## End-to-end datasets and files

Having retrieved data and placed it in the ref and sample-data folders, tests can be run with the following command:
```bash
NXF_VER=23.10.0 nf-test test --profile docker
```

If you are running individual tests, you can run them with the following command:
```bash
NXF_VER=23.10.0 nf-test test tests/test[n].main.nf.test --profile <docker|singularity>
```

Note that the `NXF_VER` is expected to changed in future releases of the pipeline, and should be updated to the version of Nextflow that is being used to run the tests.

Make sure you download/clone `quants-data` from this repository `https://gitlab.internal.sanger.ac.uk/sci/quants-data` into your chosen directory on your local machine. Before running the end-to-end tests copy the contents `ref/` and `sample-data/` directories from your local `quants-data` repository into `tests/ref` and `tests/sample-data` respectively, overwriting existing contents.

**Note:** The `quants-data` repository is for internal Sanger use only.

Once copied and overwritten, `tests` directory structure should look like the following:
```bash
tests/
├── TESTS.md
├── lib
├── manifests
├── modules
├── modules-testdata
├── nextflow.config
├── quants-data
├── ref
├── ref-checksums
├── sample-data
├── sample-data-checksums
├── test1.main.nf.test
├── test10.main.nf.test
├── test11.main.nf.test
├── test12.main.nf.test
├── test13.main.nf.test
├── test14.main.nf.test
├── test15.main.nf.test
├── test2.main.nf.test
├── test3.main.nf.test
├── test4.main.nf.test
├── test5.main.nf.test
├── test6.main.nf.test
├── test7.main.nf.test
├── test8.main.nf.test
└── test9.main.nf.test
```

To confirm that you've retrieved the correct data, and named it appropriately if necessary, run `diff -q <(md5sum tests/sample-data/*) tests/sample-data-checksums` and `diff -q <(md5sum tests/ref/*) tests/ref-checksums`. If the commands return nothing (exit code 0), the data is as expected. Note that if you do not run this command from the top level directory of the repo, it will fail, as md5sum will output relative paths along with checksums.

## End-to-end test parameters

| Test | Source | FASTQ or CRAM | SE or PE| RevComp | Read merging | Adapter trimming | Primer Trimming | Read filtering | Read modification | QC | Quantification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `test1.main.nf.test` | Trimmed | FASTQ | SE | Y | N | N | N | N | Y | N | Y |
| `test2.main.nf.test` | Trimmed | FASTQ | SE | Y | N | N | N | N | Y | Y | Y |
| `test3.main.nf.test` | Raw | FASTQ | SE | Y | N | Y | Y | N | Y | Y | Y |
| `test4.main.nf.test` | Raw | CRAM | SE | Y | N | Y | Y | N | Y | Y | Y |
| `test5.main.nf.test` | Raw | FASTQ | PE | N | Y (SeqPrep) | Y | Y | N | N | Y | Y |
| `test6.main.nf.test` | Raw | FASTQ | PE | N | Y (Flash2) | Y | Y | Y | N | Y | Y |
| `test7.main.nf.test` | Raw | FASTQ | PE | N | Y (SeqPrep) | Y | Y | Y | N | Y | Y |
| `test8.main.nf.test` | Raw | FASTQ | PE | N | Y (Flash2) | Y | Y | Y | N | Y | Y |
| `test9.main.nf.test` | Raw | FASTQ | PE | N | Y (Flash2) | Y | Y | Y | N | Y | Y |
| `test10.main.nf.test` | Raw | FASTQ | SE | N | N | Y | Y | Y | N | Y | Y |
| `test11.main.nf.test` | Raw | FASTQ | SE | N | N | Y | Y | N | Y | Y | Y |
| `test12.main.nf.test` | Raw | CRAM | SE | N | N | Y | Y | N | Y | Y | Y |
| `test13.main.nf.test` | Raw | CRAM | PE | N | N | Y | Y | N | Y | Y | Y | Y |
| `test14.main.nf.test` | Raw | FASTQ | - | - | - | - | - | - | - | - | - | Y |
| `test15.main.nf.test` | Raw | FASTQ | PE | Y | Y (Flash2) | N | Y | N | Y | N | N |

# Module tests

Individual module tests are located in each module's tests directory, i.e. `modules/<local-or-nf-core>/<module-name>/tests/`.

Module tests should be run locally when developing or modifying a module to confirm that the module behaves as expected. Module tests can be run with the following command:
```bash
nf-test test modules --profile <docker|singularity>
```

Running individual module tests can be done with the following command:
```bash
nf-test test modules/<local-or-nf-core>/<module-name>/tests/main.nf.test
```

# Subworkflow tests

Tests for local subworkflow are located in each subworkflows' tests directory, i.e. `subworkflows/local/<subworkflow-name>/tests/`.

Subworkflow tests should be run locally when developing or modifying a subworkflow to confirm that the subworkflow behaves as expected. Subworkflow tests can be run with the following command:
```bash
nf-test test subworkflows --profile <docker|singularity>
```

Running individual subworkflow tests can be done with the following command:
```bash
nf-test test subworkflows/local/<subworkflow-name>/tests/main.nf.test --profile <docker|singularity>
```

# Overview of the QUANTS tests: test types, directories and purpose

### nf-tests
```bash
# Module level nf-test
modules/local/*
modules/nf-core/*
tests/modules/*

# Subworkflow level nf-test
subworkflows/local/*/tests

# End to end tests
tests/test1.main.nf.test
tests/test2.main.nf.test
tests/test3.main.nf.test
tests/test4.main.nf.test
tests/test5.main.nf.test
tests/test6.main.nf.test
tests/test7.main.nf.test
tests/test8.main.nf.test
tests/test9.main.nf.test
tests/test10.main.nf.test
tests/test11.main.nf.test
tests/test12.main.nf.test
tests/test13.main.nf.test
tests/test14.main.nf.test
tests/test15.main.nf.test
```

### Python tests

```bash
bin/manifest_transformer/tests/*
bin/infer_library_orientations/tests/*
bin/pyquest_library_converter/tests/*
bin/tests/*
```
