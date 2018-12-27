# `bed_to_tabix`

`bed_to_tabix` will download a gzipped VCF file with the 2,504 genotypes from 
The 1,000 Genomes Project in the regions defined in one or more BED files.
The program will specifically handle the BED sorting, the merging of many
BEDs, the **parallel-downloading** of the different chromosome variants with `tabix` from different URLs (one per chromosome in the BED regions),
and it will merge the resulting VCFs in a single gzipped VCF. You end up with
a single multi-chromosome multi-sample merged gzipped VCF with all 1KG
genotypes in the regions that you want.

![Screenshot](screen.png)

## Requirements

- A working Internet connection.
- Python 3.6 or greater (you can get it at [Anaconda](https://www.continuum.io/downloads)).
- `tabix`, `bgzip`, `bcftools`, `gatk3`, `java` (for GATK). You can download the first three from [htslib.org](http://www.htslib.org/download), choosing the `htslib` and `bcftools` packages. If you have an old `tabix` version, update it because the command line interface changed from older versions. GATK3 can be downloaded from [their GitHub](https://github.com/broadgsa/gatk/releases), and it requires Java to run. If you're in bioinformatics, you will likely have all of these programs already installed.
- A human reference genome in `fasta` format for GATK3 to run. Instructions to
  get it working [here](https://software.broadinstitute.org/gatk/documentation/article?id=11013).

## How to Install `bed_to_tabix`

Clone this repo and install the package:

```bash
git clone https://github.com/biocodices/bed_to_tabix
cd bed_to_tabix
python setup.py install
```

## Usage

I'm not sure if there's any risk of getting banned if you perform too many
parallel downloads from 1kG servers, so experiment with `--threads` at your own
risk.

```bash
# Download the regions in regions1.bed to regions1.vcf.gz
bed_to_tabix --in regions1.bed

# Download the regions in regions1.bed, 10 downloads at a time, to 1kg.vcf
bed_to_tabix --in regions1.bed --threads 10 --unzipped --out 1kg

# Download the regions in both bed files to regions1__regions2.vcf.gz
bed_to_tabix --in regions1.bed --in regions2.bed
```

You will get a [gzipped] VCF file with the 1kG variants found in your regions.

In case you can't connect to port 21 (FTP) --I know this is usual in some
University networks--, you can use the HTTP URLs from 1000 Genomes:

```bash
# Download from the HTTP URLs in case your traffic to FTP is blocked
bed_to_tabix --in regions1.bed --http
```

## For devs

Contributions are welcome! To run the small test suite:

```bash
pytest -q bed_to_tabix/test
```
