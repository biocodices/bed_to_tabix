from os import getpid

from package_info import PACKAGE_INFO


BED_COLUMNS = 'chrom start stop name'.split()
TEMP_PREFIX = '{}_{}'.format(PACKAGE_INFO['PROGRAM_NAME'], getpid())
THOUSAND_GENOMES_TBI_PATTERN = 'ALL.chr*.phase3_shapeit*.vcf.gz.tbi'
