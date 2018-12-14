from subprocess import check_output, STDOUT


def merge_vcfs(vcfs, outfile, path_to_bcftools, gzip=True):
    """
    Merge a list of VCF files by calling bcftools. Return the filename of the
    resulting VCF, gzipped by default.
    """
    command_to_run = '{} concat {} > {}'.format(
        path_to_bcftools, ' '.join(vcfs), outfile
    )

    if gzip:
        command_to_run = command_to_run.replace('>', '| bgzip >')

    check_output(command_to_run, shell=True, stderr=STDOUT)
    return outfile
