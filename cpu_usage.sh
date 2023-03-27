#!/bin/bash
cpu_us=`top -bn 1 | grep 'Cpu(s)' | awk -F'[" "%]+' '{print $3}'`
cpu_sy=`top -bn 1 | grep 'Cpu(s)' | awk -F'[" "%]+' '{print $5}'`
cpu_sum=$(echo "$cpu_us+$cpu_sy"|bc)%
echo "CPU: $cpu_sum"
