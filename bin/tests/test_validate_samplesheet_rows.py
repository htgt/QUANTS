import pytest
from unittest import mock

from types import SimpleNamespace

from validate_samplesheet_rows import (is_valid_sequence, validate_row, display_validation_report)


# is_valid_sequence tests
@pytest.mark.parametrize("sequence,expected",
                         [("ATcg", True),
                          ("12XZ", False),
                          ("AXtz", False),
                          ("", False)])
def test_is_valid_sequence(sequence, expected):
    assert is_valid_sequence(sequence) is expected


# validate_row fixtures
@pytest.fixture
def input_row():
    return SimpleNamespace(
        row_identifier=2,
        sample="sample1",
        expt_forward_primer="ATCG",
        expt_reverse_primer="CGTA",
        oligo_library="Library1",
        append_start="",
        append_end="",
        primer_start="",
        primer_end="",
        read_transform="",
        adapter_path="",
        group_id=""
    )


@pytest.fixture
def input_params():
    return SimpleNamespace(
        single_end=True,
        input_type="fastq",
        raw_sequencing_qc=False,
        adapter_trimming="",
        adapter_trimming_qc=False,
        primer_trimming="",
        primer_trimming_qc=False,
        read_modification=False,
        append_quality="",
        transform_library=False,
        quantification="",
        pyquest_library_converter_options="",
        downsampling=False,
        infer_library_orientations=False,
    )


# validate_rows tests
@mock.patch("validate_samplesheet_rows.print_error")
def test_validate_row_infer_library_orientations_true_missing_expt_primer(mock_error, input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.expt_forward_primer = "noCol"

    with pytest.raises(SystemExit):
        validate_row(input_row, input_params)

    mock_error.assert_called_once_with("ERROR: If infer_library_orientations is set globally, the samplesheet "
                                       "must include both the expt_forward_primer and expt_reverse_primer columns.")


def test_validate_row_infer_library_orientations_empty_reverse_primer(input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.expt_reverse_primer = ""

    warnings, errors = validate_row(input_row, input_params)

    assert warnings == []
    assert len(errors) == 1
    assert "expt_reverse_primer should not be empty" in errors[0]


@mock.patch("validate_samplesheet_rows.is_valid_sequence")
def test_validate_row_infer_library_orientations_invalid_forward_primer(mock_is_valid_sequence,
                                                                        input_row,
                                                                        input_params):
    input_params.infer_library_orientations = True

    # Forward primer False, reverse True
    mock_is_valid_sequence.side_effect = [False, True]

    warnings, errors = validate_row(input_row, input_params)

    assert warnings == []
    assert len(errors) == 1
    assert "expt_forward_primer is not a valid DNA sequence." in errors[0]


@mock.patch("validate_samplesheet_rows.print_error")
def test_validate_row_infer_library_orientations_missing_oligo_library(mock_error, input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.oligo_library = "noCol"

    with pytest.raises(SystemExit):
        validate_row(input_row, input_params)

    mock_error.assert_called_once_with("ERROR: If infer_library_orientations is set globally, the oligo_library "
                                       "column must exist in the samplesheet.")


def test_validate_row_infer_library_orientations_empty_oligo_library(input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.oligo_library = ""

    warnings, errors = validate_row(input_row, input_params)

    assert warnings == []
    assert len(errors) == 1
    assert ("If infer_library_orientations is set globally, then oligo_library "
            "must be set in the samplesheet.") in errors[0]


def test_validate_row_infer_library_orientations_append_start_warning(input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.append_start = "ATCG"

    # To avoid error when read_modification set to False but append_start not empty
    input_params.read_modification = True
    input_params.append_quality = "?"

    warnings, errors = validate_row(input_row, input_params)

    assert errors == []
    assert len(warnings) == 1
    assert "append_start value will be overridden" in warnings[0]


def test_validate_row_infer_library_orientations_append_end_warning(input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.append_end = "ATCG"

    # To avoid error when read_modification set to False but append_end not empty
    input_params.read_modification = True
    input_params.append_quality = "?"

    warnings, errors = validate_row(input_row, input_params)

    assert errors == []
    assert len(warnings) == 1
    assert "append_end value will be overridden" in warnings[0]


def test_validate_row_infer_library_orientations_read_transform_warning(input_row, input_params):
    input_params.infer_library_orientations = True
    input_row.read_transform = "reverse-complement"

    warnings, errors = validate_row(input_row, input_params)

    assert errors == []
    assert len(warnings) == 1
    assert "read_transform value will be overridden" in warnings[0]


# display_validation_report tests
@mock.patch("validate_samplesheet_rows.print_info")
@mock.patch("validate_samplesheet_rows.print_error")
def test_display_validation_report_no_messages(mock_error, mock_info):
    display_validation_report([], [])

    mock_info.assert_not_called()
    mock_error.assert_not_called()


@mock.patch("validate_samplesheet_rows.print_info")
@mock.patch("validate_samplesheet_rows.print_error")
def test_display_validation_report_warning(mock_error, mock_info):
    display_validation_report(["my_warning"], [])

    mock_info.assert_called_once_with("WARNING: my_warning")
    mock_error.assert_not_called()


@mock.patch("validate_samplesheet_rows.print_info")
@mock.patch("validate_samplesheet_rows.print_error")
def test_display_validation_report_raises_error(mock_error, mock_info):
    with pytest.raises(SystemExit):
        display_validation_report([], ["my_error"])

    mock_info.assert_not_called()
    mock_error.assert_called_once_with("ERROR: my_error")
