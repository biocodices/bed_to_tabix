from bed_to_tabix.lib import thousand_genomes_chromosome_url


def test_thousand_genomes_chromosome_url():
    result = thousand_genomes_chromosome_url('1')
    assert result == 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'

    result = thousand_genomes_chromosome_url('X')
    assert result == 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrX.phase3_shapeit2_mvncall_integrated_v1b.20130502.genotypes.vcf.gz'

    result = thousand_genomes_chromosome_url('Y', http=True)
    assert result == 'http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chrY.phase3_integrated_v2a.20130502.genotypes.vcf.gz'

    result = thousand_genomes_chromosome_url('3', local_dir='/path/to/1KG')
    assert result == '/path/to/1KG/ALL.chr3.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz'
