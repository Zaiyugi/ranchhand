#!/usr/bin/env python

from PySide import QtCore, QtGui
from PySide.QtCore import *

from ranchhand import wrangling
import sys

class IntSignal(QObject):

   valueChanged = QtCore.Signal(int)

   def __init__(self, parent=None):
      super(IntSignal, self).__init__(parent)

   def update(self, val):
      self.valueChanged.emit(val)

class TupleSignal(QObject):

   valueChanged = QtCore.Signal(tuple)

   def __init__(self, parent=None):
      super(TupleSignal, self).__init__(parent)

   def update(self, val):
      self.valueChanged.emit(val)

class UnassignedWranglingWidget(QtGui.QWidget):

   def __init__(self, parent=None):
      super(UnassignedWranglingWidget, self).__init__(parent)

      self.new_items_to_grab = IntSignal()
      self.selected_wrangle_items = []

      self.initUI()
      self.createActions()

   def initUI(self):

      self.header_labels = ["Created", "Wrangle ID"]
      self.tree_widget = QtGui.QTreeWidget()
      # self.tree_widget.setAlternatingRowColors(True)
      self.tree_widget.setHeaderLabels(self.header_labels)
      self.tree_widget.setRootIsDecorated(False)
      self.tree_widget.setUniformRowHeights(True)
      self.tree_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      self.tree_widget.setSortingEnabled(True)
      self.tree_widget.sortByColumn(1, QtCore.Qt.AscendingOrder)
      self.tree_widget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

      self.tree_widget.itemSelectionChanged.connect(self.trackSelectedWrangleItems)

      self.button_box = QtGui.QDialogButtonBox()
      self.grab_button = self.button_box.addButton("Grab", QtGui.QDialogButtonBox.ActionRole)
      self.update_button = self.button_box.addButton("Update", QtGui.QDialogButtonBox.ActionRole)

      self.grab_button.clicked.connect(self.assignSelectedWrangleItems)
      self.update_button.clicked.connect(self.updateUnassignedWrangleList)

      ### Layout ###

      self.main_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
      self.main_splitter.addWidget(self.tree_widget)
      self.main_splitter.setStretchFactor(0, 40)

      layout = QtGui.QVBoxLayout(self)
      layout.setSpacing(4)
      layout.setContentsMargins(4, 4, 4, 4)
      layout.addWidget(self.main_splitter)
      layout.addWidget(self.button_box)
      self.setLayout(layout)

      self.setWindowTitle('Unassigned Wrangling Items')
      self.resize(400, 800)

   def createActions(self):
      self.exit_action = QtGui.QAction("Exit", self, triggered=self.close)

   def buildUnassignedWrangleList(self):
      self.tree_widget.clear()
      self.tree_widget.setHeaderLabels(self.header_labels)

      # List:
      # - Wrangle ID, Creation Date
      self.wrangle_items = wrangling.unassignedWrangleList()

      self.tree_items = []
      for wrangle_item in self.wrangle_items:
         tree_item = QtGui.QTreeWidgetItem( str(wrangle_item[0]) )

         # Column Order: 
         # - Creation Date, Wrangle ID
         tree_item.setData( 0, QtCore.Qt.DisplayRole, str(wrangle_item[1]) )
         tree_item.setData( 1, QtCore.Qt.DisplayRole, str(wrangle_item[0]) )
         
         self.tree_items.append(tree_item)

      self.tree_widget.addTopLevelItems(self.tree_items)


   #############
   ### Slots ###
   #############

   def trackSelectedWrangleItems(self):
      self.selected_wrangle_items = []
      items = self.tree_widget.selectedItems()
      for i in items:
         #print i.text(1)
         self.selected_wrangle_items.append( str(i.text(1)) )
      #print "\n"

   def assignSelectedWrangleItems(self):
      # print "Grab selected"
      self.new_items_to_grab.update( len(self.selected_wrangle_items) )

   def updateUnassignedWrangleList(self):
      # print "Update unassigned list"
      self.buildUnassignedWrangleList()

   ###############
   ### Getters ###
   ###############

   def selectedWrangleItems(self):
      return self.selected_wrangle_items

   # End of class ControlsWidget

if __name__ == "__main__":
   app = QApplication(sys.argv)

   window = UnassignedWranglingWidget()

   sys.exit(app.exec_())
