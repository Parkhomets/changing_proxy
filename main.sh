#!/bin/sh

service squid start
python3 torghost.py --start

while :
do
    python3 torghost.py --switch
done