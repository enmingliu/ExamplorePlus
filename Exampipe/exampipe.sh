#!/bin/bash

for ((size=0; size<=9000; size+=100)); do
    python3 exampipe.py "$size" 10
    sleep 1h
done
