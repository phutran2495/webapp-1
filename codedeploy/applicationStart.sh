#!/bin/bash

sudo touch /home/ubuntu/csye6225.log
sudo chmod 666 /home/ubuntu/csye6225.log
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/ubuntu/amazon-cloudwatch-agent.json
nohup python3 /home/ubuntu/app/application/main.py > /dev/null 2> /dev/null < /dev/null &

