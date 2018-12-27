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

    outfile1 = str(tmpdir.join('test_out.vcf.gz'))
    merge_vcfs(gzipped_copies,
               outfile1,
               path_to_java=path_to_java,
               path_to_tabix=path_to_tabix,
               path_to_gatk3=path_to_gatk3,
               path_to_reference_fasta=path_to_reference_fasta,
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
    merge_vcfs(gzipped_copies,
               outfile2,
               path_to_java=path_to_java,
               path_to_tabix=path_to_tabix,
               path_to_gatk3=path_to_gatk3,
               path_to_reference_fasta=path_to_reference_fasta,
               path_to_bgzip=path_to_bgzip,
               gzip_output=False)

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
