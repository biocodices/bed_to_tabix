pytest_plugins = ['helpers_namespace']

from os import environ
from os.path import realpath, join, dirname

import pytest

@pytest.helpers.register
def file(filename):
    return join(dirname(realpath(__file__)), 'files', filename)

@pytest.fixture
def path_to_bcftools():
    varname = 'PATH_TO_BCFTOOLS'
    if varname not in environ:
        raise Exception(f'Please run pytest with ENV variable {varname}')
    return environ.get(varname)

@pytest.fixture
def path_to_bgzip():
    varname = 'PATH_TO_BGZIP'
    if varname not in environ:
        raise Exception(f'Please run pytest with ENV variable {varname}')
    return environ.get(varname)

@pytest.fixture
def path_to_tabix():
    varname = 'PATH_TO_TABIX'
    if varname not in environ:
        raise Exception(f'Please run pytest with ENV variable {varname}')
    return environ.get(varname)
