def bed_stats(regions_df):
    """Take a pd.DataFrame of regions with columns 'stop', 'start' and
    'chrom' and compute some basic BED stats to display."""
    def region_len(region):
        return region['stop'] - region['start']

    region_lengths = regions_df.apply(region_len, axis=1)

    return {
        'n_regions': len(regions_df),
        'shorter_region_length': region_lengths.min(),
        'total_bases': region_lengths.sum(),
        'longer_region_length': region_lengths.max(),
        'n_chromosomes': len(regions_df['chrom'].unique())
    }
