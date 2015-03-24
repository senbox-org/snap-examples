package org.acme.snap.examples;

import org.esa.snap.rcp.SnapDialogs;
import org.openide.awt.ActionID;
import org.openide.awt.ActionReference;
import org.openide.awt.ActionRegistration;
import org.openide.util.NbBundle;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

@ActionID(
        category = "Examples",
        id = "HelloFromPluginAction"
)
@ActionRegistration(
        displayName = "#CTL_HelloFromPluginAction_Name"
)
@ActionReference(path = "Menu/Tools/Examples")
@NbBundle.Messages({
        "CTL_HelloFromPluginAction_Name=Basic Extension Sample",
        "CTL_HelloFromPluginAction_Text=Hello from Plugin!"
})
public class HelloFromPluginAction implements ActionListener {
    @Override
    public void actionPerformed(ActionEvent e) {
        SnapDialogs.showInformation(Bundle.CTL_HelloFromPluginAction_Text(), null);
    }
}

