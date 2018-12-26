import pandas as pd


_CHROM_LIST = [str(chrom) for chrom in list(range(1, 23)) + ['X', 'Y', 'MT']]


def make_chromosome_series_categorical(series):
    """
    Receives a pandas Series with chromosomes and returns a new categorical
    Series with the same values. Removes "chr" from chromosome names and
    replaces 23 for X and 24 for Y.
    """
    new_series = series.astype(str)  # Creates a new copy of the series
    new_series = new_series.str.replace('chr', '')
    new_series = new_series.replace('23', 'X').replace('24', 'Y').astype(str)
    sorted_chromosomes = [c for c in _CHROM_LIST if c in new_series.values]

    return pd.Categorical(
        new_series,
        categories=sorted_chromosomes,
        ordered=True
    )
