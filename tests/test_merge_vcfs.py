from os.path import isfile, getsize
import gzip

import pytest

from bed_to_tabix.lib import merge_vcfs


def test_merge_vcfs(tmpdir, path_to_bcftools, path_to_bgzip, monkeypatch):
    files = [
        pytest.helpers.file('chr_1.vcf'),
        pytest.helpers.file('chr_2.vcf'),
    ]

    outfile1 = str(tmpdir.join('test_out.vcf.gz'))
    merge_vcfs(files, outfile1,
               path_to_bcftools=path_to_bcftools,
               path_to_bgzip=path_to_bgzip)

    assert isfile(outfile1)
    assert getsize(outfile1) > 0

    with gzip.open(outfile1) as f:
        lines = [l.decode('utf-8') for l in f]
    genotypes = [l for l in lines if not l.startswith('#')]

    assert len(genotypes) == 6
    assert 'rs10' in genotypes[0]
    assert 'rs11' in genotypes[1]
    assert 'rs12' in genotypes[2]
    assert 'rs20' in genotypes[3]
    assert 'rs21' in genotypes[4]
    assert 'rs22' in genotypes[5]

    outfile2 = str(tmpdir.join('test_out.vcf'))
    merge_vcfs(files, outfile2,
               path_to_bcftools=path_to_bcftools,
               path_to_bgzip=path_to_bgzip,
               gzip=False)

    assert isfile(outfile2)
    assert getsize(outfile2) > 0

    with open(outfile2) as f:
        lines = [l for l in f]
    genotypes = [l for l in lines if not l.startswith('#')]

    assert len(genotypes) == 6
    assert 'rs10' in genotypes[0]
    assert 'rs11' in genotypes[1]
    assert 'rs12' in genotypes[2]
    assert 'rs20' in genotypes[3]
    assert 'rs21' in genotypes[4]
    assert 'rs22' in genotypes[5]
