/*
 * Copyright (C) 2011 Brockmann Consult GmbH (info@brockmann-consult.de)
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

package org.esa.snap.examples.selection;

import com.bc.ceres.swing.figure.Figure;
import com.bc.ceres.swing.figure.FigureSelection;
import com.bc.ceres.swing.figure.ShapeFigure;
import org.esa.snap.core.dataio.ProductIO;
import org.esa.snap.core.dataio.ProductSubsetBuilder;
import org.esa.snap.core.dataio.ProductSubsetDef;
import org.esa.snap.core.dataio.dimap.DimapFileFilter;
import org.esa.snap.core.datamodel.Product;
import org.esa.snap.rcp.SnapApp;
import org.esa.snap.rcp.actions.file.ProductFileChooser;
import org.esa.snap.rcp.actions.file.ProductOpener;
import org.esa.snap.rcp.actions.file.WriteProductOperation;
import org.esa.snap.rcp.util.Dialogs;
import org.esa.snap.rcp.util.MultiSizeIssue;
import org.esa.snap.ui.product.ProductSceneView;
import org.netbeans.api.progress.BaseProgressUtils;
import org.openide.awt.ActionID;
import org.openide.awt.ActionReference;
import org.openide.awt.ActionReferences;
import org.openide.awt.ActionRegistration;
import org.openide.util.ContextAwareAction;
import org.openide.util.Lookup;
import org.openide.util.LookupEvent;
import org.openide.util.LookupListener;
import org.openide.util.NbBundle;
import org.openide.util.Utilities;
import org.openide.util.WeakListeners;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JFileChooser;
import java.awt.event.ActionEvent;
import java.io.File;
import java.io.IOException;
import java.util.prefs.Preferences;


@ActionID(category = "Example", id = "org.esa.snap.examples.selection.SubsetByGeometryAction" )
@ActionRegistration(
        displayName = "#CTL_SubsetByGeometryAction_MenuText",
        popupText = "#CTL_SubsetByGeometryAction_PopupText",
        lazy = false
)
@ActionReferences({
        @ActionReference(path = "Menu/Tools/Examples",position = 60 ), // adds action to the main menu
        @ActionReference(path = "Context/ProductSceneView" , position = 40) // makes the action visible in the context menu of the scene view 
})
@NbBundle.Messages({
        "CTL_SubsetByGeometryAction_MenuText=Subset by Geometry",
        "CTL_SubsetByGeometryAction_PopupText=Subset by Geometry",
        "CTL_SubsetByGeometryAction_DialogTitle=Subset by Geometry",
        "CTL_SubsetByGeometryAction_ShortDescription=Subset a product by a selected geometry."
})

public class SubsetByGeometryAction extends AbstractAction implements ContextAwareAction, LookupListener {

    private static final String ERR_MSG_BASE = "Cannot create subset:\n";

    private final Lookup.Result<FigureSelection> result;

    @SuppressWarnings("unused")
    public SubsetByGeometryAction() {
        this(Utilities.actionsGlobalContext());
    }

    public SubsetByGeometryAction(Lookup lkp) {
        super(Bundle.CTL_SubsetByGeometryAction_MenuText());
        putValue("popupText", Bundle.CTL_SubsetByGeometryAction_PopupText());
        result = lkp.lookupResult(FigureSelection.class);
        result.addLookupListener(WeakListeners.create(LookupListener.class, this, result));
        updateEnableState(getCurrentFigureSelection());
    }

    /**
     * Invoked when a command action is performed.
     *
     * @param event the command event
     */
    @Override
    public void actionPerformed(ActionEvent event) {
        final ProductSceneView sceneView = SnapApp.getDefault().getSelectedProductSceneView();
        if(sceneView != null && sceneView.getProduct().isMultiSize()) {
            MultiSizeIssue.maybeResample(sceneView.getProduct());
            //as the following code relies on current selections, nothing is done after resampling
        } else {
            createSubset();
        }
    }

    @Override
    public Action createContextAwareInstance(Lookup lkp) {
        return new SubsetByGeometryAction(lkp);
    }

    @Override
    public void resultChanged(LookupEvent le) {
        updateEnableState(getCurrentFigureSelection());
    }

    private void createSubset() {

        // Get current view showing a product's band
        final ProductSceneView view = SnapApp.getDefault().getSelectedProductSceneView();
        if (view == null) {
            return;
        }
        final FigureSelection selection = getCurrentFigureSelection();

        // Get the geometry of the selection
        ShapeFigure geometry = null;
        if (selection.getFigureCount() > 0) {
            Figure figure = selection.getFigure(0);
            if (figure instanceof ShapeFigure) {
                geometry = (ShapeFigure) figure;
            }
        }

        if (geometry == null) {
            Dialogs.showError(Bundle.CTL_SubsetByGeometryAction_DialogTitle(),
                              ERR_MSG_BASE + "There is no geometry defined in the current selection.");
            return;
        }

        Product subset;
        try {
            Product product = view.getProduct();
            String productName = product.getName();
            ProductSubsetDef subsetDef = new ProductSubsetDef();
            subsetDef.setRegion(geometry.getBounds().getBounds());
            subset = ProductSubsetBuilder.createProductSubset(product, subsetDef, productName + "_subset",
                                                                             "Subset of " + productName);
        } catch (IOException e) {
            Dialogs.showError(Bundle.CTL_SubsetByGeometryAction_DialogTitle(),
                                  ERR_MSG_BASE + "An I/O error occurred:\n" + e.getMessage());
            return;
        }

        Preferences preferences = SnapApp.getDefault().getPreferences();
        ProductFileChooser fc = new ProductFileChooser(new File(preferences.get(ProductOpener.PREFERENCES_KEY_LAST_PRODUCT_DIR, ".")));
        fc.setDialogType(JFileChooser.SAVE_DIALOG);
        fc.setSubsetEnabled(true);
        fc.addChoosableFileFilter(new DimapFileFilter());
        fc.setProductToExport(subset);
        int returnVal = fc.showSaveDialog(SnapApp.getDefault().getMainFrame());
        File newFile = fc.getSelectedFile();
        if (returnVal != JFileChooser.APPROVE_OPTION || newFile == null) {
            // cancelled
            return;
        }

        WriteProductOperation operation = new WriteProductOperation(subset, newFile, ProductIO.DEFAULT_FORMAT_NAME, false);
        BaseProgressUtils.runOffEventThreadWithProgressDialog(operation,
                                                              Bundle.CTL_SubsetByGeometryAction_DialogTitle(),
                                                              operation.getProgressHandle(),
                                                              true,
                                                              50,
                                                              1000);

    }

    private FigureSelection getCurrentFigureSelection() {
        return result.allInstances().stream().findFirst().orElse(null);
    }

    private void updateEnableState(FigureSelection figureSelection) {
        setEnabled(figureSelection != null);
    }

}
