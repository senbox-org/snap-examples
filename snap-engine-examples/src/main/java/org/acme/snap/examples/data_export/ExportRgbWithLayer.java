package org.acme.snap.examples.data_export;

import com.bc.ceres.core.ProgressMonitor;
import com.bc.ceres.glayer.CollectionLayer;
import com.bc.ceres.glayer.Layer;
import com.bc.ceres.glayer.LayerContext;
import com.bc.ceres.glayer.support.ImageLayer;
import com.bc.ceres.glevel.MultiLevelModel;
import com.bc.ceres.grender.Viewport;
import com.bc.ceres.grender.support.BufferedImageRendering;
import com.bc.ceres.grender.support.DefaultViewport;
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
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.geom.AffineTransform;
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

        String[] rgBbandNames = new String[]{"radiance_1", "radiance_1", "radiance_1", };
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
        MultiLevelModel multiLevelModel = bands[0].getMultiLevelModel();

        // RGB
        ImageLayer RGBLayer = new ImageLayer(renderedRGB, bands[0].getImageToModelTransform(), 1);

        // Vector
        VectorDataNode vectorDataNode = product.getVectorDataGroup().get(vectorName);
        VectorDataLayer vectorDataLayer = new VectorDataLayer(ctx, vectorDataNode, provider );

    /* Create the complete image by overlaying */
        collectionLayer.getChildren().add(vectorDataLayer);
        collectionLayer.getChildren().add(RGBLayer);

        BufferedImage buffered = new BufferedImage(renderedRGB.getWidth(), renderedRGB.getHeight(), BufferedImage.TYPE_INT_ARGB);
        BufferedImageRendering rendering = createRendering(buffered, multiLevelModel);
        collectionLayer.render(rendering);

        JAI.create("filestore", rendering.getImage(), rgbFile.toString(), "PNG");

    }

    private static BufferedImageRendering createRendering(BufferedImage bufferedImage, MultiLevelModel multiLevelModel) {
        AffineTransform m2iTransform = multiLevelModel.getModelToImageTransform(0);
        final Viewport vp2 = new DefaultViewport(new Rectangle(bufferedImage.getWidth(), bufferedImage.getHeight()),
                                                 m2iTransform.getDeterminant() > 0.0);
        vp2.zoom(multiLevelModel.getModelBounds());

        final BufferedImageRendering imageRendering = new BufferedImageRendering(bufferedImage, vp2);
        // because image to model transform is stored with the exported image we have to invert
        // image to view transformation
        final AffineTransform v2mTransform = vp2.getViewToModelTransform();
        v2mTransform.preConcatenate(m2iTransform);
        final AffineTransform v2iTransform = new AffineTransform(v2mTransform);

        final Graphics2D graphics2D = imageRendering.getGraphics();
        v2iTransform.concatenate(graphics2D.getTransform());
        graphics2D.setTransform(v2iTransform);
        return imageRendering;
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
