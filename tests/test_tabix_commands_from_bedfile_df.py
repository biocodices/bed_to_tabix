import re
from os import remove
from os.path import isfile

import pandas as pd

from bed_to_tabix.lib import tabix_commands_from_bedfile_df


def clean_temp_bedfiles(commands):
    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands]

    for temp_bedfile in temp_bedfiles:
        remove(temp_bedfile)


def test_tabix_commands_from_bedfile_df(path_to_tabix, path_to_bgzip, path_to_bcftools):
    regions = pd.DataFrame({
        'chrom': ['1', '2', 'X', 'Y'] # 4 chromosomes => 4 download commands
    })

    commands_to_run = tabix_commands_from_bedfile_df(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        path_to_bcftools=path_to_bcftools,
        remove_SVs=True,
        http=False
    )

    assert len(commands_to_run) == 4  # the 4 chromosomes from the regions above

    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands_to_run]

    try:
        assert all('tabix' in cmd['cmd'] for cmd in commands_to_run)
        assert all('filter' in cmd['cmd'] for cmd in commands_to_run)
        assert all(cmd['dest_file'] in cmd['cmd'] for cmd in commands_to_run)
        assert all(isfile(temp_bedfile) for temp_bedfile in temp_bedfiles)
    finally:
        clean_temp_bedfiles(commands_to_run)
