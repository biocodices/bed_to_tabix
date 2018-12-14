from os import getpid

from bed_to_tabix.package_info import PACKAGE_INFO


BED_COLUMNS = 'chrom start stop feature'.split()
TEMP_PREFIX = '{}_{}'.format(PACKAGE_INFO['PROGRAM_NAME'], getpid())
_base_path = 'ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/'
THOUSAND_GENOMES_FTP = 'ftp://' + _base_path
THOUSAND_GENOMES_HTTP = 'http://' + _base_path
THOUSAND_GENOMES_TBI_PATTERN = 'ALL.chr*.phase3_shapeit*.vcf.gz.tbi'
