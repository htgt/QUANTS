import pytest
import subprocess

from check_samplesheet import check_sequencing_fields, OPTIONAL_HEADERS, REQUIRED_HEADERS, validate_all_samples, validate_headers
from types import SimpleNamespace
from unittest import mock


@pytest.fixture(autouse=True)
def reset_required_headers():
    REQUIRED_HEADERS[:] = ["sample"]


def test_validate_headers_all_present_fastq():
    all_fieldnames = REQUIRED_HEADERS + ["fastq_1", "fastq_2"] + OPTIONAL_HEADERS

    result = validate_headers(fieldnames = all_fieldnames, file_type = "fastq")

    assert result == REQUIRED_HEADERS + OPTIONAL_HEADERS


def test_validate_headers_all_present_cram():
    all_fieldnames = REQUIRED_HEADERS + ["cram_path"] + OPTIONAL_HEADERS

    result = validate_headers(fieldnames = all_fieldnames, file_type = "cram")

    assert result == REQUIRED_HEADERS + OPTIONAL_HEADERS


def test_validate_headers_no_row_headers(capsys):
    row_headers = []

    with pytest.raises(SystemExit) as exc_info:
        validate_headers(row_headers = row_headers, is_params = True)

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert captured.out.strip() == "No row to validate headers."


def test_validate_headers_missing_required_headers():
    fieldnames = ["sample", "fastq_1"]
    with pytest.raises(ValueError) as excinfo:
        validate_headers(fieldnames = fieldnames, file_type = "fastq")

    assert "ERROR: samplesheet missing required headers:" in str(excinfo.value)


def test_validate_headers_raises_error_when_fieldnames_empty():
    fieldnames = []
    with pytest.raises(ValueError) as excinfo:
        validate_headers(fieldnames = fieldnames, file_type = "fastq")

    assert "ERROR: samplesheet file doesn't contain any fields." in str(excinfo.value)


def test_validate_headers_missing_optional_headers():
    fieldnames = [
            "sample",
            "fastq_1",
            "fastq_2",
            "oligo_library",
            "adapter_path",
            "primer_start",
            "primer_end",
            "append_start",
            "append_end"
            ]

    with mock.patch("builtins.print") as mock_print:
        validate_headers(fieldnames = fieldnames, file_type = "fastq")

    # Check that the warning message is printed
    missing_optional_headers = [header for header in OPTIONAL_HEADERS if header not in fieldnames]

    mock_print.assert_called_once_with(
        f"WARNING: samplesheet missing optional headers: {', '.join(missing_optional_headers)}"
    )

    # Check at least once print statement was called
    # This is to ensure that the function executed and printed something
    assert mock_print.call_count == 1


def test_check_sequencing_fields_missing_fastq_1():
    line = {
        "fastq_1": "",
        "fastq_2": ""
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="fastq",
            line=line,
            single_end=True
        )

    mock_error.assert_any_call(
        "fastq_1 file path missing!",
        "Line",
        ","
    )


def test_check_sequencing_fields_missing_fastq_2_paired_end():
    line = {
        "fastq_1": "s1_1.fastq.gz",
        "fastq_2": ""
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="fastq",
            line=line,
            single_end=False
        )

    mock_error.assert_any_call(
        "fastq_2 file path missing but single_end is set globally to False!",
        "Line",
        "s1_1.fastq.gz,"
    )


def test_check_sequencing_fields_fastq_2_provided_single_end():
    line = {
        "fastq_1": "s1_1.fastq.gz",
        "fastq_2": "s1_2.fastq.gz"
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="fastq",
            line=line,
            single_end=True
        )

    mock_error.assert_any_call(
        "fastq_2 provided but single_end is set globally to True!",
        "Line",
        "s1_1.fastq.gz,s1_2.fastq.gz"
    )


def test_check_sequencing_fields_missing_cram():
    line = {
        "cram_path": ""
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="cram",
            line=line,
            single_end=True
        )

    mock_error.assert_any_call(
        "cram_path file path missing!",
        "Line",
        ""
    )


def test_check_sequencing_fields_fastq_path_with_spaces():
    line = {
        "fastq_1": "s1 1.fastq.gz",
        "fastq_2": ""
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="fastq",
            line=line,
            single_end=True
        )

    mock_error.assert_called_once_with(
        "FASTQ file path contains spaces!",
        "Line",
        "s1 1.fastq.gz,"
    )


def test_check_sequencing_fields_cram_path_wrong_extension():
    line = {
        "cram_path": "s1.bam"
    }

    with mock.patch("check_samplesheet.print_error") as mock_error:
        check_sequencing_fields(
            input_type="cram",
            line=line,
            single_end=True
        )

    mock_error.assert_called_once_with(
        "CRAM file extension can only be .cram!",
        "Line",
        "s1.bam"
    )

@mock.patch("check_samplesheet.get_params")
@mock.patch("check_samplesheet.validate_headers")
@mock.patch("check_samplesheet.get_row")
@mock.patch("check_samplesheet.validate_row")
@mock.patch("check_samplesheet.display_validation_report")
def test_validate_all_samples_no_messages(
    mock_display_report,
    mock_validate_row,
    mock_get_row,
    mock_validate_headers,
    mock_get_params
):
    samplesheet_data = [
        {"sample": "A"},
        {"sample": "B"},
    ]
    params = {"foo": "bar"}

    mock_get_params.return_value = SimpleNamespace()
    mock_get_row.return_value = SimpleNamespace()
    mock_validate_row.return_value = ([], [])

    validate_all_samples(
        samplesheet_data=samplesheet_data,
        params=params,
        file_type="fastq",
    )

    mock_get_params.assert_called_once_with(params)
    assert mock_validate_headers.call_count == 2
    assert mock_get_row.call_count == 2
    assert mock_validate_row.call_count == 2
    mock_display_report.assert_not_called()


@mock.patch("check_samplesheet.get_params")
@mock.patch("check_samplesheet.validate_headers")
@mock.patch("check_samplesheet.get_row")
@mock.patch("check_samplesheet.validate_row")
@mock.patch("check_samplesheet.display_validation_report")
def test_validate_all_samples_message(
    mock_display_report,
    mock_validate_row,
    mock_get_row,
    mock_validate_headers,
    mock_get_params
):
    samplesheet_data = [
        {"sample": "A"},
        {"sample": "B"},
    ]
    params = {"foo": "bar"}
    warning_message = "Some warning message"
    error_message = "Some error message"

    mock_get_params.return_value = SimpleNamespace()
    mock_get_row.return_value = SimpleNamespace()
    mock_validate_row.return_value = ([warning_message], [error_message])

    validate_all_samples(
        samplesheet_data=samplesheet_data,
        params=params,
        file_type="fastq",
    )

    mock_get_params.assert_called_once_with(params)
    assert mock_validate_headers.call_count == 2
    assert mock_get_row.call_count == 2
    assert mock_validate_row.call_count == 2
    mock_display_report.assert_called_once_with([warning_message, warning_message],
                                                [error_message, error_message])


@mock.patch("check_samplesheet.get_params")
@mock.patch("check_samplesheet.get_row")
@mock.patch("check_samplesheet.validate_row")
def test_validate_all_samples_add_row_id(
    mock_validate_row,
    mock_get_row,
    mock_get_params
):
    samplesheet_data = [
        {"sample": "A"}
    ]
    params = {"foo": "bar"}

    mock_get_params.return_value = SimpleNamespace()
    mock_get_row.return_value = SimpleNamespace()
    mock_validate_row.return_value = ([], [])

    validate_all_samples(
        samplesheet_data=samplesheet_data,
        params=params,
        file_type="fastq",
    )

    mock_get_row.assert_called_with({"sample": "A", "row_identifier": 2})


def test_check_samplesheet_command_runs_as_expected_fastq(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )
    
    input_json.write_text(
        '{\n'
        # NB, '"single_end": true' works for testing purposes, but second sample in samplesheet is actually paired-end
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": true,\n'
        '"adapter_trimming": "cutadapt",\n'
        '"adapter_trimming_qc": true,\n'
        '"primer_trimming": "cutadapt",\n'
        '"primer_trimming_qc": true,\n'
        '"read_modification": true,\n'
        '"append_quality": "?",\n'
        '"transform_library": true,\n'
        '"quantification": "pyquest",\n'
        '"pyquest_library_converter_options": "-N 1 -S 24",\n'
        '"downsampling": true,\n'
        '"downsampling_size": 12000000\n'
        '}\n'
    )

    expected_output_csv = tmp_path / "expected_output.csv"

    expected_output_csv.write_text(
        "sample,single_end,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,1,SAMPLE_SE_RUN1_1.fastq.gz,,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )

    # Run the command to check the samplesheet
    _ = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Check that the output file exists and has the expected header
    assert output_csv.exists()

    with open(output_csv) as f:
        header = f.readline().strip()
    expected_header = "sample,single_end,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform"
    assert header == expected_header, "Header does not match expected output."

    # Check if input csv is same as expected output csv
    with open(expected_output_csv) as f_in, open(output_csv) as f_out:
        expected_output_csv = f_in.read().strip()
        output_content = f_out.read().strip()

    assert expected_output_csv == output_content, "Input and output samplesheet contents do not match."


def test_check_samplesheet_command_runs_as_expected_cram(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,cram_path,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.cram,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,SAMPLE_SE_RUN1_1.cram,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )
    
    input_json.write_text(
        '{\n'
        # NB, '"single_end": true' works for testing purposes, but second sample in samplesheet is actually paired-end
        '"single_end": true,\n'
        '"input_type": "cram",\n'
        '"raw_sequencing_qc": true,\n'
        '"adapter_trimming": "cutadapt",\n'
        '"adapter_trimming_qc": true,\n'
        '"primer_trimming": "cutadapt",\n'
        '"primer_trimming_qc": true,\n'
        '"read_modification": true,\n'
        '"append_quality": "?",\n'
        '"transform_library": true,\n'
        '"quantification": "pyquest",\n'
        '"pyquest_library_converter_options": "-N 1 -S 24",\n'
        '"downsampling": true,\n'
        '"downsampling_size": 12000000\n'
        '}\n'
    )

    expected_output_csv = tmp_path / "expected_output.csv"

    expected_output_csv.write_text(
        "sample,single_end,cram_path,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_1.cram,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,1,SAMPLE_SE_RUN1_1.cram,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )

    # Run the command to check the samplesheet
    _ = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Check that the output file exists and has the expected header
    assert output_csv.exists()

    with open(output_csv) as f:
        header = f.readline().strip()
    expected_header = "sample,single_end,cram_path,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform"
    assert header == expected_header, "Header does not match expected output."

    # Check if input csv is same as expected output csv
    with open(expected_output_csv) as f_in, open(output_csv) as f_out:
        expected_output_csv = f_in.read().strip()
        output_content = f_out.read().strip()

    assert expected_output_csv == output_content, "Input and output samplesheet contents do not match."


def test_check_samplesheet_inconsistent_number_of_columns(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,,\n"
        "SAMPLE_SE,SAMPLE_PE_RUN1_2.fastq.gz,,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": true,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "pyquest",\n'
        '"downsampling": true\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "Inconsistent number of columns" in process_out.stdout


def test_check_samplesheet_invalid_number_columns(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2\n"
        "s1,,\n"
        "s2,,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "Invalid number of populated columns" in process_out.stdout


def test_check_samplesheet_no_sample_entry(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2\n"
        ",s1_1.fq.gz,s1_2.fq.gz\n"
        ",s2_2.fq.gz,s2_2.fq.gz\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": false,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "Sample entry has not been specified!" in process_out.stdout


def test_check_samplesheet_duplicate_rows(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2\n"
        "s1,s1.fq.gz,\n"
        "s1,s1.fq.gz,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "Samplesheet contains duplicate rows!" in process_out.stdout


def test_check_samplesheet_group_id_missing_all(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2\n"
        "s1,s1.fq.gz,\n"
        "s1,s2.fq.gz,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Check error message in stdout or stderr
    assert "Samplesheet group_id column not found or entirely empty" in process_out.stdout


def test_check_samplesheet_group_id_missing_some(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "group_id,sample,fastq_1,fastq_2\n"
        "grp1,s1,s1.fq.gz,\n"
        ",s1,s2.fq.gz,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that error was raised
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "Please ensure that all samples have values for group_id in the samplesheet" in process_out.stderr

def test_check_samplesheet_extra_column(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,var1\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,var1\n"
        "SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,,SAMPLE_SE_meta.csv,var1\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": true,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "pyquest",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "ERROR: Check for invalid headers in the samplesheet: var1" in process_out.stderr


def test_check_samplesheet_extra_commas(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,,fastq_1,fastq_2\n"
        "sample1,,/path/to/sample1.fastq.gz,\n"
        "sample2,,/path/to/sample1.fastq.gz,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "ERROR: Check in the samplesheet if there are any extra commas" in process_out.stderr


def test_check_samplesheet_multiple_rows_same_sample(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta_1.csv\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_2.fastq.gz,,SAMPLE_PE_meta_2.csv\n"
        "SAMPLE_SE,SAMPLE_PE_RUN1.fastq.gz,,SAMPLE_PE_meta_3.csv\n"

    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": true,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "pyquest",\n'
        '"downsampling": false\n'
        '}\n'
    )

    expected_output_csv = tmp_path / "expected_output.csv"

    expected_output_csv.write_text(
       "sample,single_end,fastq_1,fastq_2,oligo_library\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta_1.csv\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_2.fastq.gz,,SAMPLE_PE_meta_2.csv\n"
        "SAMPLE_SE,1,SAMPLE_PE_RUN1.fastq.gz,,SAMPLE_PE_meta_3.csv\n"
    )

    # Run the command to check the samplesheet
    _ = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Check that the output file exists and has the expected header
    assert output_csv.exists()

    with open(output_csv) as f:
        header = f.readline().strip()
    expected_header = "sample,single_end,fastq_1,fastq_2,oligo_library"
    assert header == expected_header, "Header does not match expected output."

    # Check if input csv is same as expected output csv
    with open(expected_output_csv) as f_in, open(output_csv) as f_out:
        expected_output_csv = f_in.read().strip()
        output_content = f_out.read().strip()

    assert expected_output_csv == output_content, "Input and output samplesheet contents do not match."


def test_check_samplesheet_wrong_file_extension(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    input_json = tmp_path / "params.json"
    output_csv = tmp_path / "samplesheet.valid.csv"

    input_csv.write_text(
        "sample,fastq_1,fastq_2\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,\n"
        "SAMPLE_SE,SAMPLE_PE_RUN1_2.cram,\n"
    )

    input_json.write_text(
        '{\n'
        '"single_end": true,\n'
        '"input_type": "fastq",\n'
        '"raw_sequencing_qc": false,\n'
        '"adapter_trimming": "",\n'
        '"primer_trimming": "",\n'
        '"read_modification": false,\n'
        '"transform_library": false,\n'
        '"quantification": "",\n'
        '"downsampling": false\n'
        '}\n'
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet.py",
            str(input_csv),
            str(input_json),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr

    assert "FASTQ file extension can only be .fastq.gz or .fq.gz" in process_out.stdout
