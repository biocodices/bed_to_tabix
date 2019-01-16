from os.path import basename

from ..lib import run_shell_command


def merge_vcfs(gzipped_vcfs, outlabel, path_to_reference_fasta, path_to_bgzip,
               path_to_tabix, path_to_gatk3, path_to_java, gzip_output=True):
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

    # Index the different chrom .gz files
    for gzipped_vcf in gzipped_vcfs:
        command = f'{path_to_tabix} -f {gzipped_vcf}'
        run_shell_command(command)

    # Merge the files
    command = (f'{path_to_java} -jar {path_to_gatk3} ' +
               f'-T CombineVariants ' +
               f'-R {path_to_reference_fasta} ')

    tags = [basename(gzipped_vcf) for gzipped_vcf in gzipped_vcfs]
    for gzipped_vcf, tag in zip(gzipped_vcfs, tags):
        command += f'--variant:{tag},VCF {gzipped_vcf} '

    command += (f'--genotypemergeoption PRIORITIZE '+
                f'-priority {",".join(tags)} ' +
                f'-o {out_vcf}')

    run_shell_command(command)

    if gzip_output:
        gzip_command = f'{path_to_bgzip} -c {out_vcf} > {out_vcf}.gz'
        run_shell_command(gzip_command)

    return f'{out_vcf}.gz' if gzip_output else out_vcf
