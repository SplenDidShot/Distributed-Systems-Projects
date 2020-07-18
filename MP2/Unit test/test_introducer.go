package main

import (
	"fmt"
	"net"
	"time"
	"strconv"
	"os/exec"
)


//sends update to the introducer every 1s
func send_to_introducer(self_ip string){
	for {
		time.Sleep( time.Duration(1)*time.Second )
		address := "172.22.154.138" //the tenth machine
		raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 8080,}
				
		conn, err := net.DialUDP("udp", nil, &raddr) 
		if err != nil { println(err.Error()); return; }
				
		data := []byte( self_ip + "," + strconv.FormatInt(time.Now().Unix(), 10) + ";" )
		conn.Write( data ) 
		conn.Close()
		fmt.Println(string(data))
	
	}
}

func listening_response(){
	listener, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4zero, Port: 4040})
	if err != nil { fmt.Println("[ERROR]", err); return; }
		
	data := make([]byte, 1024)
	for {
		n, remoteAddr, err := listener.ReadFromUDP(data)
		if err != nil { fmt.Printf("[ERROR]] during read: %s\n", err) }
		fmt.Printf("[INFO] %s sends: %s\n", remoteAddr, data[:n])
	}
}



func main(){

	cmd := exec.Command("hostname", "-i")
	result, _ := cmd.Output()

	self_ip := string(result[ 0:len(result)-1 ])
	fmt.Println(self_ip)


	go send_to_introducer(self_ip)

	go listening_response()

	for{
		time.Sleep( time.Duration(1)*time.Second )
	}
}