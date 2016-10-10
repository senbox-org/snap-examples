package org.acme.snap.examples.data_export;

import com.bc.ceres.core.ProgressMonitor;
import com.bc.ceres.glayer.CollectionLayer;
import com.bc.ceres.glayer.Layer;
import com.bc.ceres.glayer.LayerContext;
import com.bc.ceres.glayer.support.ImageLayer;
import com.bc.ceres.grender.support.BufferedImageRendering;
import org.esa.snap.core.dataio.ProductIO;
import org.esa.snap.core.datamodel.Band;
import org.esa.snap.core.datamodel.ImageInfo;
import org.esa.snap.core.datamodel.Product;
import org.esa.snap.core.datamodel.SceneTransformProvider;
import org.esa.snap.core.datamodel.VectorDataNode;
import org.esa.snap.core.gpf.GPF;
import org.esa.snap.core.image.ImageManager;
import org.esa.snap.core.util.ProductUtils;
import org.esa.snap.core.util.io.FileUtils;
import org.esa.snap.ui.product.VectorDataLayer;

import javax.media.jai.JAI;
import java.awt.image.BufferedImage;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;

/**
 * @author Marco Peters
 */
public class ExportRgbWithLayer {

    public static void main(String[] args) throws IOException {
        Product product = ProductIO.readProduct(args[0]);
        File vectorFile = new File(args[1]);
        File rgbFile = new File(args[2]);

        String[] rgBbandNames = new String[]{"radiance_7", "radiance_5", "radiance_2", };
        HashMap<String, Object> parameters = new HashMap<>();
        parameters.put("vectorFile", vectorFile);
        parameters.put("separateShapes", false);
        product = GPF.createProduct("Import-Vector", parameters, product);
        String vectorName = FileUtils.getFilenameWithoutExtension(vectorFile);

        quicklookRGBwOverlay(product, rgbFile, rgBbandNames, vectorName);
    }


    public static void quicklookRGBwOverlay(Product product, File rgbFile, String[] RGBbandNames, String vectorName) throws IOException {
    /* Create RGB image */
        Band[] bands = new Band[3];

        for (int k = 0; k < RGBbandNames.length; k++){
            bands[k] = product.getBand(RGBbandNames[k]);
        }

        ImageInfo information = ProductUtils.createImageInfo(bands, true, ProgressMonitor.NULL);
        RenderedImage renderedRGB = ImageManager.getInstance().createColoredBandImage(bands, information, 0);

    /* Create image layers*/
        CollectionLayer collectionLayer = new CollectionLayer();
        LayerContext ctx = new MyLayerContext(product, collectionLayer);
        SceneTransformProvider provider = bands[0];

        // RGB
        ImageLayer RGBLayer = new ImageLayer(renderedRGB);

        // Vector
        VectorDataNode vectorDataNode = product.getVectorDataGroup().get(vectorName);
        VectorDataLayer vectorDataLayer = new VectorDataLayer(ctx, vectorDataNode, provider );

        BufferedImage buffered = new BufferedImage(renderedRGB.getWidth(), renderedRGB.getHeight(), BufferedImage.TYPE_INT_ARGB);
        BufferedImageRendering rendering = new BufferedImageRendering(buffered);

    /* Create the complete image by overlaying */
        collectionLayer.getChildren().add(vectorDataLayer);
        collectionLayer.getChildren().add(RGBLayer);

        collectionLayer.render(rendering);

        JAI.create("filestore", rendering.getImage(), rgbFile.toString(), "PNG");

    }

    private static class MyLayerContext implements LayerContext {

        private final Product product;
        private final Layer rootLayer;

        public MyLayerContext(Product product, Layer rootLayer) {
            this.product = product;
            this.rootLayer = rootLayer;
        }

        @Override
        public Object getCoordinateReferenceSystem() {
            return product.getSceneGeoCoding().getMapCRS();
        }

        @Override
        public Layer getRootLayer() {
            return rootLayer;
        }
    }
}
