import pandas as pd

from .constants import BED_COLUMNS
from .read_bed import read_bed


def merge_beds(bedfiles):
    """Read a list of bedfiles and return a pandas DataFrame with no dupes."""
    frames = [read_bed(bedfile) for bedfile in bedfiles]
    bedfile_df = pd.concat(frames).reset_index(drop=True)
    bedfile_df.drop_duplicates(subset=BED_COLUMNS[:3], inplace=True)
    bedfile_df.sort_values(by=BED_COLUMNS, inplace=True)
    return bedfile_df
