from os.path import join
from functools import partial

import pandas as pd

from .helpers import make_chromosome_series_categorical


BED_COLUMNS = 'chrom start stop feature'.split()
THOUSAND_GENOMES_BASE_URL = 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/'


def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_table(bedfile, names=BED_COLUMNS)
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    df.sort_values(by=['chrom', 'start', 'stop'], inplace=True)
    return df.reset_index(drop=True)


def extract_gene_from_feature(bedfile_df):
    """
    Parse the feature ID in search of <gene>.chr1... Return a dataframe with a
    new 'gene' column that contains the values of that extraction.
    """
    df = bedfile_df.copy()
    df['gene'] = df['feature'].str.extract(r'(\w+)\.', expand=False)
    return df


def tabix_commands_from_bedfile_df(bedfile_df, out_directory):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    func = partial(tabix_command_from_chromosome_regions,
                   out_directory=out_directory)
    commands_and_dest_files = bedfile_df.groupby('chrom').apply(func)

    return dict(commands_and_dest_files)


def tabix_command_from_chromosome_regions(regions_df, out_directory):
    """
    Generate a tabix command to download the regions present in regions_df
    from the given chromosome in The 1000 Genomes FTP servers.

    Returns a tuple: (tabix_command, destination_filepath)
    """
    seen_chromosomes = list(regions_df['chrom'].unique())
    import q; q(regions_df.iloc[0])
    assert len(seen_chromosomes) == 1
    chrom = seen_chromosomes.pop()

    # Create a bed file just with this chromosome's regions
    chrom_bedfile = join('/tmp', 'chr_{0}.bed'.format(chrom))
    regions_df.to_csv(chrom_bedfile, sep='\t', header=False, index=False)

    # Define the destination VCF filename for this chromosome
    dest_file = join(out_directory, 'chr_{0}.vcf.gz'.format(chrom))

    # Generate the tabix command to download 1kG genotypes for this
    # chromosome regions:
    tabix_command = 'tabix -fh -R {0} {1} | bgzip > {2}'
    tabix_command = tabix_command.format(chrom_bedfile,
            thousand_genomes_chromosome_url(chrom), dest_file)
    return tabix_command, dest_file



def thousand_genomes_chromosome_url(chromosome):
    """Generate the chromosome url from 1000 Genomes. Used for tabix."""
    version = 'v5a' if chromosome in [str(n) for n in range(1, 23)] else 'v1b'
    # ^ 1000 Genomes different file naming according to chromosome

    fn = 'ALL.chr{0}.phase3_shapeit2_mvncall_integrated_{1}.20130502.genotypes.vcf.gz'
    return THOUSAND_GENOMES_BASE_URL + fn.format(chromosome, version)

