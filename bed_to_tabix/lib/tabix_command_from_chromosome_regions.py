from os.path import basename

from .temp_filepath import temp_filepath
from .thousand_genomes_chromosome_url import thousand_genomes_chromosome_url


def tabix_command_from_chromosome_regions(regions_df, http=False):
    """
    Generate a tabix command to download the regions present in regions_df
    from the given chromosome in The 1000 Genomes servers via FTP or HTTP.

    Returns a tuple: (tabix_command, destination_filepath)
    """
    # Make sure there's only one chromosome in the regions_df
    seen_chromosomes = list(regions_df['chrom'].unique())
    assert len(seen_chromosomes) == 1
    chrom = seen_chromosomes.pop()

    # Create a temporary bed file with this chromosome's regions
    # It will be used in the tabix command
    chrom_bedfile = temp_filepath('chr_{}.bed'.format(chrom))
    regions_df.to_csv(chrom_bedfile, sep='\t', header=False, index=False)

    # Define the destination VCF filename for this chromosome
    dest_file = temp_filepath('chr_{}.vcf.gz'.format(chrom))

    chrom_1kg_url = thousand_genomes_chromosome_url(chrom, http)
    # Generate the tabix command to download 1kG genotypes for these regions
    tabix_command = ('tabix -fh -R {0} {1} | bgzip > {2}'
                     .format(chrom_bedfile, chrom_1kg_url, dest_file))

    chrom_index_file = basename(chrom_1kg_url) + '.tbi'

    return {'cmd': tabix_command,
            'dest_file': dest_file,
            'chrom_bedfile': chrom_bedfile,
            'chrom_index_file': chrom_index_file}
