import argparse
import socket, struct, pickle

def sendOneMessage(conn, data):
	packed_data = pickle.dumps(data)
	length = len(packed_data)
	conn.sendall(struct.pack('!I', length))
	conn.sendall(packed_data)

if __name__ == '__main__':
	# Argument parser
	parser = argparse.ArgumentParser(description='Runs the exchange sequence program.')
	parser.add_argument('address', action='store', nargs=1, help='ip address of the remote RPI')
	parser.add_argument('port', action='store', nargs=1, type=int, help='port of the remote RPI')
	parser.add_argument('--start', dest='running', action='store_true', default=True, help='starts the remote simulation')
	parser.add_argument('--stop', dest='running', action='store_false', default=False, help='stops the remote simulation')
	
	options = parser.parse_args()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((options.address[0], options.port[0]))
	sendOneMessage(sock, options)
	
	print 'Sent ' + str(options)