from os.path import join
from tempfile import gettempdir

from .constants import TEMP_PREFIX


def temp_filepath(filename):
    return join(gettempdir(), '{}__{}'.format(TEMP_PREFIX, filename))
