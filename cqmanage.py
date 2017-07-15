#!/usr/bin/python

import os,sys,time
import subprocess
from cheesyq.dpapipetools import *
from cheesyq.DPAColors import *
from cheesyq.DPACheesyQNotes import *
from cheesyq.DPACheesyQ import *
from cheesyq.DPACheesyQTasks import *

from dpa.frange import Frange

import re
import cheesyq.DPADataLibrary as DPADataLibrary

colorWaiting = colorMagenta
colorRunning = colorGreen
colorDone    = colorBlue
colorArchive = colorWhite
colorMachines = colorYellow

def extensionFiltered( listing, extensionlist ):
    filtered = []
    for l in listing:
        lext = os.path.splitext(l)
        for e in extensionlist:
            if lext[1] == "." + e:
                filtered.append(l)
                break
    return filtered

def qtaskList(taskid, frange):
    fids = Frange(input_range=frange)
    frameList = fids.frames
    dl = DPADataLibrary.DjangoLibrary(BaseQName)

    ret = []
    for frame in frameList:
        tid = taskid + "_" + str(frame).zfill(4)

        entry = ["~", "~", "~", "~", "~", "~"]
        entry[0] = tid
        task = dl.get(tid)

        entry[1] = task.queueName
        entry[2] = task.queueStatus
        if task.queueStatus == "archived":
            entry[2] = "done"
        if task.queueStatus == "open":
            entry[2] = "waiting"

        entry[3] = task.queueMachine
        entry[4] = task.queueStartTime
        entry[5] = task.queueElapsedTime
        if task.queueStartTime != "" and task.queueEndTime == "":
            entry[5] = DpaPipeElapsedUnspacedTime( task.queueStartTime, DpaPipeFormattedUnspacedTime() )
        if task.queueStartTime != "" and task.queueEndTime != "":
            entry[5] = DpaPipeElapsedUnspacedTime( task.queueStartTime, task.queueEndTime )

        ret.append(entry)

    return ret

def qtaskMetadata(taskid):
    task = DPADataLibrary.DjangoLibrary(BaseQName).get(taskid)
    if task != "":
        return str(task)
    return ""

def qtaskLogFile(taskid):
    task = DPADataLibrary.DjangoLibrary(BaseQName).get(taskid)
    if task != "":
        return task.logFileName
    return ""

def cqQueueList():
    return getCheesyQueuesList()

def resubmitTask(task, queue):
    cmd = "cqresubmittask " + str(queue) + " " + str(task)
    os.system( cmd )

def transferTask(toQueue, fromQueue, amt):
    cmd = "cqtransfertask " + str(toqueue) + " " + str(fromqueue) + " " + str(amt)
    os.system( cmd )

def view(task):
    cmd = "cqlogviewer " + str(task)
    os.system( cmd )

def display(taskid):
    task = DPADataLibrary.DjangoLibrary(BaseQName).get(taskid)
    if not os.path.exists( task.outputLocation ):
        print "Image directory does not exist. No action taken."
        return

    cmd = "dpavur " + task.outputFileName + " &"
    os.system(cmd)

    bannerMessage = "Displayed " + str(task)
    
def doneTask(task):
    cmd = "cqdonetask " + str(task)
    os.system( cmd )

def examineTask(task):
    cmd = "cqexaminetask " + str(task)
    os.system( cmd )

def moveTask(task, queue):
    cmd = "cqmovetask " + " " + str(queue) + " " + str(task)
    os.system( cmd )

def holdTask(task):
    cmd = "cqmovetask hold " + str(task)
    os.system( cmd )

def stopTask(task):
    cmd = "cqstop " + str(task)
    os.system( cmd )
    
def history():
    cmd = "cqshowhistory"
    os.system( cmd )

# def clobberTask(task, ):
#     cmd = "cqclobbertask " + keypieces[1].strip()
#     for a in keypieces[2:]:
#         cmd = cmd + " " + a.strip() 
#     os.system( cmd )
#     bannerMessage = "Task " + keypieces[2].strip() + " cleaned from queue " + keypieces[1].strip()
