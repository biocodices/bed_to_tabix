from os.path import join
from tempfile import gettempdir

from ..lib import TEMP_PREFIX


def temp_filepath(filename, tmp_dir=None):
    return join(tmp_dir or gettempdir(),
                '{}__{}'.format(TEMP_PREFIX, filename))
