_base_path = 'ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/'
THOUSAND_GENOMES_FTP = 'ftp://' + _base_path
THOUSAND_GENOMES_HTTP = 'http://' + _base_path
THOUSAND_GENOMES_TBI_PATTERN = 'ALL.chr*.phase3_shapeit*.vcf.gz.tbi'


def make_chromosome_series_categorical(series):
    """
    Receives a pandas Series with chromosomes and returns a new categorical
    Series with the same values.
    """
    new_series = series.astype(str)  # Creates a new copy of the series
    if all(new_series.str.startswith('chr')):
        new_series = new_series.str.replace('chr', '')

    new_series = new_series.replace('23', 'X').replace('24', 'Y').astype(str)
    chromosomes = [str(chrom) for chrom in list(range(1, 23)) + ['X', 'Y']
                   if str(chrom) in new_series.values]
    new_series = new_series.astype('category', categories=chromosomes,
                                   ordered=True)
    return new_series


def thousand_genomes_chromosome_url(chromosome, http=False):
    """Generate the chromosome url from 1000 Genomes. Used for tabix."""
    version = 'v5a' if chromosome in [str(n) for n in range(1, 23)] else 'v1b'
    # ^ 1000 Genomes different file naming according to chromosome

    fn = 'ALL.chr{0}.phase3_shapeit2_mvncall_integrated_{1}.20130502.genotypes.vcf.gz'
    base_url = THOUSAND_GENOMES_HTTP if http else THOUSAND_GENOMES_FTP
    return base_url + fn.format(chromosome, version)
