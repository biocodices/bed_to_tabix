#!/usr/bin/env python
"""
Welcome to BED TO TABIX! This tool will download the genotypes from The 1000
Genomes Proyect 2,504 samples at the regions defined in a .bed file.

Usage:

    bed_to_tabix BEDFILE

Options:
    -h --help       Show this help.
    -v --version    Show version.
"""

from os.path import dirname
import logging

from docopt import docopt
from beeprint import pp

from bed_to_tabix.lib.pipeline import (sort_bed,
                                       read_bed,
                                       #  extract_gene_from_feature,
                                       tabix_commands_from_bedfile_df,
                                       run_commands)


logger = logging.getLogger('bed_to_tabix')
logging_format = '[{asctime}] {levelname:8} {message}'
logging.basicConfig(level=logging.DEBUG, format=logging_format, style='{')


def run_pipeline(bedfile):
    """Get the 1000 Genomes genotypes for 2,504 samples for the regions in the
    passed bedfile. Return the name of the new .vcf.gz."""
    logger.debug('Sort %s' % bedfile)
    sorted_bedfile = sort_bed(bedfile)

    logger.debug('Read "%s" into a DataFrame' % sorted_bedfile)
    bedfile_df = read_bed(sorted_bedfile)

    #  logger.debug('Extract the "gene" column from the bed df')
    #  bedfile_df = extract_gene_from_feature(bedfile_df)

    logger.debug('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df,
            out_directory=dirname(bedfile))

    logger.debug('Execute the tabix commands to download 1kG genotypes')
    ran_commands = run_commands(tabix_commands)

    #  print(len(bedfile_df['gene'].unique()), 'genes tested')
    #  pp(tabix_commands)
    return True

def main():
    arguments = docopt(__doc__)
    pp(arguments)
    run_pipeline('~/Downloads/testing/test.bed')

if __name__ == '__main__':
    main()
