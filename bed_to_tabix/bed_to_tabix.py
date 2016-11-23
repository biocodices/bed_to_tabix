#!/usr/bin/env python
"""
Welcome to BED-TO-TABIX! This tool will download the genotypes from The 1,000
Genomes Proyect's at the regions defined in one or more .bed files.

Usage:
    bed_to_tabix --in BEDFILE... [--out VCFFILE] [--threads N] [--unzipped]
                                 [--dry-run] [--http]
    bed_to_tabix (--help | --version)

Options:
    --in BEDFILE...   One or more input .bed file(s) with the genomic
                      regions to download. Mandatory argument(s). Repeat
                      the --in flag with a different .bed each time for more
                      than one input file.

    --out VCFFILE     Output filepath for the VCF. You don't need to add
                      '.vcf' to the name. If not set, bed_to_tabix will
                      use the input filepath and replace .bed with .vcf.gz.
                      WARNING: if a file with the same filename exists, it
                      will be overwritten.

    --threads N       Perform the downloads in N parallel threads. Default: 6.

    --unzipped        If set, the downloaded VCF will not be gzipped.

    --dry-run         If set, it will just print the tabix commands to
                      STDOUT, instead of running them.

    --http            Use HTTP 1000 Genomes URLs instead of FTP.

    -h --help         Show this help.
    -v --version      Show version.
"""

import sys
from os import getcwd
from os.path import dirname, basename, join
import logging

from docopt import docopt
from beeprint import pp

from bed_to_tabix.package_info import PACKAGE_INFO
from bed_to_tabix.lib.pipeline import run_pipeline


defaults = {
        '--threads': 6,
    }

def parse_arguments(arguments):
    if arguments['--version']:
        msg = '{PROGRAM_NAME} {VERSION} ({DATE}) by {AUTHOR}\nCheck: {URL}'
        print(msg.format(**PACKAGE_INFO))
        sys.exit()

    if arguments['--threads']:
        arguments['--threads'] = int(arguments['--threads'])
    else:
        arguments['--threads'] = defaults['--threads']

    if not arguments['--out']:
        filename = '__'.join(basename(bed).replace('.bed', '')
                             for bed in arguments['--in'])
        arguments['--out'] = join(getcwd(), filename)

    if not arguments['--out'].endswith('.vcf'):
        arguments['--out'] += '.vcf'

    if not arguments['--unzipped']:
        arguments['--out'] += '.gz'

    return arguments


def main():
    arguments = parse_arguments(docopt(__doc__))

    run_pipeline(bedfiles=arguments['--in'],
                 parallel_downloads=arguments['--threads'],
                 outfile=arguments['--out'],
                 gzip=(not arguments['--unzipped']),
                 dry_run=arguments['--dry-run'],
                 http=arguments['--http'])


if __name__ == '__main__':
    main()
