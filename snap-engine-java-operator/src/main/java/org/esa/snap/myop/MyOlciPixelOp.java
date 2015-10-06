/*
 * Copyright (C) 2012 Brockmann Consult GmbH (info@brockmann-consult.de)
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, see http://www.gnu.org/licenses/
 */

package org.esa.snap.myop;

import org.esa.snap.core.datamodel.Band;
import org.esa.snap.core.datamodel.FlagCoding;
import org.esa.snap.core.datamodel.Mask;
import org.esa.snap.core.datamodel.Product;
import org.esa.snap.core.datamodel.ProductData;
import org.esa.snap.core.datamodel.SampleCoding;
import org.esa.snap.core.datamodel.TiePointGrid;
import org.esa.snap.core.datamodel.VirtualBand;
import org.esa.snap.core.gpf.OperatorException;
import org.esa.snap.core.gpf.OperatorSpi;
import org.esa.snap.core.gpf.annotations.OperatorMetadata;
import org.esa.snap.core.gpf.annotations.Parameter;
import org.esa.snap.core.gpf.annotations.SourceProduct;
import org.esa.snap.core.gpf.annotations.TargetProduct;
import org.esa.snap.core.gpf.pointop.PixelOperator;
import org.esa.snap.core.gpf.pointop.ProductConfigurer;
import org.esa.snap.core.gpf.pointop.Sample;
import org.esa.snap.core.gpf.pointop.SourceSampleConfigurer;
import org.esa.snap.core.gpf.pointop.TargetSampleConfigurer;
import org.esa.snap.core.gpf.pointop.WritableSample;
import org.esa.snap.util.ProductUtils;

import java.awt.Color;

/**
 * The <code>MyMerisPointOp</code> serves as a template for other MERIS L1B/OLCI point ops.
 *
 * @author Norman
 */
@OperatorMetadata(
        alias = "MyOp",
        category = "Optical Processing/Thematic <Water|Land> Processing",
        description = "The '<your operator name here>' operator retrieves '<your operator product(s) here>' from MERIS/OLCI L1B products.",
        authors = "<your name here>",
        copyright = "<your copyright info here>")
public class MyOlciPixelOp extends PixelOperator {

    @SourceProduct(alias = "source", description = "The source product.")
    private Product sourceProduct;

    @TargetProduct
    private Product targetProduct;

    @Parameter(defaultValue = "0.0", description = "<your parameter description here>.")
    private double threshold;

    @Parameter(defaultValue = "true", description = "Weather or not to copy the Level-1 quality information.")
    private boolean copySourceFlags;

    /**
     * Configures all source samples that this operator requires for the computation of target samples.
     * Source sample are defined by using the provided {@link SourceSampleConfigurer}.
     * <p/>
     * <p/> The method is called by {@link #initialize()}.
     *
     * @param sampleConfigurer The configurer that defines the layout of a pixel.
     * @throws OperatorException If the source samples cannot be configured.
     */
    @Override
    protected void configureSourceSamples(SourceSampleConfigurer sampleConfigurer) throws OperatorException {
        sampleConfigurer.defineSample(0, findWaveBand(sourceProduct, true, 400, 15, ""));
        sampleConfigurer.defineSample(1, findWaveBand(sourceProduct, true, 412.5, 10, ""));
        sampleConfigurer.defineSample(2, findWaveBand(sourceProduct, true, 442.5, 10, ""));
        sampleConfigurer.defineSample(3, findWaveBand(sourceProduct, true, 490, 10, ""));
        sampleConfigurer.defineSample(4, findWaveBand(sourceProduct, true, 510, 10, ""));
        sampleConfigurer.defineSample(5, findWaveBand(sourceProduct, true, 560, 10, ""));
        sampleConfigurer.defineSample(6, findWaveBand(sourceProduct, true, 620, 10, ""));
        sampleConfigurer.defineSample(7, findWaveBand(sourceProduct, true, 665, 10, ""));
        sampleConfigurer.defineSample(8, findWaveBand(sourceProduct, true, 673.75, 7.5, ""));
        sampleConfigurer.defineSample(9, findWaveBand(sourceProduct, true, 681.25, 7.5, ""));
        sampleConfigurer.defineSample(10, findWaveBand(sourceProduct, true, 708.75, 10, ""));
        sampleConfigurer.defineSample(11, findWaveBand(sourceProduct, true, 753.75, 7.5, ""));
        sampleConfigurer.defineSample(12, findWaveBand(sourceProduct, true, 761.25, 2.5, ""));
        sampleConfigurer.defineSample(13, findWaveBand(sourceProduct, true, 764.375, 3.75, ""));
        sampleConfigurer.defineSample(14, findWaveBand(sourceProduct, true, 767.5, 2.5, ""));
        sampleConfigurer.defineSample(15, findWaveBand(sourceProduct, true, 778.75, 15, ""));
        sampleConfigurer.defineSample(16, findWaveBand(sourceProduct, true, 865, 20, ""));
        sampleConfigurer.defineSample(17, findWaveBand(sourceProduct, true, 885, 10, ""));
        sampleConfigurer.defineSample(18, findWaveBand(sourceProduct, true, 900, 10, ""));
        sampleConfigurer.defineSample(19, findWaveBand(sourceProduct, true, 940, 20, ""));
        sampleConfigurer.defineSample(20, findWaveBand(sourceProduct, true, 1020, 40, ""));
    }

    /**
     * Configures all target samples computed by this operator.
     * Target samples are defined by using the provided {@link TargetSampleConfigurer}.
     * <p/>
     * <p/> The method is called by {@link #initialize()}.
     *
     * @param sampleConfigurer The configurer that defines the layout of a pixel.
     * @throws OperatorException If the target samples cannot be configured.
     */
    @Override
    protected void configureTargetSamples(TargetSampleConfigurer sampleConfigurer) throws OperatorException {
        sampleConfigurer.defineSample(0, "chl");
        sampleConfigurer.defineSample(1, "l2_flags");
        // add more target samples here
    }

    /**
     * Configures the target product via the given {@link ProductConfigurer}. Called by {@link #initialize()}.
     * <p/>
     * Client implementations of this method usually add product components to the given target product, such as
     * {@link Band bands} to be computed by this operator,
     * {@link VirtualBand virtual bands},
     * {@link Mask masks}
     * or {@link SampleCoding sample codings}.
     * <p/>
     * The default implementation retrieves the (first) source product and copies to the target product
     * <ul>
     * <li>the start and stop time by calling {@link ProductConfigurer#copyTimeCoding()},</li>
     * <li>all tie-point grids by calling {@link ProductConfigurer#copyTiePointGrids(String...)},</li>
     * <li>the geo-coding by calling {@link ProductConfigurer#copyGeoCoding()}.</li>
     * </ul>
     * <p/>
     * Clients that require a similar behaviour in their operator shall first call the {@code super} method
     * in their implementation.
     *
     * @param productConfigurer The target product configurer.
     * @throws OperatorException If the target product cannot be configured.
     * @see Product#addBand(Band)
     * @see Product#addBand(String, String)
     * @see Product#addTiePointGrid(TiePointGrid)
     * @see Product#getMaskGroup()
     */
    @Override
    protected void configureTargetProduct(ProductConfigurer productConfigurer) {
        super.configureTargetProduct(productConfigurer);

        if (copySourceFlags) {
            // Copy Level-1 quality information to target
            ProductUtils.copyFlagBands(sourceProduct, targetProduct, true);
        }

        targetProduct.addBand("chl", ProductData.TYPE_FLOAT32);
        targetProduct.addBand("l2_flags", ProductData.TYPE_INT16);

        FlagCoding qualityFlags = new FlagCoding("l2_flags");
        qualityFlags.addFlag("INVALID", 0x01, "Pixel is invalid");
        // add more flags here

        targetProduct.getFlagCodingGroup().add(qualityFlags);
        // add more flag codings here

        targetProduct.addMask("invalid", "l2_flags.INVALID", "Pixel is invalid", Color.RED, 0.7);
        // add more masks here
    }

    /**
     * Computes the target samples from the given source samples.
     * <p/>
     * The number of source/target samples is the maximum defined sample index plus one. Source/target samples are defined
     * by using the respective sample configurer in the
     * {@link #configureSourceSamples(SourceSampleConfigurer) configureSourceSamples} and
     * {@link #configureTargetSamples(TargetSampleConfigurer) configureTargetSamples} methods.
     * Attempts to read from source samples or write to target samples at undefined sample indices will
     * cause undefined behaviour.
     *
     * @param x             The current pixel's X coordinate.
     * @param y             The current pixel's Y coordinate.
     * @param sourceSamples The source samples (= source pixel).
     * @param targetSamples The target samples (= target pixel).
     */
    @Override
    protected void computePixel(int x, int y, Sample[] sourceSamples, WritableSample[] targetSamples) {
        double rad1 = sourceSamples[0].getDouble();
        double rad2 = sourceSamples[1].getDouble();
        double rad3 = sourceSamples[2].getDouble();
        double rad4 = sourceSamples[3].getDouble();
        double rad5 = sourceSamples[4].getDouble();
        double rad6 = sourceSamples[5].getDouble();
        double rad7 = sourceSamples[6].getDouble();
        double rad8 = sourceSamples[7].getDouble();
        double rad9 = sourceSamples[8].getDouble();
        double rad10 = sourceSamples[9].getDouble();
        double rad11 = sourceSamples[10].getDouble();
        double rad12 = sourceSamples[11].getDouble();
        double rad13 = sourceSamples[12].getDouble();
        double rad14 = sourceSamples[13].getDouble();
        double rad15 = sourceSamples[14].getDouble();
        double rad16 = sourceSamples[15].getDouble();
        double rad17 = sourceSamples[16].getDouble();
        double rad18 = sourceSamples[17].getDouble();
        double rad19 = sourceSamples[18].getDouble();
        double rad20 = sourceSamples[19].getDouble();
        double rad21 = sourceSamples[20].getDouble();

        double chl = (rad1 + rad2 + rad3 + rad4 + rad5 + rad6 + rad7 + rad8 + rad9 + rad10 +
                rad11 + rad12 + rad13 + rad14 + rad15 + rad16 + rad17 + rad18 + rad19 + rad20 +
                rad21) / 21.0;

        targetSamples[0].set(chl);
    }

    // package local for testing reasons only
    static String findWaveBand(Product product, boolean fail, double centralWavelength, double maxDeltaWavelength, String... bandNames) {
        Band[] bands = product.getBands();
        String bestBand = null;
        double minDelta = Double.MAX_VALUE;
        for (Band band : bands) {
            double bandWavelength = band.getSpectralWavelength();
            if (bandWavelength > 0.0) {
                double delta = Math.abs(bandWavelength - centralWavelength);
                if (delta < minDelta && delta <= maxDeltaWavelength) {
                    bestBand = band.getName();
                    minDelta = delta;
                }
            }
        }
        if (bestBand != null) {
            return bestBand;
        }
        for (String bandName : bandNames) {
            Band band = product.getBand(bandName);
            if (band != null) {
                return band.getName();
            }
        }
        if (fail) {
            throw new OperatorException("Missing band at " + centralWavelength + " nm");
        }
        return null;
    }

    public static class Spi extends OperatorSpi {

        public Spi() {
            super(MyOlciPixelOp.class);
        }

    }
}
