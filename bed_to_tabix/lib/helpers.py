from itertools import zip_longest


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
    if chromosome == 'X':
        fn = 'ALL.chrX.phase3_shapeit2_mvncall_integrated_v1b.20130502.genotypes.vcf.gz'
    elif chromosome == 'Y':
        fn = 'ALL.chrY.phase3_integrated_v2a.20130502.genotypes.vcf.gz'
    else:
        fn = 'ALL.chr{0}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'
        fn = fn.format(chromosome)

    base_url = THOUSAND_GENOMES_HTTP if http else THOUSAND_GENOMES_FTP
    return base_url + fn


def grouped(the_list, group_size):
    """Return a list items in groups of group_size."""
    groups = zip_longest(*(iter(the_list), ) * group_size)
    groups = [list(group) for group in groups]
    for group in groups:
        if None in group:
            group.remove(None)
    return groups


def bed_stats(bedfile_df):
    stats = {
            'n_regions': len(bedfile_df),
            'total_bases': bedfile_df.apply(
                lambda row: row['stop'] - row['start'], axis=1).sum(),
            'n_chromosomes': len(bedfile_df['chrom'].unique())
        }
    return stats

