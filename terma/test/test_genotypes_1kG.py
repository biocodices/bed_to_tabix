from os import remove
from os.path import realpath, dirname, join

import pytest

from ..utils import sort_bed


@pytest.fixture
def bedfile():
    return join(dirname(realpath(__file__)), 'files/unsorted.bed')

def test_sort_bed(bedfile):
    outfile = sort_bed(bedfile)

    with open(outfile) as f:
        lines = f.readlines()
        chromosomes = [line.split()[0] for line in lines]
        assert chromosomes == sorted(chromosomes)
        # TODO: Check that the positions are ordered, too.

    remove(outfile)
