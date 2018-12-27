from os.path import basename

from lib import temp_filepath
from lib import thousand_genomes_chromosome_url


def tabix_command_from_chromosome_regions(regions_df,
                                          path_to_tabix,
                                          path_to_bgzip,
                                          http=False):
    """
    Generate a tabix command to download the regions present in regions_df
    from The 1000 Genomes Project servers via FTP or HTTP. Requires that all
    regions are located in the same chromosome.

    Returns a tuple: (tabix_command, destination_filepath)
    """
    # Make sure there's only one chromosome in the regions_df
    seen_chromosomes = list(regions_df['chrom'].unique())
    assert len(seen_chromosomes) == 1
    chrom = seen_chromosomes.pop()

    # Create a temporary bed file with this chromosome's regions
    # It will be used in the tabix command, as the -R parameter
    chrom_bedfile = temp_filepath('chr_{}.bed'.format(chrom))
    regions_df.to_csv(chrom_bedfile, sep='\t', header=False, index=False)

    # Define the destination VCF filename for this chromosome
    dest_file = temp_filepath('chr_{}.vcf.gz'.format(chrom))

    chrom_1kg_url = thousand_genomes_chromosome_url(chrom, http)
    # Generate the tabix command to download 1kG genotypes for these regions
    tabix_command = (
        f'{path_to_tabix} -fh -R {chrom_bedfile} {chrom_1kg_url} | ' +
        f'{path_to_bgzip} > {dest_file}'
    )

    chrom_index_file = basename(chrom_1kg_url) + '.tbi'

    return {'cmd': tabix_command,
            'dest_file': dest_file,
            'chrom_bedfile': chrom_bedfile,
            'chrom_index_file': chrom_index_file}
