import re
from os import remove
from os.path import isfile

import pytest

from bed_to_tabix.lib import read_bed
from bed_to_tabix.lib import tabix_commands_from_bedfile_df


def clean_temp_bedfiles(commands):
    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands]

    for temp_bedfile in temp_bedfiles:
        remove(temp_bedfile)


def test_tabix_commands_from_bedfile_df():
    unsorted_bed = pytest.helpers.file('usorted.bed')
    bedfile_df = read_bed(unsorted_bed)
    commands_to_run = tabix_commands_from_bedfile_df(bedfile_df)

    assert len(commands_to_run) == 23  # All chromosomes in the test file

    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands_to_run]

    try:
        assert all(cmd['cmd'].startswith('tabix') for cmd in commands_to_run)
        assert all(cmd['dest_file'] in cmd['cmd'] for cmd in commands_to_run)
        assert all(isfile(temp_bedfile) for temp_bedfile in temp_bedfiles)
    finally:
        clean_temp_bedfiles(commands_to_run)
