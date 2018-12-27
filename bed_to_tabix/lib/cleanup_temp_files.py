from os import remove
from os.path import join
from glob import glob
from tempfile import gettempdir

from lib.constants import TEMP_PREFIX, THOUSAND_GENOMES_TBI_PATTERN
from lib.logger import logger


def cleanup_temp_files():
    """Remove all temp BED, VCF and tbi files found."""
    glob_pattern = join(gettempdir(), TEMP_PREFIX + '*')
    temp_files = glob(glob_pattern)

    for fn in sorted(temp_files):
        logger.debug(f'Cleanup: remove {fn}')
        remove(fn)

    # The .tbi files are downloaded to the directory where tabix is run,
    # not to the destination directory of the VCF, so I have to remove them
    # from there.
    for fn in glob(THOUSAND_GENOMES_TBI_PATTERN):
        logger.debug(f'Cleanup: remove {fn}')
        remove(fn)
