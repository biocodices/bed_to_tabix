#!/usr/bin/env python
"""
Welcome to BED-TO-TABIX! This tool will download the genotypes from The 1,000
Genomes Proyect's at the regions defined in a .bed file.

Usage:
    bed_to_tabix --in BEDFILE [--out VCFFILE] [--threads N] [--unzipped]
                              [--dry-run] [--http]
    bed_to_tabix (--help | --version)

Options:
    -i BEDFILE, --in BEDFILE    Input .bed file with the genomic regions to
                                download. This is a mandatory argument.

    -o VCFFILE, --out VCFFILE   Output filepath for the VCF. If not set,
                                it will use the input filepath and replace
                                .bed with .vcf.gz. WARNING: if a file with the
                                same filename exists, it will be overwritten.

    -t --threads N              Perform the downloads in N parallel threads.
                                Default: 5. Don't go too high or you might
                                get banned.

    --unzipped                  If set, the downloaded VCF will not be gzipped.

    --dry-run                   If set, it will just print the tabix commands
                                to STDOUT, instead of running them.

    --http                      Use HTTP 1000 Genomes URLs instead of FTP.

    -h --help                   Show this help.
    -v --version                Show version.
"""

import sys
from os.path import dirname
import logging

from docopt import docopt
from beeprint import pp

from bed_to_tabix.package_info import PACKAGE_INFO
from bed_to_tabix.lib.pipeline import run_pipeline


def parse_arguments(arguments):
    if arguments['--version']:
        msg = '{PROGRAM_NAME} {VERSION} ({DATE}) by {AUTHOR}\nCheck: {URL}'
        print(msg.format(**PACKAGE_INFO))
        sys.exit()

    arguments['--threads'] = int(arguments['--threads']) or 5

    if not arguments['--out']:
        arguments['--out'] = arguments['--in'].replace('.bed', '')

    if not arguments['--out'].endswith('.vcf'):
        arguments['--out'] += '.vcf'

    if not arguments['--unzipped']:
        arguments['--out'] += '.gz'

    return arguments


def main():
    arguments = parse_arguments(docopt(__doc__))

    run_pipeline(bedfile=arguments['--in'],
                 parallel_downloads=arguments['--threads'],
                 outfile=arguments['--out'],
                 gzip=(not arguments['--unzipped']),
                 dry_run=arguments['--dry-run'],
                 http=arguments['--http'])


if __name__ == '__main__':
    main()