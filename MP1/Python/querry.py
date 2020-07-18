import time, paramiko, multiprocessing


def sending_command( i , mode ,content):
    address = "fa19-cs425-g41-" + "{:0>2d}".format(i) + ".cs.illinois.edu"
    pkey = paramiko.RSAKey.from_private_key_file('id_rsa')
    trans = paramiko.Transport((address, 22))
    trans.connect(username='zitongc2', pkey=pkey)
    
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    # stdin, stdout, stderr = ssh.exec_command('grep -ac html ' + 'vm'+ str(i) +'.log ')
    if (mode == "E"): 
        stdin, stdout, stderr = ssh.exec_command('grep -acE '+ content + ' vm'+str(i)+'.log')
    if (mode == "ac"):
        stdin, stdout, stderr = ssh.exec_command('grep -ac '+ content + ' vm'+str(i)+'.log')
	
	
    print("[INFO] ", address, ": ", stdout.read().decode())
    trans.close()

	

def main():
    mode = input("input the mode:\n")
    content = input("input the content:\n")
    plist = [ multiprocessing.Process( target=sending_command, args=( i , mode,content,  ) ) for i in range (1,11) ]
    for process in plist:
        process.start()
	
    for process in plist:
        process.join()
		
		
main()