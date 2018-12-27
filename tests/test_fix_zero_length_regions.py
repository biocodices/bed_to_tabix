import pytest
import pandas as pd

from bed_to_tabix.lib import fix_zero_length_regions


def test_fix_zero_length_regions():
    regions = pd.DataFrame({
        'start': [100, 200],
        'stop': [100, 210],
    })
    result = fix_zero_length_regions(regions)

    # Fix the SNP, don't fix the indel:
    assert list(result['start']) == [99, 200]
    assert list(result['stop']) == [101, 210]

    regions = pd.DataFrame({
        'start': [100],
        'stop': [99], # 99 < 100 !
    })
    with pytest.raises(ValueError):
        fix_zero_length_regions(regions)
