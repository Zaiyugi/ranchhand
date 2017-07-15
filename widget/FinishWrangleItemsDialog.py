from PySide.QtGui import QDialog, QFormLayout, QDialogButtonBox, QLabel, QComboBox, QApplication
from PySide.QtCore import Qt, QDateTime

from ranchhand import cqmanage

class FinishWrangleItemsDialog(QDialog):
    def __init__(self, parent = None):
        super(FinishWrangleItemsDialog, self).__init__(parent)

        layout = QFormLayout(self)
        
        self.status_selector = QComboBox()
        status_list = ["abort", "done", "publish", "cancel"]
        for status in status_list:
            self.status_selector.addItem(str(status))

        layout.addRow("Finished Status:", self.status_selector)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle("Select Finished Status")
        self.resize(250, 100)

    # get current status from the dialog
    def status(self):
        return self.status_selector.currentText()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getStatus(parent = None):
        dialog = FinishWrangleItemsDialog(parent)
        result = dialog.exec_()
        status = dialog.status()
        return (status, result == QDialog.Accepted)