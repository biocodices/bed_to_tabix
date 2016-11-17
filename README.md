# `bed_to_tabix`

## Requirements

- Python 3.5 or greater. You can download and install from [Anaconda](https://www.continuum.io/downloads)
- `tabix` and `bgzip` command line utilities (>= 1.3.2). You can download and install both from [htslib.org](http://www.htslib.org/download). Choose the `htslib` package to download. If you have an old `tabix` version, update it, since the command line interface changed from older versions. After downloading the package:

```bash
tar xvf htslib-1.3.2.tar.bz2  # Replace with the exact filename you downloaded

cd htslib-1.3.2

./configure

make

sudo make install
```

## How to Install `bed_to_tabix`

You need `git` for this. In case you don't have it installed, `sudo apt-get install git` will work in Ubuntu.

```bash
git clone https://github.com/biocodices/bed_to_tabix
```

If you don't have and don't want to install `git`, you can just visit the [github repo](https://github.com/biocodices/bed_to_tabix), download the `.zip` and extract it.

Then:

```bash
cd bed_to_tabix
python setup.py install
```

## Usage

This comand will print the typical use case and options on screen:

```bash
bed_to_tabix --help
```

You just have to pass the path of a `.bed` file, and `bed_to_tabix` will download
the genotypes of the 2,504 samples from The 1,000 Genomes Project into a `.vcf.gz`.
