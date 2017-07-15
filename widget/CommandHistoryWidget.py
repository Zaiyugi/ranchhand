#!/usr/bin/env python

from PySide import QtCore, QtGui
from PySide.QtCore import *

import sys

class IntSignal(QObject):

   valueChanged = QtCore.Signal(int)

   def __init__(self, parent=None):
      super(IntSignal, self).__init__(parent)

   def update(self, val):
      self.valueChanged.emit(val)

class CommandHistoryWidget(QtGui.QWidget):

   def __init__(self, parent=None):
      super(CommandHistoryWidget, self).__init__(parent)

      self._mutex = QMutex()

      self.initUI()
      self.createActions()

      color = QtGui.QColor()
      color.setNamedColor("#ff0000")
      self.incomplete_brush = QtGui.QBrush(color)

   def initUI(self):

      self.header_labels = ["Status", "Command"]
      self.tree_widget = QtGui.QTreeWidget()
      self.tree_widget.setHeaderLabels(self.header_labels)
      self.tree_widget.setRootIsDecorated(False)
      self.tree_widget.setUniformRowHeights(True)
      self.tree_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      self.tree_widget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

      ### Layout ###

      self.main_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
      self.main_splitter.addWidget(self.tree_widget)
      self.main_splitter.setStretchFactor(0, 40)

      layout = QtGui.QVBoxLayout(self)
      layout.setSpacing(4)
      layout.setContentsMargins(4, 4, 4, 4)
      layout.addWidget(self.main_splitter)
      self.setLayout(layout)

      self.setWindowTitle('Command History')
      self.resize(400, 800)

   def createActions(self):
      self.exit_action = QtGui.QAction("Exit", self, triggered=self.close)

   def appendToHistory(self, qcmd):
      ndx = self.tree_widget.topLevelItemCount()

      item_id = str(ndx) + "_" + qcmd
      tree_item = QtGui.QTreeWidgetItem( item_id )

      # Column Order: 
      # - Status, Command
      tree_item.setData( 0, QtCore.Qt.DisplayRole, "Incomplete" )
      tree_item.setData( 1, QtCore.Qt.DisplayRole, qcmd )
      tree_item.setForeground( 0, self.incomplete_brush )

      self.tree_widget.insertTopLevelItem( ndx, tree_item )

      return ndx

   #############
   ### Slots ###
   #############

   def updateItemInHistory(self, ndx, status, brush):
      self.tree_widget.topLevelItem( ndx ).setData( 0, QtCore.Qt.DisplayRole, status )
      self.tree_widget.topLevelItem( ndx ).setForeground( 0, brush )

   ###############
   ### Getters ###
   ###############

   # End of class ControlsWidget

if __name__ == "__main__":
   app = QApplication(sys.argv)

   window = CommandHistoryWidget()

   sys.exit(app.exec_())
