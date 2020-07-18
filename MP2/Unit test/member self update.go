package main

import(
	"fmt"
//	"strings"
	"time"
	"strconv"
)


func member_self_update( member_list map[string]string , self_ip string){
	for {
		time.Sleep( time.Duration(1)*time.Second )
		now := int(time.Now().Unix())

		for address, timestamp := range member_list{
			if address == self_ip {
				member_list[address] = strconv.FormatInt(time.Now().Unix(), 10)
			}else{
				time, _ := strconv.Atoi(timestamp)
				if (now - time) > 5{
					delete(member_list, address)
				}
			}
		}
		fmt.Println(member_list)
	}
}

func main() {
	member_list := make( map[string]string )
	member_list["172.22.154.135"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.136"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.137"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.138"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.139"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.140"] =  strconv.FormatInt(time.Now().Unix(), 10)
	
	fmt.Println("-----------------")
	member_self_update(member_list, "172.22.154.137")
}