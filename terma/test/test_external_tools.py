from os import remove
from os.path import realpath, dirname, join

import pytest

from ..utils import *


FIXTURE_DIR = dirname(realpath(__file__))


@pytest.fixture
def unsorted_bedfile():
    return join(FIXTURE_DIR, 'files/unsorted.bed')


@pytest.fixture
def sorted_bedfile():
    return join(FIXTURE_DIR, 'files/sorted.bed')


def test_sort_bed(unsorted_bedfile):
    outfile = sort_bed(unsorted_bedfile)

    with open(outfile) as f:
        lines = f.readlines()
        chromosomes = [line.split()[0] for line in lines]
        assert chromosomes == sorted(chromosomes)
        # TODO: Check that the positions are ordered, too.

    remove(outfile)

def test_read_bed(sorted_bedfile):
    df = read_bed(sorted_bedfile)
    assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    assert not df.dropna().empty  # Makes sure no datum missing in every entry

    num_lines = sum(1 for line in open(sorted_bedfile))
    assert len(df) == num_lines

