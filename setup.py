from setuptools import setup, find_packages
from bed_to_tabix.package_info import *


dependencies = [
    'pandas',
    'docopt',
]

setup(name=PROGRAM_NAME,
      version=VERSION,
      description=DESCRIPTION,
      url=URL,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      install_requires=dependencies,
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
            'bed_to_tabix = bed_to_tabix.bed_to_tabix:main'
          ]
      },
      zip_safe=False)
