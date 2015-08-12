# Here is how to configure SNAP for your Python version. Type:
#   > cd ${SNAP_HOME}/bin
#   > snap --nogui --nosplash --python C:\Python34\python.exe C:\Users\Norman\JavaProjects\senbox

import sys
sys.path.append('C:\\Users\\Norman\\JavaProjects\\senbox')

import snappy

ProductIOPlugInManager = snappy.jpy.get_type('org.esa.snap.framework.dataio.ProductIOPlugInManager')
Logger = snappy.jpy.get_type('java.util.logging.Logger')
Level = snappy.jpy.get_type('java.util.logging.Level')
HashMap = snappy.jpy.get_type('java.util.HashMap')
Logger.getLogger('').setLevel(Level.OFF)
snappy.SystemUtils.LOG.setLevel(Level.OFF)

snappy.SystemUtils.init3rdPartyLibs(None)

reader_spi_it = ProductIOPlugInManager.getInstance().getAllReaderPlugIns()
while reader_spi_it.hasNext():
    reader_spi = reader_spi_it.next()
    print("reader_spi:", reader_spi.getClass())

snappy.GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()


op_spi_it = snappy.GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpis().iterator()
while op_spi_it.hasNext():
    op_spi = op_spi_it.next()
    print("op_spi:", op_spi.getOperatorAlias())


parameters = HashMap()
parameters.put('file', snappy.File('L3_subset_watermask.dim'))
p = snappy.GPF.createProduct("Read", parameters)
#p = snappy.ProductIO.readProduct('L3_subset_watermask.dim')

name = p.getName()
w = p.getSceneRasterWidth()
h = p.getSceneRasterHeight()

print(name + ":", w, "x", h, "pixels")
