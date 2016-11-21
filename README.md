# `bed_to_tabix`

## Requirements

- A working Internet connection without any weird proxy settings. I know `tabix`
  doesn't work in some University network settings.
- Python 3.5 or greater ([Anaconda](https://www.continuum.io/downloads)).
- `tabix`, `bgzip` and `bcftools` command line utilities (>= 1.3.2). You can download all of them from [htslib.org](http://www.htslib.org/download). Choose the `htslib` and `bcftools` packages to download. If you have an old `tabix` version, update it, since the command line interface changed from older versions.

After downloading the packages, you can install them with these commands
(replace `htslib` with `bcftools` to install the latter):

```bash
tar xvf htslib-1.3.2.tar.bz2  # Replace with the exact filename you downloaded

cd htslib-1.3.2

./configure

make

sudo make install
```

Check they were correctly installed and that you have a version >= 1.3.2:

```bash
tabix -h

bgzip -h

bcftools -h
```

## How to Install `bed_to_tabix`

You need `git` for this. In case you don't have it, `sudo apt-get install git` will work in Ubuntu.

```bash
git clone https://github.com/biocodices/bed_to_tabix
cd bed_to_tabix
python setup.py install
```

## Usage

Don't set `--threads` too high or you might get banned! The default of 3 seems
to be fine, but you can experiment with higher numbers at your own risk.

```bash
# Download the regions in regions1.bed to regions1.vcf.gz
bed_to_tabix --in regions1.bed

# Download the regions in regions1.bed, 5 downloads at a time, to 1kg.vcf
bed_to_tabix --in regions1.bed --threads 5 --unzipped --out 1kg

# Download the regions in both bed files to regions1__regions2.vcf.gz
bed_to_tabix --in regions1.bed --in regions2.bed
```

You will get a [gzipped] VCF file with the genotypes from the 2,504 samples in
the 1kG Proyect.

## For devs

Contributions are welcome! To run the small test suite:

```bash
pytest -q tests
```
