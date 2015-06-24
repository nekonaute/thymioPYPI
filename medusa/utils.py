import struct
import pickle
import inspect

class MessageType :
    # Special
    NONE = -1

    # Query messages
    INIT, START, STOP, KILL, QUERY = range(0, 5)

    # Info message
    ACK, LISTENING, STARTED = range(10, 13)

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
	packed_data = pickle.dumps(data)
	length = len(packed_data)
	conn.sendall(struct.pack('!I', length))
	conn.sendall(packed_data)
