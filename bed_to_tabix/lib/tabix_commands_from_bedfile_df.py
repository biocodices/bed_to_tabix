from lib import tabix_command_from_chromosome_regions


def tabix_commands_from_bedfile_df(bedfile_df,
                                   path_to_tabix,
                                   path_to_bgzip,
                                   http=False):
    """
    Generate the tabix commands to download 1000 Genomes genotypes for the
    regions included in a bedfile, passed as a DataFrame. Returns a dictionary
    { tabix_command1: destination_file1, tabix_command2: ... }
    """
    commands_to_run = []
    for chrom, regions_df in bedfile_df.groupby('chrom'):
        if not len(regions_df):
            continue
        command = tabix_command_from_chromosome_regions(
            regions_df,
            path_to_tabix=path_to_tabix,
            path_to_bgzip=path_to_bgzip,
            http=http
        )
        commands_to_run.append(command)

    return commands_to_run
