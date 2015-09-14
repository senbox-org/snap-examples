from javax.swing import Action
from javax.swing import AbstractAction

from org.esa.snap.rcp import SnapDialogs
from org.esa.snap.rcp.scripting import SnapUtils


# Demonstrates how to add new actions to SNAP Desktop


class MyAction1(AbstractAction):
    def __init__(self):
        self.putValue(Action.NAME, 'Hey ho!')

    def actionPerformed(self, actionEvent):
        SnapDialogs.showMessage("Hey ho, hello from Jython!", None)


class MyAction2(AbstractAction):
    def __init__(self):
        self.putValue(Action.NAME, 'What is...')

    def actionPerformed(self, actionEvent):
        SnapDialogs.showMessage("...this? Hello from Jython!", None)


class Activator:
    def start(self):
        self.actions = [
            SnapUtils.addAction(MyAction1(), 'Menu/Tools'),
            SnapUtils.addAction(MyAction2(), 'Menu/Help')
        ]

    def stop(self):
        for action in self.actions:
            if action:
                SnapUtils.removeAction(action)
