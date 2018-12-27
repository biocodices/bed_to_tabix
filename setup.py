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
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      packages = find_packages(),
      entry_points = {
          'console_scripts': ['bed_to_tabix = bed_to_tabix.cli:main']
      },
      zip_safe=False)

