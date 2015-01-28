import socket
import sys
print "New Session"
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

# initialize variables
num_of_devs = 2 # there are 2 devices pre-added into the data base
IP_address = None
port_num = None
dev_name = None
dev_IP_address = None
target_val = None

# create a list class to store atrributes
class db_list(object):
    device_name = None
    read_value = None
    target_value = None
    IP_address = None

# create a null list (data-base)
data_base = []
# append and initialize the first two rows of data (given)
data_base.append(db_list())
data_base.append(db_list())
# device 1
data_base[0].device_name = 'Thermostat-Main Room'
data_base[0].read_value = 19
data_base[0].target_value = 23
data_base[0].IP_address = '177.68.25.17'
# device 2
data_base[1].device_name = 'Thermostat-Living Room'
data_base[1].read_value = 18
data_base[1].target_value = 22
data_base[1].IP_address = '177.68.25.18'

# custom function to receive data from client
def getData():
    msg = connection.recv(BYTE_LENGH)
    return msg

# custom function to print all attributes of the specified device
def printDevice(data_base, index):
    print data_base[index].device_name,',', \
          data_base[index].read_value,',', \
          data_base[index].target_value,',', \
          data_base[index].IP_address 

# custom function to add device into data base
def funcAdd():
    data_base.append(db_list()) # append an empty list object into data base
    dev_name = getData() # get the device name from client
    data_base[num_of_devs - 1].device_name = dev_name # assign atrribute value
    dev_IP_address = getData()
    data_base[num_of_devs - 1].IP_address = dev_IP_address
    print '\nAdded device:\n'
    printDevice(data_base, num_of_devs - 1)
          
    print '\nTotal devices:'
    for j in range (0, len(data_base)):
        print '#', j
        printDevice(data_base, j)
        
    return dev_name

# custom function to remove specific device
def funcRemove():
    dev_name = getData()
    for i in range (0, len(data_base)): # for loop to find the user defined device
        if data_base[i].device_name == dev_name:
            print 'Removed device: ' + data_base[i].device_name
            data_base.remove(data_base[i]) # remove
            break
    print '\nTotal devices:'
    for j in range (0, len(data_base)):
        print '#', j
        printDevice(data_base, j)
        
    return dev_name

# custom function to read the value (Read-value)
def funcRead():
    dev_name = getData()
    for i in range (0, len(data_base)):
        if data_base[i].device_name == dev_name:
            print 'Found device: ' + data_base[i].device_name
            print 'Its Read-value is: ', data_base[i].read_value
            print 'Its Target-value is: ', data_base[i].target_value
            printDevice(data_base, i)
            return str(data_base[i].read_value) + ', ' + str(data_base[i].target_value)
        else:
            if i == len(data_base) - 1: # already reach the end of list
                print 'The device %s does not exist in the data base.' %dev_name
                return False

# custom function to write the target value
def funcWrite():
    dev_name = getData()
    target_val = getData()
    for i in range (0, len(data_base)):
        if data_base[i].device_name == dev_name:
            print 'Found device: ' + data_base[i].device_name
            data_base[i].target_value = target_val # overwrite the target value
            print 'Change target value to: ', data_base[i].target_value
            printDevice(data_base, i)
            return str(data_base[i].target_value)
        else:
            if i == len(data_base) - 1: # already reach the end of list
                print 'The device %s does not exist in the data base.' %dev_name
                return False

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.1.7', 61556)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while connection_flag: # connection will maintain active unless user quits
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    
    try:
        print >>sys.stderr, 'connection from', client_address

        while connection_flag: # connection will maintain active unless user quits
            data = getData()
            print >>sys.stderr, '\nreceived "%s"' % data
            
            if data == CMD_ADD:
                num_of_devs += 1 # add one device
                # send info to client to confirm the device is being added
                connection.sendall(funcAdd()) 
	    elif data == CMD_REMOVE:
		connection.sendall(funcRemove())
		num_of_devs -= 1 # delete one device
	    elif data == CMD_READ:
		info = funcRead()
		# depend on if the user-entered device is found
		if info == False:
                    connection.sendall(ERROR)
                else:
                    connection.sendall(info)
	    elif data == CMD_WRITE:
		info = funcWrite()
		# depend on if the user-entered device is found
		if info == False:
                    connection.sendall(ERROR)
                else:
                    connection.sendall(info)
	    elif data == CMD_QUIT:
                connection_flag = False
                connection.close()
                print 'Closed connection'              
            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()
