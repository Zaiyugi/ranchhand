#!/usr/bin/env python

from PySide import QtCore, QtGui
from PySide.QtCore import *

from ranchhand import cqmanage
import sys

class LogViewerWidget(QtGui.QWidget):

   def __init__(self, parent=None):
      super(LogViewerWidget, self).__init__(parent)

      self.selected_qtask_id = ""

      self.initUI()
      
   def initUI(self):

      self.log_display = QtGui.QPlainTextEdit()
      self.log_display.setReadOnly(True)
      self.log_display.setWordWrapMode(QtGui.QTextOption.NoWrap)

      layout = QtGui.QVBoxLayout(self)
      layout.setSpacing(4)
      layout.setContentsMargins(4, 4, 4, 4)
      layout.addWidget(self.log_display)
      self.setLayout(layout)

      self.setWindowTitle('')
      self.resize(800, 1200)

   def createActions(self):
      self.exit_action = QtGui.QAction("Exit", self, triggered=self.close)

   def buildLogDisplay(self):
      logfile = cqmanage.qtaskLogFile(self.selected_qtask_id)
      
      logtext = ""
      if logfile != "":
         log_fo = open(logfile, 'r')
         for line in log_fo:
            logtext = logtext + line
         log_fo.close()
      else:
         logtext = "QTask " + self.selected_qtask_id + " has no log\n"

      self.log_display.document().setPlainText(logtext)

   ###############
   ### Setters ###
   ###############

   def setQTaskID(self, taskid):
      self.selected_qtask_id = taskid
      self.buildLogDisplay()
      self.setWindowTitle("Viewing Log for: " + taskid)

   ###############
   ### Getters ###
   ###############

   def selectedQTaskID(self):
      return self.selected_qtask_id

   # End of class LogViewerWidget

if __name__ == "__main__":
   app = QApplication(sys.argv)

   window = LogViewerWidget()

   sys.exit(app.exec_())
