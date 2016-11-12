def make_chromosome_series_categorical(series):
    """
    Receives a pandas Series with chromosomes and returns a new categorical
    Series with the same values.
    """
    chromosomes = [str(chrom) for chrom in range(1, 23)] + ['X', 'Y']
    new_series = series.replace(23, 'X').replace(24, 'Y').astype(str)
    new_series = new_series.astype('category', categories=chromosomes,
                                   ordered=True)
    return new_series

