import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 4500)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'connection from', client_address
    # Receive the data in small chunks and retransmit it
    while True:
        data = connection.recv(16)
		list(data)
		left = data[0]
		right = data[1]
		forward = data[2]
		backward = data[3]
		cClockwise = data[4]
		clockwise = data[5]
		up = data[6]
		down = data[7]
            print >>sys.stderr, 'received "%s"' % data
                if data:
                      print >>sys.stderr, 'sending data back to the client'
                      connection.sendall(data)
        else:
                    print >>sys.stderr, 'no more data from', client_address
                    break

    finally:
            # Clean up the connection
    connection.close()

