import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'radius_selector_dialog_base.ui'))


class RadiusSelectorDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(RadiusSelectorDialog, self).__init__(parent)
        self.setupUi(self)

