from os import remove
from os.path import isfile
import re

import pytest

from bed_to_tabix.lib.pipeline import (read_bed,
                                       tabix_commands_from_bedfile_df,
                                       run_parallel_commands,
                                       merge_vcfs)


UNSORTED_BEDFILE = pytest.helpers.file('unsorted.bed')
PATH_TO_BCFTOOLS = pytest.helpers.file('bcftools')



def test_read_bed():
    df = read_bed(UNSORTED_BEDFILE)
    assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    assert 'Y' not in df['chrom'].values
    assert not df.dropna().empty  # Makes sure no datum missing in every entry

    num_lines = sum(1 for line in open(UNSORTED_BEDFILE))

    assert len(df) == num_lines - 1
    # NOTE: -1 because I'm removing the entry of the Y chromosome now!




def test_run_parallel_commands():
    commands_to_run = [{'cmd': 'pwd > /dev/null'}]
    run_parallel_commands(commands_to_run, threads=2)
    # No assertions. If the commands fail, CalledProcessError will be raised.

