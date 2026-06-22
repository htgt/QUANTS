# Adapted from benchling_utils infer-library-orientations
# Original author: Jamie Billington
import pytest
from unittest.mock import MagicMock, patch, mock_open, Mock
from infer_library_orientations.orientations import (
    reverse_complement,
    SequenceLibrary,
)


@pytest.fixture
def seq_lib():
    # bypass __init__
    lib = SequenceLibrary.__new__(SequenceLibrary)

    # minimal mocked dependency
    lib.library = Mock()
    lib.library.name = "test_library"

    return lib


def test_reverse_complement():
    assert reverse_complement("ATGC") == "GCAT"
    assert reverse_complement("AAAACC") == "GGTTTT"
    assert reverse_complement("GCGC") == "GCGC"


def test_reverse_complement_case_insensitive():
    assert reverse_complement("ATgc") == "GCAT"


def test_reverse_complement_invalid_input():
    with pytest.raises(ValueError):
        reverse_complement("ATGCN")
    with pytest.raises(ValueError):
        reverse_complement("ATG123")


def test_calculate_orientation_forward(seq_lib):
    counts = [10, 5, 2, 1]  # counts[0] + counts[3] > counts[1] + counts[2]
    orientation = seq_lib._calculate_orientation(counts)
    assert orientation == "fwd"


def test_calculate_orientation_reverse(seq_lib):
    counts = [2, 10, 5, 1]  # counts[0] + counts[3] < counts[1] + counts[2]
    orientation = seq_lib._calculate_orientation(counts)
    assert orientation == "rev"


def test_calculate_orientation_equal_counts(seq_lib):
    counts = [5, 5, 5, 5]
    with pytest.raises(
        ValueError,
        match=(
            "test_library: Equal counts detected. "
            "Unable to determine orientation."
        )
    ):
        seq_lib._calculate_orientation(counts)


def test_calculate_transformations_rev_fwd():
    library_name = "dummy_library"
    lib_orientation = "rev"
    read_orientation = "fwd"
    fwd_primer = "ATCG"
    rev_primer = "CGTA"
    transformations = SequenceLibrary._calculate_transformations(
        lib_orientation, read_orientation, fwd_primer, rev_primer
    )
    assert transformations.effective_fwd == fwd_primer
    assert transformations.effective_rev == reverse_complement(rev_primer)
    assert transformations.append_fwd == rev_primer
    assert transformations.append_rev == reverse_complement(fwd_primer)


def test_calculate_transformations_rev_rev():
    lib_orientation = "rev"
    read_orientation = "rev"
    fwd_primer = "ATCG"
    rev_primer = "CGTA"
    transformations = SequenceLibrary._calculate_transformations(
        lib_orientation, read_orientation, fwd_primer, rev_primer
    )
    assert transformations.effective_fwd == rev_primer
    assert transformations.effective_rev == reverse_complement(fwd_primer)
    assert transformations.append_fwd == rev_primer
    assert transformations.append_rev == reverse_complement(fwd_primer)


def test_calculate_transformations_fwd_rev():
    lib_orientation = "fwd"
    read_orientation = "rev"
    fwd_primer = "ATCG"
    rev_primer = "CGTA"
    transformations = SequenceLibrary._calculate_transformations(
        lib_orientation, read_orientation, fwd_primer, rev_primer
    )
    assert transformations.effective_fwd == rev_primer
    assert transformations.effective_rev == reverse_complement(fwd_primer)
    assert transformations.append_fwd == fwd_primer
    assert transformations.append_rev == reverse_complement(rev_primer)


def test_calculate_transformations_fwd_fwd():
    lib_orientation = "fwd"
    read_orientation = "fwd"
    fwd_primer = "ATCG"
    rev_primer = "CGTA"
    transformations = SequenceLibrary._calculate_transformations(
        lib_orientation, read_orientation, fwd_primer, rev_primer
    )
    assert transformations.effective_fwd == fwd_primer
    assert transformations.effective_rev == reverse_complement(rev_primer)
    assert transformations.append_fwd == fwd_primer
    assert transformations.append_rev == reverse_complement(rev_primer)


def test_sequence_library_init():
    # Mock library object with necessary attributes
    mock_library = MagicMock()
    mock_library.name = "dummy_library"
    mock_library.expt_forward_primer = "ATCG"
    mock_library.expt_reverse_primer = "AAAA"
    mock_library.valiant_meta = MagicMock()
    mock_library.fastq_1 = "test.fastq"

    # Mock data for CSV and FASTQ
    csv_data = "mseq\nATCGATCGTTTT\nATCGAGTATTTT\n"
    fastq_data = (
        "@SEQ_ID\n"
        "ATCGTTTT\n"
        "+\n"
        "!!!!!!!!\n"
        "@SEQ_ID2\n"
        "ATCGTTTT\n"
        "+\n"
        "!!!!!!!!\n"
    )

    with patch("builtins.open", mock_open(read_data=fastq_data)) as mock_file:
        with patch(
            "csv.DictReader",
            return_value=[
                {"mseq": "ATCGCGTA"},
                {"mseq": "CGTATACG"}
            ]
        ):
            seq_lib = SequenceLibrary(mock_library)
            # Perform assertions on the initialized attributes
            assert seq_lib.sequences == [
                mock_library.expt_forward_primer,
                mock_library.expt_reverse_primer,
                reverse_complement(mock_library.expt_forward_primer),
                reverse_complement(mock_library.expt_reverse_primer),
            ]
