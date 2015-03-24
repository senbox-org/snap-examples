package org.acme.snap.plugin2;

import org.esa.snap.rcp.SnapDialogs;
import org.openide.awt.ActionID;
import org.openide.awt.ActionReference;
import org.openide.awt.ActionRegistration;
import org.openide.util.NbBundle;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

@ActionID(
        category = "Examples",
        id = "HelloFromPlugin2Action"
)
@ActionRegistration(
        displayName = "#CTL_HelloFromPlugin2Action_Name"
)
@ActionReference(path = "Menu/Tools/Examples")
@NbBundle.Messages({
        "CTL_HelloFromPlugin2Action_Name=Basic Extension Sample (Plugin 2)",
        "CTL_HelloFromPlugin2Action_Text=Hello from Plugin #2!"
})
public class HelloFromPlugin2Action implements ActionListener {
    @Override
    public void actionPerformed(ActionEvent e) {
        SnapDialogs.showInformation(Bundle.CTL_HelloFromPlugin2Action_Text(), null);
    }
}

