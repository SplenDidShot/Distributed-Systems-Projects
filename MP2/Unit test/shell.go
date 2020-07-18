package main
import (
	"fmt"
	"bufio"
	"os"
	"strings"
)


func machine_exit( member_list *SafeMap, self_ip string ){

	for _, address := range HB_list(member_list, self_ip) {               
		raddr := net.UDPAddr{ IP: net.ParseIP(address), Port: 4040,}
				
		conn, err := net.DialUDP("udp", nil, &raddr) 
		if err != nil { println(err.Error()); return;}

		// member_self_update(member_list, self_ip)
		conn.Write( []byte( self_ip+","+"0" ) )
		conn.Close()
	}

}


func main() {
	
	for{
		var inputReader *bufio.Reader
		var input string

		
		inputReader = bufio.NewReader(os.Stdin)
		fmt.Println("Please enter some input: ")
		input, _ = inputReader.ReadString('\n')
		
		if( strings.TrimRight(input, "\n") == "q"  ){
			machine_exit()
			os.Exit(0)
		}
		if( strings.TrimRight(input, "\n") == "l"  ){
			fmt.Print("member list")
		}
		
	}


}