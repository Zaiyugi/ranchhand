#!/usr/bin/env python

from PySide import QtCore, QtGui
from PySide.QtCore import *

from ranchhand import cqmanage

from subprocess import check_output
import sys

class MetadataViewerWidget(QtGui.QWidget):

   def __init__(self, parent=None):
      super(MetadataViewerWidget, self).__init__(parent)

      self.selected_qtask_id = ""

      self.initUI()
      
      color = QtGui.QColor()
      self.brushes = {}
      color.setNamedColor("#ddd")
      self.text_brush = QtGui.QBrush(color)

   def initUI(self):

      self.metadata_header_labels = ["Tag", "Data"]

      self.metadata_display = QtGui.QTreeWidget()
      self.metadata_display.setHeaderLabels(self.metadata_header_labels)
      self.metadata_display.setRootIsDecorated(False)
      self.metadata_display.setUniformRowHeights(True)
      self.metadata_display.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      self.metadata_display.setSortingEnabled(False)
      self.metadata_display.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

      layout = QtGui.QVBoxLayout(self)
      layout.setSpacing(4)
      layout.setContentsMargins(4, 4, 4, 4)
      layout.addWidget(self.metadata_display)
      self.setLayout(layout)

      self.setWindowTitle('')
      self.resize(800, 1200)

   def createActions(self):
      self.exit_action = QtGui.QAction("Exit", self, triggered=self.close)

   def buildMetadataDisplay(self):
      self.metadata_display.clear()
      self.metadata_display.setHeaderLabels(self.metadata_header_labels)

      qid = self.selected_qtask_id
      qmd = check_output(["rhshowtask", qid])
      qmd = qmd.split("\n")

      # metadata = cqmanage.qtaskMetadata(self.selected_qtask_id)
      
      md_items = []
      for line in qmd:
         line = ''.join(line.split())
         line = line.split(":")

         item = QtGui.QTreeWidgetItem( str(line[0]) )
         item.setData( 0, QtCore.Qt.DisplayRole, str(line[0]) )
         item.setForeground(0, self.text_brush)
         data = ""
         if len(line) == 2:
            data = line[1]
         item.setData( 1, QtCore.Qt.DisplayRole, data )
         item.setForeground(1, self.text_brush)
         md_items.append(item)

      self.metadata_display.addTopLevelItems(md_items)

   ###############
   ### Setters ###
   ###############

   def setQTaskID(self, taskid):
      self.selected_qtask_id = taskid
      self.buildMetadataDisplay()
      self.setWindowTitle("Viewing Metadata for: " + taskid)

   ###############
   ### Getters ###
   ###############

   def selectedQTaskID(self):
      return self.selected_qtask_id

   # End of class MetadataViewerWidget

if __name__ == "__main__":
   app = QApplication(sys.argv)

   window = MetadataViewerWidget()

   sys.exit(app.exec_())
