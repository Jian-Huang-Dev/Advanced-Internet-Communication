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

# contants
CMD_LIST_ALL = 'list'
CMD_READ = 'read'
CMD_WRITE = 'write'
CMD_BYE = 'bye'
CMD_QUIT = 'quit' 
CMD_CONNECT = 'connect'
FOUND = 'FOUND'
NOT_FOUND = 'NOT_FOUND'
YES = 'Y'
NO = 'N'
BYTE_LENGTH = 64
END_MARKER = '@#' # a random symbol to indicate end of line
OPERATION_COMPLETE = 'OPERATION_COMPLETE!'
OPERATION_IMCOMPLETE = 'ERROR: OPERATION_IMCOMPLETE!'

# directory path for server files foder(CHANGE THIS ACCORDINGLY)
SERVER_ADDRESS = \
r'C:\Dropbox\McMaster_Final_Year_2014-2015\4DN4_Advanced_Internet_Communication\Labs&Assignments\lab_2\4DN4_LAB2\Server_dir'

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

# initialize COMMAND QUIT message
quit_msg = None

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
    
    files = os.listdir(SERVER_ADDRESS + '\\' + folder)
    for f in files:
        # only looking for files, NOT directories (folders)
        if os.path.isdir(f) == False:
            if f == file_name:
                return True
                
    return False

# custom function to receive data from client
def getData(self):
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

    
# custom function to send data with a end marker "@#"
# a work-around indication to tell if the message being ...
# fully received by server
def sendData(self, text):
    self.request.sendall(text + END_MARKER)

# return the file size of the specific file
# parameter as string type
def getFileSize(file_name):
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    file = open(SERVER_ADDRESS + '\\' + folder + '\\' + file_name, getReadMode())
    # to the end of the file '2' so it can 'tell' the full size of the file
    file.seek(0, 2)
    size = file.tell()
    file.close()
    
    return size
    
# list all files from server's files folder
# including the sub-directory name
def listAllFiles():
    # this 'objects' is a two dimentional list (list of list)
    # the outter list in objects will represent folder objects, while each folder object ...
    # includes "folder name (sub-directory) and a list of files in that sub-directory"
    # i.e [['MOVIE', ['file1', 'file2']], ['MUSIC', ['file1', 'file2']]]
    
    # initialize the folder objects
    folders_list = []
    
    # get all the directories
    folders = next(os.walk(SERVER_ADDRESS))[1]
    
    folder_index = 0
    for fold in folders:     
        print '\nSub_Directory %d: *%s*' %(folder_index + 1, fold)
        # one folder (sub-directory) append folder object
        folders_list.append(folder())
        # assign the folder name
        folders_list[folder_index].directory = fold
        
        # get all the files inside the folder
        files = next(os.walk(SERVER_ADDRESS + '\\' + fold))[2]
        
        file_index = 0
        
        # initialize a list that contains all the files within the sub-directory
        # will always set to empty list before going into another folder (sub-directory)
        files_list = []
        for f in files:
            f_size = getFileSize(f)
            
            print 'FILE %d: %s --> SIZE: %.2f KB (%d bytes)' \
            %(file_index + 1, f, f_size/1024., f_size)
            
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
            
# receive and write file to server's files folder
def receiveFile(self, file_name, file_size):
    print 'Receiving file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    file_path = SERVER_ADDRESS + '\\' + folder + '\\' + file_name
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
                sys.stdout.write('Current received file size (byte): %d (expected: %s) - %.2f%% \r'\
                %(sum_bytes, file_size, progress))
                sys.stdout.flush()
                
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

# send file to client side
def sendFile(self, file_name, file_size):
    print 'sending file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    file = open(SERVER_ADDRESS + '\\' + folder + '\\' + file_name, getReadMode())
    
    sum_bytes = 0
    for line in file:
        sum_bytes = sum_bytes + len(line)
        progress = float(sum_bytes)/float(file_size) * 100.
        sys.stdout.write('Current sent file size (byte): %d (expected: %s) - %.2f%% \r'\
        %(sum_bytes, file_size, progress))
        sys.stdout.flush()
        
        self.request.sendall(line)
        
    # if the client received the exact file size
    if self.request.recv(BYTE_LENGTH) == FOUND:
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
        global quit_msg
        
        # now the threaded server_thread connection's status is changed to establish
        thread_connection = True
    
        # identify current thread
        cur_thread = threading.current_thread()  
        # get thread-number in python
        thread_name = cur_thread.name        
    
        print '\nServer Thread %s receives request: preparing response ' % thread_name
      
        try:
            while thread_connection:
                # synchronous I/O non-blocking approach to detect ...
                # if there is any incoming data from main server  
                read, _, _ = select.select([self.request], [], [], 0)
                if read:
                    data = getData(self)
                
                # check if the main server's connection being disconnected
                # disconnect server_thread if so
                elif server_connection == False:
                    thread_connection = False
                    data = CMD_QUIT
                    
                else:
                    # return to the start of this while loop
                    data = None
       
                if data == CMD_LIST_ALL:
                    print 'COMMAND: ' + CMD_LIST_ALL
                    # list all the folders and files in server's window
                    folders = listAllFiles()
                    
                    # send the files_list to client 
                    # (two dimentional list objects(serialized))
                    # serialization
                    serial_data = cPickle.dumps(folders)
                    sendData(self, serial_data)
                    
                elif data == CMD_READ:
                    print 'COMMAND: ' + CMD_READ
                    file_name = getData(self)
                    
                    if findFile(file_name):           
                        sendData(self, FOUND)
                        
                        is_exit_on_client = getData(self)
                        
                        if is_exit_on_client == FOUND:
                            # get user permission from client
                            usr_permission = getData(self)
                            
                            if usr_permission == YES:
                                print 'WARNING: Over-writting file \"%s\"' %file_name
                                # senf file to client
                                file_size = getFileSize(file_name)
                                sendData(self, str(file_size))
                                sendFile(self, file_name, file_size)
                                
                            else:
                                print 'User declined operation!'
                                
                        else:
                            # send to client the file right away
                            file_size = getFileSize(file_name)
                            sendData(self, str(file_size))
                            sendFile(self, file_name, file_size)
                            
                    else:
                        # need this because if don't send data ...
                        # the socket will hang
                        sendData(self, NOT_FOUND)
                        
                elif data == CMD_WRITE:
                    print 'COMMAND: ' + CMD_WRITE
                    
                    file_name = getData(self)
                
                    # check if the file overlap
                    if findFile(file_name):
                        # notify client that is file is found (overlap)
                        sendData(self, FOUND)
                        # get user permission
                        usr_permission = getData(self)
                        
                        if usr_permission == YES:
                            print 'WARNING: Over-writting file \"%s\"' %file_name
                            file_size = getData(self)
                            receiveFile(self, file_name, file_size)
                        
                        else:
                            print 'Client had declined operation!'
                        
                    
                    else:
                        # notify client that the file is not found (no overlap)
                        sendData(self, NOT_FOUND)
                        file_size = getData(self)
                        receiveFile(self, file_name, file_size)
                        print 'Writting file \"%s\"' %file_name
                
                elif data == CMD_BYE:
                    thread_connection = False
                        
                elif data == CMD_QUIT:
                    sendData(self, CMD_QUIT)

            print '%s terminated!' %thread_name
        
        finally:
            print 'Reached Finally Clause'

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 1212

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
    
    # keep the user input active
    while server_connection:
        quit_msg = raw_input('You can enter \"%s\" anytime to exit this program! \n' \
        %CMD_QUIT)
        
        if quit_msg == CMD_QUIT:
            server_connection = False
            print 'QUIT FROM SERVER!\n'
    
    print '\nMain server thread shutting down the server and terminating'
    server.shutdown()
