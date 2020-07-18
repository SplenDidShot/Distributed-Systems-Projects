package main

import (
	"fmt"
	"os/exec"
)

func print_list( list []string ){
	for _, element := range list{
		fmt.Print(element+"\n")
	}
}


func main() {
 
	var list = []string{  "172.22.154.135",
							"172.22.156.135",
							"172.22.152.140",                            
							"172.22.154.136",                            
							"172.22.156.136",                            
							"172.22.152.141",                            
							"172.22.154.137",                            
							"172.22.156.137",                            
							"172.22.152.142",                            
							"172.22.154.138"}
	print_list(list)
	exec.Command("clear")
	print_list(list)
}