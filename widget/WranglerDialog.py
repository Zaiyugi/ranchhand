from PySide.QtGui import QDialog, QFormLayout, QDialogButtonBox, QLabel, QLineEdit, QApplication
from PySide.QtCore import Qt, QDateTime

class WranglerDialog(QDialog):
    def __init__(self, parent = None):
        super(WranglerDialog, self).__init__(parent)

        layout = QFormLayout(self)

        self.wrangler_field = QLineEdit("")

        layout.addRow("Wrangler:", self.wrangler_field)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle("Set Wrangler")
        self.resize(250, 100)

    # get current date and time from the dialog
    def wrangler(self):
        return self.wrangler_field.text()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getWrangler(parent = None):
        dialog = WranglerDialog(parent)
        result = dialog.exec_()
        wrangler = dialog.wrangler()
        return (wrangler, result == QDialog.Accepted)