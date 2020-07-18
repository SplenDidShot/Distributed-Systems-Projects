package main

import (
	"fmt"
	"time"
	"strconv"
	"sort"
)

func main() {
	self_ip := "172.22.156.136"
	member_list := make( map[string]string )
	member_list["172.22.154.135"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.156.135"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.152.140"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.154.136"] =  strconv.FormatInt(time.Now().Unix(), 10)
	time.Sleep(time.Duration(2)*time.Second)
	member_list["172.22.156.136"] =  strconv.FormatInt(time.Now().Unix(), 10)

	
	
	list := make([]string, 0, len(member_list))
	for key := range member_list {
		list = append(list, key)
	}
	sort.Strings(list)
	for i := 0; i < 4; i++{
		list = append(list, list[i])
	}
	
	num := -1
	for index, val := range list {
		 if val == self_ip {
			  num = index 
		 }
	}
	fmt.Println(list[num:num+4])
	
	
	
	for _, k := range list {
		fmt.Println(k, member_list[k])
	}
}