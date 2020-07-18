
from fsplit.filesplit import FileSplit
import os, math, ftplib

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
		
def dispatchFile(fileName: str, nodeList: list):

	fs = FileSplit(file=fileName, splitsize= math.ceil( os.path.getsize(fileName) / len(nodeList) ) + 10 , output_dir='.')
	def func(filePath, size, count):
		print("Dispatching file: {0}, size: {1}, count: {2}".format(filePath, size, count))
		num = int(filePath.split('_')[-1].split('.')[0]) - 1
		
		send_file( nodeList[ num ], filePath, filePath.split('/')[-1] )
		os.remove(filePath)

	fs.split(callback=func)
	

host_list = ['172.22.152.140', '172.22.152.141', '172.22.152.142', '172.22.154.135', '172.22.154.136', '172.22.154.137', '172.22.154.138', '172.22.156.135', '172.22.156.136', '172.22.156.137']

dispatchFile('test.txt', host_list)