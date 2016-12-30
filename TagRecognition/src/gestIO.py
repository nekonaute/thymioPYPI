# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:28:54 2016

@author: 3200234
"""

import os,tools
import time, datetime
import threading

def writeOutputFile(myStr, directory=None, path=None, log=False):
    """
    Write the times computed
    """
    extension = ".txt" if not log else ".log"
    if directory is None:
        directory = tools.FILE_PATH if not log else tools.LOG_PATH		
    if path is None:
        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin')
        filename = st+""+extension
        path = directory+""+filename
    else:
        directory = os.path.abspath(os.path.dirname(path))
    # creating the directory if not existing
    if not os.path.exists(directory):
        os.makedirs(directory)
    # overriding the previous one (if existing)
    with open(path,'w') as monfile:
        monfile.write(myStr+"\nEnd vizualization\n")


class WriteLog(threading.Thread):
    def __init__(self, string_init):
        threading.Thread.__init__(self)
        self._stop = False
        self.daemon = True
        self.string = string_init+"\nStarting Vizualization\n"
        self.filename = tools.LOG_PATH+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin')+".log"
        self.file_stream = None
        # initializating the file
        self.preStart()

    def preStart(self):
        self.file_stream = open(self.filename, "a+")
        self.file_stream.write(self.string)
        self.string = ""
        self.file_stream.close()

    def run(self):
        while not self._stop:
            self.file_stream = open(self.filename, "a+")
            self.file_stream.write(self.string)
            self.string = ""
            self.file_stream.close()

        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin')
        string = "\nEnd vizualization on {}".format(st)
        self.file_stream = open(self.filename, "a+")
        self.file_stream.write(string)
        self.file_stream.close()

    def stopping(self):
        self._stop = True

    def nextString(self, nstr):
        self.string += nstr
