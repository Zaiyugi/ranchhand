from PySide import QtCore, QtGui
from PySide.QtCore import *

from cheesyq.dpapipetools import *
from cheesyq.DPAColors import *
from cheesyq.DPAWranglingNotes import *
from cheesyq.DPAWrangler import *
from cheesyq.DPACheesyQ import *
import dpa.frange
import cheesyq.DPADataLibrary as DPADataLibrary

from ranchhand import wrangling

class AssignedWrangleListWorker(QObject):
    workRequested = QtCore.Signal()
    finished = QtCore.Signal()
    setNumberOfAssigned = QtCore.Signal(int)
    updateProgress = QtCore.Signal(int)
    jobComplete = QtCore.Signal(list)

    def __init__(self, wrangler, parent = None):
        super(self.__class__, self).__init__(parent)

        self._working = False
        self._abort = False
        self._mutex = QMutex()

        self._wrangler = wrangler

    def setCurrentWrangler(self, wrangler):
        self._wrangler = wrangler

    def requestWork(self):
        self._mutex.lock()
        self._working = True
        self._abort = False
        self._mutex.unlock()

        self.workRequested.emit()

    def abort(self):
        self._mutex.lock()
        if self._working :
            self._abort = True
        self._mutex.unlock()

    def process(self):
        assigned = GetWranglerDB().get(self._wrangler).showAssignment()
        self.wrangle_items = []

        self.setNumberOfAssigned.emit( len(assigned) )
        
        wdb = GetWranglingDB()
        wnotes = WranglingNotes()
        wrd = wrangling.waitRunDone( assigned )
        count = 0
        progress = 0
        for a in assigned:
            self._mutex.lock()
            flag = self._abort
            self._mutex.unlock()

            if flag:
                break

            entry = ["~", "~", "~", "~", "~", "~"]
            entry[0] = a

            waitrundone = wrd[count]
            adata = wdb.get(a)

            if adata != "":
                if waitrundone[2] > 0:
                    adata.status = "running"
                    wdb.set( adata.baseId, adata )
                elif waitrundone[1] > 0:
                    adata.status = "waiting"
                    wdb.set( adata.baseId, adata )
                if adata != "":
                    if waitrundone[2] == 0 and waitrundone[1] == 0 and len(adata.completedFrames) == len(adata.frames) and adata.status != "done" and adata.status != "published" and adata.status != "aborted" and adata.status != "pending":
                        adata.status = "pending"
                        wdb.set( adata.baseId, adata )
                    frames = str(dpa.frange.Frange(input_range=adata.frames))
                    compframes = str(dpa.frange.Frange(input_range=adata.completedFrames))
                    badframes = str(dpa.frange.Frange(input_range=adata.badFrames))
                    entry[1] = frames
                    entry[2] = compframes
                    entry[3] = badframes

            entry[4] = adata.status
            entry[5] = adata.creationDate
            self.wrangle_items.append(entry)

            progress += 1
            self.updateProgress.emit(progress)

        self._mutex.lock()
        self._working = False
        self._mutex.unlock()

        self.jobComplete.emit(self.wrangle_items)
        self.finished.emit()

    # End of AssignedWrangleListWorker class