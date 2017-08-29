# Here is how to configure SNAP for your Python version. Type:
#   > cd ${SNAP_HOME}/bin
#   > snap --nogui --nosplash --python C:\Python34\python.exe C:\Users\Norman\JavaProjects\senbox


import snappy
#print('snappy.__file__:', snappy.__file__)

from snappy import jpy, GPF, HashMap, File

ProductIOPlugInManager = snappy.jpy.get_type('org.esa.snap.core.dataio.ProductIOPlugInManager')
Logger = jpy.get_type('java.util.logging.Logger')
Level = jpy.get_type('java.util.logging.Level')
Arrays = jpy.get_type('java.util.Arrays')

Logger.getLogger('').setLevel(Level.OFF)
snappy.SystemUtils.LOG.setLevel(Level.OFF)



reader_spi_it = ProductIOPlugInManager.getInstance().getAllReaderPlugIns()
while reader_spi_it.hasNext():
    reader_spi = reader_spi_it.next()
    print("reader_spi: " + ', '.join(reader_spi.getFormatNames()) + " (" + reader_spi.getClass().getName() + ")")


writer_spi_it = ProductIOPlugInManager.getInstance().getAllWriterPlugIns()
while writer_spi_it.hasNext():
    writer_spi = writer_spi_it.next()
    print("writer_spi: " + ', '.join(writer_spi.getFormatNames()) + " (" + writer_spi.getClass().getName() + ")")


op_spi_it = GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpis().iterator()
while op_spi_it.hasNext():
    op_spi = op_spi_it.next()
    print("op_spi:", op_spi.getOperatorAlias())


parameters = HashMap()
parameters.put('file', File('L3_subset_watermask.dim'))
p = GPF.createProduct("Read", parameters)
#p = ProductIO.readProduct('L3_subset_watermask.dim')

name = p.getName()
w = p.getSceneRasterWidth()
h = p.getSceneRasterHeight()

print(name + ":", w, "x", h, "pixels")
