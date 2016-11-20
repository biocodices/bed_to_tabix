from os import system, remove
from os.path import expanduser, abspath, dirname, basename, join
from concurrent.futures import ThreadPoolExecutor
import time
import datetime
import logging

import coloredlogs
import pandas as pd

from bed_to_tabix.lib.helpers import (make_chromosome_series_categorical,
                                      thousand_genomes_chromosome_url)


BED_COLUMNS = 'chrom start stop feature'.split()

logger = logging.getLogger('bed_to_tabix')
#  logging.basicConfig(level=logging.INFO)
coloredlogs.DEFAULT_LOG_FORMAT = '[@%(hostname)s %(asctime)s] %(message)s'
coloredlogs.install(level='INFO')


def run_pipeline(bedfiles, parallel_downloads, outfile, gzip=True,
                 dry_run=False, http=False):
    """Get the 1000 Genomes genotypes for the regions in the passed bedfile.
    Return the name of the resulting .vcf.gz file."""
    t0 = time.time()
    logger.info('Read %s' % ', '.join(bedfiles))
    bedfile_df = read_beds(bedfiles)

    logger.info('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df,
            out_directory=dirname(outfile), http=http)

    if dry_run:
        logger.info('Dry run! I would run these tabix commands:')
        print(*[command['cmd'] for command in tabix_commands], sep='\n')
        return

    logger.info('Execute the tabix commands to download 1kG genotypes')
    tabix_results = run_commands(tabix_commands,
                                 parallel_downloads=parallel_downloads)

    logger.info('Merge the downloaded .vcf.gz files:')
    vcfs = [result['dest_file'] for result in tabix_commands]  # tabix_results
    result_vcf = merge_vcfs(vcfs, outfile, gzip)

    logger.info('Clean the temp bedfiles and the partial VCF files')
    clean_tempfiles(tabix_commands)

    elapsed_time = datetime.timedelta(seconds=time.time() - t0)
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
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    return df.reset_index(drop=True)


def tabix_commands_from_bedfile_df(bedfile_df, out_directory, http=False):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    commands_to_run = []
    for chrom, regions_df in bedfile_df.groupby('chrom'):
        command_to_run = tabix_command_from_chromosome_regions(regions_df,
                out_directory=out_directory, http=http)
        commands_to_run.append(command_to_run)

    return commands_to_run


def tabix_command_from_chromosome_regions(regions_df, out_directory, http=False):
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
    chrom_bedfile = join('/tmp', 'chr_{0}.bed'.format(chrom))
    regions_df.to_csv(chrom_bedfile, sep='\t', header=False, index=False)

    # Define the destination VCF filename for this chromosome
    dest_file = join(out_directory, 'chr_{0}.vcf.gz'.format(chrom))

    chrom_1kg_url = thousand_genomes_chromosome_url(chrom, http)
    # Generate the tabix command to download 1kG genotypes for these regions
    tabix_command = 'tabix -fh -R {0} {1} | bgzip > {2}'.format(
            chrom_bedfile, chrom_1kg_url, dest_file)

    chrom_index_file = basename(chrom_1kg_url) + '.tbi'

    return {'cmd': tabix_command,
            'dest_file': dest_file,
            'chrom_bedfile': chrom_bedfile,
            'chrom_index_file': chrom_index_file}


def run_commands(commands_to_run, parallel_downloads):
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
        logger.info('Running command: %s' % command['cmd'])
        exit_status = system(command['cmd'])
        command_with_result = dict(command)
        command_with_result.update({'exit_status': exit_status})
        return command_with_result

    with ThreadPoolExecutor(max_workers=parallel_downloads) as pool:
        results = pool.map(syscall, commands_to_run)

    return list(results)


def merge_vcfs(vcfs, outfile, gzip=True):
    """
    Merge a list of VCF files by calling bcftools. Return the filename of the
    resulting VCF, gzipped by default.
    """
    command_to_run = 'bcftools concat {} > {}'.format(' '.join(vcfs), outfile)

    if gzip:
        command_to_run = command_to_run.replace('>', '| bgzip >')

    logger.info('Running: %s' % command_to_run)
    system(command_to_run)

    return outfile


def clean_tempfiles(tabix_commands):
    """Remove .vcf.gz.tbi index files and single chromosome VCF files."""
    for tabix_command in tabix_commands:
        from beeprint import pp; pp(tabix_command)
        remove(tabix_command['dest_file'])
        remove(tabix_command['chrom_bedfile'])
        remove(tabix_command['chrom_index_file'])
