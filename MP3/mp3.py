import os, multiprocessing, threading, time, pickle, socket, ftplib, hashlib
from shutil import copyfile

# port 8080 for file managing info : UDP/TCP
# port 8081 file update command: UDP
# port 9090 for Heartbeart : UDP
# port 6666 for FTP 

host_list = ['172.22.152.140', '172.22.152.141', '172.22.152.142', '172.22.154.135', '172.22.154.136', '172.22.154.137', '172.22.154.138', '172.22.156.135', '172.22.156.136', '172.22.156.137']
self_ip = socket.gethostbyname(socket.gethostname())

#TODO check sychronization : when iterater through data structure that has multiple thread operate on it, don't use iterator 

# --------------------------------------------------- file transmittion functions ---------------------------------------------------
# note that here path always contain file name 

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
	

def exist_file(address : str, file_name: str) -> bool:
	ftp = ftp_setup( address )
	return True if (file_name in ftp.nlst()) else False


# --------------------------------------------------- hashing function ---------------------------------------------------
def md5(fname):
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

def name_hash( file_name: str ) -> int:
	return int(hashlib.sha256(file_name.encode('utf-8')).hexdigest(), 16) % 10

# --------------------------------------------------- Node List ---------------------------------------------------

# node status tracking
class NodeList(): 
	def __init__(self, ip: str):
		self.list = {}
		self.ip = ip
		self.update_new(self.ip)
	
	def __repr__(self):
		ret = "[NODE] alive number: " + str(len(self.list)) + "\n"
		for key in list( self.list.keys() ):
			ret += key + "\n"
		return ret
	
	def send_file_list(self, file_name: str): 
		#return a list of host that one machine need to send file to when add file to sdfs
		hosts = sorted( list(self.list.keys()) )

		if len(hosts) < 5:
			return hosts
		else:
			file_hash = name_hash(file_name)
			while True:
				if host_list[file_hash] in hosts:
					index = hosts.index( host_list[file_hash] )
					break
				else:
					file_hash +=1
					file_hash %= 10
			hosts += hosts[0:4]
			return hosts[ (index + 1) : (index + 5) ] 
	
	def send_file_info_list(self):
		# return a list of machine that this machine need to send file list to (which is all but this machine)
		hosts = list(self.list.keys()) 
		del hosts[ hosts.index(self.ip) ]
		return hosts 
	
	def update_new(self, address: str):
		# update node list when new machine joins 
		self.list[address] = time.time()
	
	def update_old(self, handler): #$$$
		# update node list to delete old machine, return a list old machine and then do file replication 
		while True:
			now = time.time()
			self.list[self.ip] = now
			outdated = []
			for machine, timestamp in list(self.list.items()):
				if (now - timestamp) >  5:
					outdated.append(machine)
			if outdated:
				for ip in outdated:
					del self.list[ip]
				handler(outdated)
				
			time.sleep(0.5)
	
	def receiving_HB(self, handler ):#$$$
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', 9090))

		def link(msg, addr):
			if msg == b'beat':
				if addr[0] not in self.list :
					self.update_new(addr[0])
					# t = threading.Thread(target=handler)
					# t.start()
					handler()
					return
				self.update_new(addr[0])
				
		while True:
			msg, addr = sock.recvfrom(4)
			t = threading.Thread(target=link, args=(msg, addr))
			t.start()

	def sending_HB(self):#$$$
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		while True:
			time.sleep(0.5)
			for ip in host_list:
				sock.sendto(b'beat', (ip, 9090))


# --------------------------------------------------- File List ---------------------------------------------------

class FileList(): 

	def __init__(self, path:str, ip: str):
		self.ip = ip
		self.sdfs_dir = path
		self.file_list   = dict() # { ip: {filename :  (hash, timestamp) } }
		self.file_list[ self.ip ] = dict()
	
	def __repr__(self):
		ret = ""
		for ip, ip_file_list in list(self.file_list.items()):
			ret += "[" + str(ip) + "] "+ str(len(ip_file_list)) +" ------------------------------\n" 
			for filename, info in list(ip_file_list.items()):
				ret += filename + "\t\t\t: " + str(info) + '\n'
		return ret
		
	# ----- file list interface -----

	def add_file(self, file_name: str, file_hash: str, timestamp: str): 
		self.file_list[ self.ip ][ file_name ] = [file_hash, timestamp]
		
	def delete_file(self, file_name: str):
		
		if file_name in self.file_list[ self.ip ]:
			print("[INFO] deleting :", file_name )
			del self.file_list[ self.ip ][ file_name ]
		else:
			print("[INFO] file not found in file list :", file_name )
	
	def update_file(self, file_name: str, hash: str, timestamp: str): 
		self.file_list[ self.ip ][ file_name ][0] = hash
		self.file_list[ self.ip ][ file_name ][1] = timestamp

	def search_ip(self, file_name: str ): 
		#list all machine (VM) addresses where this file is currently being stored;
		print("[INFO] searching for:", file_name)
		ip_list = []
		for ip, ip_file_list in list(self.file_list.items()):
			if file_name in ip_file_list:
				ip_list.append(ip)
		
		if len(ip_list) == 0:
			print("[INFO] File not exist")

		return ip_list

	def search_file( self, file_name: str ):
		# return file info 
		for ip, ip_file_list in self.file_list.items():
			if file_name in ip_file_list:
				return self.file_list[ip][file_name]		
		return 0

	def all_file(self) -> list:
		file_list = dict()
		for _, ip_file_list in list(self.file_list.items()): 
			for filename, info in list(ip_file_list.items()):
				file_list[filename] = info
		return [(k,v) for k,v in file_list.items()]
	
	def check(self):
		#this function checks the file list that if all the file has exact 4 replications 
		file_list = dict()
		for _, ip_file_list in list(self.file_list.items()): 
			for filename, _ in list(ip_file_list.items()):
				if(filename in file_list):
					file_list[filename] += 1
				else:
					file_list[filename] = 1
		print("[INFO] # of file: ", len(file_list))
		for f, num in file_list.items():
			print(f, "\t\t : ",num)

	def update_file_local_all(self): #$$$
		# local file self update (for local machine only) 
		# TODO 如果莫名其妙的多了或者少了一个file
		while True:
			#update new 
			for file_name in os.listdir(self.sdfs_dir):
				if file_name not in self.file_list[ self.ip ]:
					print("[Warning] sychronization ++ ", file_name) # 莫名其妙的多了一个file
						
			#update deleted
			for file_name in list(self.file_list[ self.ip ].keys()):
				if file_name not in os.listdir(self.sdfs_dir):
					print("[Warning] sychronization -- ", file_name) # 莫名其妙的少了一个file

			time.sleep(5)	

	# ----- communication interface -----
	
	# -- command interface: 
	# interface in this section involks function to update self.file_list[ self.ip ]

	def handle_update_request(self): #$$$
		# update command recieving
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', 8081))

		def link(msg, addr):
			if msg[0:6] == b'update':
				arg_list = str(msg[6:-1], encoding='utf8').split(';')
				if len(arg_list) != 3:
					print("[ERROR] invaild command recieved handle_update_request")
					return 

				if arg_list[0] in self.file_list[self.ip]:
					self.update_file( arg_list[0], arg_list[1], arg_list[2] ) 
				else:
					self.add_file( arg_list[0],arg_list[1], arg_list[2])
			
			if msg[0:6] == b'delete':
				file_name = str(msg, encoding='utf8')[6:]
				self.delete_file( file_name )

		while True:
			msg, addr = sock.recvfrom(256)
			t = threading.Thread(target=link, args=(msg, addr))
			t.start()

	def send_update_request(self, file_name: str, file_hash: str, timestamp: str, ip_list: list): 
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		for ip in ip_list:
			sock.sendto(bytes('update' + file_name + ';'+ file_hash +';' + str(timestamp), encoding='utf8'), (ip, 8081))
			
	def send_delete_request(self, file_name: str, ip_list: list): 
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		for ip in ip_list:
			sock.sendto(bytes('delete' + file_name , encoding='utf8'), (ip, 8081))
			
	# -- Info interface 
	# interface in this section updates file info on machine other than self.file_list[ self.ip ]

	def send_list(self, ip_getter):  #$$$
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		while True:
			time.sleep(0.7)
			data = pickle.dumps( self.file_list[self.ip] )
			for ip in ip_getter():
				sock.sendto( data , (ip, 8080))
	
	def get_list(self): #$$$
		# remote file list update, for other machine only
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', 8080))

		def link(msg, addr):
			self.file_list[addr[0]] = pickle.loads(msg) 
					
		while True:
			msg, addr = sock.recvfrom(4096)
			t = threading.Thread(target=link, args=(msg, addr))
			t.start()


# --------------------------------------------------- Thread management ---------------------------------------------------

class management():

	def __init__(self, path : str):
		self.sdfs_dir =  path
		self.ip = socket.gethostbyname(socket.gethostname())
		self.nodelist = NodeList(self.ip)
		self.filelist = FileList(path, self.ip)
		
	
	# ----- process control -----
	def run_note(self):
		# node management 
		node_t0 = threading.Thread(target=self.nodelist.receiving_HB, args=( self.other_joined, ) ) 
		node_t1 = threading.Thread(target=self.nodelist.sending_HB) 
		node_t2 = threading.Thread(target=self.nodelist.update_old, args=( self.other_failed, ) )

		node_t0.start()
		node_t1.start()
		node_t2.start()


	def run_file(self):
		# file management 
		file_t0 = threading.Thread(target=self.filelist.send_list, args=(self.nodelist.send_file_info_list,))
		file_t1 = threading.Thread(target=self.filelist.get_list)
		file_t2 = threading.Thread(target=self.filelist.handle_update_request)
		file_t3 = threading.Thread(target=self.filelist.update_file_local_all)

		file_t0.start()
		file_t1.start()
		file_t2.start()
		file_t3.start()
		
	
	def run(self):
		#delete all file in sdfs folder 
		l = [ f for f in os.listdir(self.sdfs_dir)]
		for f in l:
			os.remove(os.path.join(self.sdfs_dir, f))
		print("[INFO] removed all file in: ", self.sdfs_dir)

		# running node and file list service 
		self.run_note()
		self.run_file()

		# joining in the group 
		print("[INFO] Joining the group")
		self.join()

		# starting the shell
		self.shell()


	# ----- Replication Control -----
	def get_file_replication(self, file_name: str, info: list):
		#check local exist 
		if os.path.isfile( self.sdfs_dir + file_name ):
			return

		dest_list = self.nodelist.send_file_list(file_name)
		if self.ip in dest_list:
			avail_list = self.filelist.search_ip(file_name)
			for ip in avail_list:
				#check remote exit 
				if exist_file(ip, file_name): #need to check hash ?
					ret = get_file(ip, file_name, self.sdfs_dir + file_name) 
					if ret == 0:
						self.filelist.add_file( file_name, info[0], info[1])
					break

	def join(self): 
		# call when this machine want to join the group, it checks every file to see if this machine needs a copy 	
		time.sleep(2)
		for file_name, info in self.filelist.all_file():		
			t = threading.Thread(target=self.get_file_replication, args=( file_name, info, ))
			t.start()
					
	def other_failed(self, ip_list:list ): 
		# call when a node failed 
		for ip in ip_list:
			print("[INFO] handling failed machine ", ip)
			for file_name, info in list(self.filelist.file_list[ip].items()):
				t = threading.Thread(target=self.get_file_replication, args=( file_name, info, ))
				t.start()
			del self.filelist.file_list[ip]
					
	def other_joined(self): 
		# call when a node (other than this machine) join
		# TODO 当join太快, replication会删的太快, 导致没地方get files
		print("[INFO] new processing join, handling")
		for file_name, _ in list(self.filelist.file_list[self.ip].items()):
			dest_list = self.nodelist.send_file_list(file_name)
			if self.ip not in dest_list:
				delete_file(self.ip, self.sdfs_dir + file_name)
				self.filelist.delete_file( file_name )

	
	# ----- User operation interface -----
	def put(self, local_file_path:str, sdfs_file_name: str): #add file to sdfs 

		if os.path.isfile(local_file_path):
			
			#check timestamp and md5
			info = self.filelist.search_file(sdfs_file_name)
			if ( info ):
				file_hash = md5(local_file_path)
				if file_hash == info[0]:
					print("[ERROR] same file already exist")
					return

				now = time.time()
				if (now - float(info[1]) ) < 60:
					while True:
						commit = input("Two updates update occurs within 1 minute, commit[y/n]?")
						if(commit == 'y'):
							break
						elif(commit == 'n'):
							return
						else:
							print("[ERROR] Invalid input")
			
			#copy file to sdfs
			ip_list = self.nodelist.send_file_list(sdfs_file_name)
			for ip in ip_list:
				t = threading.Thread(target=send_file, args=(ip, local_file_path, sdfs_file_name, ) )
				t.start()
			
			# update file timestamp
			self.filelist.send_update_request(sdfs_file_name, md5(local_file_path), time.time(), ip_list) 
			print( "[INFO] Done sending file" )
			

	def get(self, local_file_path:str, sdfs_file_name: str): 
		#fetches file from sdfs
		if os.path.isfile( self.sdfs_dir + sdfs_file_name ) :
			copyfile(self.sdfs_dir + sdfs_file_name, local_file_path)
			return
		else:
			ip_list = self.filelist.search_ip(sdfs_file_name)
			for ip in ip_list:
				if exist_file(ip, sdfs_file_name):
					get_file(ip, sdfs_file_name , local_file_path)
					return
		
		print("[ERROR] No such file")
				
				
	def delete(self, sdfs_file_name: str): 
		#delete local and remote file 
		ip_list = self.filelist.search_ip(sdfs_file_name)
		for ip in ip_list:
			delete_file(ip, self.sdfs_dir + sdfs_file_name)
		
		self.filelist.send_delete_request(sdfs_file_name, ip_list)
		print( "[INFO] Done deleting", sdfs_file_name )
		
			
	# ----- the shell -----
	def shell(self):
		while True:
			command = input("Enter Command:   ")
			if  ( len(command) < 1): 
				print("[INFO] no command inputed")

			elif(command == 'ip'):
				print(self.ip)

			elif( command == 'f' ):# print file list 
				print(self.filelist)

			elif( command == 'n'): # print node list
				print(self.nodelist)

			# elif( command == 'ls'): # print node list
			# 	print ( str(os.listdir("/home/zitongc2/")).replace(",", "\n").replace("\'", "").replace("[", " ").replace("]", "") )

			elif( command[0:2] == 'ex' ):
				print("[INFO] excuting system command:" , command[2:] )
				os.system(command[2:])

			elif( command[0] == 'p'): # put file to sdfs
				parameter = command.split(' ')
				if (len(parameter) != 3): 
					print("[ERROR] wrong number of parameter")
					continue
				self.put( parameter[1], parameter[2])
				
			elif( command[0] == 'g'): # get file from sdfs
				parameter = command.split(' ')
				if (len(parameter) != 3): 
					print("[ERROR] wrong number of parameter")
					continue
				self.get( parameter[2], parameter[1])
				
			elif( command[0] == 'd'): #delete file in sdfs
				parameter = command.split(' ')
				if (len(parameter) != 2): 
					print("[ERROR] wrong number of parameter")
					continue
				print("[input]:", parameter[1])
				self.delete(parameter[1])
				
			elif( command[0] == 'l'): #list all machine (VM) addresses where this file is currently being stored
				parameter = command.split(' ')
				if (len(parameter) != 2): 
					print("[ERROR] wrong number of parameter")
					continue
				print( self.filelist.search_ip(parameter[1]) )
				
			elif( command[0] == 's'):# store
				if(len(command) == 1):
					print ( str(os.listdir(self.sdfs_dir)).replace(",", "\n").replace("\'", "").replace("[", " ").replace("]", "") )
			
			elif( command == 'q'):
				break

			elif( command == 'testrun'):
				for i in range(16):
					self.put( "/home/zitongc2/" + str(i) + ".txt", str(i) + ".txt")
			
			elif( command == 'check' ):
				self.filelist.check()


			else: print("[ERROR] command not valid")


manager = management("/home/zitongc2/test/")
manager.run() 