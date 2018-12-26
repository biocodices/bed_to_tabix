from bed_to_tabix.lib import run_shell_command


def merge_vcfs(vcfs, outfile, path_to_bcftools, path_to_bgzip, gzip=True):
    """
    Merge a list of VCF files by calling bcftools. Return the filename of the
    resulting VCF, gzipped by default.
    """
    joined_vcfs = ' '.join(vcfs)
    command = f'{path_to_bcftools} concat {joined_vcfs} > {outfile}'

    if gzip:
        command = command.replace('>', f'| {path_to_bgzip} >')

    run_shell_command(command)
    return outfile
