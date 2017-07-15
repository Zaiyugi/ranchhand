from PySide.QtGui import QDialog, QFormLayout, QDialogButtonBox, QLabel, QLineEdit, QApplication
from PySide.QtCore import Qt, QDateTime

class TakeWrangleItemsDialog(QDialog):
    def __init__(self, parent = None):
        super(TakeWrangleItemsDialog, self).__init__(parent)

        layout = QFormLayout(self)

        self.wrangler_field = QLineEdit("")
        self.task_regex = QLineEdit("")

        layout.addRow("Wrangler:", self.wrangler_field)
        layout.addRow("Tasks (regex):", self.task_regex)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle("Take Wrangle Items")
        self.resize(250, 100)

    def wrangler(self):
        return self.wrangler_field.text()

    def qtaskRegex(self):
        return self.task_regex.text()

    @staticmethod
    def getTaskRegex(parent = None):
        dialog = TakeWrangleItemsDialog(parent)
        result = dialog.exec_()
        wrangler = dialog.wrangler()
        taskregex = dialog.qtaskRegex()
        return (wrangler, taskregex, result == QDialog.Accepted)