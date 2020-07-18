package main

import (
	"fmt"
	"time"
)

func sth(){
	for{
		fmt.Print("kajsdbv,adb  ")
	}
}

func main() {
	go sth()
	time.Sleep( time.Duration(1)*time.Second )
	close(sth )
}