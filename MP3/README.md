To test, need to have FTP on the sdfs folder and operate on a port other than 6666 (because i am using it), and modify the port number on the code

Filegen.sh generate 15 15MB files 







To run, simply setup the FTP by 

```
python3 -m pyftpdlib -w -u 428 -P zheshiwomenMP3demima -p port_num -d $(sdfs_dir)
```

and then do

```
python3 mp3.py 
```

Be sure to modify sdfs direcotory in mp3.py on the very last line



checkout the shell function to see all the command avalible 

```
ip: self ip

f: print file list

n: print node list

p /home/zitongc2/2.txt 2.txt: put file 

g 2.txt /home/zitongc2/2.txt: get file 

d 2.txt: delete file

l 2.txt: list all machine have 2.txt

s: all the file on local machine 

q: quit 

testrun: put 15 file into sdfs (name 1.txt .....)

check: list number of replication of all file 

```

