#!/bin/bash

for i in {1..15}
do
        head -c 15728640 /dev/urandom >  "$i.txt"
done

