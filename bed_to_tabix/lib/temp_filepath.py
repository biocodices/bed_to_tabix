from os.path import join

from .constants import TEMP_DIR, TEMP_PREFIX


def temp_filepath(filename):
    return join(TEMP_DIR, '{}__{}'.format(TEMP_PREFIX, filename))
