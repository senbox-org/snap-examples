from javax.swing import JTree
from javax.swing import JTable
from javax.swing import JScrollPane
from java.awt import BorderLayout
from java.lang import Runnable

from org.openide.windows import TopComponent
from org.openide.windows import WindowManager


# Demonstrates how to add new tool windows to SNAP Desktop
# see http://bits.netbeans.org/dev/javadoc/org-openide-windows/org/openide/windows/doc-files/api.html#create-top

class MyWindow1(TopComponent):
    def __init__(self):
        self.setName('Hello from Jython')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTree()), BorderLayout.CENTER)

    def getPersistenceType(self):
        # Required, as Jython implementations of TopComponent class cannot be deserialized
        return TopComponent.PERSISTENCE_NEVER


class MyWindow2(TopComponent):
    def __init__(self):
        self.setName('Hi from Jython')
        self.setLayout(BorderLayout())
        self.add(JScrollPane(JTable()), BorderLayout.CENTER)

    def getPersistenceType(self):
        # Required, as Jython implementations of TopComponent class cannot be deserialized
        return TopComponent.PERSISTENCE_NEVER


def open_window(window, mode_name='explorer', request_active=False):
    mode = WindowManager.getDefault().findMode(mode_name)
    if mode:
        mode.dockInto(window)
    window.open()
    if request_active:
        window.requestActive()


class Starter(Runnable):
    def run(self):
        open_window(MyWindow1(), "explorer")
        open_window(MyWindow2(), "output", True)


def on_snap_start():
    WindowManager.getDefault().invokeWhenUIReady(Starter())


def on_snap_stop():
    pass
