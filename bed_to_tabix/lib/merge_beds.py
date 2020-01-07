import pandas as pd

from ..lib import BED_COLUMNS
from ..lib import read_bed
from ..lib import logger


def merge_beds(bedfiles):
    """Read a list of bedfiles and return a pd.DataFrame with no dupes, sorted
    by chromosome, start and end position."""
    frames = [read_bed(bedfile) for bedfile in bedfiles]
    regions = pd.concat(frames).reset_index(drop=True)

    logger.debug(f'{len(regions)} regions read from {len(bedfiles)} files.')
    regions.drop_duplicates(subset=BED_COLUMNS[:3], inplace=True)
    logger.debug(f'{len(regions)} unique regions after removing duplicates.')

    logger.debug('Sorting the regions by position')
    regions.sort_values(by=BED_COLUMNS, inplace=True)
    return regions
