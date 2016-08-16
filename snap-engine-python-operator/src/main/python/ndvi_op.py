###################################################################################################
# This operator class implementation serves as a template for writing SNAP operators in Python.
# It is shown how thw source products and it's data is accessed, how the values
# of the parameters, specified in the accompanying ndvi_op-info.xml file, are retrieved and
# validated. Also how the resulting target product can be defined along with flags, masks, etc. is
# shown in this example. A guide about the development of a python operator can be found at
# http://senbox.atlassian.net/wiki/display/SNAP/How+to+write+a+processor+in+Python
# For further questions please consult the forum at http://forum.step.esa.int
###################################################################################################

import ndvi_algo
import numpy
import snappy
from snappy import FlagCoding

NDVI_HIGH_THRESHOLD = 0.8
NDVI_LOW_THRESHOLD = -0.5

# If a Java type is needed which is not imported by snappy by default it can be retrieved manually.
# First import jpy
from snappy import jpy

# and then import the type
Float = jpy.get_type('java.lang.Float')
Color = jpy.get_type('java.awt.Color')


class NdviOp:
    def __init__(self):
        self.lower_band = None
        self.upper_band = None
        self.ndvi_band = None
        self.ndvi_flags_band = None
        self.algo = None
        self.lower_factor = 0.0
        self.upper_factor = 0.0

    def initialize(self, context):
        # Via the context object the source product which shall be processed can be retrieved
        source_product = context.getSourceProduct('source')
        print('initialize: source product location is', source_product.getFileLocation())

        width = source_product.getSceneRasterWidth()
        height = source_product.getSceneRasterHeight()

        # Retrieve a parameters defined in ndvi_op-info.xml
        lower_band_name = context.getParameter('lowerName')
        self.lower_factor = context.getParameter('lowerFactor')
        upper_band_name = context.getParameter('upperName')
        self.upper_factor = context.getParameter('upperFactor')

        self.lower_band = self._get_band(source_product, lower_band_name)
        self.upper_band = self._get_band(source_product, upper_band_name)

        print('initialize: lower_band =', self.lower_band, ', upper_band =', self.upper_band)
        print('initialize: lower_factor =', self.lower_factor, ', upper_factor =', self.upper_factor)

        # As it is always a good idea to separate responsibilities the algorithmic methods are put
        # into an other class
        self.algo = ndvi_algo.NdviAlgo(NDVI_LOW_THRESHOLD, NDVI_HIGH_THRESHOLD)

        # Create the target product
        ndvi_product = snappy.Product('py_NDVI', 'py_NDVI', width, height)
        # ProductUtils provides several useful helper methods to build the target product.
        # In most cases it is sufficient to copy the information from the source to the target.
        # That's why mainly copy methods exist like copyBand(...), copyGeoCoding(...), copyMetadata(...)
        snappy.ProductUtils.copyGeoCoding(source_product, ndvi_product)
        snappy.ProductUtils.copyMetadata(source_product, ndvi_product)
        # For copying the time information no helper method exists yet, but will come in SNAP 5.0
        ndvi_product.setStartTime(source_product.getStartTime())
        ndvi_product.setEndTime(source_product.getEndTime())

        # Adding new bands to the target product is straight forward.
        self.ndvi_band = ndvi_product.addBand('ndvi', snappy.ProductData.TYPE_FLOAT32)
        self.ndvi_band.setDescription('The Normalized Difference Vegetation Index')
        self.ndvi_band.setNoDataValue(Float.NaN)
        self.ndvi_band.setNoDataValueUsed(True)
        self.ndvi_flags_band = ndvi_product.addBand('ndvi_flags', snappy.ProductData.TYPE_UINT8)
        self.ndvi_flags_band.setDescription('The flag information')

        # Create a flagCoding for the flag band. This helps to display the information properly within SNAP.
        ndviFlagCoding = FlagCoding('ndvi_flags')
        # The NDVI_LOW flag shall be at bit position 0 and has therefor the value 1, NDVI_HIGH has the
        # value 2 (bit 1) and so one
        low_flag = ndviFlagCoding.addFlag("NDVI_LOW", 1, "NDVI below " + str(NDVI_LOW_THRESHOLD))
        high_flag = ndviFlagCoding.addFlag("NDVI_HIGH", 2, "NDVI above " + str(NDVI_HIGH_THRESHOLD))
        neg_flag = ndviFlagCoding.addFlag("NDVI_NEG", 4, "NDVI negative")
        pos_flag = ndviFlagCoding.addFlag("NDVI_POS", 8, "NDVI positive")
        ndvi_product.getFlagCodingGroup().add(ndviFlagCoding)
        self.ndvi_flags_band.setSampleCoding(ndviFlagCoding)

        # Also for each flag a layer should be created
        ndvi_product.addMask('mask_' + low_flag.getName(), 'ndvi_flags.' + low_flag.getName(),
                             low_flag.getDescription(), Color.YELLOW, 0.3)
        ndvi_product.addMask('mask_' + high_flag.getName(), 'ndvi_flags.' + high_flag.getName(),
                             high_flag.getDescription(), Color.GREEN, 0.3)
        ndvi_product.addMask('mask_' + neg_flag.getName(), 'ndvi_flags.' + neg_flag.getName(),
                             neg_flag.getDescription(), Color(255, 0, 0), 0.3)
        ndvi_product.addMask('mask_' + pos_flag.getName(), 'ndvi_flags.' + pos_flag.getName(),
                             pos_flag.getDescription(), Color.BLUE, 0.3)

        # Provide the created target product to the framework so the computeTileStack method can be called
        # properly and the data can be written to disk.
        context.setTargetProduct(ndvi_product)

    def computeTileStack(self, context, target_tiles, target_rectangle):
        # The operator is asked by the framework to provide the data for a rectangle when the data is needed.
        # The required source data for the computation can be retrieved by getSourceTile(...) via the context object.
        lower_tile = context.getSourceTile(self.lower_band, target_rectangle)
        upper_tile = context.getSourceTile(self.upper_band, target_rectangle)

        # The actual data can be retrieved from the tiles by getSampleFloats(), getSamplesDouble() or getSamplesInt()
        lower_samples = lower_tile.getSamplesFloat()
        upper_samples = upper_tile.getSamplesFloat()
        # Values at specific pixel locations can be retrieved for example by lower_tile.getSampleFloat(x, y)

        # Convert the data into numpy data. It is easier and faster to work with as if you use plain python arithmetic
        lower_data = numpy.array(lower_samples, dtype=numpy.float32) * self.lower_factor
        upper_data = numpy.array(upper_samples, dtype=numpy.float32) * self.upper_factor

        # Doing the actual computation
        ndvi = self.algo.compute_ndvi(lower_data, upper_data)
        ndvi_flags = self.algo.compute_flags(ndvi)

        # The target tile which shall be filled with data are provided as parameter to this method
        ndvi_tile = target_tiles.get(self.ndvi_band)
        ndvi_flags_tile = target_tiles.get(self.ndvi_flags_band)

        # Set the result to the target tiles
        ndvi_tile.setSamples(ndvi)
        ndvi_flags_tile.setSamples(ndvi_flags)

    def dispose(self, context):
        pass

    def _get_band(self, product, name):
        # Retrieve the band from the product
        # Some times data is not stored in a band but in a tie-point grid or a mask or a vector data.
        # To get access to this information other methods are exposed by the product class. Like
        # getTiePointGridGroup().get('name'), getVectorDataGroup().get('name') or getMaskGroup().get('name')
        # For bands and tie-point grids a short cut exists. Simply use getBand('name') or getTiePointGrid('name')
        band = product.getBandGroup().get(name)
        if not band:
            raise RuntimeError('Product does not contain a band named', name)
        return band
