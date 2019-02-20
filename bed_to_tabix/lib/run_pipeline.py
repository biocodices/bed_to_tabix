import time
import inspect
import shutil

from humanfriendly import format_timespan

from ..lib import (
    logger,
    merge_beds,
    bed_stats,
    tabix_commands_from_bedfile_df,
    run_parallel_commands,
    merge_vcfs,
    cleanup_temp_files,
    expand_zero_length_regions,
)


def run_pipeline(bedfiles,
                 threads,
                 outlabel,
                 path_to_bcftools,
                 path_to_tabix,
                 path_to_bgzip,
                 path_to_java,
                 path_to_gatk3,
                 path_to_reference_fasta,
                 one_vcf_per_chrom=False,
                 remove_SVs=True,
                 gzip_output=True,
                 dry_run=False,
                 no_cleanup=False,
                 http=True):
    """
    Take a list of BED files and produce one (or one per chrom) VCF file with
    the genotypes of 1KG samples at those coordinates. Also produces the
    BED resulting from the merge/sort/zero-length-region-expansion of the
    input BEDs.

    Inputs:

    - bedfiles: a list of BED files with the regions of interest.
    - threads: how many parallel downloads from 1KG servers to run.
    - outlabel: path to the VCF prefix that will be produced. Do not include
      ".vcf" in the name, it's just the prefix that will be used wither for
      one or many VCFs and for the merged BED.
    - one_vcf_per_chrom: set to True if you want separate VCF files per
      chromosome. Otherwise, the result will be merged in a single VCF.
    - remove_SVs: whether to remove structural variants or not from the
      downloaded genotypes. SVs sometimes give problems when merging the
      1000 Genomes VCFs.
    - path_to...: path to executables of {bcftools,tabix,bgzip,gatk3,java}.
    - path_to_reference_fasta: path to the reference .fasta that will be used
      internally by GATK3 CombineVariants to merge 1KG VCFs.
    - gzip_output: should the output be gzipped? This only applies to the
      merged output. The separate chrom VCFs are always gzipped.
    - dry_run: set to True to only print and return the tabix commands that
      would be run.
    - http: use HTTP URLs, set to false to use FTP URLs from 1KG.
    - no_cleanup: set to True if you want to leave the temporary chromosome
      files (useful for debugging).
    """
    t0 = time.time()

    outlabel = outlabel.replace('.vcf', '').replace('.gz', '')

    if one_vcf_per_chrom and not gzip_output:
        logger.warning('`gzip_output` requested, but the VCFs per chromosome ' +
                       'will be gzipped (that option works for the merged VCF)')

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    logger.info('Received the following inputs:')
    for arg in args:
        logger.info(f' * {arg} = {values[arg]}')

    regions = merge_beds(bedfiles)

    logger.info('Expand zero-length regions.')
    regions = expand_zero_length_regions(regions)

    msg = ('Found {n_regions} regions in {n_chromosomes} chromosomes, '
           'spanning {total_bases} bases.')
    logger.info(msg.format(**bed_stats(regions)))

    bed_out = f'{outlabel}.merged-sorted-expanded.bed'
    regions.to_csv(bed_out, index=False, sep='\t')
    logger.info(f'Written merged/sorted/expanded BED to: {bed_out}')

    logger.info('Generate the tabix commands for the given regions.')
    tabix_commands = tabix_commands_from_bedfile_df(
        regions,
        path_to_tabix=path_to_tabix,
        path_to_bgzip=path_to_bgzip,
        path_to_bcftools=path_to_bcftools,
        remove_SVs=remove_SVs,
        http=http,
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

    if one_vcf_per_chrom:
        logger.info('Separate chromosome files requested. Moving from tempdir.')
        for c in tabix_commands:
            out_fn = f'{outlabel}.chr{c["chromosome"]}.vcf.gz'
            logger.debug(f' * {c["dest_file"]} -> {out_fn}')
            shutil.copy(c['dest_file'], out_fn)
    else:
        logger.info('Merge the downloaded temporary .vcf.gz files.')
        merge_vcfs(
            gzipped_vcfs=[result['dest_file'] for result in tabix_commands],
            outlabel=outlabel,
            path_to_bcftools=path_to_bcftools,
            path_to_java=path_to_java,
            path_to_gatk3=path_to_gatk3,
            path_to_tabix=path_to_tabix,
            path_to_bgzip=path_to_bgzip,
            path_to_reference_fasta=path_to_reference_fasta,
            gzip_output=gzip_output,
        )

    if not no_cleanup:
        cleanup_temp_files()

    elapsed_time = format_timespan(time.time() - t0)
    logger.info(f'Done! Took {elapsed_time}. Check {outlabel}*')
