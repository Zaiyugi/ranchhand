from PySide.QtGui import QDialog, QFormLayout, QDialogButtonBox, QLabel, QComboBox, QLineEdit, QApplication
from PySide.QtCore import Qt, QDateTime

from ranchhand import cqmanage

class TransferTaskDialog(QDialog):
    def __init__(self, parent = None):
        super(TransferTaskDialog, self).__init__(parent)

        layout = QFormLayout(self)

        self.to_queue_selector = QComboBox()
        self.from_queue_selector = QComboBox()

        queue_list = cqmanage.cqQueueList()
        for queue in queue_list:
            self.to_queue_selector.addItem(str(queue))
            self.from_queue_selector.addItem(str(queue))

        self.number_to_transfer = QLineEdit("")

        layout.addRow("To Queue:", self.to_queue_selector)
        layout.addRow("From Queue:", self.from_queue_selector)
        layout.addRow("Amount:", self.number_to_transfer)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle("Transfer Tasks")
        self.resize(225, 150)

    def toQueue(self):
        return self.to_queue_selector.currentText()

    def fromQueue(self):
        return self.from_queue_selector.currentText()

    def amount(self):
        amt = self.number_to_transfer.text()
        if amt == "":
            return 0
        return int(amt)

    # static method to create the dialog and return parameter
    @staticmethod
    def getTransfer(parent = None):
        dialog = TransferTaskDialog(parent)
        result = dialog.exec_()
        toqueue = dialog.toQueue()
        fromqueue = dialog.fromQueue()
        amt = dialog.amount()
        return (toqueue, fromqueue, amt, result == QDialog.Accepted)