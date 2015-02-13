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
END_MARKER = '@#' # a random symbol to indicate end of line

connection_flag = False

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
    part = ''
    msg = ''
    while True:
        part = sock.recv(BYTE_LENGH)
        # check if the end marker "@#" received or not, if so break the while loop
        if END_MARKER in part:
            # append text into the message, but elimate the last two string "@#"
            msg += part[0:len(part) - 2]
            break
        # the end of line is not reached yet, hence keep adding text into the message
        else:
            msg += part
    return msg

# custom function to ask user for port number
def getPortNum():
    port_num = False
    # check if the user entered the port number is in correct format
    while port_num == False:
        port_num = getInt(raw_input('Enter port number: '))
    return port_num
    
# custom function to send data with a end marker "@#"
def sendData(text):
    sock.sendall(text + END_MARKER)
    
# custom function to convert string to integer
def getInt(string):
    try:
        return int(string)
    except ValueError:
        print "Oops!  That was no valid number.  Try again..."
        return False

while connection_flag == False: # Will ask usr to perform connection
    msg = raw_input('\nEnter Commands:\nCONNECT\n')
        
    # notify server to enable connection
    if msg == CMD_CONNECT:
        IP_address = raw_input('Enter IP address: ')
        port_num = getPortNum()
        # connnect
        sock = funcConnect(IP_address, int(port_num))
        # if connection is established, continue to promote user with commands
        if sock:
            connection_flag = True   
       
    try:
        while connection_flag: # connection will maintain active unless user quits
            # prmote user to enter commands
            msg = raw_input('\nEnter Commands:\n\nADD\nREMOVE\n\
READ-value\nWRITE-target\nQUIT\n\n')
            # notify server to add device
            if msg == CMD_ADD:             
                sendData(msg)
                dev_name =raw_input('Enter device name: ')
                sendData(dev_name)
                dev_IP = raw_input('Enter device IP address: ')
                sendData(dev_IP)
                info = getData()
                if info == 'ERROR':
                    print 'Device already exist'
                    
                else:
                    print 'Device', info, 'added to the data base'
            # notify servr to remove device
            elif msg == CMD_REMOVE:
                sendData(msg)
                dev_name = raw_input('Enter device name to remove: ')
                sendData(dev_name)
                info = getData()
                if info == 'ERROR':
                    print 'device does not exit'
                else:
                    print 'Device', info, 'removed from the data base'
            # notify server to read device value
            elif msg == CMD_READ:
                sendData(msg)
                dev_name = raw_input('Enter device name to get value: ')
                sendData(dev_name)
                # depend on if the user-entered device is found
                info = getData()
                if info == ERROR:
                    print 'Device', dev_name, 'is not found on the data base'
                else:
                    print 'Device', dev_name,'\'s Read and Target values are: ', info
            # notify server to write target value of a device
            elif msg == CMD_WRITE:
                sendData(msg)
                dev_name = raw_input('Enter device name: ')
                sendData(dev_name)
                target_val = raw_input ('Enter the device target value: ')
                sendData(target_val)
                # depend on if the user-entered device is found
                info = getData()
                if info == ERROR:
                    print 'Device', dev_name, 'is not found on the data base'
                else:
                    print 'Device', dev_name,'\'s Target value is changed to: ', info
            # notify server to quit the connection
            elif msg == CMD_QUIT:
                connection_flag = False
                # if connection was established, and trying to quit
                if sock: 
                    sendData(msg)
                    sock.close()
                # else if the connection was not established ...
                # while trying to quit, then break it
                else:
                    # do nothing
                    break 
            else:
                print 'Please enter the correct command'

    finally:
         print >>sys.stderr, 'Connection aborting...'
         #sock.close()
