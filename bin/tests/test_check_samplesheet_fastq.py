import subprocess
from unittest import mock
import pytest
from check_samplesheet_fastq import validate_headers


REQUIRED_HEADERS = [
            "sample",
            "fastq_1",
            "fastq_2"
        ]

OPTIONAL_HEADERS = [
            "oligo_library",
            "adapter_path",
            "primer_start",
            "primer_end",
            "append_start",
            "append_end",
            "read_transform"
        ]


def test_validate_headers_all_present():
    all_fieldnames = [
            "sample",
            "fastq_1",
            "fastq_2",
            "oligo_library",
            "adapter_path",
            "primer_start",
            "primer_end",
            "append_start",
            "append_end",
            "read_transform"
        ]

    result = validate_headers(all_fieldnames, REQUIRED_HEADERS, OPTIONAL_HEADERS)
    assert result == REQUIRED_HEADERS + OPTIONAL_HEADERS


def test_validate_headers_missing_required_headers():
    fieldnames = ["sample", "fastq_1"]
    with pytest.raises(ValueError) as excinfo:
        validate_headers(fieldnames, REQUIRED_HEADERS, [])

    assert "ERROR: samplesheet missing required headers:" in str(excinfo.value)


def test_validate_headers_raises_error_when_fieldnames_empty():
    fieldnames = []
    with pytest.raises(ValueError) as excinfo:
        validate_headers(fieldnames, REQUIRED_HEADERS, OPTIONAL_HEADERS)

    assert "ERROR: samplesheet file doesn't contain any fields." in str(excinfo.value)


def test_validate_headers_missing_optional_headers():
    fieldnames = [
            "oligo_library",
            "adapter_path",
            "primer_start",
            "primer_end",
            "append_start",
            "append_end"
            ]

    with mock.patch("builtins.print") as mock_print:
        validate_headers(fieldnames, [], OPTIONAL_HEADERS)

    # Check that the warning message is printed
    mock_print.assert_called_once_with(
        "WARNING: samplesheet missing optional headers: read_transform \nThese will be taken from params.json file"
    )

    # Check at least once print statement was called
    # This is to ensure that the function executed and printed something
    assert mock_print.call_count == 1


def test_check_samplesheet_command_runs_as_expected(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    output_csv = tmp_path / "samplesheet.valid.csv"
    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,SAMPLE_SE_RUN1_2.fastq.gz,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )

    expected_output_csv = tmp_path / "expected_output.csv"

    expected_output_csv.write_text(
        "sample,single_end,fastq_1,fastq_2,oligo_library,adapter_path,primer_start,primer_end,append_start,append_end,read_transform\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,path/to/illumina_adaptors.fa,GAA,AAG,CTT,TTC,reverse_complement\n"
        "SAMPLE_SE,0,SAMPLE_SE_RUN1_1.fastq.gz,SAMPLE_SE_RUN1_2.fastq.gz,SAMPLE_SE_meta.csv,path/to/illumina_adaptors.fa,GTT,TAC,GTT,TAC,\n"
    )

    # Run the command to check the samplesheet
    _ = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet_fastq.py",
            str(input_csv),
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


def test_check_samplesheet_inconsistent_number_of_columns(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    output_csv = tmp_path / "samplesheet.valid.csv"
    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,,\n"
        "SAMPLE_SE,SAMPLE_PE_RUN1_2.fastq.gz,,\n"
    )

    # Run the command to check the samplesheet
    process_out = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet_fastq.py",
            str(input_csv),
            str(output_csv)
        ],
        capture_output=True,
        text=True,
    )

    # Assert that sys.exit(1) was called
    assert process_out.returncode == 1

    # Check error message in stdout or stderr
    assert "ERROR: Please check samplesheet -> Inconsistent number of columns!" in process_out.stdout


def test_check_samplesheet_extra_column(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    output_csv = tmp_path / "samplesheet.valid.csv"
    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library,var1\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv,var1\n"
        "SAMPLE_SE,SAMPLE_SE_RUN1_1.fastq.gz,SAMPLE_SE_RUN1_2.fastq.gz,SAMPLE_SE_meta.csv,var1\n"
    )

    expected_output_csv = tmp_path / "expected_output.csv"

    expected_output_csv.write_text(
        "sample,single_end,fastq_1,fastq_2,oligo_library\n"
        "SAMPLE_PE,1,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta.csv\n"
        "SAMPLE_SE,0,SAMPLE_SE_RUN1_1.fastq.gz,SAMPLE_SE_RUN1_2.fastq.gz,SAMPLE_SE_meta.csv\n"
    )

    # Run the command to check the samplesheet
    _ = subprocess.run(
        [
            "python3",
            "bin/check_samplesheet_fastq.py",
            str(input_csv),
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


def test_check_samplesheet_multiple_rows_same_sample(tmp_path):
    # Prepare a minimal valid samplesheet
    input_csv = tmp_path / "samplesheet.csv"
    output_csv = tmp_path / "samplesheet.valid.csv"
    input_csv.write_text(
        "sample,fastq_1,fastq_2,oligo_library\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_1.fastq.gz,,SAMPLE_PE_meta_1.csv\n"
        "SAMPLE_PE,SAMPLE_PE_RUN1_2.fastq.gz,,SAMPLE_PE_meta_2.csv\n"
        "SAMPLE_SE,SAMPLE_PE_RUN1.fastq.gz,,SAMPLE_PE_meta_3.csv\n"

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
            "bin/check_samplesheet_fastq.py",
            str(input_csv),
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
