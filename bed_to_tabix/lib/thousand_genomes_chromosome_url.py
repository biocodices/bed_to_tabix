from .constants import THOUSAND_GENOMES_FTP, THOUSAND_GENOMES_HTTP


def thousand_genomes_chromosome_url(chromosome, http=False):
    """Generate the chromosome url from 1000 Genomes. Used for tabix."""
    if chromosome == 'X':
        fn = 'ALL.chrX.phase3_shapeit2_mvncall_integrated_v1b.20130502.genotypes.vcf.gz'
    elif chromosome == 'Y':
        fn = 'ALL.chrY.phase3_integrated_v2a.20130502.genotypes.vcf.gz'
    else:
        fn = 'ALL.chr{0}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'
        fn = fn.format(chromosome)

    base_url = THOUSAND_GENOMES_HTTP if http else THOUSAND_GENOMES_FTP
    return base_url + fn
