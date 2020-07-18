import os, threading, socket, ftplib, hashlib, time

# this program uses port 9090

host_list = ['172.22.152.140', '172.22.152.141', '172.22.152.142', '172.22.154.135', '172.22.154.136', '172.22.154.137', '172.22.154.138', '172.22.156.135', '172.22.156.136', '172.22.156.137']


# --------------------------------------------------- Node List ---------------------------------------------------

# node status tracking
class NodeList(): 
	def __init__(self):
		self.list = {}
		self.ip = socket.gethostbyname(socket.gethostname())
		self.update_new(self.ip)

	def run(self):
		thread0  = threading.Thread( target=self.update_old)
		thread1  = threading.Thread( target=self.receiving_HB )
		thread2  = threading.Thread( target=self.sending_HB )
		thread0.start()
		thread1.start()
		thread2.start()

	def __repr__(self):
		ret = "[NODE] alive number: " + str(len(self.list)) + "\n"
		for key in list( self.list.keys() ):
			ret += key + "\n"
		return ret
	
	def update_new(self, address: str):
		# update node list when new machine joins 
		self.list[address] = time.time()
	
	def update_old(self): #$$$
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
				# handler(outdated)
				
			time.sleep(0.5)
	
	def receiving_HB(self):#$$$
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', 9090))

		def link(msg, addr):
			if msg == b'beat':
				if addr[0] not in self.list :
					self.update_new(addr[0])
					# t = threading.Thread(target=handler)
					# t.start()
					# handler()
					return
				self.update_new(addr[0])
				
		while True:
			msg, addr = sock.recvfrom(4)
			t = threading.Thread(target=link, args=(msg, addr))
			t.start()

	def sending_HB(self):#$$$
		sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		while True:
			time.sleep(0.2)
			for ip in host_list:
				sock.sendto(b'beat', (ip, 9090))

nodeList = NodeList()
nodeList.run()
while 1:
	print(nodeList)
	time.sleep(1)
