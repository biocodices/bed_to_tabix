pytest_plugins = ['helpers_namespace']

from os.path import realpath, join, dirname

import pytest

@pytest.helpers.register
def file(filename):
    return join(dirname(realpath(__file__)), 'files', filename)
