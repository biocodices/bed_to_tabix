from os.path import join


def thousand_genomes_chromosome_url(chromosome, http=False, local_dir=None):
    """Generate the chromosome url from 1000 Genomes. Used for tabix.
    If *local_dir* is provided, use vcf files from a local directory instead
    of the 1KG servers. If *http* is True, use http URLs instead of ftp."""
    if chromosome == 'X':
        variable_part = 'phase3_shapeit2_mvncall_integrated_v1b'
    elif chromosome == 'Y':
        variable_part = 'phase3_integrated_v2a'
    else:
        variable_part = 'phase3_shapeit2_mvncall_integrated_v5a'
    filename = f'ALL.chr{chromosome}.{variable_part}.20130502.genotypes.vcf.gz'

    if local_dir:
        return join(local_dir, filename)
    else:
        protocol = 'http' if http else 'ftp'
        domain = 'ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502'
        return f'{protocol}://{domain}/{filename}'
