package main

import(
	"fmt"
	"time"
)



func main() {
	begin := time.Now().Unix()
	for {
		now := time.Now().Unix()
		if( now - begin >= 1){
			begin = now
			fmt.Print(now, "\r")
		}
	}
	
}