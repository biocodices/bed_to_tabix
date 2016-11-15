from setuptools import setup, find_packages


dependencies = [
    'pandas',
    'docopt',
]

setup(name='bed_to_tabix',
      version='1.0',
      description='Download the genotypes of the regions in a .bed file from 1kG',
      url='http://github.com/biocodices/bed_to_tabix',
      author='Juan Manuel Berros',
      author_email='juanma.berros@gmail.com',
      install_requires=dependencies,
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
            'bed_to_tabix = bed_to_tabix.main:main'
          ]
      },
      zip_safe=False)
