import shutil
from os.path import isfile, getsize, basename
import gzip
import logging
import subprocess

import pytest

from bed_to_tabix.lib import merge_vcfs


def test_merge_vcfs(tmpdir, path_to_java, path_to_gatk3, path_to_bgzip,
                    path_to_tabix, path_to_reference_fasta, monkeypatch,
                    caplog):

    caplog.set_level(logging.DEBUG)

    # Merge_vcfs takes gzipped VCFs, but it's easier to test with plain text
    # files to modify them whenever you need to, so here I gzip them for
    # the test. However, this test depends on bgzip now.
    vcfs = [
        pytest.helpers.file('chr_1.vcf'),
        pytest.helpers.file('chr_2.vcf'),
    ]
    copies = [str(tmpdir.join(basename(vcf))) for vcf in vcfs]
    gzipped_copies = [f'{copy}.gz' for copy in copies]

    for vcf, copy, gzipped_copy in zip(vcfs, copies, gzipped_copies):
        print(f'[Test preparation] Copy: {vcf} -> {copy}')
        shutil.copy(vcf, copy)

        command = f'{path_to_bgzip} -c {copy} > {gzipped_copy}'
        print(f'[Test preparation] Compress: {command}')
        subprocess.check_output(command, shell=True)

    outlabel1 = str(tmpdir.join('test_out_1'))
    merge_vcfs(gzipped_copies,
               outlabel=outlabel1,
               gzip_output=True,
               path_to_java=path_to_java,
               path_to_tabix=path_to_tabix,
               path_to_gatk3=path_to_gatk3,
               path_to_reference_fasta=path_to_reference_fasta,
               path_to_bgzip=path_to_bgzip)

    expected_vcf = f'{outlabel1}.vcf.gz'
    assert isfile(expected_vcf)
    assert getsize(expected_vcf) > 0

    with gzip.open(expected_vcf) as f:
        lines = [l.decode('utf-8') for l in f]
    genotypes = [l for l in lines if not l.startswith('#')]

    assert len(genotypes) == 6
    assert 'rs10' in genotypes[0]
    assert 'rs11' in genotypes[1]
    assert 'rs12' in genotypes[2]
    assert 'rs20' in genotypes[3]
    assert 'rs21' in genotypes[4]
    assert 'rs22' in genotypes[5]

    outlabel2 = str(tmpdir.join('test_out_2'))
    merge_vcfs(gzipped_copies,
               outlabel=outlabel2,
               gzip_output=False,
               path_to_java=path_to_java,
               path_to_tabix=path_to_tabix,
               path_to_gatk3=path_to_gatk3,
               path_to_reference_fasta=path_to_reference_fasta,
               path_to_bgzip=path_to_bgzip)

    expected_fn = f'{outlabel2}.vcf'
    assert isfile(expected_fn)
    assert getsize(expected_fn) > 0

    with open(expected_fn) as f:
        lines = [l for l in f]
    genotypes = [l for l in lines if not l.startswith('#')]

    assert len(genotypes) == 6
    assert 'rs10' in genotypes[0]
    assert 'rs11' in genotypes[1]
    assert 'rs12' in genotypes[2]
    assert 'rs20' in genotypes[3]
    assert 'rs21' in genotypes[4]
    assert 'rs22' in genotypes[5]
