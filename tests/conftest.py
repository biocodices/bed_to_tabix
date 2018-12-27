pytest_plugins = ['helpers_namespace']

from os import environ
from os.path import realpath, join, dirname

import pytest

@pytest.helpers.register
def file(filename):
    return join(dirname(realpath(__file__)), 'files', filename)

def path_to_exec(name):
    varname = f'PATH_TO_{name}'
    if varname not in environ:
        raise Exception(f'Please run pytest with ENV variable {varname}')
    return environ.get(varname)

@pytest.fixture
def path_to_bcftools():
    return path_to_exec('BCFTOOLS')

@pytest.fixture
def path_to_bgzip():
    return path_to_exec('BGZIP')

@pytest.fixture
def path_to_tabix():
    return path_to_exec('TABIX')

@pytest.fixture
def path_to_gatk3():
    return path_to_exec('GATK3')

@pytest.fixture
def path_to_java():
    return path_to_exec('JAVA')

@pytest.fixture
def path_to_reference_fasta():
    return path_to_exec('REFERENCE_FASTA')
