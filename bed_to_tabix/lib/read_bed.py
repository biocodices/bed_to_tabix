import pandas as pd

from ..lib import BED_COLUMNS
from ..lib import make_chromosome_series_categorical


def read_bed(bedfile):
    """Read a bedfile and return a pd.DataFrame with the regions."""
    df = pd.read_csv(bedfile, sep=r"\s+", names=BED_COLUMNS)
    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    return df
