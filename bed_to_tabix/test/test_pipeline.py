from os import remove
from os.path import realpath, dirname, join, isfile, getsize
import re

from bed_to_tabix.lib.pipeline import (read_bed,
                                       tabix_commands_from_bedfile_df,
                                       run_parallel_commands,
                                       merge_vcfs)
from bed_to_tabix.lib.helpers import thousand_genomes_chromosome_url


TEST_DIR = dirname(realpath(__file__))


def _test_filename(filename):
    return join(TEST_DIR, filename)


UNSORTED_BEDFILE = _test_filename('files/unsorted.bed')


def vcfs():
    return [_test_filename('files/chr_9.vcf.gz'),
            _test_filename('files/chr_10.vcf.gz')]


def clean_temp_bedfiles(commands):
    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands]

    for temp_bedfile in temp_bedfiles:
        remove(temp_bedfile)


def test_thousand_genomes_chromosome_url():
    result = thousand_genomes_chromosome_url('1')
    assert result == 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'

    result = thousand_genomes_chromosome_url('X')
    assert result == 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrX.phase3_shapeit2_mvncall_integrated_v1b.20130502.genotypes.vcf.gz'

    result = thousand_genomes_chromosome_url('Y')
    assert result == 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrY.phase3_integrated_v2a.20130502.genotypes.vcf.gz'


def test_read_bed():
    df = read_bed(UNSORTED_BEDFILE)
    assert all(df.columns == ['chrom', 'start', 'stop', 'feature'])
    assert 'Y' not in df['chrom'].values
    assert not df.dropna().empty  # Makes sure no datum missing in every entry

    num_lines = sum(1 for line in open(UNSORTED_BEDFILE))

    assert len(df) == num_lines - 1
    # NOTE: -1 because I'm removing the entry of the Y chromosome now!


def test_tabix_commands_from_bedfile_df():
    bedfile_df = read_bed(UNSORTED_BEDFILE)
    commands_to_run = tabix_commands_from_bedfile_df(bedfile_df)

    assert len(commands_to_run) == 23  # All chromosomes in the test file

    temp_bedfiles = [re.search(r'-R (.+\.bed) ', cmd['cmd']).group(1)
                     for cmd in commands_to_run]

    try:
        assert all(cmd['cmd'].startswith('tabix') for cmd in commands_to_run)
        assert all(cmd['dest_file'] in cmd['cmd'] for cmd in commands_to_run)
        assert all(isfile(temp_bedfile) for temp_bedfile in temp_bedfiles)
    finally:
        clean_temp_bedfiles(commands_to_run)


def test_run_parallel_commands():
    commands_to_run = [{'cmd': 'pwd > /dev/null'}]
    run_parallel_commands(commands_to_run, threads=2)
    # No assertions. If the commands fail, CalledProcessError will be raised.


def test_merge_vcfs(tmpdir):
    outfile1 = str(tmpdir.join('test_out.vcf.gz'))
    merge_vcfs(vcfs(), outfile1)

    outfile2 = str(tmpdir.join('test_out.vcf'))
    merge_vcfs(vcfs(), outfile2, gzip=False)

    assert isfile(outfile1)
    assert getsize(outfile1) > 0

    assert isfile(outfile2)
    assert getsize(outfile2) > 0

    # TODO:
    # Test that the variants are the same in the in and out files!
    # Test that the samples are the same!
