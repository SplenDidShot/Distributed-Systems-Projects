package main

import(
	"fmt"
	"strings"
	"time"
	"strconv"
)



func message_parser( msg string ) [][]string {
	msg_list := strings.Split(msg, ";")
	var result [][]string
	for _,item := range msg_list {
		if strings.Contains(item, ","){
			result = append( result, strings.Split(item, ",") )
		}
	}
	return result
}

func update_member( member_list map[string]string, new_info_list [][]string ){
	
	for _, iterm := range new_info_list{
			member_list[ iterm[0] ] = iterm[1]
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
	
	fmt.Println(member_list["172.22.154.140"])
	fmt.Println(member_list)
	
	time.Sleep(time.Duration(2)*time.Second)
	msg := "172.22.154.136,"+ strconv.FormatInt(time.Now().Unix(), 10) +";"+ "172.22.154.136,"+ strconv.FormatInt(time.Now().Unix(), 10) + ";"

//	fmt.Println(msg)
	
	
	result := message_parser(msg)
	fmt.Println(result)
	
	update_member(member_list, result)
	fmt.Println(member_list)
	
}