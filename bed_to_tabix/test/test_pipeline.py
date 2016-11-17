from os import remove
from os.path import realpath, dirname, join, isfile
import re

import pytest

from bed_to_tabix.lib.pipeline import (read_bed,
                                       tabix_commands_from_bedfile_df,
                                       run_commands)


TEST_DIR = dirname(realpath(__file__))


@pytest.fixture
def unsorted_bedfile():
    return join(TEST_DIR, 'files/unsorted.bed')

@pytest.fixture
def bedfile_df(unsorted_bedfile):
    return read_bed(unsorted_bedfile)

def clean_temp_bedfiles(commands):
    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands]

    for temp_bedfile in temp_bedfiles:
        remove(temp_bedfile)

def test_read_bed(unsorted_bedfile):
    df = read_bed(unsorted_bedfile)
    assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    assert not df.dropna().empty  # Makes sure no datum missing in every entry

    num_lines = sum(1 for line in open(unsorted_bedfile))
    assert len(df) == num_lines

def test_tabix_commands_from_bedfile_df(bedfile_df):
    commands_to_run = tabix_commands_from_bedfile_df(bedfile_df,
                                                     join(TEST_DIR, 'files'))

    assert all(cmd['cmd'].startswith('tabix') for cmd in commands_to_run)
    assert all(cmd['dest_file'] in cmd['cmd'] for cmd in commands_to_run)

    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands_to_run]
    assert all(isfile(temp_bedfile) for temp_bedfile in temp_bedfiles)

    clean_temp_bedfiles(commands_to_run)

def test_tabix_commands_with_gzip(bedfile_df):
    commands_to_run = tabix_commands_from_bedfile_df(
            bedfile_df, join(TEST_DIR, 'files'), gzip=True)

    assert all('bgzip >' in cmd['cmd'] for cmd in commands_to_run)

    clean_temp_bedfiles(commands_to_run)

def test_tabix_commands_(bedfile_df):
    commands_to_run = tabix_commands_from_bedfile_df(bedfile_df,
                                                     join('/tmp', 'testing'))

    assert all('/tmp/testing' in cmd['cmd'] for cmd in commands_to_run)

    clean_temp_bedfiles(commands_to_run)

#  def test_run_commands(commands):
    #  for command, dest_file in commands_and_dest_files.items():
        #  result = run_tabix_commands(command)

#  def test_run_pipeline(unsorted_bedfile):
    #  assert run_pipeline(unsorted_bedfile)
