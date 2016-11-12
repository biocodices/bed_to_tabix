#!/usr/bin/env python

from subprocess import run
from os.path import expanduser, abspath, dirname, basename, join


def sort_bed(bedfile, outfile=None):
    """Sort a .bed file and produce a new .bed with filename the passed 'out'
    filename in the same directory. Pass an absolute path to put it in another
    directory."""
    bedpath = abspath(expanduser(bedfile))

    if outfile is None:
        # If the file doesn't end in .bed, this will just add .sorted.bed
        outfile = basename(bedpath).replace('.bed', '') + '.sorted.bed'

    outpath = join(dirname(bedpath), outfile)

    command_args = 'bedtools sort -i {}'.format(bedpath).split()
    with open(outpath, 'w') as f:
        run(command_args, stdout=f, check=True)

    return outpath

# sort_bed('~/Downloads/test.bed')

