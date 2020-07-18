package main
import (
        "fmt"
        "net"
        "os/exec"
        "os"
        "strings"
)

func grep(parameter string, content string, path string,remoteAddr *net.UDPAddr){
        var result []byte
        var err error
        var cmd *exec.Cmd

        // Greping
        cmd = exec.Command("grep", parameter, content, path)
        if result, err = cmd.Output(); err != nil && result==nil{
                fmt.Println(err)
                os.Exit(1)
        }
        // Print result 
        fmt.Print(string(result))
        raddr := net.UDPAddr{
                IP:   remoteAddr.IP,
                Port: 4000,
        }

        // send result back
        conn, err := net.DialUDP("udp", nil, &raddr)
        if err != nil {
                println(err.Error())
                return
        }
        conn.Write(result)
        conn.Close()

}

func main() {
        // listening for request 
        listener, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4zero, Port: 3000})
        if err != nil {
                fmt.Println(err)
                return
        }

        // handling request
        fmt.Println("[INFO] Listening on Port 3000")
        data := make([]byte, 1024)
        for {
                n, remoteAddr, err := listener.ReadFromUDP(data)
                if err != nil {
                        fmt.Printf("[ERROR]] during read: %s\n", err)
                                }

                                fmt.Printf("[INFO] %s sends: %s\n", remoteAddr, data[:n])
                                fmt.Print(string(data))
                                command := strings.Split(string(data), " ")
                                if command[0] == "grep"{
                                    grep(command[1], command[2], command[3],remoteAddr)
                        }
    }
}