import socket
import threading
import thread
import SocketServer
import time
import random
import os
import cPickle
import platform
import select
import sys
import errno

# commands
CMD_LISTL = 'listl'
CMD_LISTR = 'listr'
CMD_SEARCH = 'search'
CMD_DISCOVER = 'discover'
CMD_KNOWN_PEERS = 'known'
CMD_RESET = 'reset'
CMD_GET = 'get'
CMD_QUIT = 'quit' 
CMD_COMMAND = 'command'

FORWARD = 'forward'
BACKWARD = 'backward'

CMD_CONNECT = 'connect'
FOUND = 'FOUND'
NOT_FOUND = 'NOT_FOUND'
YES = 'Y'
NO = 'N'
BYTE_LENGTH = 64
END_MARKER = '@#' # a random symbol to indicate the end of line
OPERATION_COMPLETE = 'OPERATION_COMPLETE!'
OPERATION_IMCOMPLETE = 'ERROR: OPERATION_IMCOMPLETE!'

# different operating systems have different read-write modes
MAC_OS = 'Darwin'
WINDOWS_OS = 'Windows'
MAC_READ_MODE = 'r'
MAC_WRITE_MODE = 'w'
WIN_READ_MODE = 'rb'
WIN_WRITE_MODE = 'wb'

# file types group into different folders ...
# any types not listed here will belong to unknown file type
MOVIE_FILE_TYPES = ['mov', 'mp4', 'rmvb']
MUSIC_FILE_TYPES = ['mp3', 'flac', 'acc']
PHOTO_FILE_TYPES = ['jpg', 'png', 'PNG']

# sub-directory folder names
MOVIE = 'MOVIE'
MUSIC = 'MUSIC'
PHOTO = 'PHOTO'
UNKNOWN = 'UNKNOWN'

# initialize server's connection
server_connection = False

# initialize known peers list
known_peers_list = []

# peer ID object
class peer(object):
    ip = None
    port = None
    
# an object stores all the attributes for information exchange over P2P
class dataSeries(object):
    command = '' # commands such as CMD_DISCOVER, CMD_SEARCH
    connection_direction = '' # connection direction such as FORWARD, BACKWARD
    file_name = '' 
    file_size = ''
    original_peer = '' # original requesting peer ID (ip, port)
    this_peer = '' # this peer's ID (ip, port)
    known_peers_list = ''
    folders = '' # stores all folder and file names
    TTL = '' # time to live (number of hops)
    exist = '' # check if file exists
    usr_perm = '' # user permission
    
# a file object to store its file name and size
class file(object):
    file_name = None
    file_size = None

# a folder object to store its folder name and files inside of it
class folder(object):
    directory = None
    files = []

# check all pre-defined file types
# return the corresponding file type
def checkFileType(file_name):
    # split the full_file_name (XY.Z) ... 
    # into file_name (XY) and file_type (Z)
    # return the file_type (Z) only
    file_type = file_name.split('.', 1)[1]
    
    # loop through the list and check
    for type in MOVIE_FILE_TYPES:
        if type == file_type:
            return MOVIE
    
    for type in MUSIC_FILE_TYPES:
        if type == file_type:
            return MUSIC
     
    for type in PHOTO_FILE_TYPES:
        if type == file_type:
            return PHOTO
    
    # if the file type is unknown    
    return UNKNOWN

# search for the specific file    
def findFile(file_name):
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    files = os.listdir(peer_file_directory + '/' + folder)
    for f in files:
        # only looking for files, NOT directories (folders)
        if os.path.isdir(f) == False:
            if f == file_name:
                return True
                
    return False

# custom function to convert string to integer
def getInt(string):
    try:
        return int(string)
    except ValueError:
        print "Oops!  That was no valid number.  Try again..."
        return False
        
# custom function to ask user for port number
def getPortNum():
    port_num = False
    # check if the user entered the port number is in correct format
    # will proceed if the user entered the correct format
    while port_num == False:
        port_num = getInt(raw_input('Enter port number: '))
        
    return port_num
    
# custom function to ask user for peer number
def getPeerNum():
    port_num = False

    while port_num == False:
        port_num = getInt(raw_input('Enter peer number: '))
        
    return port_num
    
# different operating systems have different read-write modes
# need to identify
def getReadMode():
    if platform.system() == MAC_OS:
        return MAC_READ_MODE
        
    else: # WINDOWS_OS (have not tried on Linux system yet!)
        return WIN_READ_MODE
        
def getWriteMode():
    if platform.system() == MAC_OS:
        return MAC_WRITE_MODE
        
    else: # WINDOWS_OS (have not tried on Linux system yet!)
        return WIN_WRITE_MODE

# send list over the socket
def sendDataSeries(sock, list):
    serialized_list = cPickle.dumps(list)
    sendData(sock, serialized_list)
    
def serverSendDataSeries(self, list):
    serialized_list = cPickle.dumps(list)
    serverSendData(self, serialized_list)
    
def serverGetDataSeries(self):
    serialized_list = serverGetData(self)
    deserialized_list = cPickle.loads(serialized_list)
    
    return deserialized_list
        
def serverGetData(self):
    global server_connection
    part = ''
    msg = ''
    # global server_connection
    # print '\ngetData' + str(server_connection)
    while server_connection:
        part = self.request.recv(BYTE_LENGTH)
        # check if the end marker "@#" ...
        # received or not, if so break the while loop
        if END_MARKER in part:
            # append text into the message, but ...
            # elimate the last two string "@#"
            msg += part[0:len(part) - len(END_MARKER)]
            break
        # the end of line is not reached yet, hence ...
        # keep adding text into the message
        else:
            msg += part
    return msg
    
# custom function to send data with a end marker "@#"
# a work-around indication to tell if the message being ...
# fully received
def serverSendData(self, text):
    self.request.sendall(text + END_MARKER)
    
def sendData(sock, text):
    sock.sendall(text + END_MARKER)

# perform socket connection 
def funcConnect(IP_address, port_num):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_address = (IP_address, port_num)
    sock.connect(server_address)
    print 'connected to %s port %s' % server_address
    return sock
    
# custom function to receive data from client
def getData(sock):
    part = ''
    msg = ''
    while True:
        part = sock.recv(BYTE_LENGTH)
        # check if the end marker "@#" ...
        # received or not, if so break the while loop
        if END_MARKER in part:
            # append text into the message, but ...
            # elimate the last two string "@#"
            msg += part[0:len(part) - len(END_MARKER)]
            break
        # the end of line is not reached yet, hence ...
        # keep adding text into the message
        else:
            msg += part
    return msg
    
# check if the specified peer exist
def findPeerInList(peer):
    for p in known_peers_list:
        if p.port == peer.port:
            return True
                
    return False
    
def getFileName():
    # will not proceed until user has the correct file name inputed
    while True:
        file_name = raw_input('Enter file name with file type: ')
        if isFile(file_name):
            return file_name
    
def getUserPermission():
    # will only proceed if the user entered correct command
    while True:
        usr_permission = \
        raw_input('WARNING: The file \"%s\" existing on files folder, over-write? (Y/N)\n' \
        % file_name)
        
        if usr_permission == YES or usr_permission == NO:
            return usr_permission
    
# return the file size of the specific file
# parameter as string type
def getFileSize(file_name):
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    file = open(peer_file_directory + '/' + folder + '/' + file_name, getReadMode())
    # to the end of the file '2' so it can 'tell' the full size of the file
    file.seek(0, 2)
    size = file.tell()
    file.close()
    
    return size
    
# check if the file_name contains a file type 
# valid file name: XY.Z, invalid file name: XY
def isFile(file_name):
    for string in file_name:
        if string == '.':
            return True
    
    return False
    
# list this peer's known peers
def listKnownPeers():
    i = 0
    for peer in known_peers_list:
        i = i + 1
        print '\nPeer[%d]: IP: %s, Port: %d' \
        %(i, peer.ip, peer.port) 
    
# list all files from peer's files folder
# including the sub-directory name
def listAllFiles(objects):
    # this 'objects' is a two dimentional list (list of list)
    # the outter list in objects will represent folder objects, while each folder object ...
    # includes "folder name (sub-directory) and a list of files in that sub-directory"
    # i.e [['MOVIE', ['file1', 'file2']], ['MUSIC', ['file1', 'file2', 'file3']]]
    
    folder_index = 0
    for folder in objects:
        print '\nSub_Directory %d: *%s*' %(folder_index + 1, folder.directory)
        
        file_index = 0
        for f in folder.files:
            file_name = f.file_name
            file_size = f.file_size
            print 'FILE %d: %s --> SIZE: %.2f KB (%d bytes)' \
            %(file_index + 1, file_name, int(file_size)/1024., file_size)
            file_index = file_index + 1
    
        folder_index = folder_index + 1
    
    print '\n' + OPERATION_COMPLETE    

# get all files from peer's files folder
# including the sub-directory name
def getAllFiles():
    # this 'objects' is a two dimentional list (list of list)
    # the outter list in objects will represent folder objects, while each folder object ...
    # includes "folder name (sub-directory) and a list of files in that sub-directory"
    # i.e [['MOVIE', ['file1', 'file2']], ['MUSIC', ['file1', 'file2', 'file3']]]
    
    # initialize the folder objects
    folders_list = []
    
    # get all the directories
    # folders = next(os.walk(peer_file_directory))[1]
    folders = os.listdir(peer_file_directory)
    
    folder_index = 0
    for fold in folders:
        if fold != '.DS_Store':
            # print '\nSub_Directory %d: *%s*' %(folder_index + 1, fold)
            # one folder (sub-directory) append folder object
            folders_list.append(folder())
            # assign the folder name
            folders_list[folder_index].directory = fold
            
            # get all the files inside the folder
            # files = next(os.walk(peer_file_directory + '\\' + fold))[2]
            files = os.listdir(peer_file_directory + '/' + fold)
            
            file_index = 0
            
            # initialize a list that contains all the files within the sub-directory
            # will always set to empty list before going into another folder (sub-directory)
            files_list = []
            for f in files:
                f_size = getFileSize(f)
                
                # print 'FILE %d: %s --> SIZE: %.2f KB (%d bytes)' \
                # %(file_index + 1, f, f_size/1024., f_size)
                
                # append the file object ...
                # and store its name and file size into the files_list
                files_list.append(file())
                files_list[file_index].file_name = f
                files_list[file_index].file_size = f_size
                
                file_index = file_index + 1
            
            # after storing all the available files, ...
            # then store it into the folder object's files attribute
            folders_list[folder_index].files = files_list
            folder_index = folder_index + 1;
        
    print '\n' + OPERATION_COMPLETE
    return folders_list
            
# receive and write file to peer's directory
def receiveFile(self, file_name, file_size):
    print 'Receiving file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    file_path = peer_file_directory + '/' + folder + '/' + file_name
    file = open(file_path, getWriteMode())
    
    print 'storing file: %s' %file_name
    
    try:
        sum_bytes = 0
        while int(sum_bytes) < int(file_size):
            data = self.request.recv(BYTE_LENGTH)
            
            if data:
                file.write(data)
                sum_bytes = sum_bytes + len(data)
                progress = float(sum_bytes)/float(file_size) * 100.
                print'Current received file size (byte): %d (expected: %s) - %.2f%% \r'\
                %(sum_bytes, file_size, progress)
                # sys.stdout.write('Current received file size (byte): %d (expected: %s) - %.2f%% \r'\
                # %(sum_bytes, file_size, progress))
                # sys.stdout.flush()
                
            else:
                print 'done receiving file'
                print 'Total received file size (byte): %d (expected: %s)'\
                %(sum_bytes, file_size)
                
                # once reached 'else' statement, will break the while loop
                # senerio 1: the file is successfully received at full size
                # senerio 2: the file is not fully received ...
                # (user abruptly closed the connection)
                break
    
    # in case the connection is lost 
    #(i.e user close the console window)
    except socket.error as error:
        if error.errno == errno.WSAECONNRESET:
            # clean up the corrupted file
            file.close()
            os.remove(file_path)
            
    except KeyboardInterrupt:
        print 'User pressed (CTRL-C ) to shut down client'
        # clean up the corrupted file
        file.close()
        os.remove(file_path)
            
    # if the file size received correctly
    # operation completes
    if int(sum_bytes) == int(file_size):
        print 'done receiving file'
        print 'Total received file size (byte): %d (expected: %s)'\
        %(sum_bytes, file_size) 
        self.request.sendall(FOUND)
        file.close()
        print '\n' + OPERATION_COMPLETE
    
    else:
        # operation imcomplete
        file.close()
        # clean up the corrupted file
        os.remove(file_path)
        
        print '\n' + OPERATION_IMCOMPLETE

# send file to specified peer
def sendFile(socket, file_name, file_size):
    print 'sending file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    file = open(peer_file_directory + '/' + folder + '/' + file_name, getReadMode())
    
    sum_bytes = 0
    for line in file:
        sum_bytes = sum_bytes + len(line)
        progress = float(sum_bytes)/float(file_size) * 100.
        sys.stdout.write('Current sent file size (byte): %d (expected: %s) - %.2f%% \r'\
        %(sum_bytes, file_size, progress))
        sys.stdout.flush()
        
        socket.sendall(line)
        
    # if the client received the exact file size
    if socket.recv(BYTE_LENGTH) == FOUND:
        print 'Total sent file size (byte): %d (expected: %s)'\
            %(sum_bytes, file_size)
        file.close() 
        print '\n'+ OPERATION_COMPLETE
    
    else:
        file.close()
        print '\n' + OPERATION_IMCOMPLETE
               
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    
    # a handler to deal with client's commands
    def handle(self):
        global server_connection
        
        # now the threaded server_thread connection's status is changed to establish
        thread_connection = True
    
        # identify current thread
        cur_thread = threading.current_thread()  
        # get thread-number in python
        thread_name = cur_thread.name        
      
        try:
            while thread_connection:
                # synchronous I/O non-blocking approach to detect ...
                # if there is any incoming data from main server  
                read, _, _ = select.select([self.request], [], [], 0)
                if read:
                    data_series = serverGetDataSeries(self)
                    data = data_series.command
                
                # check if the main server's connection being disconnected
                # disconnect server_thread if so
                elif server_connection == False:
                    thread_connection = False
                    data = CMD_QUIT
                    
                else:
                    # return to the start of this while loop
                    data = None

                if data == CMD_LISTR:
                    print '\nCOMMAND: ' + CMD_LISTR
                    
                    info = data_series.connection_direction
                    
                    # each new thread will only respond to either FORWARD or BACKWARD
                    
                    # if this peer receives from other peer (forwarding)
                    if info == FORWARD:
                        # retrieve all the folder names
                        # and file names associated with the folder names
                        folders = getAllFiles()
                        serialized_folders = cPickle.dumps(folders)
                        
                        # retrieve original requesting peer ID (string format), 
                        # and convert it back to object format
                        serialized_original_peer = data_series.original_peer
                        deserialized_original_peer = cPickle.loads(serialized_original_peer)
                        
                        # send all the folder and file names to the original requesting peer
                        socket = funcConnect\
                        (deserialized_original_peer.ip, deserialized_original_peer.port)
                        
                        # create an object structure to store all the attributes
                        # and send them as a whole
                        list_in_listr = dataSeries()
                        list_in_listr.command = CMD_LISTR
                        list_in_listr.connection_direction = BACKWARD
                        list_in_listr.folders = serialized_folders
                        sendDataSeries(socket, list_in_listr)
                        
                    # if original requesting peer receives from other peer (backwarding)
                    else: # BACKWARD
                        folders = data_series.folders
                        deserialized_folders = cPickle.loads(folders)
                        
                        # print out folders and file
                        listAllFiles(deserialized_folders)
                        
                    # close this thread    
                    thread_connection = False
                    
                elif data == CMD_SEARCH:
                    print '\nCOMMAND: ' + CMD_SEARCH
                    
                    data = data_series.connection_direction
                    
                    if data == FORWARD:
                        # send this peer's ID back to original requesting peer
                        
                        file_name = data_series.file_name
                        
                        serialized_original_peer = data_series.original_peer
                        deserialized_original_peer = cPickle.loads(serialized_original_peer)
                        
                        socket = funcConnect\
                        (deserialized_original_peer.ip, deserialized_original_peer.port)
                        
                        list_in_search = dataSeries()
                        list_in_search.command = CMD_SEARCH
                        list_in_search.connection_direction = BACKWARD
                        
                        if findFile(file_name):
                            list_in_search.exist = FOUND
                            
                            serialized_self_peer = cPickle.dumps(self_peer)
                            list_in_search.this_peer = serialized_self_peer
                            list_in_search.file_name = file_name
                            
                        else: # NOT_FOUND
                            list_in_search.exist = NOT_FOUND
                            
                        sendDataSeries(socket, list_in_search)
                            
                        ttl = int(data_series.TTL)
                        # if still got ttl available, ... 
                        # continue broadcast deeper over the network
                        if ttl >= 1:
                            for peer in known_peers_list:
                                socket = funcConnect(peer.ip, peer.port)
                                list_in_search2 = dataSeries()
                                list_in_search2.command = CMD_SEARCH
                                list_in_search2.connection_direction = FORWARD
                                list_in_search2.file_name = file_name
                                list_in_search2.original_peer = serialized_original_peer
                                list_in_search2.TTL = str(ttl - 1)
                                sendDataSeries(socket, list_in_search2)
                            
                    else: # BACKWARD
                        # receive other peer's ID
                        # and display the peer(s) who has the specified file
                        is_file_found = data_series.exist

                        if is_file_found == FOUND:
                            serialized_self_peer = data_series.this_peer
                            deserialized_self_peer = cPickle.loads(serialized_self_peer)
                            
                            print 'Found peer: \"%s\", \"%d\" has \"%s\"' \
                            %(deserialized_self_peer.ip, deserialized_self_peer.port,\
                            data_series.file_name)
                    
                    thread_connection = False
                    
                elif data == CMD_DISCOVER:
                    print '\nCOMMAND: ' + CMD_DISCOVER

                    data = data_series.connection_direction
                    
                    if data == FORWARD:
                        # send this peer's known_peers_list to the original requesting peer
                        
                        serialized_original_peer = data_series.original_peer
                        deserialized_original_peer = cPickle.loads(serialized_original_peer)
                        
                        socket = funcConnect\
                        (deserialized_original_peer.ip, deserialized_original_peer.port)
                        
                        serialized_known_peer_list = cPickle.dumps(known_peers_list)
                        
                        list_in_discover = dataSeries()
                        list_in_discover.command = CMD_DISCOVER
                        list_in_discover.connection_direction = BACKWARD
                        list_in_discover.known_peers_list = serialized_known_peer_list
                        sendDataSeries(socket, list_in_discover)
                        
                        ttl = int(data_series.TTL)
                        # if still got ttl available,
                        # continue to broadcast deeper over the network
                        if ttl >= 1:
                            for peer in known_peers_list:
                                socket = funcConnect(peer.ip, peer.port)
                                list_in_discover2 = dataSeries()
                                list_in_discover2.command = CMD_DISCOVER
                                list_in_discover2.connection_direction = FORWARD
                                list_in_discover2.original_peer = serialized_original_peer
                                list_in_discover2.TTL = str(ttl - 1)
                                sendDataSeries(socket, list_in_discover2)
                                
                    else: # BACKWARD
                        # receive other peer's known_peers_list 
                        # and append them to own known_peers_list
                    
                        serialized_known_peer_list = data_series.known_peers_list
                        deserialized_known_peer_list = \
                        cPickle.loads(serialized_known_peer_list)
                        
                        for peer in deserialized_known_peer_list:
                            # if this peer already exist on the known_peers_list
                            # then no need to add
                            isPeerInList = findPeerInList(peer)
                            if not isPeerInList:
                                known_peers_list.append(peer)
                        
                        # print out all the known peers
                        listKnownPeers()
                    
                    thread_connection = False
                
                elif data == CMD_GET:
                    info = data_series.connection_direction
                    
                    if info == FORWARD:
                        # sending the file to original requesting peer
                    
                        file_name = data_series.file_name
                        serialized_original_peer = data_series.original_peer
                        deserialized_original_peer = cPickle.loads(serialized_original_peer)
      
                        file_size = getFileSize(file_name)
      
                        socket = funcConnect\
                        (deserialized_original_peer.ip, deserialized_original_peer.port)
                        
                        list_in_get = dataSeries()
                        list_in_get.command = CMD_GET
                        list_in_get.connection_direction = BACKWARD
                        list_in_get.file_name = file_name
                        list_in_get.file_size = str(file_size)
                        sendDataSeries(socket, list_in_get)
                        
                        # (BAD) avoid sendding two data at the same time
                        # sometimes causing problems (i.e file data lost)
                        time.sleep(0.01)
                        
                        # send file
                        sendFile(socket, file_name, file_size)
                        
                    else: # BACKWARD
                        # receiving the file from the specified peer
                        
                        file_size = data_series.file_size
                        file_name = data_series.file_name

                        # receive file
                        receiveFile(self, file_name, file_size)
                    
                    thread_connection = False
                
                elif data == CMD_QUIT:
                    sys.exit(1)

            print '\n%s terminated!' %thread_name
        
        except KeyboardInterrupt:
            print 'User pressed (CTRL-C ) to shut down client'
            sys.exit(1)
        
        # finally:
            # print 'Exit!'

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
    
def client():
    client_flag = True
    global server_connection
    global known_peers_list
    # serialize peer ID (so able to send over the socket)
    serialized_original_peer = cPickle.dumps(self_peer)
    
    try:
        while client_flag: # connection will maintain active unless user quits
        
            # prmote user to enter commands
            msg = raw_input()
            
            # list this peer's folders and files
            if msg == CMD_LISTL: 
                print '\nCOMMAND: ' + CMD_LISTL
                
                # find all the folders and files
                # and print out them all
                folders = getAllFiles()
                listAllFiles(folders)
            
            # list folders and files from remote peer
            elif msg == CMD_LISTR:
                print '\nCOMMAND: ' + CMD_LISTR
                
                ip = 'localhost'
                port = getPortNum()
                
                socket = funcConnect(ip, port)
                # create an object structure to store all the attributes
                # and send them as a whole
                list = dataSeries()
                list.command = CMD_LISTR
                list.connection_direction = FORWARD
                list.original_peer = serialized_original_peer
                sendDataSeries(socket, list)
            
            # search for specific file with ttl
            elif msg == CMD_SEARCH:
                print '\nCOMMAND: ' + CMD_SEARCH
                
                file_name = raw_input('Please enter file name: ')
                ttl = int(raw_input('Time to live #: '))

                if ttl >= 1:
                    for peer in known_peers_list:
                        socket = funcConnect(peer.ip, peer.port)
                        # create an object structure to store all the attributes
                        # and send them as a whole
                        list = dataSeries()
                        list.command = CMD_SEARCH
                        list.connection_direction = FORWARD
                        list.file_name = file_name
                        list.original_peer = serialized_original_peer
                        list.TTL = str(ttl - 1)
                        sendDataSeries(socket, list)
                        
                else:
                    print 'ERROR: ttl less than 1'
                
            # discover and add peers into this peer's "known_peers_list"
            elif msg == CMD_DISCOVER:
                print '\nCOMMAND: ' + CMD_DISCOVER
                
                # ttl (time to live), 
                # the number of hops this peer is going to broadcast
                ttl = int(raw_input('Time to live #: '))
                
                # reason decrease one ttl here is due to that ...
                # this peer initially has one known peer
                ttl = ttl - 1
                
                # if true, start broadcasting to other peers
                if ttl >= 1:
                    # need to broadcast from all the known peers
                    for peer in known_peers_list:
                        socket = funcConnect(peer.ip, peer.port)
                        # create an object structure to store all the attributes
                        # and send them as a whole
                        list = dataSeries()
                        list.command = CMD_DISCOVER
                        list.connection_direction = FORWARD
                        list.original_peer = serialized_original_peer
                        list.TTL = str(ttl - 1)
                        sendDataSeries(socket, list)
                        
                else: # ttl == 0
                    listKnownPeers()

            # retrieve specific file from specific peer
            elif msg == CMD_GET:
                print '\nCOMMAND: ' + CMD_GET
                
                # ip = raw_input('Please enter ip address: ')
                ip = 'localhost'
                port_num = getPortNum()
                file_name = getFileName()
                
                socket = funcConnect(ip, port_num)
                # create an object structure to store all the attributes
                # and send them as a whole
                list = dataSeries()
                list.command = CMD_GET
                list.file_name = file_name
                list.connection_direction = FORWARD
                list.original_peer = serialized_original_peer
                sendDataSeries(socket, list)
            
            # display known peers that this peer knows about
            elif msg == CMD_KNOWN_PEERS:
                listKnownPeers() 
            
            # display all the commands available to operate
            elif msg == CMD_COMMAND:
                print '\nEnter Commands:\n\n%s\n%s\n%s<fileName><TTL>\n%s<TTL>\n%s<fileName><ipAddress><portNum>\
                \n%s\n%s\n%s\n'\
                %(CMD_LISTL, CMD_LISTR, CMD_SEARCH, CMD_DISCOVER, \
                CMD_GET, CMD_KNOWN_PEERS, CMD_RESET, CMD_QUIT)
                
            # reset known peer list
            elif msg == CMD_RESET: 
                known_peers_list = []
                known_peers_list.append(ini_known_peer)
                
                listKnownPeers()
                
            # close this peer's connection and program
            elif msg == CMD_QUIT:
                client_flag = False
                server_connection = False
                sys.exit(1)
            
            else:
                print 'Please enter the correct command or \n\
                enter \"%s\" to display all the available commands!'
    
    except KeyboardInterrupt:
        print 'User pressed (CTRL-C ) to shut down client'
        sys.exit(1)
        
    finally:
            print >>sys.stderr, '\nShut down peer\n'
            sys.exit(1)

if __name__ == "__main__":
    
    # Port 0 means to select an arbitrary unused port
    peer_num = getPeerNum()
    port_num = peer_num + 2000
    HOST, PORT = "localhost", port_num

    print "\nStart Threaded-Server on PORT %s " % PORT

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    
    # Terminate the server when the main thread terminates 
    # by setting daemon to True
    server_thread.daemon = True
    server_thread.start()
    
    server_connection = True
    print "Main Server using thread %s " % server_thread.name
    
    # myself (this peer)
    self_peer = peer()
    self_peer.ip = 'localhost'
    self_peer.port = port_num

    # at start up, each peer knows one other peer
    ini_known_peer = peer()
    ini_known_peer.ip = 'localhost'
    ini_known_peer.port = port_num + 1

    known_peers_list.append(ini_known_peer)
    
    # get associate peer's file directory
    peer_file_directory = os.getcwd() + '/peer_' + str(peer_num)
    
    print 'You can enter \"%s\" anytime to display all the commands' %CMD_COMMAND
    
    # place client function here ...
    # user can operate as long as it wants ...
    # until 'QUIT' command executed ...
    # server will also be shutted down
    client()
    
    print '\nMain server thread shutting down the server and terminating'
    server.shutdown()
