from PySide.QtGui import QDialog, QFormLayout, QDialogButtonBox, QLabel, QComboBox, QApplication
from PySide.QtCore import Qt, QDateTime

from ranchhand import cqmanage

class QueueDialog(QDialog):
    def __init__(self, parent = None):
        super(QueueDialog, self).__init__(parent)

        layout = QFormLayout(self)
        
        self.queue_selector = QComboBox()
        queue_list = cqmanage.cqQueueList()
        for queue in queue_list:
            self.queue_selector.addItem(str(queue))

        layout.addRow("Queue:", self.queue_selector)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowTitle("Select Queue")
        self.resize(200, 100)

    # get current queue name from the dialog
    def queueName(self):
        return self.queue_selector.currentText()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getQueue(parent = None):
        dialog = QueueDialog(parent)
        result = dialog.exec_()
        queueName = dialog.queueName()
        return (queueName, result == QDialog.Accepted)