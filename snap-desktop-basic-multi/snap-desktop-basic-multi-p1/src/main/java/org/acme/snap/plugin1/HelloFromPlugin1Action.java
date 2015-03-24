package org.acme.snap.plugin1;

import org.esa.snap.rcp.SnapDialogs;
import org.openide.awt.ActionID;
import org.openide.awt.ActionReference;
import org.openide.awt.ActionRegistration;
import org.openide.util.NbBundle;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

@ActionID(
        category = "Examples",
        id = "HelloFromPlugin1Action"
)
@ActionRegistration(
        displayName = "#CTL_HelloFromPlugin1Action_Name"
)
@ActionReference(path = "Menu/Tools/Examples")
@NbBundle.Messages({
        "CTL_HelloFromPlugin1Action_Name=Basic Extension Sample (Plugin 1)",
        "CTL_HelloFromPlugin1Action_Text=Hello from Plugin #1!"
})
public class HelloFromPlugin1Action implements ActionListener {
    @Override
    public void actionPerformed(ActionEvent e) {
        SnapDialogs.showInformation(Bundle.CTL_HelloFromPlugin1Action_Text(), null);
    }
}

