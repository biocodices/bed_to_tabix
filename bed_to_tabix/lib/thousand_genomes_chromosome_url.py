def thousand_genomes_chromosome_url(chromosome, http=False):
    """Generate the chromosome url from 1000 Genomes. Used for tabix."""
    if chromosome == 'X':
        variable_part = 'phase3_shapeit2_mvncall_integrated_v1b'
    elif chromosome == 'Y':
        variable_part = 'phase3_integrated_v2a'
    else:
        variable_part = 'phase3_shapeit2_mvncall_integrated_v5a'

    protocol = 'http' if http else 'ftp'
    domain = 'ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502'
    fn = f'ALL.chr{chromosome}.{variable_part}.20130502.genotypes.vcf.gz'

    return f'{protocol}://{domain}/{fn}'
