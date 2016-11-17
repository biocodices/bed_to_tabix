from os import system
from os.path import expanduser, abspath, dirname, basename, join
from functools import partial
from subprocess import run
from concurrent.futures import ThreadPoolExecutor
import logging

import pandas as pd
from beeprint import pp

from bed_to_tabix.lib.helpers import (make_chromosome_series_categorical,
                                      thousand_genomes_chromosome_url)


BED_COLUMNS = 'chrom start stop feature'.split()

logger = logging.getLogger('bed_to_tabix')
logging_format = '[{asctime}] {levelname}: {message}'
logging.basicConfig(level=logging.DEBUG, format=logging_format, style='{')


def run_pipeline(bedfile, parallel_downloads, outfile, gzip=True,
                 dry_run=False, http=False):
    """Get the 1000 Genomes genotypes for the regions in the passed bedfile.
    Return the name of the resulting .vcf.gz file."""
    logger.debug('Read "%s" into a DataFrame' % bedfile)
    bedfile_df = read_bed(bedfile)

    logger.debug('Sort the DataFrame by chromosome and position')
    bedfile_df.sort_values(by=BED_COLUMNS, inplace=True)

    logger.debug('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df,
            out_directory=dirname(bedfile), gzip=gzip, http=http)

    if dry_run:
        logger.debug('Dry run! I would run these tabix commands:')
        print(*[command['cmd'] for command in tabix_commands], sep='\n')
        return

    logger.debug('Execute the tabix commands to download 1kG genotypes')
    tabix_results = run_commands(tabix_commands,
                                 parallel_downloads=parallel_downloads)

    # TODO:
    # logger.debug('Merge the downloaded .vcf.gz files')
    # result_vcf = merge_results(tabix_results, outfile, gzip)

    # TODO:
    # logger.debug('Clean the temp bedfiles and the partial VCF files.')
    # clean_tempfiles(tabix_commands)



def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_table(bedfile, names=BED_COLUMNS)
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    return df.reset_index(drop=True)


def tabix_commands_from_bedfile_df(bedfile_df, out_directory, gzip=True,
                                   http=False):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    commands_to_run = []
    for chrom, regions_df in bedfile_df.groupby('chrom'):
        command_to_run = tabix_command_from_chromosome_regions(regions_df,
                out_directory=out_directory, gzip=gzip, http=http)
        commands_to_run.append(command_to_run)

    return commands_to_run


def tabix_command_from_chromosome_regions(regions_df, out_directory, gzip,
        http=False):
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

    # Generate the tabix command to download 1kG genotypes for these regions
    tabix_command = 'tabix -fh -R {0} {1} > {2}'.format(chrom_bedfile,
            thousand_genomes_chromosome_url(chrom, http), dest_file)

    if gzip:
        tabix_command = tabix_command.replace('>', '| bgzip >')

    return {'cmd': tabix_command, 'dest_file': dest_file,
            'chrom_bedfile': chrom_bedfile}


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
        logger.debug('Running command: %s' % command['cmd'])
        result = system(command['cmd'])
        return dict(command).update({'exit_status': result})

    with ThreadPoolExecutor(max_workers=parallel_downloads) as pool:
        results = pool.map(syscall, commands_to_run)

        for result in results:
            pp(result.get())

    return results

def merge_results(tabix_commands):
    pass

def clean_tempfiles(tabix_commands):
    pass
