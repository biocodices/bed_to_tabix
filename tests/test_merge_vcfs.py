from os.path import isfile, getsize

import pytest

from bed_to_tabix.lib import merge_vcfs


def test_merge_vcfs(tmpdir):
    VCFs = [pytest.helpers.file(fn)
            for fn in ['chr_9.vcf.gz', 'chr_10.vcf.gz']]

    outfile1 = str(tmpdir.join('test_out.vcf.gz'))
    merge_vcfs(VCFs, outfile1, path_to_bcftools=PATH_TO_BCFTOOLS)

    outfile2 = str(tmpdir.join('test_out.vcf'))
    merge_vcfs(VCFs, outfile2, path_to_bcftools=PATH_TO_BCFTOOLS, gzip=False)

    assert isfile(outfile1)
    assert getsize(outfile1) > 0

    assert isfile(outfile2)
    assert getsize(outfile2) > 0

    # TODO:
    # Test that the variants are the same in the in and out files!
    # Test that the samples are the same!
