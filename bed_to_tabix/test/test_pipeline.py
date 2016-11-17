from os import remove
from os.path import realpath, dirname, join, isfile
import re

import pytest

from bed_to_tabix.lib.pipeline import (sort_bed,
                                       read_bed,
                                       tabix_commands_from_bedfile_df,
                                       run_commands)


TEST_DIR = dirname(realpath(__file__))


@pytest.fixture
def unsorted_bedfile():
    return join(TEST_DIR, 'files/unsorted.bed')

@pytest.fixture
def sorted_bedfile():
    return join(TEST_DIR, 'files/sorted.bed')

@pytest.fixture
def bedfile_df(sorted_bedfile):
    return read_bed(sorted_bedfile)

def test_sort_bed(unsorted_bedfile):
    outfile = sort_bed(unsorted_bedfile)

    with open(outfile) as f:
        lines = f.readlines()
        chromosomes = [line.split()[0] for line in lines]
        assert chromosomes == sorted(chromosomes)
        # TODO: Check that the positions are ordered, too.

    remove(outfile)  # Cleanup

def test_read_bed(sorted_bedfile):
    df = read_bed(sorted_bedfile)
    assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    assert not df.dropna().empty  # Makes sure no datum missing in every entry

    num_lines = sum(1 for line in open(sorted_bedfile))
    assert len(df) == num_lines

def test_tabix_commands_from_bedfile_df(bedfile_df):
    chromosomes = bedfile_df['chrom'].unique()
    commands_to_run = tabix_commands_from_bedfile_df(bedfile_df,
                                                     join(TEST_DIR, 'files'))

    # {tabix_cmd1: dest_file1, tabix_cmd2: dest_file2, ... }
    assert all(cmd['cmd'].startswith('tabix') for cmd in commands_to_run)
    assert all(cmd['dest_file'] in cmd['cmd'] for cmd in commands_to_run)

    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands_to_run]
    assert all(isfile(temp_bedfile) for temp_bedfile in temp_bedfiles)

    for temp_bedfile in temp_bedfiles:
        remove(temp_bedfile)  # Cleanup

#  def test_run_commands(commands):
    #  for command, dest_file in commands_and_dest_files.items():
        #  result = run_tabix_commands(command)

#  def test_run_pipeline(unsorted_bedfile):
    #  assert run_pipeline(unsorted_bedfile)
