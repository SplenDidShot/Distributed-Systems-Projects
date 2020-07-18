package main
 
import (
	"net"
	"fmt"
	"bufio"
    "os"
    "strconv"
    "time"
)

func send_request(command string){
    // list of IP address of all the avalible machine
    var list = [10]string{  "172.22.154.135",
                            "172.22.156.135",
                            "172.22.152.140",                            
                            "172.22.154.136",                            
                            "172.22.156.136",                            
                            "172.22.152.141",                            
                            "172.22.154.137",                            
                            "172.22.156.137",                            
                            "172.22.152.142",                            
                            "172.22.154.138"}

    for index, element := range list {              //for loop to request all the machine 
        raddr := net.UDPAddr{                       //address and port specification 
            IP:   net.ParseIP(element),
            Port: 3000,
        }
        conn, err := net.DialUDP("udp", nil, &raddr) // connecting and error handling
        if err != nil {
                println(err.Error())
                return
        }

        // print result
        fmt.Print(command)
        conn.Write( []byte(command[0:len(command)-1] + " vm" + strconv.Itoa(index+1) + ".log ") )
        conn.Close()
    }
}

func get_result(){
    
    // listening for response
    listener, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4zero, Port: 4000})
    if err != nil {
            fmt.Println(err)
            return
    }
    
    // print response 
    fmt.Println("[INFO] responce from device")
    data := make([]byte, 1024)
    for i:=0; i<10; i++ {
        n, remoteAddr, err := listener.ReadFromUDP(data)
        if err != nil {
                fmt.Printf("[ERROR]] during read: %s\n", err)
        }
        fmt.Printf("[INFO] %s sends: %s\n", remoteAddr, data[:n])
    }
    

}

func main() {

    // getting input
	inputReader := bufio.NewReader(os.Stdin)
    fmt.Println("Please enter the command that you want to execute:")
    command, err := inputReader.ReadString('\n')
    if err != nil {
        fmt.Println("There were errors reading, exiting program.")
        return
	}

    // sending request
    start := time.Now()
    send_request(command)

	// recieving responce 
    get_result()

    //time measuring
    passed := time.Since(start)
    fmt.Println("[INFO]time used: ", passed)

}

