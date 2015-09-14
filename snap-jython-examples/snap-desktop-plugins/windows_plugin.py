from javax.swing import JTree
from javax.swing import JTable
from javax.swing import JScrollPane
from java.awt import BorderLayout

from org.esa.snap.rcp.scripting import SnapUtils
from org.esa.snap.rcp.scripting import TransientTopComponent

# Demonstrates how to add new tool windows to SNAP Desktop
# see http://bits.netbeans.org/dev/javadoc/org-openide-windows/org/openide/windows/doc-files/api.html#create-top

class MyWindow1(TransientTopComponent):
    def __init__(self):
        self.setName('Hello from Jython')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTree()), BorderLayout.CENTER)


class MyWindow2(TransientTopComponent):
    def __init__(self):
        self.setName('Hi from Jython')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTable()), BorderLayout.CENTER)


class Activator:

    def onStart(self):
        SnapUtils.openWindow(MyWindow1())
        SnapUtils.openWindow(MyWindow2())

    def onStop(self):
        pass
