#!/bin/bash

# 检查发推系统是否已经在运行
if pgrep -f "python3 posting_system_final.py" > /dev/null; then
    echo "Posting system is already running"
else
    # 启动发推系统
    nohup python3 posting_system_final.py > twitter_bot.log 2>&1 &
    echo "Posting system started. Check twitter_bot.log for details"
fi

# 检查互动系统是否已经在运行
if pgrep -f "python3 engagement_system.py" > /dev/null; then
    echo "Engagement system is already running"
else
    # 启动互动系统
    nohup python3 engagement_system.py > engagement.log 2>&1 &
    echo "Engagement system started. Check engagement.log for details"
fi
