# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 19:48:05 2016

File to create special exceptions or write on the error stream

@author: daphnehb
"""

import sys

"""
Write a message on the error stream of the system
"""
def print_err(str_error):
    sys.stderr.write(str_error+"\n")
    
"""
Exception raised for Shutdown camera
"""
class NoneCameraException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)