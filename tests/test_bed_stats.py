import pandas as pd

from bed_to_tabix.lib import bed_stats


def test_bed_stats():
    regions = pd.DataFrame({
        'chrom': ['1', '1', 'X', 'Y'],
        'start': [100, 100, 100, 100],
        'stop': [101, 101, 101, 110],
    })
    result = bed_stats(regions)

    assert result == {
        'n_regions': 4,
        'shorter_region_length': 1,
        'longer_region_length': 10,
        'total_bases': 13,
        'n_chromosomes': 3,
    }
