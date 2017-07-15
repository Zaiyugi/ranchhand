from PySide import QtCore, QtGui
from PySide.QtCore import *

from cheesyq.dpapipetools import *
from cheesyq.DPAColors import *
from cheesyq.DPACheesyQNotes import *
from cheesyq.DPACheesyQ import *
from cheesyq.DPACheesyQTasks import *

from dpa.frange import Frange
import cheesyq.DPADataLibrary as DPADataLibrary

import re
from Queue import *
import time

from ranchhand import cqmanage

class CommandLineTask():
    def __init__(self):
        self.taskid = ""
        self.command = ""
        self.to_queue = ""
        self.from_queue = ""
        self.transfer_amt = 0
        self.history_ndx = -1

class CommandLineWorker(QObject):
    workRequested = QtCore.Signal()
    finished = QtCore.Signal()
    setTotalItems = QtCore.Signal(int)
    updateProgress = QtCore.Signal(int)
    jobComplete = QtCore.Signal(int)

    valid_commands = ["cqmovetask", "cqholdtask", "cqdonetask", "cqstop", "cqtransfertask", "cqresubmittask"]

    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)

        self._working = False
        self._abort = False
        self._activity_mutex = QMutex()

        self._command_queue = Queue(maxsize=0)

    def addToQueue(self, item):
        self._command_queue.put(item)

    def requestWork(self):
        self._activity_mutex.lock()
        self._working = True
        self._abort = False
        self._activity_mutex.unlock()

        self.workRequested.emit()

    def abort(self):
        self._activity_mutex.lock()
        if self._working :
            self._abort = True
        self._activity_mutex.unlock()

    def process(self):

        # Run until abort is set
        while True:
            self._activity_mutex.lock()
            flag = self._abort
            self._activity_mutex.unlock()
            if flag:
                break

            if not self._command_queue.empty():
                task = self._command_queue.get()

                taskid = task.taskid
                cmd = task.command

                print("CLWorker starting on " + cmd + " on tasks " + taskid)

                if cmd == "cqmovetask":
                    cqmanage.moveTask(taskid, task.to_queue)
                elif cmd == "cqholdtask":
                    cqmanage.holdTask(taskid)
                elif cmd == "cqdonetask":
                    cqmanage.doneTask(taskid)
                elif cmd == "cqstop":
                    cqmanage.stopTask(taskid)
                elif cmd == "cqtransfertask":
                    cqmanage.transferTask(task.to_queue, task.from_queue, task.transfer_amt)
                elif cmd == "cqresubmittask":
                    cqmanage.resubmitTask(taskid, task.to_queue)

                self.jobComplete.emit(task.history_ndx)
            else:
                time.sleep(2)

        self._activity_mutex.lock()
        self._working = False
        self._activity_mutex.unlock()

        self.finished.emit()

    # End of CommandLineWorker class