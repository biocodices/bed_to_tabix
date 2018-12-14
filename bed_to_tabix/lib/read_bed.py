import pandas as pd

from .constants import BED_COLUMNS
from .helpers import logger
from .make_chromosome_series_categorical import make_chromosome_series_categorical


def read_bed(bedfile):
    """Read a bedfile and return a pandas DataFrame with the features."""
    df = pd.read_csv(bedfile, sep=r"\s+", names=BED_COLUMNS)

    if 'Y' in df['chrom'].values or 'chrY' in df['chrom'].values:
        in_chrom_Y = df['chrom'].isin(['Y', 'chrY'])
        logger.warning('Removing {} regions in chromosome "Y"!'
                       .format(len(df[in_chrom_Y])))
        df = df[~in_chrom_Y].reset_index(drop=True)

    df['chrom'] = make_chromosome_series_categorical(df['chrom'])
    return df
