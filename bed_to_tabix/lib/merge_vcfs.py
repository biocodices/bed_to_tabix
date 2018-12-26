from subprocess import check_output, STDOUT, CalledProcessError

from bed_to_tabix.lib import logger


def merge_vcfs(vcfs, outfile, path_to_bcftools, path_to_bgzip, gzip=True):
    """
    Merge a list of VCF files by calling bcftools. Return the filename of the
    resulting VCF, gzipped by default.
    """
    joined_vcfs = ' '.join(vcfs)
    command = f'{path_to_bcftools} concat {joined_vcfs} > {outfile}'

    if gzip:
        command = command.replace('>', f'| {path_to_bgzip} >')

    logger.info(f'Running: {command}')
    try:
        check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        error = e.stdout.decode('utf-8')
        message = f'Command:\n\n{command}\n\nFailed with message:\n\n{error}'
        raise CalledProcessError(message)

    return outfile
