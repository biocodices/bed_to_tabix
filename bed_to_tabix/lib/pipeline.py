from os import remove, getpid
from os.path import basename, join
from concurrent.futures import ThreadPoolExecutor, as_completed
from subprocess import check_output, CalledProcessError, STDOUT
import time
import logging
from glob import glob

import pandas as pd
from humanfriendly import format_timespan

from bed_to_tabix.package_info import PACKAGE_INFO
from bed_to_tabix.lib.helpers import (make_chromosome_series_categorical,
                                      grouped,
                                      bed_stats,
                                      thousand_genomes_chromosome_url,
                                      THOUSAND_GENOMES_TBI_PATTERN)


TEMP_PREFIX = '{}_{}'.format(PACKAGE_INFO['PROGRAM_NAME'], getpid())
TEMP_DIR = '/tmp'
BED_COLUMNS = 'chrom start stop feature'.split()

logger = logging.getLogger(PACKAGE_INFO['PROGRAM_NAME'])


def run_pipeline(bedfiles, threads, outfile, gzip=True,
                 dry_run=False, http=False):
    """Get the 1000 Genomes genotypes for the regions in the passed bedfile.
    Return the name of the resulting .vcf.gz file."""
    t0 = time.time()
    logger.info('Read %s' % ', '.join(bedfiles))
    bedfile_df = read_beds(bedfiles)

    msg = ('Found {n_regions} regions in {n_chromosomes} chromosomes, '
           'spanning {total_bases} bases')
    logger.info(msg.format(**bed_stats(bedfile_df)))

    logger.info('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df, http=http)

    if dry_run:
        logger.info('Dry run! I would run these tabix commands:')
        print(*[command['cmd'] for command in tabix_commands], sep='\n')
        return

    logger.info('Execute tabix in batches of {} to download the '
                '1kG genotypes (this might take a while!)'.format(threads))
    run_parallel_commands(tabix_commands, threads=threads)
    # ^ If any tabix call fails, a CalledProcessError will be raised and
    # execution will stop.
    # TODO: Condiser handling CalledProcessError?

    logger.info('Merge the downloaded .vcf.gz files')
    vcfs = [result['dest_file'] for result in tabix_commands]  # tabix_results
    merge_vcfs(vcfs, outfile, gzip)

    elapsed_time = format_timespan(time.time() - t0)
    logger.info('Done! Took {}. Check {}'.format(elapsed_time, outfile))


def read_beds(bedfiles):
    """Read a list of bedfiles and return a pandas DataFrame with no dupes."""
    frames = [read_bed(bedfile) for bedfile in bedfiles]
    bedfile_df = pd.concat(frames).reset_index(drop=True)
    bedfile_df.drop_duplicates(subset=BED_COLUMNS[:3], inplace=True)
    bedfile_df.sort_values(by=BED_COLUMNS, inplace=True)
    return bedfile_df


def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_table(bedfile, names=BED_COLUMNS)

    if 'Y' in df['chrom'].values or 'chrY' in df['chrom'].values:
        in_chrom_Y = df['chrom'].isin(['Y', 'chrY'])
        logger.warn('Removing {} regions in chromosome "Y"!'
                    .format(len(df[in_chrom_Y])))
        df = df[~in_chrom_Y].reset_index(drop=True)

    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    return df


def tabix_commands_from_bedfile_df(bedfile_df, http=False):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    commands_to_run = []
    for chrom, regions_df in bedfile_df.groupby('chrom'):
        if not len(regions_df):
            continue
        command_to_run = tabix_command_from_chromosome_regions(regions_df,
                                                               http=http)
        commands_to_run.append(command_to_run)

    return commands_to_run


def tabix_command_from_chromosome_regions(regions_df, http=False):
    """
    Generate a tabix command to download the regions present in regions_df
    from the given chromosome in The 1000 Genomes servers via FTP or HTTP.

    Returns a tuple: (tabix_command, destination_filepath)
    """
    # Make sure there's only one chromosome in the regions_df
    seen_chromosomes = list(regions_df['chrom'].unique())
    assert len(seen_chromosomes) == 1
    chrom = seen_chromosomes.pop()

    # Create a temporary bed file with this chromosome's regions
    # It will be used in the tabix command
    chrom_bedfile = temp_filepath('chr_{0}.bed'.format(chrom))
    regions_df.to_csv(chrom_bedfile, sep='\t', header=False, index=False)

    # Define the destination VCF filename for this chromosome
    dest_file = temp_filepath('chr_{}.vcf.gz'.format(chrom))

    chrom_1kg_url = thousand_genomes_chromosome_url(chrom, http)
    # Generate the tabix command to download 1kG genotypes for these regions
    tabix_command = 'tabix -fh -R {0} {1} | bgzip > {2}'.format(
            chrom_bedfile, chrom_1kg_url, dest_file)

    chrom_index_file = basename(chrom_1kg_url) + '.tbi'

    return {'cmd': tabix_command,
            'dest_file': dest_file,
            'chrom_bedfile': chrom_bedfile,
            'chrom_index_file': chrom_index_file}


def run_parallel_commands(commands_to_run, threads):
    """
    Expects a list of dicts with the commands to run and the destination files:

        [{'cmd': command_1, 'dest_file': dest_file_1},
         {'cmd': command_2, 'dest_file': dest_file_2},
          ... ]

    Will run the commands in N threads and return a new list with the same
    entries and a 'success' key:

        [{'cmd': command_1, 'dest_file': dest_file_1, 'success': True},
         ... ]

    """
    def syscall(command):
        ix = id(command['cmd'])
        logger.debug('Running command {}: {}'.format(ix, command['cmd']))
        output = check_output(command['cmd'], shell=True, stderr=STDOUT)
        logger.debug('Output {}: {}'.format(ix, output.decode('utf-8')))

    threads = min(threads, len(commands_to_run))
    for group_of_commands in grouped(commands_to_run, group_size=threads):
        # I have to group the commands in groups of size=threads before using
        # ThreadPoolExecutor because otherwise the extra commands can't be
        # easily stopped with CTRL-C or whenever an Exception is raised.
        with ThreadPoolExecutor(len(group_of_commands)) as executor:
            results = executor.map(syscall, group_of_commands)
            list(results)  # raises Exception from any of the threads


def merge_vcfs(vcfs, outfile, gzip=True):
    """
    Merge a list of VCF files by calling bcftools. Return the filename of the
    resulting VCF, gzipped by default.
    """
    command_to_run = 'bcftools concat {} > {}'.format(' '.join(vcfs), outfile)

    if gzip:
        command_to_run = command_to_run.replace('>', '| bgzip >')

    check_output(command_to_run, shell=True, stderr=STDOUT)

    return outfile


def cleanup_temp_files():
    """Remove all temp BED, VCF and tbi files found."""
    for fn in sorted(glob(join(TEMP_DIR, TEMP_PREFIX + '*'))):
        logger.debug('Cleanup: remove {}'.format(fn))
        remove(fn)

    # The .tbi files are downloaded to the directory where tabix is run,
    # not to the destination directory of the VCF, so I have to remove them
    # from there.
    for fn in glob(THOUSAND_GENOMES_TBI_PATTERN):
        remove(fn)

def temp_filepath(filename):
    return join(TEMP_DIR, '{}__{}'.format(TEMP_PREFIX, filename))

