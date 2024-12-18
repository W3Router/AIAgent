#!/bin/bash

# 查找并终止发推系统进程
posting_pid=$(pgrep -f "python3 posting_system.py")
if [ -z "$posting_pid" ]; then
    echo "Posting system is not running"
else
    kill $posting_pid
    echo "Posting system stopped"
fi

# 查找并终止互动系统进程
engagement_pid=$(pgrep -f "python3 engagement_system.py")
if [ -z "$engagement_pid" ]; then
    echo "Engagement system is not running"
else
    kill $engagement_pid
    echo "Engagement system stopped"
fi
