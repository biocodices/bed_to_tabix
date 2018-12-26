import pandas as pd

from bed_to_tabix.lib import bed_stats


def test_bed_stats():
    regions = pd.DataFrame({
        'chrom': ['1', '1', 'X', 'Y'],
        'start': [100, 100, 100, 100],
        'stop': [110, 200, 200, 210],
    })
    result = bed_stats(regions)

    assert result == {
        'n_regions': 4,
        'shorter_region_length': 10,
        'total_bases': 320,
        'longer_region_length': 110,
        'n_chromosomes': 3,
    }
