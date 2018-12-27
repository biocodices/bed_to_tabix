from os.path import isfile
import gzip

import pytest

from bed_to_tabix.lib import run_pipeline


def test_run_pipeline(path_to_tabix, path_to_bcftools, path_to_bgzip,
                      path_to_java, path_to_gatk3, path_to_reference_fasta,
                      tmpdir):
    fn = pytest.helpers.file('real_regions_to_test.bed')
    out_fn = str(tmpdir.join('out.vcf.gz'))

    args = dict(
        bedfiles=[fn],
        threads=8,
        outfile=out_fn,
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
        'HG00096',
        'NA21144',
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

    ##### FTP URLs and non-gzipped output

    out_fn = str(tmpdir.join('out-nonzipped.vcf'))
    args['outfile'] = out_fn
    args['http'] = False
    args['gzip_output'] = False
    run_pipeline(**args)

    with open(out_fn) as f:
        content = f.read()

    for item in samples_expected + variants_expected:
        assert item in content
