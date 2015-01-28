import socket
import sys

# constants
CMD_ADD = 'ADD'
CMD_REMOVE = 'REMOVE'
CMD_READ = 'READ-value'
CMD_WRITE = 'WRITE-target'
CMD_QUIT = 'QUIT'
CMD_CONNECT = 'CONNECT'
BYTE_LENGH = 32
ERROR = 'ERROR'

connection_flag = True

sock = None #socket
dev_name = None
dev_IP = None
target_val = None

# custom function to create connection to the server
def funcConnect(IP_address, port_num):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_address = (IP_address, port_num)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)
    print 'connected to %s port %s' % server_address
    return sock

# custom function to receive data from client
def getData():
    msg = sock.recv(BYTE_LENGH)
    return msg

# custom function to convert string to integer
def getInt(string):
    try:
        return int(string)
    except ValueError:
        print "Oops!  That was no valid number.  Try again..."
        return False

while connection_flag: # connection will maintain active unless user quits     
    try:
        while connection_flag: # connection will maintain active unless user quits
            # prmote user to enter commands
            msg = raw_input('\nEnter Commands:\nCONNECT\nADD\nREMOVE\n\
READ-value\nWRITE-target\nQUIT\n\n')
            # notify server to add device
            if msg == CMD_ADD:              
                sock.sendall(msg)
                dev_name =raw_input('Enter device name: ')
                sock.sendall(dev_name)
                dev_IP = raw_input('Enter device IP address: ')
                sock.sendall(dev_IP)
                print 'Device', getData(), 'added to the data base'
            # notify servr to remove device
            elif msg == CMD_REMOVE:
                sock.sendall(msg)
                dev_name = raw_input('Enter device name to remove: ')
                sock.sendall(dev_name)
                print 'Device', getData(), 'removed from the data base'
            # notify server to read device value
            elif msg == CMD_READ:
                sock.sendall(msg)
                dev_name = raw_input('Enter device name to get value: ')
                sock.sendall(dev_name)
                # depend on if the user-entered device is found
                info = getData()
                if info == ERROR:
                    print 'Device', dev_name, 'is not found on the data base'
                else:
                    print 'Device', dev_name,'\'s Read and Target values are: ', info
            # notify server to write target value of a device
            elif msg == CMD_WRITE:
                sock.sendall(msg)
                dev_name = raw_input('Enter device name: ')
                sock.sendall(dev_name)
                target_val = raw_input ('Enter the device target value: ')
                sock.sendall(target_val)
                # depend on if the user-entered device is found
                info = getData()
                if info == ERROR:
                    print 'Device', dev_name, 'is not found on the data base'
                else:
                    print 'Device', dev_name,'\'s Target value is changed to: ', info
            # notify server to quit the connection
            elif msg == CMD_QUIT:
                connection_flag = False
                sock.sendall(msg)
                sock.close()
            # notify server to enable connection
            elif msg == CMD_CONNECT:
                IP_address = raw_input('Enter IP address: ')
                port_num = getInt(raw_input('Enter port number: '))
                # check if the user entered the port number in correct format
                while port_num == False:
                    port_num = getInt(raw_input('Enter port number: '))
                # connnect
                sock = funcConnect(IP_address, int(port_num))

    finally:
         print >>sys.stderr, 'Connection aborting...'
         #sock.close()
