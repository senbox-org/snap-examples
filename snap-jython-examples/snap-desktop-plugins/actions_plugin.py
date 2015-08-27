from org.openide import DialogDisplayer
from org.openide import NotifyDescriptor
from javax.swing import Action
from javax.swing import AbstractAction

from org.esa.snap.rcp.actions import ProxyAction


# Demonstrates how to add new actions to SNAP Desktop


class MyAction1(AbstractAction):
    def __init__(self):
        self.putValue(Action.NAME, 'Hey ho!')

    def actionPerformed(self, actionEvent):
        msg = NotifyDescriptor.Message("Hey ho, hello from Jython!")
        DialogDisplayer.getDefault().notify(msg)


class MyAction2(AbstractAction):
    def __init__(self):
        self.putValue(Action.NAME, 'What is...')

    def actionPerformed(self, actionEvent):
        msg = NotifyDescriptor.Message("...this? Hello from Jython!")
        DialogDisplayer.getDefault().notify(msg)


actions = []


def on_snap_start():
    global actions
    actions = [
        ProxyAction.addAction(MyAction1(), 'Menu/Tools'),
        ProxyAction.addAction(MyAction2(), 'Menu/Help')
    ]


def on_snap_stop():
    global actions
    for action in actions:
        if action:
            ProxyAction.removeAction(action)
