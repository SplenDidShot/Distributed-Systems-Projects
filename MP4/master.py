from rpyc.utils.classic import teleport_function
from rpyc.utils.zerodeploy import DeployedServer
from rpyc.utils.zerodeploy import MultiServerDeployment

from plumbum import SshMachine

import rpyc, math, threading, io, socket
import subprocess
import os, ftplib, hashlib


# --------------------------------------------------- ftp function ---------------------------------------------------

def ftp_setup( address : str ):
	ftp = ftplib.FTP()
	host = address
	port = 6666
	try:
		ftp.connect(host, port)
		ftp.login("428", "zheshiwomenMP3demima")
	except:
		print("[INFO] unable to connect to FTP in ", address)
	return ftp

def send_file( address : str, local_path: str, sdfs_fname: str):
	# remote_path no use
	ftp = ftp_setup( address )
	
	try:
		file = open( local_path,'rb' ) 
		ftp.storbinary('STOR '+ sdfs_fname, file)     # send the file
		print ("[INFO] sent file to ", address)   
		return 0
	except:
		print("[ERROR] failed to send file to ", address )
		return 1

def get_file( address : str, file_name: str, local_path: str  ):
	ftp = ftp_setup( address )
	try:
		file = open( local_path,'wb' ).write
		ftp.retrbinary('RETR '+file_name, file)    
		print ("[INFO] got file from ", address)   
		return 0
	except:
		print("[ERROR] failed to get file from ", address )
		return 1
	
def delete_file(address : str, remote_path: str):
	if( address == self_ip ):
		os.remove( remote_path )
		print("[INFO] deleted file:", remote_path)
	else:
		ftp = ftp_setup( address )
		file_name = remote_path.split("/")[-1]
		try:
			ftp.delete(file_name)
			print("[INFO] deleted file on:", address)
			return 0
		except:
			print("[ERROR] fail to delete file:", file_name, " in ", address)
			return 1



def append_data_mem( address : str, input_data: str, sdfs_fname: str): 
	# address: address of the remote machine
	# input_data : data that we want to append to the remote machine
	# sdfs_fname: name of the file in the sdfs
	ftp = ftp_setup( address )
	
	try:
		data = io.BytesIO( bytes(input_data, 'utf-8') )
		ftp.storbinary ('APPE ' + sdfs_fname, data, 1)
		print ("[INFO] append data to  ", address)   
		ftp.close()
		return 0
	except:
		print("[ERROR] failed to send file to ", address )
		return 1

def append_data_file( address : str, input_file_path : str, sdfs_fname: str): 
	ftp = ftp_setup( address )
	
	try:
		f = open(input_file_path, 'rb')
		ftp.storbinary ('APPE ' + sdfs_fname, f, 1)
		print ("[INFO] append data to  ", address)   
		ftp.close()
		return 0
	except:
		print("[ERROR] failed to send file to ", address )
		return 1

def exist_file(address : str, file_name: str) -> bool:
	ftp = ftp_setup( address )
	return True if (file_name in ftp.nlst()) else False

def name_hash( file_name: str ) -> int:
        import hashlib
        # return int(hashlib.sha256(file_name.encode('utf-8')).hexdigest(), 16) % 10
        return int(hashlib.sha256(file_name.encode('utf-8')).hexdigest(), 16)


# --------------------------------------------------- MJ function ---------------------------------------------------


def file_len(fname):
	p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result, err = p.communicate()
	if p.returncode != 0:
			raise IOError(err)
	return int(result.strip().split()[0])

def dispatchFile(fileName: str, nodeList: list):
	cmd = ["split", "-l", str( int(file_len(fileName)/10 ) + 5), fileName, "filexxoo"]
	subprocess.check_call(cmd) 
	
	for splitedFile in [f for f in os.listdir('.') if (f[0:8] == 'filexxoo') ]  :
		num = int( ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].index( splitedFile[-1] ) ) 
		send_file( nodeList[ num ], splitedFile, 'phase0/input' )
		os.remove(splitedFile)
		

		


def mapleDeployment(host, loacalMaple, loaclMapleHandler, loaclMapleDataMerger, loaclGetDestination):
    # create the deployment
    mach = SshMachine(host, user="zitongc2", keyfile="/home/zitongc2/.ssh/id_rsa" )
    server = DeployedServer(mach)

    # and now you can connect to it the usual way
    conn = server.classic_connect()
    print ("[INFO] Connected to ", host)
    conn._config['sync_request_timeout'] = None

    def getResult(string):
        print(string)

    remoteMaple = conn.teleport(loacalMaple)
    remoteMapleHandler = teleport_function(conn, loaclMapleHandler)
    remoteMapleHandler( remoteMaple, "/home/zitongc2/test/phase0/input", getResult)

    print("[INFO] Done processing, now sendind result to desinated location")
    remoteMapleDataMerger = teleport_function(conn, loaclMapleDataMerger)
    remoteMapleDataMerger( loaclGetDestination )


    # when you're done - close the server and everything will disappear
    server.close()




def mapleHandler( maple, inFileName, getResult ): # function, input file (obj), output file (obj)
    import os
    print("[INFO] cleaning caches")
    for folder in [ '/home/zitongc2/test/phase1', '/home/zitongc2/test/phase2', '/home/zitongc2/test/phase3' ]:
        filelist = [ f for f in os.listdir(folder) ]
        for f in filelist:
            os.remove(os.path.join(folder, f))

    inFile = open(inFileName, 'r')
    result = map(maple, inFile) 

    filePointerList = dict()
	
    counter = 0

    for pairs in result:
        # write to file
		
        for pair in pairs: 
		
            key = pair[0].strip()
            value = str(pair[1]) + '\n'
            file_path = "/home/zitongc2/test/phase1/" + str(key)
            if os.path.isfile( file_path ):
                
                if filePointerList[key].closed:
                    filePointerList[key] = open(filePointerList[key].name, 'a')
                    counter += 1
                    # getResult(counter)
                    # getResult("*********************************")

                filePointerList[key].write(value) # append_data
            else:
                if( counter > 1000 ):
                    for pointer in filePointerList.values():
                        pointer.close()
                    
                    counter = 0

                filePointerList[key] = open(file_path, 'a') # create_file
                counter += 1
                # getResult(counter)
                # getResult("*********************************")
                filePointerList[key].write(value) # append_data	
    
    inFile.close()

    for pointer in filePointerList.values():
        pointer.close()


def mapleDataMerger( getDestination ):
    import threading, ftplib, os

    def ftp_setup( address : str ):
        ftp = ftplib.FTP()
        host = address
        port = 6666
        try:
            ftp.connect(host, port)
            ftp.login("428", "zheshiwomenMP3demima")
        except:
            print("[INFO] unable to connect to FTP in ", address)
        return ftp

    def append_data_file( address : str, input_file_path : str, sdfs_fname: str):
        ftp = ftp_setup( address )

        try:
            f = open(input_file_path, 'rb')
            ftp.storbinary ('APPE ' + sdfs_fname, f, 1)
            print ("[INFO] append data to  ", address)
            ftp.close()
            return 0
        except:
            print("[ERROR] failed to send file to ", address )
            return 1

    def transfer_processed_data( key:str, getDestination ):
        key_path = "/home/zitongc2/test/phase1/"+key

        # get desination ip
        destination = getDestination(key)
        append_data_file( destination, key_path, 'phase2/' + key)


    threadList = [ threading.Thread(target=transfer_processed_data, args=( file_name, getDestination,  )) for file_name in os.listdir("/home/zitongc2/test/phase1") ]
    for thread in threadList:
        thread.start()

    for thread in threadList:
        thread.join()

# ------------
def juiceDeployment(host, loacalJuice, loaclJuiceHandler, localJuiceDataMerger):
    # create the deployment
    mach = SshMachine(host, user="zitongc2", keyfile="/home/zitongc2/.ssh/id_rsa" )
    server = DeployedServer(mach)

    # and now you can connect to it the usual way
    conn = server.classic_connect()
    print ("[INFO] Connected to ", host)
    conn._config['sync_request_timeout'] = None

    remoteJuice = conn.teleport(loacalJuice)
    remoteMapleHandler = teleport_function(conn, loaclJuiceHandler)
    remoteMapleHandler( remoteJuice )

    print("[INFO] Done processing, now sendind result to desinated location")
    remoteJuiceDataMerger = teleport_function(conn, localJuiceDataMerger)
    remoteJuiceDataMerger( socket.gethostbyname(socket.gethostname())  )

    # when you're done - close the server and everything will disappear
    server.close()


def juiceHandler( juice: callable ):
    import os
    inFileList = os.listdir("/home/zitongc2/test/phase2") 
    for inFileName in inFileList:
        outFile = open('/home/zitongc2/test/phase3/result', 'a')
        inFile = open( '/home/zitongc2/test/phase2/' + inFileName ,'r')
        result = juice( inFileName, inFile) 
		
        for item in result:
            outFile.write( str(item) + '\n')
        
        inFile.close()  
        outFile.close()

def juiceDataMerger( master_ip:str ):
    import ftplib, os

    def ftp_setup( address : str ):
        ftp = ftplib.FTP()
        host = address
        port = 6666
        try:
            ftp.connect(host, port)
            ftp.login("428", "zheshiwomenMP3demima")
        except:
            print("[INFO] unable to connect to FTP in ", address)
        return ftp

    def append_data_file( address : str, input_file_path : str, sdfs_fname: str):
        ftp = ftp_setup( address )

        try:
            f = open(input_file_path, 'rb')
            ftp.storbinary ('APPE ' + sdfs_fname, f, 1)
            print ("[INFO] append data to  ", address)
            ftp.close()
            return 0
        except:
            print("[ERROR] failed to send file to ", address )
            return 1

    append_data_file( master_ip, '/home/zitongc2/test/phase3/result', 'result')


# --------------------------------------------------- main function ---------------------------------------------------
		
def maple(line:str): # a single line in the file 
    result = []
    l = line.split(" ")
    for word in l:
        parsed = ''.join(filter(str.isalnum, word))
        if parsed.isalnum():
            result.append( ( parsed , 1) )
    return result

def juice(key:str, values): # values will be a file pointer, and this function will return a generator 
	result = sum( 1 for _ in values)
	# result = file_len(values.name)
	yield key + ' ' + str(result)

def maple2(line:str): # a single line in the file 
    input = line.split(' ')
    return [ ( 1,  input[0] + ' ' +input[1] ) ]

def juice2(key:str, values): # values will be a file pointer, and this function will return a generator 
    totalCount = 0
    for line in values:
        totalCount += int(line.split(' ')[-1])
    
    values.seek(0)
    for line in values:
        yield line.split(' ')[0] + ' ' + str(int(line.split(' ')[-1])/totalCount)


# ----------------------------------
def getDestination( key: str ):
    return host_list[ name_hash(key)%len(host_list) ]

host_list = ['172.22.152.140', '172.22.152.141', '172.22.152.142', '172.22.154.135', '172.22.154.136', '172.22.154.137', '172.22.154.138', '172.22.156.135', '172.22.156.136', '172.22.156.137']


#  ------------- Maple -------------
inputFileName = "/home/zitongc2/input_data/input"#input("[INPUT] file path?")
print("[MAPLE] spliting and sendingfile")
dispatchFile( inputFileName, host_list)

print("[MAPLE] deploying maple")
mapleWorkerThreadList = [ threading.Thread( target=mapleDeployment, args=(host, maple, mapleHandler, mapleDataMerger, getDestination,  ) ) for host in host_list ]

for thread in mapleWorkerThreadList:
    thread.start()

for thread in mapleWorkerThreadList:
    thread.join()

print("[MAPLE] done --------------------------- ")


#  ------------- Juice -------------
print("[JUICE] deploying juice")
juiceWorkerThreadList = [ threading.Thread( target=juiceDeployment, args=(host, juice, juiceHandler, juiceDataMerger,  ) ) for host in host_list ]

for thread in juiceWorkerThreadList:
    thread.start()

for thread in juiceWorkerThreadList:
    thread.join()

os.rename("./test/result", "output.txt")
print("[JUICE] done ---------------------------")


