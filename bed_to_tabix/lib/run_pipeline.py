import time

from humanfriendly import format_timespan

from bed_to_tabix.lib import (
    logger,
    merge_beds,
    bed_stats,
    tabix_commands_from_bedfile_df,
    run_parallel_commands,
    merge_vcfs,
)


def run_pipeline(bedfiles,
                 threads,
                 outfile,
                 path_to_bcftools,
                 path_to_tabix,
                 path_to_bgzip,
                 gzip_output=True,
                 dry_run=False,
                 http=False):
    """
    Take a list of BED files and produce a single VCF file with the genotypes
    of 1KG samples at those coordinates.

    Inputs:

    - bedfiles: a list of BED files with the regions of interest.
    - threads: how many parallel downloads from 1KG servers to run.
    - outfile: path to the VCF that will be produced.
    - path_to...: path to executables of {bcftools,tabix,bgzip}.
    - gzip_output: should the output be gzipped?
    - dry_run: set to True to only print and return the tabix commands that
      would be run.
    - http: use HTTP URLs instead of FTP from 1KG.
    """
    t0 = time.time()
    logger.info('Read:\n\n' + '\n'.join(bedfiles) + '\n\n')
    regions = merge_beds(bedfiles)

    msg = ('Found {n_regions} regions in {n_chromosomes} chromosomes, '
           'spanning {total_bases} bases')
    logger.info(msg.format(**bed_stats(regions)))

    logger.info('Generate the tabix commands for the given regions')
    tabix_commands = tabix_commands_from_bedfile_df(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        http=http
    )

    if dry_run:
        logger.info('Dry run! I would run these tabix commands:')
        logger.info(*[command['cmd'] for command in tabix_commands], sep='\n')
        return tabix_commands

    logger.info('Execute tabix in batches of {} to download the '
                '1kG genotypes (this might take a while!)'.format(threads))
    run_parallel_commands([c['cmd'] for c in tabix_commands],
                          threads=threads)
    # ^ If any tabix call fails, a CalledProcessError will be raised and
    # execution will stop.
    # TODO: Condiser handling CalledProcessError?

    logger.info('Merge the downloaded .vcf.gz files')
    vcfs = [result['dest_file'] for result in tabix_commands]  # tabix_results
    merge_vcfs(
        vcfs,
        outfile,
        path_to_bcftools=path_to_bcftools,
        path_to_bgzip=path_to_bgzip,
        gzip=gzip_output,
    )

    elapsed_time = format_timespan(time.time() - t0)
    logger.info('Done! Took {}. Check {}'.format(elapsed_time, outfile))
