#!/usr/bin/env python

from os.path import dirname
import logging

from pipeline import (read_bed,
                      extract_gene_from_feature,
                      tabix_commands_from_bedfile_df,
                      run_commands)


logger = logging.getLogger('terma')
logging.basicConfig(level=logging.DEBUG)


def run_pipeline(bedfile):
    """Get the 1000 Genomes genotypes for 2,504 samples for the regions in the
    passed bedfile. Return the name of the new .vcf.gz."""
    logger.debug('Read "%s" into a DataFrame' % bedfile)
    bedfile_df = read_bed(bedfile)

    logger.debug('Extract the "gene" column from the bed df')
    bedfile_df = extract_gene_from_feature(bedfile_df)

    logger.debug('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df,
            out_directory=dirname(bedfile))

    logger.debug('Execute the tabix commands to download 1kG genotypes')
    ran_commands = run_commands(tabix_commands)

    #  print(len(bedfile_df['gene'].unique()), 'genes tested')
    #  pp(tabix_commands)
    return True


if __name__ == '__main__':
    run_pipeline('~/Downloads/testing/test.bed')

