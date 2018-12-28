from os.path import isfile
import gzip

import pytest
import logging

from bed_to_tabix.lib import run_pipeline


def test_run_pipeline(path_to_tabix, path_to_bcftools, path_to_bgzip,
                      path_to_java, path_to_gatk3, path_to_reference_fasta,
                      tmpdir, caplog):

    caplog.set_level(logging.DEBUG)

    fn = pytest.helpers.file('real_regions_to_test.bed')
    out_fn = str(tmpdir.join('out.vcf.gz'))

    args = dict(
        bedfiles=[fn],
        threads=8,
        outfile=out_fn,
        merge_chrom_vcfs=True,
        path_to_java=path_to_java,
        path_to_gatk3=path_to_gatk3,
        path_to_reference_fasta=path_to_reference_fasta,
        path_to_bgzip=path_to_bgzip,
        path_to_tabix=path_to_tabix,
        path_to_bcftools=path_to_bcftools,
    )

    ##### Dry run

    args['dry_run'] = True
    result = run_pipeline(**args)

    for cmd in result:
        print(cmd)

    assert not isfile(out_fn)
    assert len(result) == 3 # Three tabix commands to run for three chromosomes

    variants_expected = [
        'rs200162368',
        'rs268',
        'rs35661435',
    ]
    samples_expected = [
        'HG00096', # male sample (it will be present in chrY VCF)
        'NA21135', # male sample (it will be present in chrY VCF)
    ]

    ##### HTTP URLs and gzipped output

    args['dry_run'] = False
    args['http'] = True
    args['gzip_output'] = True
    run_pipeline(**args)

    with gzip.open(out_fn) as f:
        content = f.read().decode('utf-8')

    for item in samples_expected + variants_expected:
        assert item in content

    ##### HTTP URLs, gzipped output, don't merge the result

    out_fn = str(tmpdir.join('out.vcf'))

    args['outfile'] = out_fn
    args['merge_chrom_vcfs'] = False
    run_pipeline(**args)

    for chrom, snp in zip(['Y', '8', 'X'], variants_expected):
        chrom_fn = out_fn.replace('.vcf', f'.{chrom}.vcf')
        print(chrom_fn)
        with gzip.open(chrom_fn) as f:
            content = f.read().decode('utf-8')

        assert snp in content

        for sample in samples_expected:
            assert sample in content

    ##### FTP URLs and non-gzipped output

    out_fn = str(tmpdir.join('out-nonzipped.vcf'))
    args['merge_chrom_vcfs'] = True
    args['outfile'] = out_fn
    args['http'] = False
    args['gzip_output'] = False
    run_pipeline(**args)

    with open(out_fn) as f:
        content = f.read()

    for item in samples_expected + variants_expected:
        assert item in content
