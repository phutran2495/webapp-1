#!/bin/bash

export user
sudo /var/lib/cloud/instance/scripts/part-001
nohup python3 /home/ubuntu/app/application/main.py > /dev/null 2> /dev/null < /dev/null &

