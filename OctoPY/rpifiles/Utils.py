import struct
import pickle
import inspect
import sys
import traceback

"""
OCTOPY : Utils.py

Stores usefull classes and methods.
"""

class MessageType :
    # Special
    NONE = -1

    # Query messages
    INIT, START, PAUSE, RESTART, STOP, KILL, OFF, SET, DATA, QUERY, REGISTER = range(0, 11)

    # Info message
    ACK, LISTENING, STARTED, NOTIFY, COM = range(11, 16)

    @staticmethod
    def getAllAttributes() :
        listAtt = inspect.getmembers(MessageType, lambda att : not(inspect.isroutine(att)))
        listAtt = [att for att in listAtt if not(att[0].startswith('__') and att[0].endswith('__'))]
        return listAtt

class Message :
    msgType = MessageType.NONE
    data = None


def recvall(conn, count):
    buf = b''
    while count:
        newbuf = conn.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def recvOneMessage(socket):
    lengthbuf = recvall(socket, 4)
    if not lengthbuf: return None
    length, = struct.unpack('!I', lengthbuf)
    recvD = recvall(socket, length)
    data = pickle.loads(recvD)
    return data

def sendOneMessage(conn, data):
    try :
        packed_data = pickle.dumps(data)
        length = len(packed_data)
        conn.sendall(struct.pack('!I', length))
        conn.sendall(packed_data)
    except :
        destIP = str(conn.getpeername())
        print "sendOneMessage - Unexpected error while sending message to "+ destIP +" : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc() 
