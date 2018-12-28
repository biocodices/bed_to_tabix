import time
import inspect
import shutil
from os.path import dirname

from humanfriendly import format_timespan

from ..lib import (
    logger,
    merge_beds,
    bed_stats,
    tabix_commands_from_bedfile_df,
    run_parallel_commands,
    merge_vcfs,
    cleanup_temp_files,
    fix_zero_length_regions,
)


def run_pipeline(bedfiles,
                 threads,
                 outfile,
                 path_to_bcftools,
                 path_to_tabix,
                 path_to_bgzip,
                 path_to_java,
                 path_to_gatk3,
                 path_to_reference_fasta,
                 merge_chrom_vcfs=True,
                 gzip_output=True,
                 dry_run=False,
                 do_cleanup=True,
                 http=True):
    """
    Take a list of BED files and produce a single VCF file with the genotypes
    of 1KG samples at those coordinates.

    Inputs:

    - bedfiles: a list of BED files with the regions of interest.
    - threads: how many parallel downloads from 1KG servers to run.
    - outfile: path to the VCF that will be produced.
    - path_to...: path to executables of {bcftools,tabix,bgzip}.
    - path_to_reference_fasta: path to the reference .fasta that will be used
      internally by GATK3 CombineVariants to merge 1KG VCFs.
    - gzip_output: should the output be gzipped?
    - dry_run: set to True to only print and return the tabix commands that
      would be run.
    - http: use HTTP URLs, set to false to use FTP URLs from 1KG.
    - do_cleanup: whether to remove the temporary chromosome files or not.
    """
    t0 = time.time()

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    logger.info('Received the following inputs:')
    for arg in args:
        logger.info(f' * {arg} = {values[arg]}')

    regions = merge_beds(bedfiles)

    logger.info('Expand zero-length regions.')
    regions = fix_zero_length_regions(regions)

    msg = ('Found {n_regions} regions in {n_chromosomes} chromosomes, '
           'spanning {total_bases} bases.')
    logger.info(msg.format(**bed_stats(regions)))

    logger.info('Generate the tabix commands for the given regions.')
    tabix_commands = tabix_commands_from_bedfile_df(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        http=http
    )

    if dry_run:
        logger.info('Dry run! I would run these tabix commands:')
        for command in tabix_commands:
            logger.info(f'* {command["cmd"]}')
        return tabix_commands

    logger.info('Execute tabix in batches of {} to download the '
                '1kG genotypes (this might take a while!)'.format(threads))
    command_to_dest_file = {c['cmd']: c['dest_file'] for c in tabix_commands}
    completed_commands = run_parallel_commands(
        list(command_to_dest_file.keys()),
        threads=threads
    )
    for completed_command in completed_commands:
        dest_file = command_to_dest_file[completed_command]
        logger.info(f' * Downloaded: {dest_file}')

    if merge_chrom_vcfs:
        logger.info('Merge the downloaded temporary .vcf.gz files.')
        merge_vcfs(
            gzipped_vcfs=[result['dest_file'] for result in tabix_commands],
            outfile=outfile,
            path_to_java=path_to_java,
            path_to_gatk3=path_to_gatk3,
            path_to_tabix=path_to_tabix,
            path_to_bgzip=path_to_bgzip,
            path_to_reference_fasta=path_to_reference_fasta,
            gzip_output=gzip_output,
        )
    else:
        logger.info('Separate chromosome files requested. Moving from tempdir.')
        for c in tabix_commands:
            out_fn = outfile.replace('.vcf', f'.{c["chromosome"]}.vcf')
            logger.debug(' * {gzipped_chrom_vcf} -> {out_fn}')
            shutil.copy(c['dest_file'], out_fn)

    if do_cleanup:
        cleanup_temp_files()

    elapsed_time = format_timespan(time.time() - t0)
    logger.info('Done! Took {}. Check {}'.format(elapsed_time, outfile))
