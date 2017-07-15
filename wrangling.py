#!/usr/bin/env python

import os,sys,time
from cheesyq.dpapipetools import *
from cheesyq.DPAColors import *
from cheesyq.DPAWranglingNotes import *
from cheesyq.DPAWrangler import *
from cheesyq.DPACheesyQ import *
import dpa.frange
import re
import cheesyq.DPADataLibrary as DPADataLibrary
import readline

def getCurrentWrangler():
    currentWrangler = DpaPipeCmdLineFind("-wrangler",DpaPipeGetUser())
    if not GetWranglerDB().exists( currentWrangler ):
        print "\nWrangler " + currentWrangler + " does not exist."
        print"\nIf you need to become a wrangler, enter the following on the command line:"
        print colorYellow + "\n\tcqaddwrangler \"Your Name\" " + currentWrangler + " <your email address>" + colorWhite
        print "\nThen try cqwrangling again.\n"
        exit(0)

    return currentWrangler;

def waitRunDone( baseid_list ):
    queueList = getCheesyQueuesList()
    result = []

    taskRunningList = []
    taskWaitingList = []
    taskDoneList = []
    for q in queueList:
        tasksRunning = CheesyQTasks( q, "running")
        tasksWaiting = CheesyQTasks( q, "open")
        tasksDone = CheesyQTasks( q, "done")
        taskRunningList = taskRunningList + tasksRunning.showTasks()
        taskWaitingList = taskWaitingList + tasksWaiting.showTasks()
        taskDoneList    = taskDoneList    + tasksDone.showTasks()
    for baseid in baseid_list:
        nbRunning = 0
        nbWaiting = 0
        nbDone = 0
        for t in taskRunningList:
            if re.search( baseid, t ):
                nbRunning = nbRunning + 1
        for t in taskWaitingList:
            if re.search( baseid, t ):
                nbWaiting = nbWaiting + 1
        for t in taskDoneList:
            if re.search( baseid, t ):
                nbDone = nbDone + 1
        summary = "%4s %4s %4s" % ( str(nbWaiting), str(nbRunning), str(nbDone) )
        result.append(  [ summary, nbWaiting, nbRunning, nbDone ] )
    return result


def assignStatus( baseId ):
    statusOptions = [ "waiting", "running", "pending", "aborted", "done", "published", "cancel" ]
    records = GetWranglingDB().match(baseId)
    if len(records) == 0:
        return False
    print "\n\nStatus Options:\n"
    for o in statusOptions:
        print "\t" + o
    keyselect = ""
    while statusOptions.count(keyselect) == 0:
        keyselect = raw_input("Select status >> ")
    if keyselect != "cancel":
        return ChangeWranglingStatus( records, keyselect )
    return False

def grabWrangleItem(wrangler, task):
    AssignWranglerTask(wrangler, str(task) )

def grab( wrangler, baseId ):
    baseIdlist = []
    n = GetWranglerDB().get("none")
    available = list( n.showAssignment() )
    try:
        nbgrab = int(baseId)
        if nbgrab > len(available):
            nbgrab = len(available)
        baseIdlist = available[0:nbgrab]
    except:
        for i in available:
            if re.search( baseId, i ):
                baseIdlist.append( i )
    for i in baseIdlist:
        AssignWranglerTask( wrangler, i )

def releaseWrangleItem(wrangler, task):
    DeassignWranglerTask(wrangler, task)

def release( wrangler, baseId ):
    baseIdlist = []
    n = GetWranglerDB().get(wrangler)
    available = list( n.showAssignment() )
    if baseId == "all":
        baseIdlist = available
    else:
        for i in available:
            if re.search( baseId, i ):
                baseIdlist.append( i )
    for i in baseIdlist:
        DeassignWranglerTask( wrangler, i )


def publish( baseId ):
    record = GetWranglingDB().get(baseId)
    if record == "":
        return 
    print "Publishing is not functioning at this time.\n\n"
    return

def finish( wrangler, baseIds, status ):
    n = GetWranglerDB().get(wrangler)
    if len(baseIds) > 0:
        if status == "cancel":
            return
        if status == "abort":
            if ChangeWranglingStatus( baseIds, "aborted"):
                for i in baseIds:
                    n.removeAssignment( i )
                GetWranglerDB().set( n.username, n )
            return
        if status == "done":
            if ChangeWranglingStatus( baseIds, "done"):
                for i in baseIds:
                    n.removeAssignment( i )
                GetWranglerDB().set( n.username, n )
            return
        if status == "publish":
            if ChangeWranglingStatus( baseIds, "published"):
                db = GetWranglingDB()
                for i in baseIds:
                    publish( i )
                    n.removeAssignment( i )
                    record = db.get( i )
                    if record != "":
                        record.publisher = wrangler
                        record.dataPublished = DpaPipeFormattedUnspacedTime()
                        db.set( record.baseId, record )
                GetWranglerDB().set( n.username, n )


def complete( baseId, frange ):
    db = GetWranglingDB()
    record = db.get( baseId )
    if record == "":
        return
    ff = dpa.frange.Frange(input_range=frange)
    for frame in ff.frames:
        if record.frames.count(frame) == 0:
            return
    rfrn = dpa.frange.Frange( input_range=record.completedFrames )
    rfrn.add( frange )
    record.completedFrames = rfrn.frames
    rfrn = dpa.frange.Frange( input_range=record.badFrames )
    rfrn.remove( frange )
    record.badFrames = rfrn.frames
    db.set( record.baseId, record )


def give( wrangler, currentWrangler, baseId ):
    if GetWranglerDB().exists( wrangler ):
        DeassignWranglerTask( currentWrangler, baseId )
        AssignWranglerTask( wrangler, baseId )

def take( wrangler, currentWrangler, baseId ):
    if GetWranglerDB().exists( wrangler ):
        DeassignWranglerTask( wrangler, baseId )
        AssignWranglerTask( currentWrangler, baseId )

def takeByRegex( wrangler, currentWrangler, regexid ):
    assigned = GetWranglerDB().get(wrangler).showAssignment()
    for i in assigned:
        if re.search( regexid, i ):
            take( wrangler, currentWrangler, i )

def imageInfo( baseId ):
    info = []
    db = GetWranglingDB()
    record = db.get( baseId )
    if record == "":
        return info
    if len(record.frames) == 0:
        return info
    atask = baseId + DpaPipeFormattedFrame( record.frames[0] )
    tdb = DPADataLibrary.DjangoLibrary(BaseQName).get(atask)
    if tdb == "":
        return info
    framesDir = tdb.outputLocation
    if not os.path.exists( framesDir ):
        return info
    info.append( framesDir )
    return info



def nuke( wrangler, baseIds ):
    nodes = []
    assigned = GetWranglerDB().get(wrangler).showAssignment()
    actual_baseIds = []
    db = GetWranglingDB()
    for baseid in baseIds:
        bid = baseid.strip()
        for ii in assigned:
            if re.search( bid, ii ):
                if actual_baseIds.count(ii) == 0:
                    actual_baseIds.append(ii) 
    for bid in actual_baseIds:
        record = db.get(bid)
        if len(record.frames) > 0:
            atask = bid + "_" + DpaPipeFormattedFrame( record.frames[0] )
            tdb = DPADataLibrary.DjangoLibrary(BaseQName).get(atask)
            if tdb != "":
                framesDir = tdb.outputLocation
                if os.path.exists( framesDir ):
                    baseName = "dunno"
                    actual_frames = os.listdir( framesDir )
                    for f in actual_frames:
                        ff = f.split('.')
                        if len(ff) == 3:
                            if ff[2] == "exr":
                                baseName = ff[0]
                                break
                    frange = dpa.frange.Frange( input_range=record.frames )
                    if baseName != "dunno":
                        nodes.append( [framesDir + "/" + baseName,frange] )
                    else:
                        print "No frames found for baseid " + bid
    cmd = "nuke -t " + os.getenv('NUKE_SCRIPTS') + "/nukeWrangling.py "
    for n in nodes:
        cmd = cmd +  n[0] + ".####.exr," + str(n[1].first) + "," + str(n[1].last) + " "
    cmd = cmd + " &"
    print "Loading... \n" + cmd + "\n"
    os.system(cmd)	


def wiki( baseId ):
    db = GetWranglingDB()
    record = db.get( baseId )
    if record == "":
        print "No record found for baseid " + baseId
        return ""
    wikiLine = "|" + baseId + " || " + DpaPipeGetUser() + " || {{ " + record.status + " }}|| " + str( dpa.frange.Frange( input_range=record.badFrames) )
    return wikiLine


def detail( baseId ):
    record = GetWranglingDB().get(baseId)
    if record == "":
        print "No record for baseId " + baseId
        return
    print str(record)
    keyselect = raw_input("Hit return when done >> ")

def search( qtaskid ):
    print "Searching for qtaskid " + qtaskid
    qtask = DPADataLibrary.DjangoLibrary(BaseQName).get(qtaskid)
    if qtask == "":
        return
    print str(qtask)
    keyselect = raw_input("Hit return when done >> ")



def examine( baseId ):
    cmd = "cqexaminetask " + baseId
    os.system(cmd)
    keyselect = raw_input("Hit return when done >> ")


def resubmit( queue, baseId, frames ):
    db = GetWranglingDB()
    record = db.get( baseId )
    if record == "":
        return
    if frames == "bad":
        frames = record.badFrames
    frn = dpa.frange.Frange( input_range=frames )
    for f in frn.frames:
        tid = baseId + "_" + DpaPipeFormattedFrame( f )
        cmd = "cqresubmittask " + queue + " " + tid
        os.system( cmd )
    record = GetWranglingDB().get(baseId)
    frn = dpa.frange.Frange( input_range=record.completedFrames )
    frn.remove( frames )
    record.completedFrames = frn.frames
    frn = dpa.frange.Frange( input_range=record.badFrames )
    frn.remove( frames )
    record.badFrames = frn.frames
    GetWranglingDB().set( record.baseId, record )
    cqNote = WranglingNotes()
    note = "Frames " + str(frn) + " resubmitted to queue " + queue
    cqNote.writeNote( baseId, note )


def check( baseId ):
    record = GetWranglingDB().get(baseId)
    if record == "":
        return 
    #if record.status == "pending" or record.status == "done" or record.status == "aborted" or record.status == "published":
    #    return
    if len(record.frames) == 0:
        return
    qtaskid = record.baseId + "_" + DpaPipeFormattedFrame( record.frames[0] )
    qtask = DPADataLibrary.DjangoLibrary(BaseQName).get(qtaskid)
    if qtask == "":
        return 
    outputFiles = next( os.walk( qtask.outputLocation ) )[2]
    completedFrames = []
    badFrames = []
    badexceptions = 0
    for f in outputFiles:
        if f.endswith(".exr"):
            try:
                baseName, num, ftype = f.split(".", 2)
                framePath = qtask.outputLocation + "/" + f
                cmd = "checkFrame " + framePath # checkFrame is a C++ program which uses openEXR library to check whether an exr file is complete or not.
                checkresult = 1
                #checkresult = os.system(cmd)
                if not checkresult or checkresult == 34304: #The number 34304 is when the frame has no data to check whether the file is incomplete or not
                        badFrames.append( int(num) )
                else:
                    fileSize = float(os.path.getsize( framePath ) / 1024) #This is to check file size. If file size is less than 300KB, then probably that frame is failed.
                    if fileSize >= 300.0:      
                        completedFrames.append( int(num) ) 
                    else:
                        badFrames.append(int(num))
            except:
                #nothing to really do here
                badexceptions = badexceptions + 1
    record.completedFrames = completedFrames
    record.badFrames = badFrames
    GetWranglingDB().set( record.baseId, record )

def unassignedWrangleList():
    n = GetWranglerDB().get("none")

    result = []
    for item in n.showAssignment():
        entry = ["~", "~"]
        entry[0] = item
        s = item.split("_")
        date = "_".join(s[1:7])
        entry[1] = date
        result.append(entry)

    return result


def wrangleList(wrangler):
    assigned = GetWranglerDB().get(wrangler).showAssignment()
    result = []
    if len(assigned) == 0:
        return result
    wdb = GetWranglingDB()
    wnotes = WranglingNotes()
    scaling = 1.0/len(assigned)
    wrd = waitRunDone( assigned )
    count = 0
    for a in assigned:
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
                # compframes = str(dpa.frange.Frange(input_range=adata.completedFrames))
                # datanotes = wnotes.getNotes( adata.baseId )

        entry[4] = adata.status
        entry[5] = adata.creationDate
        result.append(entry)

    return result


def display( baseId ):
    record = GetWranglingDB().get(baseId)
    if record == "":
        return 
    #if record.status == "pending" or record.status == "done" or record.status == "aborted" or record.status == "published":
    #    return
    if len(record.frames) == 0:
        return
    cmd = "cqvur " + baseId + "_" + DpaPipeFormattedFrame(record.frames[0])
    os.system( cmd )


def movie( baseId, options ):
    record = GetWranglingDB().get(baseId)
    if record == "":
        return 
    #if record.status == "pending" or record.status == "done" or record.status == "aborted" or record.status == "published":
    #    return
    if len(record.frames) == 0:
        return
    cmd = "cqmovie " + baseId
    for o in options:
        cmd = cmd + " " + o
    os.system( cmd )
    cqNote = WranglingNotes()
    note = "cqmovie executed"
    cqNote.writeNote( baseId, note )
