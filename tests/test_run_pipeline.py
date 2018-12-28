from os.path import isfile
import gzip

import pytest
import logging

from bed_to_tabix.lib import run_pipeline


@pytest.fixture
def args(path_to_bcftools, path_to_bgzip, path_to_java,
                      path_to_gatk3, path_to_reference_fasta, path_to_tabix,
                      caplog, tmpdir):

    caplog.set_level(logging.DEBUG)

    return dict(
        bedfiles=[pytest.helpers.file('real_regions_to_test.bed')],
        outlabel = str(tmpdir.join('out')),
        threads=8,
        path_to_java=path_to_java,
        path_to_gatk3=path_to_gatk3,
        path_to_reference_fasta=path_to_reference_fasta,
        path_to_bgzip=path_to_bgzip,
        path_to_tabix=path_to_tabix,
        path_to_bcftools=path_to_bcftools,
    )


variants_expected = [
    'rs200162368',
    'rs268',
    'rs35661435',
] # This order of variants is used below! Chromosomes: Y, 8, X

samples_expected = [
    'HG00096', # male sample (it will be present in chrY VCF)
    'NA21135', # male sample (it will be present in chrY VCF)
]


def test_run_pipeline_dry_run(tmpdir, args):
    args['dry_run'] = True

    result = run_pipeline(**args)

    assert not isfile(tmpdir.join('out.vcf.gz'))
    assert not isfile(tmpdir.join('out.vcf'))
    assert all('cmd' in cmd for cmd in result) # Commands
    assert len(result) == 3 # Three tabix commands to run for three chromosomes

def test_run_pipeline_http_gzipped_out(tmpdir, args):
    args['dry_run'] = False
    args['http'] = True
    args['gzip_output'] = True
    args['remove_SVs'] = True
    args['one_vcf_per_chrom'] = False

    run_pipeline(**args)

    with gzip.open(tmpdir.join('out.vcf.gz')) as f:
        content = f.read().decode('utf-8')

    for item in samples_expected + variants_expected:
        assert item in content

    # This variant overlaps with rs268, so it's downloaded with it.
    # Here, we check it was removed:
    assert 'esv3616553' not in content

    # Check the merged BED is also written
    bed_out = tmpdir.join('out.merged-sorted-expanded.bed')
    assert isfile(bed_out)

def test_run_pipeline_dont_merge_result(tmpdir, args):
    outlabel = str(tmpdir.join('out.vcf.gz')) # Check extra ".vcf.gz" is handled

    args['outlabel'] = outlabel
    args['one_vcf_per_chrom'] = True

    run_pipeline(**args)

    for chrom, snp in zip(['Y', '8', 'X'], variants_expected):
        expected_chrom_fn = tmpdir.join(f'out.chr{chrom}.vcf.gz')
        with gzip.open(expected_chrom_fn) as f:
            content = f.read().decode('utf-8')

        assert snp in content

        for sample in samples_expected:
            assert sample in content

def test_run_pipeline_ftp_non_gzipped_output(tmpdir, args):
    outlabel = str(tmpdir.join('out-nonzipped'))

    args['one_vcf_per_chrom'] = False
    args['outlabel'] = outlabel
    args['http'] = False
    args['gzip_output'] = False

    run_pipeline(**args)

    expected_fn = tmpdir.join('out-nonzipped.vcf')
    with open(expected_fn) as f:
        content = f.read()

    for item in samples_expected + variants_expected:
        assert item in content
