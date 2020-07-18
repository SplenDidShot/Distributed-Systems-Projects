package main

import (
	"fmt"
	"strings"
	"time"
	"strconv"
	"net"
	"sort"
	"os/exec"
	"sync"
	"os"
	"bufio"
)

// the following is a thread safe data structure
type SafeMap struct {
	mux 	sync.Mutex
	list   	map[string]string
	prev_list map[string]string
	seen map[string]string
	left map[string]int
}

//-------------------------------------------------------------------
// the following set of function handles logging
func print_list( member_list *SafeMap ){
	for{
		time.Sleep( time.Duration(2)*time.Second )
		member_list.mux.Lock()
		
		if len(member_list.prev_list) < len(member_list.list){
			fmt.Println("------------------------- Member List Update -------------------------")
			for key, val := range member_list.list{
				if _, ok := member_list.prev_list[key]; ok==false {
					log_msg:=""
					if  _, in := member_list.seen[key]; in==false {
						log_msg = key + " has joined the group @ " + val						
						member_list.seen[key] = "-1"
					}else{
						log_msg = key + "-" + val + " has joined the group @ " + val
						member_list.seen[key] = val
					}
					fmt.Println(log_msg)
					write_to_log(log_msg)
					member_list.prev_list[key] = val
					member_list.left[key] = 0
				}
			} 
			fmt.Println("----------------------------------------------------------------------")
		} else if (len(member_list.prev_list) > len(member_list.list)){
			for key, _ := range member_list.prev_list{
				if _, ok := member_list.list[key]; ok==false {
	    			delete(member_list.prev_list, key)
	    			// delete(member_list.left, key)
				}
			} 
		}
		member_list.mux.Unlock()
	}
}

//-------------------------------------------------------------------
// the following function listens for update from other machine and updates member ship accordingly 

// this function update the member list according to the recieved string
func update_member( member_list *SafeMap, msg string ) {

	msg_list := strings.Split(msg, ";")
	var result [][]string
	for _,item := range msg_list {
		if strings.Contains(item, ","){
			result = append( result, strings.Split(item, ",") )
		}
	}

	member_list.mux.Lock()
	for _, iterm := range result{
		new_time, _ :=  strconv.ParseInt( iterm[1] , 10, 64)
		prev_time, _  := strconv.ParseInt(member_list.list[ iterm[0] ], 10, 64)
		//this appends timestamp in id for reincarnated nodes
		//if not seen, add to seen list
		//if seen, but key not in dictionary, it has rejoined: append timestamp to id
		_, in := member_list.list[iterm[0]]

		if(prev_time < new_time){
			member_list.list[iterm[0]] = iterm[1]
		}else if new_time == 0 && in==true{
			log_msg := "" 
			fmt.Println("------------------------- Member List Update -------------------------")
			if member_list.seen[iterm[0]] == "-1"{
				log_msg = iterm[0] + " has left the group @ " + strconv.FormatInt(prev_time, 10)
			} else {
				log_msg = iterm[0] + "-" + member_list.seen[iterm[0]] + " has left the group @ " + strconv.FormatInt(prev_time, 10)
			}
			fmt.Println(log_msg)
			fmt.Println("----------------------------------------------------------------------")		
			write_to_log(log_msg)
			member_list.left[iterm[0]] = 1
			delete(member_list.list, iterm[0])
		}
	}
	
	member_list.mux.Unlock()
}


// constantly listen for message and update the member list
func listen_update( member_list *SafeMap ) {

	listener, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4zero, Port: 4040})
	if err != nil { fmt.Println("[ERROR]", err); return; }
		
	data := make([]byte, 1024)
	for {
		n, _, err := listener.ReadFromUDP(data)
		if err != nil { fmt.Printf("[ERROR]] during read: %s\n", err) }
		update_member(member_list, string( data[:n] ))
	}
}



//-------------------------------------------------------------------
// the following functions orgnize the membership list and sends it to other machine

func map_to_string_parser( member_list *SafeMap ) string{
	result := ""

	member_list.mux.Lock()
	for key, val := range member_list.list{
		result += key + "," + val + ";"
	}
	member_list.mux.Unlock()
	return result
}

func indexOf(element string, data []string) (int) {
	for k, v := range data {
		 if element == v {
			  return k
		 }
	}
	return -1    //not found.
}

// this function returns a heart beat list
func HB_list(member_list *SafeMap, self_ip string) []string{

	list := make([]string, 0, len(member_list.list))
	member_list.mux.Lock()
	for key := range member_list.list {
		list = append(list, key)
	}
	member_list.mux.Unlock()

	if len(list) <= 5 {
		return list
	}else{

		sort.Strings(list)
		for i := 0; i <= 4; i++{
			list = append(list, list[i])
		}
		
		num := indexOf(self_ip, list)
		if(num == -1){ fmt.Println("[ERROR] self not exit in member list") }
		return list[num:num+4]
	}
	
}


// send one update msg in 1 second 
func send_update( member_list *SafeMap, self_ip string ){
	for {
		time.Sleep(time.Millisecond * 500)
			for _, address := range HB_list(member_list, self_ip) {               
				raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 4040,}
				
				conn, err := net.DialUDP("udp", nil, &raddr) 
				if err != nil { println(err.Error()); return;}

				conn.Write( []byte( map_to_string_parser(member_list) ) )
				conn.Close()
			}
	}
			
}
//---------------------------------------------------------------------
// the following function updates the member ship base on time

func member_self_update( member_list *SafeMap , self_ip string){

	for {
		time.Sleep(time.Millisecond * 200)

		now := int(time.Now().Unix())
		member_list.mux.Lock()
		for address, timestamp := range member_list.list{
			if address == self_ip {
				member_list.list[address] = strconv.FormatInt(time.Now().Unix(), 10)
			}else{
				time, _ := strconv.Atoi(timestamp)
				status, ok := member_list.left[address]
				if (now - time) > 4 && ok==true && status==0{
					log_msg := ""
					fmt.Println("------------------------- Member List Update -------------------------")
					if member_list.seen[address] == "-1"{
						log_msg = address + " has terminated unexpectedly @ " + member_list.list[address]
					} else if _, in:=member_list.seen[address]; in==true{
						log_msg = address + "-" + member_list.seen[address] + " has terminated unexpectedly @ " + member_list.list[address]
					}
					fmt.Println(log_msg)					
					fmt.Println("----------------------------------------------------------------------")
					write_to_log(log_msg)
					member_list.left[address] = 1
					delete(member_list.list, address)	
				}
			}
		}
		member_list.mux.Unlock()
	}

}

//---------------------------------------------------------------------
//the following function sends heartbeat to the introducer
func send_to_introducer(self_ip string){
	for {
		time.Sleep(time.Millisecond * 500)
		address := "172.22.154.138" //the tenth machine
		raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 8080,}
				
		conn, err := net.DialUDP("udp", nil, &raddr) 
		if err != nil { println(err.Error()); return; }
				
		conn.Write( []byte( self_ip + "," + strconv.FormatInt(time.Now().Unix(), 10) + ";" ) ) 
		conn.Close()
	
	}
}

//-------------------------------------------------------------------
// the folowing are helper funciton
func machine_exit( member_list *SafeMap, self_ip string ){

	for _, address := range HB_list(member_list, self_ip) {               
		raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 4040,}
				
		conn, err := net.DialUDP("udp", nil, &raddr) 
		if err != nil { println(err.Error()); return;}

		// member_self_update(member_list, self_ip)
		conn.Write( []byte( self_ip+","+"0"+";" ) )
		conn.Close()
	}

	address := "172.22.154.138" //the tenth machine
	raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 8080,}
			
	conn, err := net.DialUDP("udp", nil, &raddr) 
	if err != nil { println(err.Error()); return; }
			
	conn.Write( []byte( self_ip + "," + "0;" ) ) 
	conn.Close()

}
func print_list_to_screen( member_list *SafeMap ){

	fmt.Println("------------------------- Member List Update -------------------------")
	member_list.mux.Lock()
	for key, val := range member_list.list{
		if str, in := member_list.seen[key]; in==false || str=="-1"{
				fmt.Println(key + ": "+ val )
			}else {
				fmt.Println(key+"-"+str+": "+val)
			}
	}
	member_list.mux.Unlock()
	fmt.Println("----------------------------------------------------------------------")	
}

func write_to_log(msg string){
	f, err := os.OpenFile("churn_log.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()
    if err != nil {
        panic(err)
    }
    if _, err := f.Write([]byte(msg + "\n")); err != nil {
        panic(err)
    }
}

//-------------------------------------------------------------------
func main(){
	member_list := SafeMap{list: make(map[string]string), 
						   prev_list: make(map[string]string), 
						   seen: make(map[string]string),
						   left: make(map[string]int)}
	
	cmd := exec.Command("hostname", "-i")
	result, _ := cmd.Output()

	self_ip := string(result[ 0:len(result)-1 ])
	fmt.Println(self_ip)

	f, err := os.Create("churn_log.txt")
	if err!=nil{
		panic(err)
	}
	f.Close()
		

	for{
		var inputReader *bufio.Reader
		var input string

		
		inputReader = bufio.NewReader(os.Stdin)
		fmt.Println("Please enter some input: ")
		input, _ = inputReader.ReadString('\n')
		
		if( strings.TrimRight(input, "\n") == "j" ){
			// send heartbeat to introducer 
			go send_to_introducer( self_ip )

			// listen for member list update 
			go listen_update( &member_list )

			go member_self_update(&member_list, self_ip)

			// send heart beat to other machine
			go send_update( &member_list, self_ip)

			go print_list(&member_list)

		}
		if( strings.TrimRight(input, "\n") == "q"  ){
			machine_exit(&member_list, self_ip)
			os.Exit(0)
		}
		if( strings.TrimRight(input, "\n") == "l"  ){
			print_list_to_screen(&member_list)
		}
		if( strings.TrimRight(input, "\n") == "ip" ){
			fmt.Println(self_ip)
		}
		
	}
}