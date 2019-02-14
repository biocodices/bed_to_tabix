#!/usr/bin/env python
"""
Welcome to bed_to_tabix! This tool will download the genotypes from
The 1,000 Genomes Proyect's in the regions defined in one or more BED files.

Usage:
    bed_to_tabix --in BEDFILE... --outlabel LABEL [options]
    bed_to_tabix (--help | --version)

Options:
    --in BEDFILE...   One or more input .bed file(s) with the genomic
                      regions to download. Mandatory argument(s). Repeat
                      the --in flag with a different .bed each time for more
                      than one input file.

    --outlabel LABEL  Output label for the files. You don't need to add
                      '.vcf' to the label.
                      WARNING: filenames with the same label that match
                      the requested result will be overwritten without asking.

    --threads N       Perform the downloads in N parallel threads. Default: 6.

    --unzipped        If set, the downloaded VCF will not be gzipped.

    --one-vcf-per-chrom      If set, keep separate VCFs per chromosome.
                             Otherwise, the result will be merged in a single
                             multi-chromosome VCF.

    --remove-SVs      Set if you want to remove the structural variants from
                      the downloaded genotypes (sometimes the merge fails if
                      you keep them).

    -f --force        If set, it will overwrite the output file if it exists.

    --dry-run         If set, it will just print the tabix commands to
                      STDOUT, instead of running them.

    --debug           Run in DEBUG logging mode. It will print the comands
                      being run at each step.

    --no-cleanup      Don't remove the temporary files after finishing.
                      Useful for debugging.

    --path-to-bcftools PATH    Full path to bcftools executable.
                               If not present, the ENV variable
                               PATH_TO_BCFTOOLS will be searched for.

    --path-to-tabix PATH       Full path to tabix executable.
                               If not present, the ENV variable
                               PATH_TO_TABIX will be searched for.

    --path-to-bgzip PATH       Full path to bgzip executable.
                               If not present, the ENV variable
                               PATH_TO_BGZIP will be searched for.

    --path-to-java PATH        Full path to java executable.
                               If not present, the ENV variable
                               PATH_TO_JAVA will be searched for.

    --path-to-gatk3 PATH       Full path to gatk3 java file.
                               If not present, the ENV variable
                               PATH_TO_GATK3 will be searched for.

    --path-to-reference-fasta PATH       Full path to the reference fasta for
                                         GATK to use.
                                         If not present, the ENV variable
                                         PATH_TO_REFERENCE_FASTA will be
                                         searched for.

    -h --help         Show this help.
    -v --version      Show version.
"""

import sys
from os import getcwd, environ
from os.path import basename, join
import logging
from subprocess import CalledProcessError

from docopt import docopt
import coloredlogs

from .lib import run_pipeline, cleanup_temp_files, BANNER
from .package_info import PACKAGE_INFO


logger = logging.getLogger(PACKAGE_INFO['PROGRAM_NAME'])

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

    if not arguments['--outlabel']:
        filename = '__'.join(basename(bed).replace('.bed', '')
                             for bed in arguments['--in'])
        arguments['--outlabel'] = join(getcwd(), filename)

    varnames = ['bcftools', 'tabix', 'bgzip', 'gatk3', 'java',
                'reference_fasta']
    for varname in varnames:
        varname = f'path_to_{varname}'
        parameter = '--' + varname.replace('_', '-')
        env_varname = varname.upper()
        if not arguments[parameter]:
            if env_varname in environ:
                arguments[parameter] = environ[env_varname]
            else:
                print(f'Missing either {parameter} ' +
                      f'or ENV variable {env_varname}')
                sys.exit()

    return arguments


def main():
    arguments = parse_arguments(docopt(__doc__))

    logger = logging.getLogger('bed_to_tabix')
    coloredlogs.DEFAULT_LOG_FORMAT = '[@%(hostname)s %(asctime)s] %(message)s'
    loglevel = 'DEBUG' if arguments['--debug'] else 'INFO'
    coloredlogs.install(level=loglevel, logger=logger)

    print(BANNER)

    failed_exit = False
    try:
        run_pipeline(
            bedfiles=arguments['--in'],
            threads=arguments['--threads'],
            outlabel=arguments['--outlabel'],
            one_vcf_per_chrom=arguments['--one-vcf-per-chrom'],
            remove_SVs=arguments['--remove-SVs'],
            gzip_output=(not arguments['--unzipped']),
            dry_run=arguments['--dry-run'],
            path_to_bcftools=arguments['--path-to-bcftools'],
            path_to_java=arguments['--path-to-java'],
            path_to_tabix=arguments['--path-to-tabix'],
            path_to_gatk3=arguments['--path-to-gatk3'],
            path_to_bgzip=arguments['--path-to-bgzip'],
            path_to_reference_fasta=arguments['--path-to-reference-fasta'],
            no_cleanup=arguments['--no-cleanup'],
            # The FTP option is failing and is not fixed yet:
            # http=arguments['--http'],
        )
    except KeyboardInterrupt:
        logger.warning('User stopped the program. Cleanup and exit.')
        failed_exit = True
        sys.exit()
    except CalledProcessError as e:
        message = e.args[0] # This message comes from run_shell_command.py
        logger.error(message)
        failed_exit = True
        sys.exit()
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit()
    finally:
        if failed_exit:
            do_cleanup(arguments)

def do_cleanup(arguments):
    if arguments['--no-cleanup']:
        logger.info('No cleanup requested, leaving the temp files.')
    else:
        logger.info('Cleaning up temporary files.')
        cleanup_temp_files()


if __name__ == '__main__':
    main()
