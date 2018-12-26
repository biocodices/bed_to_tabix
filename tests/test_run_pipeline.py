from tempfile import gettempdir
from os import remove, getpid
from os.path import isfile, join
import gzip

import pytest

from bed_to_tabix.lib import run_pipeline


def make_tempfile():
    return join(gettempdir(),
                f'bed_to_tabix_test__run_pipeline_{getpid()}.vcf.gz')


def test_run_pipeline(path_to_tabix, path_to_bcftools, path_to_bgzip):
    fn = pytest.helpers.file('real_regions_to_test.bed')
    out_fn = make_tempfile()

    args = dict(
        bedfiles=[fn],
        threads=8,
        outfile=out_fn,
        path_to_bgzip=path_to_bgzip,
        path_to_tabix=path_to_tabix,
        path_to_bcftools=path_to_bcftools,
    )

    args['dry_run'] = True
    result = run_pipeline(**args)

    assert not isfile(out_fn)
    assert len(result) == 2 # Two tabix commands to run

    args['dry_run'] = False
    args['http'] = True
    args['gzip_output'] = True
    run_pipeline(**args)

    with gzip.open(out_fn) as f:
        content = f.read().decode('utf-8')

    assert 'rs268' in content
    assert 'HG00096' in content

    args['http'] = False
    run_pipeline(**args)

    assert 'rs268' in content
    assert 'HG00096' in content

    assert 0
    # Cleanup
    remove(out_fn)
