import struct
import pickle


class MessageType :
    # Query messages
    INIT, START, STOP, KILL, QUERY = range(0, 5)

    # Info message
    ACK, LISTENING, STARTED = range(10, 13)

class DirtyMessage :
	running = True
	kill = False
	message = -1


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
