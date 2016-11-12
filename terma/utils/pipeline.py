import pandas as pd

from .helpers import make_chromosome_series_categorical


BED_COLUMNS = 'chrom start stop feature'.split()

def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_table(bedfile, names=BED_COLUMNS)
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    df.sort_values(by=['chrom', 'start', 'stop'], inplace=True)
    return df

def extract_gene_from_feature(bedfile_df):
    """
    Parse the feature ID in search of <gene>.chr1... Return a dataframe with a
    new 'gene' column that contains the values of that extraction.
    """
    df = bedfile_df.copy()
    df['gene'] = df['feature'].str.extract(r'(\w+)\.', expand=False)
    return df

