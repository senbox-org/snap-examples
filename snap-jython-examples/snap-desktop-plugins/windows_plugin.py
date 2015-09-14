from javax.swing import JTree
from javax.swing import JTable
from javax.swing import JButton
from javax.swing import JTextArea
from javax.swing import JScrollPane
from java.awt import BorderLayout
from java.awt import GridLayout

from org.esa.snap.rcp.scripting import SnapUtils
from org.esa.snap.rcp.scripting import TransientTopComponent

# Demonstrates how to add new tool windows to SNAP Desktop
# see http://bits.netbeans.org/dev/javadoc/org-openide-windows/org/openide/windows/doc-files/api.html#create-top
# see http://docs.oracle.com/javase/8/docs/api/javax/swing/package-summary.html

class MyWindow1(TransientTopComponent):
    def __init__(self):
        self.setName('Jython Explorer')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTree()),
                 BorderLayout.CENTER)


class MyWindow2(TransientTopComponent):
    def __init__(self):
        self.setName('Jython Properties')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTable([['x', 42],
                                     ['y', 'Bibo']],
                                    ['Name', 'Value'])),
                 BorderLayout.CENTER)


class MyWindow3(TransientTopComponent):
    def __init__(self):
        self.setName('Jython Output')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTextArea('Lorem ipsum dolor sit amet, consectetur adipiscing elit, ...')),
                 BorderLayout.CENTER)


class MyWindow4(TransientTopComponent):
    def __init__(self):
        self.setName('Jython Floating')
        self.setLayout(GridLayout(-1, 1))
        self.add(JButton('Action 1'))
        self.add(JButton('Action 2'))
        self.add(JButton('Action 3'))
        self.setLocation(200, 200)
        self.setSize(100, 100)


class Activator:
    def start(self):
        SnapUtils.openWindow(MyWindow1(), "explorer", True)
        SnapUtils.openWindow(MyWindow2(), "properties")
        SnapUtils.openWindow(MyWindow3(), "output")
        SnapUtils.openWindow(MyWindow4(), "floating")
        # Other 'mode' values are "navigator"

    def stop(self):
        pass
