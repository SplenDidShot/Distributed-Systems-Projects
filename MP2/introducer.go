package main

import(
	"fmt"
	"net"
	"strings"
	"sync"
	"time"
	"strconv"
)
// the following is a thread safe data structure
type SafeMap struct {
	mux 	sync.Mutex
	list   	map[string]string
}

// this function serialized the member ship list
func map_to_string_parser( member_list *SafeMap ) string{
	result := ""
	member_list.mux.Lock()
	for key, val := range member_list.list{
		result += key + "," + val + ";"
	}
	member_list.mux.Unlock()
	return result
}

// this function updates the member ship according to the input string
func update_member_list( member_list *SafeMap, msg string ) {

	// parsing the input string
	msg_list := strings.Split(msg, ";")
	var result [][]string
	for _,item := range msg_list {
		if strings.Contains(item, ","){
			result = append( result, strings.Split(item, ",") )
		}
	}

	// updating the member ship
	member_list.mux.Lock()
	for _, iterm := range result{
		prev_time, _ :=  strconv.ParseInt( iterm[1] , 10, 64)
		new_time, _  := strconv.ParseInt(member_list.list[ iterm[0] ], 10, 64)
		if(  prev_time  <  new_time || new_time == 0 ){
			member_list.list[ iterm[0] ] = iterm[1]
		}
	}
	member_list.mux.Unlock()
}

// this function send a member ship list to the designated machine 
func send_member_list( member_list *SafeMap , address []byte ){
             
	raddr := net.UDPAddr{ IP: address, Port: 4040, }
	conn, err := net.DialUDP("udp", nil, &raddr) 
	if err != nil { println(err.Error()); return;}

	conn.Write( []byte( map_to_string_parser(member_list) ) )
	conn.Close()

}

// this function listens on the network interface for updates from pther machine
func listen_new_machine(member_list *SafeMap){

	// defining sockets 
	listener, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4zero, Port: 8080})
	if err != nil { fmt.Println(err); return;}
	
	// defining buffer
	data := make([]byte, 1024)

	for {
		// recieving data 
		n, remoteAddr, err := listener.ReadFromUDP(data)
		if err != nil {	fmt.Printf("[ERROR]] during read: %s\n", err) }
		fmt.Printf("[INFO] %s sends: %s\n", remoteAddr, data[:n])

		// updates the member ship
		update_member_list( member_list, string(data[:n]) )

		// sends a copy of the updated member ship to the newly joined machine
		send_member_list(member_list, remoteAddr.IP)
	}
}

//---------------------------------------------------------------------------------------------
// this function updates the membership list base on time (determined whether a member is timeouted)
func member_self_update( member_list *SafeMap ){

	for {
		time.Sleep( time.Duration(1)*time.Second )
		now := int(time.Now().Unix())

		// updating
		member_list.mux.Lock()
		for address, timestamp := range member_list.list{
			
			time, _ := strconv.Atoi(timestamp)
			if (now - time) > 4{
				delete(member_list.list, address)
			}
		}
		member_list.mux.Unlock()
	}
}

//-------------------------------------------------------------------
// this function prints the member ship list every 1 second
func print_list( member_list *SafeMap ){
	for{
		time.Sleep( time.Duration(1)*time.Second )
		fmt.Println("------------------------- Member List Update -------------------------")
		member_list.mux.Lock()
		for key, val := range member_list.list{
			fmt.Println(key + ": "+ val )
		}
		member_list.mux.Unlock()
		fmt.Println("----------------------------------------------------------------------")
	}
}
//-------------------------------------------------------------------

func main(){
	member_list := SafeMap{list: make(map[string]string)}

	// get heart beat from other machine
	go listen_new_machine(&member_list)

	go member_self_update(&member_list)

	go print_list(&member_list)

	for{ 
		time.Sleep( time.Duration(1)*time.Second )
	}

}