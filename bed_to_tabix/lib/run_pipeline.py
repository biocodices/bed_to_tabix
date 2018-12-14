import time

from humanfriendly import format_timespan

from .logger import logger
from .merge_beds import merge_beds
from .bed_stats import bed_stats
from .tabix_command_from_bedfile_df import tabix_commands_from_bedfile_df
from .run_parallel_commands import run_parallel_commands
from .merge_vcfs import merge_vcfs


def run_pipeline(bedfiles, threads, outfile, path_to_bcftools, gzip=True,
                 dry_run=False, http=False):
    """Get the 1000 Genomes genotypes for the regions in the passed bedfile.
    Return the name of the resulting .vcf.gz file."""
    t0 = time.time()
    logger.info('Read %s' % ', '.join(bedfiles))
    bedfile_df = merge_beds(bedfiles)

    msg = ('Found {n_regions} regions in {n_chromosomes} chromosomes, '
           'spanning {total_bases} bases')
    logger.info(msg.format(**bed_stats(bedfile_df)))

    logger.info('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(bedfile_df, http=http)

    if dry_run:
        logger.info('Dry run! I would run these tabix commands:')
        print(*[command['cmd'] for command in tabix_commands], sep='\n')
        return

    logger.info('Execute tabix in batches of {} to download the '
                '1kG genotypes (this might take a while!)'.format(threads))
    run_parallel_commands(tabix_commands, threads=threads)
    # ^ If any tabix call fails, a CalledProcessError will be raised and
    # execution will stop.
    # TODO: Condiser handling CalledProcessError?

    logger.info('Merge the downloaded .vcf.gz files')
    vcfs = [result['dest_file'] for result in tabix_commands]  # tabix_results
    merge_vcfs(vcfs, outfile, path_to_bcftools, gzip)

    elapsed_time = format_timespan(time.time() - t0)
    logger.info('Done! Took {}. Check {}'.format(elapsed_time, outfile))
