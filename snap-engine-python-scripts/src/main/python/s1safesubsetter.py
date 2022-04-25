"""
This script performs a top-split function for Sentinel-1 top-SAR SLC products.

Usage:
With SNAP running in the background (or as an active Docker instance e.g., with docker-snap):
    > python3 s1safesubetter.py -f [filepath] [additional optional arguments]
"""

import argparse
from glob import glob
import itertools
import os
import zipfile
from typing import Dict, List, NoReturn

from lxml import etree

from snappy import GPF, HashMap, Product, ProductIO


def call_snap_topsar_split(args: Dict, product: Product) -> Product:
    """..."""
    parameters = HashMap()

    try:
        if args['subswath']:
            parameters.put('subswath', args['subswath'].upper())
        if args['bursts']:
            bursts = args['bursts'].split('-')
            parameters.put('firstBurstIndex', bursts[0])
            parameters.put('lastBurstIndex', bursts[1] if len(bursts) == 2 else bursts[0])
        if args['polarization']:
            parameters.put('selectedPolarizations', args['polarization'])
        if args['wktaoi']:
            # TODO: how to parse the WKT AOI argument
            raise NotImplementedError
    except KeyError as err:
        print(f"Could not assign TOPSAR-Split attribute(s): {err}")
    else:
        return GPF.createProduct('TOPSAR-Split', parameters, product)

def generate_geotiffs(product: Product) -> Dict:
    """..."""
    # generates new GeoTIFF files, one per polarization band (containing both the real and imaginary parts)
    all_bands = [b for b in list(product.getBandNames()) if 'Intensity_' not in b]  # omit 'Intensity_' bands
    band_grps = itertools.groupby(all_bands, lambda b: b.split('_')[-1])            # group components by polarization
    output_imgs = {}                                                                # dictionary of the output images
    for pol, band_grp in band_grps:

        try:
            parameters = HashMap()
            parameters.put('sourceBands', ','.join(band_grp))
        except KeyError as err:
            print(f"Invalid band specifications: {err}")
        else: 
            product_polarizations = GPF.createProduct('BandSelect', parameters, product)

        # TODO: remove - only a subset of data is excised for visualization due to local memory limitations
        parameters = HashMap()
        parameters.put('region', '3640,700,7500,3288')
        product_polarizations = GPF.createProduct('Subset', parameters, product_polarizations)
        # ---

        try:
            output_imgs[pol] = f"tstimg-{pol}"  # store name for later reference
            ProductIO.writeProduct(product_polarizations, output_imgs[pol], 'GeoTiff-BigTiff')  # write product to disk
        except OSError as err:
            print(f"Unable to create GeoTiff from polarization: {err}")

def write_topsar_split_to_safe(args: Dict, output_imgs: Dict):
    """..."""
    # read input archive into memory as a tuple of (name, data)
    input_archive = zipfile.ZipFile(args['filepath'])
    input_archive_items = [(name, input_archive.read(name)) for name in input_archive.namelist()]

    output_archive_filepath = f"{args['filepath'].split('.zip')}_split.zip"

    # copy the appropriate data from the input archive to the output archive
    with zipfile.ZipFile(output_archive_filepath, 'w') as oafp:

        for i, (name, data) in enumerate(input_archive_items):
            if i == 0:
                base_name = name.split('.SAFE/')[0]
                new_base_name = f"{base_name}_split"
            new_name = name.replace(base_name, new_base_name)

            if ('.tiff' in name or '.xml' in name) and args['subswath'] not in name:
                continue

            if '.tiff' in name and args['subswath'] in name:
                # then overwrite 'data' with a new tiff from the topsar-split operator
                pol = 'vv' if '-vv-' in name else 'vh'
                # data = output_imgs[pol]

            oafp.writestr(new_name, data)

def edit_bursts_in_annotations_xml(file: str, bursts: List) -> NoReturn:
    """..."""
    try:
        docroot = etree.parse(file)
    except TypeError as err:
        print(f"Could not parse XML file {file}: {err}")
    else:
        for i, burst in enumerate(docroot.findall('./swathTiming/burstList/')):
            if i < bursts[0] or i > bursts[1]:
                parent = burst.getparent()
                parent.remove(burst)

        # compose the document root back into an "ElementTree" and (over)write file
        et = etree.ElementTree(docroot)
        et.write(file, pretty_print=True)

def main(args: Dict):
    """..."""
    # TODO:
    #    - validite input arguments
    #    - force 'subswath' arg with .lower()
    #    - polarization inputs are not well handled atm
    #    - no support for WKT AOI

    # read in the specified SAFE file
    try:
        print(f"Reading into memory product: \'{args['filepath']}\'")
        input_product = ProductIO.readProduct(args['filepath'])
    except OSError as err:
        print(f"Invalid filepath: {args['filepath']}")

    # use SNAP's TOPSAR-Split to split the data according to the input parameters
    print("Calling SNAP's TOPSAR-Split operator...")
    split_product = call_snap_topsar_split(args, input_product)

    generate_geotiffs()

    # confirm that the tiffs output here are the same as the original tiffs (type c-int-16; where as we're probably writing two int-16)
    # if not use gdal-translate (https://gdal.org/programs/gdal_translate.html)

    # write_topsar_split_to_safe(args, output_imgs)

    with zipfile.ZipFile(args['filepath'], 'r') as zf:
        zf.extractall(path=f"{args['path']}/")  # extract contents to disk

    archive_content = glob(f"{args['path']}/{args['name']}.SAFE/**/*.*", recursive=True)

    for file in archive_content:
        # grab the file type for the current file
        fileparts = os.path.split(file)
        # check each file and operate on it according to the following rules
        if 'annotation' in fileparts[0] and ('calibration-' in fileparts[-1] or 'noise-' in fileparts[-1]) and fileparts[-1].split('.')[-1] == 'xml':
            for p in pol:
                if f"-{args['subswath']}-slc-{p}-" not in fileparts[-1]:
                    print(f"DELETING: {file}")  # delete this file
                else:
                    print(f"NO-CHANGE: {file}")
        elif 'annotation' in fileparts[0] and 'calibration' not in fileparts[-1] and 'noise' not in fileparts[-1] and fileparts[-1].split('.')[-1] == 'xml':
            for p in pol:
                if f"-{args['subswath']}-slc-{p}-" in fileparts[-1]:
                    print(f"MODIFYING: {file}")  # modify this file
                    edit_bursts_from_annotations_xml(file, args['bursts'])
                else:
                    print(f"DELETING: {file}")  # delete this file
        elif 'measurement' in fileparts[0] and fileparts[-1].split('.')[-1] == 'tiff':
            print(f"DELETING: {file}")  # delete this file
        else:
            print(f"NO-CHANGE: {file}")
            # continue  # keep all other files as-is

    # finally, write the topsar-split files to the 'measurement' dir


if __name__ == '__main__':

    parser = \
        argparse.ArgumentParser(
            description="Performs a top-split function for Sentinel-1 top-SAR SLC products.",
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        # TODO: uncomment line with 'required', remove line with 'default'
        '-f',
        '--filepath',
        metavar='\b',
        type=str,
        # required=True,
        default='./skywatch-image-processing-testdata/S1A_IW_SLC__1SDV_20211114T231638_20211114T231705_040574_04D007_67F9.zip',
        help="    input SLC filepath; to a zip file as, -f '~/path/to/file.zip'")
    parser.add_argument(
        '-s',
        '--subswath',
        metavar='\b',
        default='iw1',
        help="    subswath; choice between iw1-3, as -s 'iw2' (default 'iw1')")
    parser.add_argument(
        '-b',
        '--bursts',
        metavar='\b',
        type=str,
        default='1-9',
        help="    bursts; single int or range between '1-9', as -b '3' or -b '2-6' (default '1-9')")
    parser.add_argument(
        '-p',
        '--polarization',
        metavar='\b',
        type=str,
        default=None,
        help="polarization; specify 'vv' or 'vh', as -p 'vv' (default both)")
    parser.add_argument(
        '-w',
        '--wktaoi',
        metavar='\b',
        type=str,
        help="    WKT AOI polygon; set of lng-lat floats as, -w '(30.0 10.1, 40.0 40.0, 10.2 20.9, 30.0 10.1)'")

    args = parser.parse_args()
    args = vars(args)

    # extend args
    args['path'], args['file'] = os.path.split(args['filepath'])
    args['path'] = '.' if args['path']=='' else args['path']
    args['name'] = args['file'].split('.')[0]

    main(args)
