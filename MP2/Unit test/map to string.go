package main

import (
	"fmt"
	"time"
	"strconv"
)

func map_to_string_parser( member_list map[string]string ) string{
	result := ""
	for key, val := range member_list{
		result += key + "," + val + ";"
	}
	return result
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
	
	fmt.Print( map_to_string_parser(member_list) )
}