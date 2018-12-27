def fix_zero_length_regions(regions):
    """Given a pd.DataFrame of regions with 'start' and 'stop', expand the
    regions (start = start - 1; stop = stop + 1) that have zero length.

    Meant to deal with BED files that mark SNPs as a single nucleotide region.
    """
    return regions.apply(_fix_zero_length_region, axis=1)

def _fix_zero_length_region(region):
    """
    Given a dict of pd.Series with 'start' and 'stop', expand it if it has
    zero length.
    """
    if region['start'] == region['stop']:
        region['start'] = region['start'] - 1
        region['stop'] = region['stop'] + 1

    if region['start'] > region['stop']:
        raise ValueError(f'Found a region where start ({region["start"]}) > ' +
                         f'stop ({region["stop"]}))')
    return region
