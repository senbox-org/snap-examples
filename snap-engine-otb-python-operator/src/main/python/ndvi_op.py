
import numpy as np
import otbApplication

import snappy


class NdviOp:

    def __init__(self):
        #jpy = snappy.jpy
        #jpy.diag.flags = jpy.diag.F_ALL

        self.red_band = None
        self.nir_band = None

        self.ndvi_band = None
        self.ndvi_flags_band = None

        self.otb_ndvi_app = otbApplication.Registry.CreateApplication("RadiometricIndices")

    def initialize(self, context):

			    # Via the context object the source product which shall be processed can be retrieved
        source_product = context.getSourceProduct('sourceProduct')

        print('initialize: source product location is', source_product.getFileLocation().toString())

				#get name of Red band from parameter 'redName'
        red_band_name = context.getParameter('redName')

				#if no band name is given for red, raise an expection
        if not red_band_name:
            raise RuntimeError('Missing parameter "redName"')

				#get instance of red band from source_product using self._get_band()
        self.red_band = self._get_band(source_product, red_band_name)

				#get name of Red band from parameter 'nirName'
        nir_band_name = context.getParameter('nirName')

				#if no band name is given for nir, raise an expection
        if not nir_band_name:
            raise RuntimeError('Missing parameter "nirName"')

				#get instance of nir band from source_product using self._get_band()
        self.nir_band = self._get_band(source_product, nir_band_name)

        print('initialize: red_band =', self.red_band, ', nir_band =', self.nir_band)

				#width and height of source product. This will be used to create target product
        width = source_product.getSceneRasterWidth()
        height = source_product.getSceneRasterHeight()

				#create target product 'ndvi_product' with same size of source product
        ndvi_product = snappy.Product('py_NDVI', 'py_NDVI', width, height)
        snappy.ProductUtils.copyGeoCoding(source_product, ndvi_product)

				#add a band to ndvi_product to store the result of ndvi
        self.ndvi_band = ndvi_product.addBand('ndvi', snappy.ProductData.TYPE_FLOAT32)

				#add a band to ndvi_product to store ndvi_flags.
        self.ndvi_flags_band = ndvi_product.addBand('ndvi_flags', snappy.ProductData.TYPE_UINT8)

        context.setTargetProduct(ndvi_product)

    def computeTileStack(self, context, target_tiles, target_rectangle):

			  #get tile for red band based that falls under target_rectangle
        tile_red = context.getSourceTile(self.red_band, target_rectangle)

				#get tile for nir band based that falls under target_rectangle
        tile_nir = context.getSourceTile(self.nir_band, target_rectangle)

				#get underlying pixel array as float
        samples_red = tile_red.getSamplesFloat()
        samples_nir = tile_nir.getSamplesFloat()

				#get the target tile where the output will be stored.
				ndvi_tile = target_tiles.get(self.ndvi_band)

				#find width and height of target tile to create input array
        w = ndvi_tile.getWidth()
        h = ndvi_tile.getHeight()

				#create an N-D array with pixel buffer from red and nir
        otb_input_array = np.dstack((np.array(samples_red, dtype=np.float32).reshape(w, h),
                                     np.array(samples_nir, dtype=np.float32).reshape(w, h)))

				#set numpy array as input parameter of otb application
        self.otb_ndvi_app.SetVectorImageFromNumpyArray("in", otb_input_array)

				#tell otb application to compute NDVI
        self.otb_ndvi_app.SetParameterStringList("list", ["Vegetation:NDVI"])

				#tell otb application which are the red and nir bands in input image (N-D array)
        self.otb_ndvi_app.SetParameterInt("channels.red", 1)
        self.otb_ndvi_app.SetParameterInt("channels.nir", 2)

				#Execute OTB application
        self.otb_ndvi_app.Execute()

				#Get output of otb application as N-D numpy array
        ndvi = self.otb_ndvi_app.GetVectorImageAsNumpyArray("out")

				#set samples for ndvi_tile from numpy array(ndvi)
				ndvi_tile.setSamples(ndvi)

        # print (ndvi_1.shape)
        # ndvi = np.ndarray(shape=(w, h, 1), dtype=np.float32)
        # ndvi[..., 0] = ndvi_1[:,:,1]
        # print (ndvi.shape)

				#create target tile for ndvi_flags_band
        ndvi_flags_tile = target_tiles.get(self.ndvi_flags_band)
        ndvi_low = ndvi < 0.0
        ndvi_high = ndvi > 0.1
        ndvi_flags = (ndvi_low + 2 * ndvi_high).astype(np.uint8)
        ndvi_flags_tile.setSamples(ndvi_flags)

    def dispose(self, context):
        pass

    def _get_band(self, product, name):
        band = product.getBand(name)
        if not band:
            raise RuntimeError('Product does not contain a band named', name)
        return band