import re

import pytest
import pandas as pd

from bed_to_tabix.lib import tabix_command_from_chromosome_regions


def test_tabix_command_from_chromosome_regions(path_to_tabix, path_to_bgzip,
                                               path_to_bcftools):
    regions = pd.DataFrame({'chrom': ['1', '1']})
    result = tabix_command_from_chromosome_regions(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        path_to_bcftools=path_to_bcftools,
        remove_SVs=True,
        http=True,
        local_dir='/path/to/1KG'
    )

    assert re.search(
        r'.*tabix -fh -R .*chr_1.bed http.* | *.bcftools filter *. | .*bgzip .*chr_1.vcf.gz',
        result['cmd']
    )
    assert result['chrom_bedfile'].endswith('chr_1.bed')
    assert result['dest_file'].endswith('chr_1.vcf.gz')
    assert result['chromosome'] == '1'
    assert '/path/to/1KG' in result['cmd']
    assert 'ftp.1000genomes.ebi.ac.uk' not in result['cmd']

    result = tabix_command_from_chromosome_regions(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        path_to_bcftools=path_to_bcftools,
        http=False,
    )
    assert 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release' in result['cmd']

    regions = pd.DataFrame({'chrom': ['1', '2']})
    with pytest.raises(AssertionError):
        tabix_command_from_chromosome_regions(
            regions,
            path_to_tabix=path_to_tabix,
            path_to_bgzip=path_to_bgzip,
            path_to_bcftools=path_to_bcftools,
            http=True
        )
