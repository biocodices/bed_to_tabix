import pytest

from bed_to_tabix.lib import merge_beds


def test_merge_beds():
    result = merge_beds([
        pytest.helpers.file('unsorted.bed'),
        pytest.helpers.file('unsorted.2.bed'),
        pytest.helpers.file('unsorted.bed'),
        pytest.helpers.file('unsorted.2.bed'),
    ])

    assert list(result['chrom']) == ['12'] * 3 + ['13'] * 3
    assert list(result['name']) == 'foo bar baz foo2 bar2 baz2'.split()

