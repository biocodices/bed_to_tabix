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

from bed_to_tabix.lib.pipeline import run_pipeline


def main():
    arguments = docopt(__doc__)
    pp(arguments)

    arguments['--in'] = '~/Downloads/testing/test.bed'
    arguments['--out'] = '~/Downloads/testing/test.vcf.gz'
    run_pipeline(bedfile=arguments['--in'], parallel_downloads=5,
                 outfile=arguments['--out'], gzip=bool(arguments['--gzip']))

if __name__ == '__main__':
    main()
