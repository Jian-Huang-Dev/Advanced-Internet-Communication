import socket
import sys
import os
import cPickle
import platform
import select
import errno

# contants
CMD_LIST_ALL = 'list'
CMD_READ = 'read'
CMD_WRITE = 'write'
CMD_BYE = 'bye'
CMD_QUIT = 'quit' 
CMD_CONNECT = 'connect'
BYTE_LENGTH = 64
ERROR = 'ERROR'
FOUND = 'FOUND'
NOT_FOUND = 'NOT_FOUND'
YES = 'Y'
NO = 'N'
# a random symbol to indicate end of line
END_MARKER = '@#' 
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

# directory path for client files folder (CHANGE THIS ACCORDINGLY)
CLIENT_ADDRESS = \
r'C:\Dropbox\McMaster_Final_Year_2014-2015\4DN4_Advanced_Internet_Communication\Labs&Assignments\lab_2\4DN4_LAB2\Client_dir'

# initialize client's connection status
connection_flag = False

# initialize socket's status
sock = None 

# a file object to store its file name and size
class file(object):
    file_name = None
    file_size = None

# a folder object to store its folder name and files inside of it
class folder(object):
    directory = None
    files = []

# check if the file_name contains a file type 
# valid file name: XY.Z, invalid file name: XY
def isFile(file_name):
    for string in file_name:
        if string == '.':
            return True
    
    return False

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
    
    files = os.listdir(CLIENT_ADDRESS + '\\' + folder)
    for f in files:
        # only looking for files, NOT directories (folders)
        if os.path.isdir(f) == False:
            if f == file_name:
                return True
  
    return False
    
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

# perform socket connection 
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

# custom function to ask user for port number
def getPortNum():
    port_num = False
    # check if the user entered the port number is in correct format
    # will proceed if the user entered the correct format
    while port_num == False:
        port_num = getInt(raw_input('Enter port number: '))
        
    return port_num
    
# custom function to send data with a end marker "@#"
# a work-around indication to tell if the message being ...
# fully received by server
def sendData(text):
    sock.sendall(text + END_MARKER)
    
# return the file size of the specific file
# parameter as string type
def getFileSize(file_name):
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    # open up the corresponding path
    file = open(CLIENT_ADDRESS + '\\' + folder + '\\' + file_name, getReadMode())
    # to the end of the file '2' so it can 'tell' the full size of the file
    file.seek(0, 2)
    size = file.tell()
    file.close()
    
    return size
    
# custom function to convert string to integer
def getInt(string):
    try:
        return int(string)
        
    except ValueError:
        print "Oops!  That was not a valid number.  Try again..."   
        return False
        
# list all files from server's files folder
# including the sub-directory name
def listAllFiles(objects):
    # this 'objects' is a two dimentional list (list of list)
    # the outter list in objects will represent folder objects, while each folder object ...
    # includes "folder name (sub-directory) and a list of files in that sub-directory"
    # i.e [['MOVIE', ['file1', 'file2']], ['MUSIC', ['file1', 'file2']]]
    
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
        
# receive and write file to client's files folder
def receiveFile(file_name, file_size):
    print 'Receiving file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    file_path = CLIENT_ADDRESS + '\\' + folder + '\\'+ file_name
    file = open(file_path, getWriteMode())
    
    print 'storing file: %s' %file_name
    sum_bytes = 0
    
    try:
        # keep receiving until the file size matches
        while int(sum_bytes) < int(file_size):
            data = sock.recv(BYTE_LENGTH)
            
            if data:
                file.write(data)
                sum_bytes = sum_bytes + len(data)
                progress = float(sum_bytes)/float(file_size) * 100.
                sys.stdout.write('Current received file size (byte): %d (expected: %s) - %.2f%% \r'\
                %(sum_bytes, file_size, progress))
                sys.stdout.flush()

            else:
                print '\nTotal received file size (byte): %d (expected: %s)'\
                %(sum_bytes, file_size) 
                
                # once reached 'else' statement, will break the while loop
                # senerio 1: the file is successfully received at full size
                # senerio 2: the file is not fully received ...
                # (user abruptly closed the connection)
                break
    
    except socket.error as error:
        if error.errno == errno.WSAECONNRESET:
            # clean up the corrupted file
            file.close()
            os.remove(file_path)
            
    # if the file size received correctly
    # notify server and close file
    if int(sum_bytes) == int(file_size):
        print '\nTotal received file size (byte): %d (expected: %s)'\
        %(sum_bytes, file_size) 
        
        # notify server that I have received file successfully
        sock.sendall(FOUND)
        file.close()
        print '\n' + OPERATION_COMPLETE
    
    else:
        file.close()
        # clean up the corrupted file
        os.remove(file_path)
        
        print '\n' + OPERATION_IMCOMPLETE
        
# send file to server side
def sendFile(file_name, file_size):
    print 'sending file: %s' %file_name
    
    # find the right folder that this file belongs to
    folder = checkFileType(file_name)
    
    file = open(CLIENT_ADDRESS + '\\' + folder + '\\' + file_name, getReadMode())
    
    sum_bytes = 0
    for line in file:
        sum_bytes = sum_bytes + len(line)
        progress = float(sum_bytes)/float(file_size) * 100.
        sys.stdout.write('Current sent file size (byte): %d (expected: %s) - %.2f%% \r'\
        %(sum_bytes, file_size, progress))
        sys.stdout.flush()
        
        sock.sendall(line)
        
    # if the client received the exact file size
    if sock.recv(BYTE_LENGTH) == FOUND:
        print 'Total sent file size (byte): %d (expected: %s)'\
            %(sum_bytes, file_size)
        file.close() 
        print '\n' + OPERATION_COMPLETE
    
    else:
        file.close()
        print '\n' + OPERATION_IMCOMPLETE
 
# main function is here
try:
    # Will ask usr to perform connection
    while connection_flag == False:
        msg = raw_input('\nEnter Commands:\nCONNECT\nQUIT\n')
            
        # notify server to enable connection
        if msg == CMD_CONNECT:
            # connnect
            sock = funcConnect('localhost', 1212)
            # if connection is established, continue to promote user with commands
            if sock:
                connection_flag = True
                
        # quit the program without being connected
        elif msg == CMD_QUIT:
            if sock == None:
                break
            # exit the python program
            connection_flag = None   
            
        try:
            while connection_flag: # connection will maintain active unless user quits
                # prmote user to enter commands
                msg = raw_input('\nEnter Commands:\n\nLIST_ALL\nREAD\nWRITE\nBYE\n')
                
                # synchronous I/O non-blocking approach to detect ...
                # if there is any incoming data from main server               
                read, _, _ = select.select([sock], [], [], 0)
                if read:
                    msg = getData()
                    
                # notify server to list all files in server's files folder
                if msg == CMD_LIST_ALL: 
                    print 'COMMAND: ' + CMD_LIST_ALL
                    sendData(msg)
                    
                    # get files_list (two dimentional list objects) from server (serialized)
                    data = getData()
                    
                    # deserialization
                    # get folders and files (two dimentional list objects)
                    deSerialized_data = cPickle.loads(data)
                    
                    # list and print all files including sub-directories
                    listAllFiles(deSerialized_data)
                    
                # notify server to store specific file into client's files folder
                elif msg == CMD_READ:
                    print 'COMMAND: ' + CMD_READ
                    # send command to notify server
                    sendData(msg)
                    
                    # will not proceed until user has the correct file name inputed
                    while True:
                        file_name = raw_input('Enter file name with file type: ')
                        if isFile(file_name):
                            break
                            
                    # send file name to server
                    sendData(file_name)
                    
                    # boolean (string type) to check if the specified file being found
                    is_exit_on_server = getData()
                    
                    if is_exit_on_server == FOUND:
                        # now check if need to over-write 
                        if findFile(file_name):      
                            # notify server that the client's directory has overlap files
                            # perform operation accordingly
                            sendData(FOUND)                         
                            
                            # will only proceed if the user entered correct command
                            while True:
                                usr_permission = \
                                raw_input('WARNING: The file \"%s\" existing on files folder, over-write? (Y/N)\n' \
                                % file_name)
                                
                                if usr_permission == YES or usr_permission == NO:
                                    break
                            
                            # let server knows user's decision
                            sendData(usr_permission)
                            
                            if usr_permission == YES:
                                file_size = getData()
                                receiveFile(file_name, file_size)
                                print 'WARNING: the file \"%s\" is being over-written on files folder' %file_name
                            
                            else:
                                print 'User declined operation!'
                        
                        else:
                            sendData(NOT_FOUND)
                            # receive file from server
                            file_size = getData()
                            receiveFile(file_name, file_size)
                            print 'Writing file \"%s\" on files folder' %file_name
                        
                    else:
                        print 'The file: \"%s\" is not found on the FTP server' %file_name
                    
                # notify server to write specific file into server's directory
                elif msg == CMD_WRITE:
                    print 'COMMAND: ' + CMD_WRITE
                    
                    # will not proceed until user has the correct file name inputed
                    while True:
                        file_name = raw_input('Enter file name with file type: ')
                        if isFile(file_name):
                            break
                    
                    # if user entered correct name
                    if findFile(file_name):
                        # send command
                        sendData(msg)
                        
                        sendData(file_name)
                        file_size = getFileSize(file_name)
                        
                        # check if the file being overlap with server's file
                        is_file_overlap = getData()
                        
                        if is_file_overlap == FOUND:
                            # if overlap, 
                            # will only proceed if the user entered correct command
                            while True:
                                usr_permission = \
                                raw_input('WARNING: The file \"%s\" existing on files folder, over-write? (Y/N)\n' \
                                % file_name)
                                
                                if usr_permission == YES or usr_permission == NO:
                                    break
                                
                            # let server knows user's decision
                            sendData(usr_permission)
                            
                            if usr_permission == YES:
                                sendData(str(file_size))
                                # send file to server and over write
                                sendFile(file_name, file_size)
                                print 'WARNING: the file \"%s\" is being over-written on the server' %file_name
                            
                            else:
                                print 'User declined operation!'
                            
                        else:
                            sendData(str(file_size))
                            # no file overlaps, send file to the server
                            print 'Writing file \"%s\" on the server' %file_name
                            sendFile(file_name, file_size)
                    
                    # user did not enter the correct file name
                    else:
                        print 'The file \"%s\" NOT found!' %file_name             

                # notify server to quit its connection
                elif msg == CMD_BYE:
                    connection_flag = False
                    # if connection was established, and trying to quit
                    if sock: 
                        sendData(msg)
                        sock.close()
                        
                    # else if the connection was not established (unlikely) ...
                    # while trying to quit, then break it
                    else:
                        # do nothing
                        break 
                
                # notify client to quit its connection
                elif msg == CMD_QUIT:  
                    connection_flag = False
                    print '***Server had shut down the connection!***'
                    # if connection was established, and trying to quit
                    if sock: 
                        sendData(msg)
                        sock.close()
                        
                    # else if the connection was not established (unlikely) ...
                    # while trying to quit, then break it
                    else:
                        # do nothing
                        break
                
                else:
                    print 'Please enter the correct command'
        
        except KeyboardInterrupt:
            print 'User pressed (CTRL-C ) to shut down client'
        
        finally:
            if connection_flag == None:
                # if no connectin was established, then do not show this msg
                pass
                
            else:
                print >>sys.stderr, '\nShut down client\n'
                
            sock.close()

except KeyboardInterrupt:
    print 'User pressed (CTRL-C ) to shut down client' 
            
finally:
    print 'Closing client\n'
    sock.close()