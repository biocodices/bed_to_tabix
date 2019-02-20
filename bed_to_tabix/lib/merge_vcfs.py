from os.path import basename

from ..lib import run_shell_command


def merge_vcfs(gzipped_vcfs, outlabel, path_to_bcftools,
               path_to_reference_fasta, path_to_bgzip, path_to_tabix,
               path_to_gatk3, path_to_java, gzip_output=True):
    """
    Merge a list of gzipped VCF files that might have shared samples.
    Meant to merge non-overlapping regions (like different chromosomes).
    The result is written as {outlabel}.vcf(.gz)?

    *outlabel* should not include ".vcf" or ".gz".

    Important note: reference contig names and gzipped_vcfs contig names must
    match. Otherwise, the output will have no genotypes!

    Return the filename of the resulting VCF, gzipped by default.
    """
    out_vcf = f'{outlabel}.vcf'
    sorted_gzipped_vcfs = [f.replace('.vcf', '.sorted.vcf')
                           for f in gzipped_vcfs]

    # Sort the different chrom .gz files (necessary for tabix to index)
    for gzipped_vcf, sorted_gzipped_vcf in zip(gzipped_vcfs, sorted_gzipped_vcfs):
        command = f'{path_to_bcftools} sort {gzipped_vcf} | ' + \
                  f'{path_to_bgzip} -c > {sorted_gzipped_vcf}'
        run_shell_command(command)

    # Index the different chrom gzipped sorted files
    for sorted_gzipped_vcf in sorted_gzipped_vcfs:
        command = f'{path_to_tabix} -f {sorted_gzipped_vcf}'
        run_shell_command(command)

    # Merge the files
    command = (f'{path_to_java} -jar {path_to_gatk3} ' +
               f'-T CombineVariants ' +
               f'-R {path_to_reference_fasta} ')

    tags = [basename(fn) for fn in sorted_gzipped_vcfs]
    for sorted_gzipped_vcf, tag in zip(sorted_gzipped_vcfs, tags):
        command += f'--variant:{tag},VCF {sorted_gzipped_vcf} '

    command += (f'--genotypemergeoption PRIORITIZE '+
                f'-priority {",".join(tags)} ' +
                f'-o {out_vcf}')

    run_shell_command(command)

    if gzip_output:
        gzip_command = f'{path_to_bgzip} -c {out_vcf} > {out_vcf}.gz'
        run_shell_command(gzip_command)

    return f'{out_vcf}.gz' if gzip_output else out_vcf
