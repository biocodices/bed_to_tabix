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


def sort_bed(bedfile, outfile=None):
    """Sort a .bed file and produce a new .bed in the same directory. Pass an
    absolute path to put it in another directory."""
    bedpath = abspath(expanduser(bedfile))

    if outfile is None:
        # If the file doesn't end in .bed, this will just add .sorted.bed
        outfile = basename(bedpath).replace('.bed', '') + '.sorted.bed'

    outpath = join(dirname(bedpath), outfile)

    # TODO: do the sorting with pandas, forget bedtools
    command_args = 'bedtools sort -i {}'.format(bedpath).split()
    with open(outpath, 'w') as f:
        run(command_args, stdout=f, check=True)

    return outpath


def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_table(bedfile, names=BED_COLUMNS)
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    df.sort_values(by=['chrom', 'start', 'stop'], inplace=True)
    return df.reset_index(drop=True)


#  def extract_gene_from_feature(bedfile_df):
    #  """
    #  Parse the feature ID in search of <gene>.chr1... Return a dataframe with a
    #  new 'gene' column that contains the values of that extraction.
    #  """
    #  df = bedfile_df.copy()
    #  df['gene'] = df['feature'].str.extract(r'(.+)\.', expand=False)
    #  return df


def tabix_commands_from_bedfile_df(bedfile_df, out_directory):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    func = partial(tabix_command_from_chromosome_regions,
                   out_directory=out_directory)

    commands_to_run = []
    for chrom, regions_df in bedfile_df.groupby('chrom'):
        command_to_run = tabix_command_from_chromosome_regions(regions_df,
                out_directory=out_directory)
        commands_to_run.append(command_to_run)

    return commands_to_run


def tabix_command_from_chromosome_regions(regions_df, out_directory):
    """
    Generate a tabix command to download the regions present in regions_df
    from the given chromosome in The 1000 Genomes FTP servers.

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
    tabix_command = 'tabix -fh -R {0} {1} | bgzip > {2}'
    tabix_command = tabix_command.format(chrom_bedfile,
            thousand_genomes_chromosome_url(chrom), dest_file)

    return {'cmd': tabix_command, 'dest_file': dest_file}


def run_commands(commands_to_run):
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

    threads = max(13, len(commands_to_run))
    with ThreadPoolExecutor(max_workers=threads) as pool:
        results = pool.map(syscall, commands_to_run)

        for result in results:
            pp(result.get())

    return results

