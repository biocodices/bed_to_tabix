import re

import pytest
import pandas as pd

from bed_to_tabix.lib import tabix_command_from_chromosome_regions


def test_tabix_command_from_chromosome_regions(path_to_tabix, path_to_bgzip):
    regions = pd.DataFrame({'chrom': ['1', '1']})
    result = tabix_command_from_chromosome_regions(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        http=True
    )

    assert re.search(
        r'.*tabix -fh -R .*chr_1.bed http.* | .*bgzip .*chr_1.vcf.gz',
        result['cmd']
    )
    assert result['chrom_bedfile'].endswith('chr_1.bed')
    assert result['dest_file'].endswith('chr_1.vcf.gz')
    assert result['chromosome'] == '1'

    result = tabix_command_from_chromosome_regions(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        http=False,
    )
    assert 'http' not in result['cmd']
    assert 'ftp' in result['cmd']

    regions = pd.DataFrame({'chrom': ['1', '2']})
    with pytest.raises(AssertionError):
        tabix_command_from_chromosome_regions(
            regions,
            path_to_tabix=path_to_tabix,
            path_to_bgzip=path_to_bgzip,
            http=True
        )
