def bed_stats(bedfile_df):

    def region_len(region):
        return region['stop'] - region['start']

    return {
        'n_regions': len(bedfile_df),
        'total_bases': bedfile_df.apply(region_len, axis=1).sum(),
        'n_chromosomes': len(bedfile_df['chrom'].unique())
    }
