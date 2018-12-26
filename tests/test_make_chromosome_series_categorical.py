import pandas as pd
from pandas.api.types import CategoricalDtype

from bed_to_tabix.lib import make_chromosome_series_categorical


def test_make_chromosome_series_categorical():
    s = pd.Series(['1', '2', '23', '1', '24', 'MT'])
    result = make_chromosome_series_categorical(s)
    assert result.dtype == CategoricalDtype(
        categories=['1', '2', 'X', 'Y', 'MT'], ordered=True
    )
    assert list(result) == ['1', '2', 'X', '1', 'Y', 'MT'] # Don't reorder

    s = pd.Series(['chr1', 'chr2', 'chrX', 'chr1', 'chrY', 'chrMT'])
    result = make_chromosome_series_categorical(s)
    assert list(result) == ['1', '2', 'X', '1', 'Y', 'MT'] # Remove "chr"
