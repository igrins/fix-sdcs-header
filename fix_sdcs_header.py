#! /bin/env python

from __future__ import print_function

import astropy.io.fits as pyfits
import numpy as np

from astropy.coordinates import Angle

class FixNotNeeded(Exception):
    pass

def convert_pa2rot(pa):
    # rot = pa - 135
    rot = 45 - pa
    return rot

assert convert_pa2rot(90) == -45

def fix_header(header):
    if "PASTART" not in header:
        return

    pa = header["PASTART"]
    crot1 = header["CROTA1"]
    crot2 = header["CROTA2"]

    h = header

    if (crot1 == crot2) and (crot1 == pa - 135):
        if pa == 45:
            raise FixNotNeeded("PA=45, no fix is needed.")
        rot = convert_pa2rot(pa)
        h.update(dict(CROTA1=rot,
                      CROTA2=rot))
    else:
        raise FixNotNeeded("header information is not compatible with this this fix")

    # return h

def fix_hdul(hdul):
    for hdu in hdul:
        try:
            fix_header(hdu.header)
        except FixNotNeeded:
            pass


def fix_fits(fin, fout=None, overwrite=False):
    f = pyfits.open(fin)

    fix_hdul(f)

    if fout is None:
        fout = fin

    f.writeto(fout,
              overwrite=overwrite)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix SDCS CROTA.')
    parser.add_argument('--overwrite', dest='overwrite',
                        action='store_const',
                        const=True, default=False,
                        help='overwrite the output file')
    parser.add_argument('infile',
                        help='input fits file')
    parser.add_argument('outfile', default=None, nargs='?',
                        help='output fits file. infile is used if not specified.')

    a = parser.parse_args()

    fix_fits(a.infile, a.outfile, overwrite=a.overwrite)


if __name__ == '__main__':
    main()
