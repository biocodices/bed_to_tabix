#!/usr/bin/env python

from os.path import dirname

from beeprint import pp

from utils import *


def run_pipeline(bedfile):
    bedfile_df = read_bed(bedfile)
    bedfile_df = extract_gene_from_feature(bedfile_df)
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df,
            out_directory=dirname(bedfile))

    print(len(df['gene'].unique()), 'genes tested')
    pp(tabix_commands)
    return True

run_pipeline('~/Downloads/testing/test.bed')

