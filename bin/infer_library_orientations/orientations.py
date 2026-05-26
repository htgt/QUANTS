# Adapted from benchling_utils infer-library-orientations
# Original author: Jamie Billington
import csv
import gzip
from Bio import SeqIO
from mimetypes import guess_type
from functools import partial
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SequenceSample:
    name: str
    expt_forward_primer: str
    expt_reverse_primer: str
    valiant_meta: Path
    fastq_1: Path
    max_reads: int


@dataclass(frozen=True)
class Transformation:
    effective_fwd: str
    effective_rev: str
    append_fwd: str
    append_rev: str


def reverse_complement(dna_sequence: str) -> str:
    valid_bases = set("ATCG")
    # Check if the input sequence contains only valid DNA bases
    if not set(dna_sequence.upper()).issubset(valid_bases):
        raise ValueError(
            "Input sequence contains invalid characters."
            "Only A, T, C, and G are allowed."
        )
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    reverse_seq = dna_sequence.upper()[::-1]
    reverse_comp = "".join(complement[base] for base in reverse_seq)
    return reverse_comp


class SequenceLibrary:
    def __init__(self, sample: SequenceSample, max_reads: int = 100):
        self.library = sample
        self.max_reads = max_reads
        self.sequences = self._get_target_sequences()
        self.lib_counts = self._count_occurrences(self._csv_reader)
        self.lib_relative_orientation = (
                self._calculate_orientation(self.lib_counts)
        )
        self.fastq_counts = self._count_occurrences(self._fastq_reader)
        self.read_relative_orientation = (
            self._calculate_orientation(self.fastq_counts)
        )
        self.read_transform = self.read_relative_orientation != "fwd"
        transformations = self._calculate_transformations(
            self.lib_relative_orientation,
            self.read_relative_orientation,
            self.library.expt_forward_primer,
            self.library.expt_reverse_primer,
        )
        self.effective_fwd = transformations.effective_fwd
        self.effective_rev = transformations.effective_rev
        self.append_fwd = transformations.append_fwd
        self.append_rev = transformations.append_rev

    def __repr__(self):
        return (
            f"library={self.library!r}\n"
            f"lib_counts={self.lib_counts!r}\n"
            f"fastq_counts={self.fastq_counts!r}\n"
            f"read_transform={self.read_transform!r}\n"
            f"effective_fwd={self.effective_fwd!r}\n"
            f"effective_rev={self.effective_rev!r}"
        )

    def _get_target_sequences(self):
        return [
            self.library.expt_forward_primer,
            self.library.expt_reverse_primer,
            reverse_complement(self.library.expt_forward_primer),
            reverse_complement(self.library.expt_reverse_primer),
        ]

    def _count_occurrences(self, reader_func):
        counts = [0] * len(self.sequences)
        for entry in reader_func():
            for i, seq in enumerate(self.sequences):
                if seq in entry:
                    counts[i] += 1
        return counts

    def _csv_reader(self):
        with self.library.valiant_meta.open("r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row["mseq"]

    def _fastq_reader(self):
        encoding = guess_type(self.library.fastq_1)[1]
        _open = partial(gzip.open, mode="rt") if encoding == "gzip" else open
        with _open(self.library.fastq_1) as handle:
            for i, record in enumerate(SeqIO.parse(handle, "fastq")):
                if i >= self.max_reads:
                    break
                yield str(record.seq)

    def _calculate_orientation(self, counts):
        # counts structure
        # 0 = forward primer
        # 1 = reverse primer
        # 2 = reverse complement(forward primer)
        # 3 = reverse complement(reverse primer)

        count_fwd = counts[0] + counts[3]
        count_rev = counts[1] + counts[2]
        if count_fwd == count_rev:
            msg = (
                f"{self.library.name}: Equal counts detected. "
                "Unable to determine orientation."
            )
            logger.error(msg)
            raise ValueError(msg)
        if count_fwd > count_rev:
            return "fwd"
        if count_fwd < count_rev:
            return "rev"
        else:
            msg = (
                f"{self.library.name}: Unable to determine "
                "orientation of primers, review expt_forward_primer "
                "and expt_reverse_primer sequences."
            )
            logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def _calculate_transformations(
        lib_orientation, read_orientation, fwd_primer, rev_primer
    ):
        if lib_orientation == "rev" and read_orientation == "fwd":
            effective_fwd = fwd_primer
            effective_rev = reverse_complement(rev_primer)
            append_fwd = rev_primer
            append_rev = reverse_complement(fwd_primer)
        elif lib_orientation == "rev" and read_orientation == "rev":
            effective_fwd = rev_primer
            effective_rev = reverse_complement(fwd_primer)
            append_fwd = rev_primer
            append_rev = reverse_complement(fwd_primer)
        elif lib_orientation == "fwd" and read_orientation == "rev":
            effective_fwd = rev_primer
            effective_rev = reverse_complement(fwd_primer)
            append_fwd = fwd_primer
            append_rev = reverse_complement(rev_primer)
        else:
            effective_fwd = fwd_primer
            effective_rev = reverse_complement(rev_primer)
            append_fwd = fwd_primer
            append_rev = reverse_complement(rev_primer)
        return Transformation(
            effective_fwd=effective_fwd,
            effective_rev=effective_rev,
            append_fwd=append_fwd,
            append_rev=append_rev,
        )
