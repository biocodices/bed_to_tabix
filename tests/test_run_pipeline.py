from os import remove
from os.path import isfile

import pandas as pd


def test_run_pipeline():
    pass
    #  assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    #  assert 'Y' not in df['chrom'].values
    #  assert not df.dropna().empty  # Makes sure no datum missing in every entry

    #  num_lines = sum(1 for line in open(UNSORTED_BEDFILE))

    #  assert len(df) == num_lines - 1
