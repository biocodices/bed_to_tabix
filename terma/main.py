#!/usr/bin/env python

from utils import read_bed, extract_gene_from_feature


def run_pipeline(bedfile):
    df = read_bed(bedfile)
    df = extract_gene_from_feature(df)

    print(len(df['gene'].unique()), 'genes tested')
    return True

run_pipeline('~/Downloads/testing/test.sorted.bed')

