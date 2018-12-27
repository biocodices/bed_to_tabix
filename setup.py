from setuptools import setup, find_packages
from bed_to_tabix.package_info import PACKAGE_INFO


setup(name = PACKAGE_INFO['PROGRAM_NAME'],
      version = PACKAGE_INFO['VERSION'],
      description = PACKAGE_INFO['DESCRIPTION'],
      url = PACKAGE_INFO['URL'],
      author = PACKAGE_INFO['AUTHOR'],
      author_email = PACKAGE_INFO['AUTHOR_EMAIL'],
      install_requires = PACKAGE_INFO['DEPENDENCIES'],
      license = 'MIT',
      packages = find_packages(),
      entry_points = {
          'console_scripts': ['bed_to_tabix = bed_to_tabix.cli:main']
      },
      zip_safe=False)

