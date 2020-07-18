#!/usr/bin/env python3
import os
import sys, random

def write_random_lowercase(n):
	min_lc = ord(b'a')
	len_lc = 26
	
	ba = bytearray(os.urandom(n))
	for i, b in enumerate(ba):
		number =  int(random.random()*999)
		if (number % 5 == 0):
			ba[i] = 32
		else:
			ba[i] = min_lc + b % len_lc # convert 0..255 to 97..122
	return ba

def main():
	secret = ["", "secrethahaha", "onlyfew", "rarestring", "treasure"]
	
	for x in range(1,11):
		f = open("test_log" + str(x), "w+")
		for i in range(0, 55000):
			rand = random.random()
			if rand<=0.005 and x==3: 
				j=4
			elif rand<=0.01 and x%2==0: 
				j=3
			elif rand<=0.02 and x%3==1: 
				j=2
			elif rand<=0.04: 
				j=1
			else: j = 0
			f.write(write_random_lowercase(int(500+random.random()*500)).decode() + secret[j]+ write_random_lowercase(500).decode()+"\n")
		f.close()

main()