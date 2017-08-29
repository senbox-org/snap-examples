# Here is how to configure SNAP for your Python version. Type:
#   > cd ${SNAP_HOME}/bin
#   > snap --nogui --nosplash --python C:\Python34\python.exe C:\Users\USER_NAME\JavaProjects\senbox

from snappy import jpy, Band, ProductIO, ProductUtils

OpType = jpy.get_type('org.esa.snap.core.datamodel.GeneralFilterBand$OpType')
GeneralFilterBand = jpy.get_type('org.esa.snap.core.datamodel.GeneralFilterBand')
Kernel = jpy.get_type('org.esa.snap.core.datamodel.Kernel')

product_file = 'G:/EOData/Meris/RR/MER_RR__1PNBCG20050709_101121_000001802038_00466_17554_0001.N1'
out_file = 'G:/EOData/temp/prod_with_filtered_band.dim'
product = ProductIO.readProduct(product_file)

sourceRaster = product.getRasterDataNode('radiance_1')
realBand = False
filteredBandName = 'myFilteredBand'
# OpType can be one of {MIN, MAX, MEDIAN, MEAN, STDDEV, EROSION, DILATION, OPENING, CLOSING}
opType = OpType.STDDEV
iterationCount = 1

kernel_data = [0, 1, 1, 1, 1, 1, 1, 1, 0,
               1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 0, 1, 1, 1, 1,
               1, 1, 1, 0, 0, 0, 1, 1, 1,
               1, 1, 0, 0, 0, 0, 0, 1, 1,
               1, 1, 1, 0, 0, 0, 1, 1, 1,
               1, 1, 1, 1, 0, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 0]
kernel = Kernel(9, 9, 4, 4, 1 / 64, kernel_data)

filtered_band = GeneralFilterBand(filteredBandName, sourceRaster, opType, kernel, iterationCount)

if isinstance(jpy.cast(sourceRaster, Band), Band):
    ProductUtils.copySpectralBandProperties(sourceRaster, filtered_band)

# Turn into real Band
if realBand:
    target_band = Band(filtered_band.getName(), filtered_band.getDataType(),
                       filtered_band.getRasterWidth(), filtered_band.getRasterHeight())
    target_band.setSourceImage(filtered_band.getSourceImage())
else:
    target_band = filtered_band

if isinstance(jpy.cast(sourceRaster, Band), Band):
    ProductUtils.copySpectralBandProperties(sourceRaster, target_band)

product.addBand(target_band)

ProductIO.writeProduct(product, out_file, 'BEAM-DIMAP')
