import pytest

from bed_to_tabix.lib import read_bed


def test_read_bed():
    fn = pytest.helpers.file('unsorted.bed')
    result = read_bed(fn)

    assert list(result['chrom']) == ['12', '12', '12']
    assert list(result['start']) == [100, 300, 500]
    assert list(result['stop']) == [200, 400, 600]
    assert list(result['name']) == ['foo', 'bar', 'baz']
