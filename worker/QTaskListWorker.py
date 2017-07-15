from PySide import QtCore, QtGui
from PySide.QtCore import *

from cheesyq.dpapipetools import *
from cheesyq.DPAColors import *
from cheesyq.DPACheesyQNotes import *
from cheesyq.DPACheesyQ import *
from cheesyq.DPACheesyQTasks import *

from dpa.frange import Frange

import re
import cheesyq.DPADataLibrary as DPADataLibrary

from ranchhand import cqmanage

class QTaskListWorker(QObject):
    workRequested = QtCore.Signal()
    finished = QtCore.Signal()
    setNumberOfQTasks = QtCore.Signal(int)
    updateProgress = QtCore.Signal(int)
    jobComplete = QtCore.Signal(list)

    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)

        self._working = False
        self._abort = False
        self._mutex = QMutex()

        self._wrangletasklist = []
        self._max_qtasks = 0
        self._current_progress = 0

    def setWrangleTaskList(self, wtl):
        self._wrangletasklist = wtl

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
        self._max_qtasks = 0
        self._current_progress = 0
        result = []
        for item in self._wrangletasklist:
            frange = str(item.text(2))
            fids = Frange(input_range=frange)
            self._max_qtasks += len(fids.frames)

        self.setNumberOfQTasks.emit(self._max_qtasks)
        self.updateProgress.emit(self._current_progress)
        for item in self._wrangletasklist:
            self._mutex.lock()
            flag = self._abort
            self._mutex.unlock()
            if flag:
                break

            taskid = str(item.text(5))
            frange = str(item.text(2))

            fids = Frange(input_range=frange)
            frameList = fids.frames

            dl = DPADataLibrary.DjangoLibrary(BaseQName)
            for frame in frameList:
                tid = taskid + "_" + DpaPipeFormattedFrame( frame )

                entry = ["~", "~", "~", "~", "~", "~"]
                entry[0] = tid
                task = dl.get(tid)

                entry[1] = task.queueName
                entry[2] = task.queueStatus
                entry[3] = task.queueMachine
                entry[4] = task.queueStartTime
                entry[5] = task.queueElapsedTime

                if task.queueStatus == "archived":
                    entry[2] = "done"
                elif task.queueStatus == "open":
                    entry[2] = "waiting"
                else:
                    if task.queueStartTime != "" and task.queueEndTime == "":
                        entry[5] = DpaPipeElapsedUnspacedTime( task.queueStartTime, DpaPipeFormattedUnspacedTime() )
                # if task.queueStartTime != "" and task.queueEndTime != "":
                #     entry[5] = DpaPipeElapsedUnspacedTime( task.queueStartTime, task.queueEndTime )

                result.append(entry)
                self._current_progress += 1
                self.updateProgress.emit(self._current_progress)

        self._mutex.lock()
        self._working = False
        self._mutex.unlock()

        self.jobComplete.emit(result)
        self.finished.emit()

    # End of QTaskListWorker class