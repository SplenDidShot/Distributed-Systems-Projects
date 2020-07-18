# Group Membership Service

This is our MP2 (Group 41), a group membership service with hearbeat style failure detection

## Execution

Run "go run introducer.go" on VM #10 before deploying other machines.
Run "go run machine.go" to ready the VM's for the group membership service.

## Usage

Joining:  
	A VM can join the group by running mahine.go, and then typing “j\n” at the prompt. 
	It will send a join request to the introducer, which will notify other nodes in the group. 
	Note that the introducer has to be up before this can happen.
	
Leaving:  
	A VM can leave the group by typing “q\n” at the prompt after it has joined the group. 
	It will notify its heartbeat receivers about leaving the group, and they will remove the leaving node from their membership lists and pass down the information.
	
Failure:  
	A VM will be marked as failed if any of its heartbeat receivers do not receive a new heartbeat within 4 seconds from the last heartbeat. 
	Upon failure, a node will be treated the same way as when it leaves, but the log messages will be different. 
	We currently set our heartbeat interval at 0.5 second.
	
Displaying membership list & logging:  
	A VM can display its up-to-date membership list at runtime by typing “l\n” after it has joined the group. 
	All the churn messages will be logged in the file churn_log.txt.  
	Whenever a machine rejoins the group after a fail/leave, its previous log file will be overwritten.
