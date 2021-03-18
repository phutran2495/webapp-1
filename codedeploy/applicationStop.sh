#!/bin/bash

sudo ps -ef | grep "python3 main.py" | awk '{print $2}' | xargs sudo kill
