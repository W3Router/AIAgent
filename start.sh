#!/bin/bash

# 创建日志目录
mkdir -p logs

# 检查发推系统是否已经在运行
if pgrep -f "python3 posting_system_final.py" > /dev/null; then
    echo "发推系统已经在运行中"
else
    # 启动发推系统并将日志输出到文件
    cd "$(dirname "$0")"  # 切换到脚本所在目录
    
    # 使用完整路径运行 Python 脚本
    PYTHON_PATH=$(which python3)
    SCRIPT_PATH="$PWD/posting_system_final.py"
    
    echo "启动发推系统..."
    nohup $PYTHON_PATH $SCRIPT_PATH >> logs/twitter_bot.log 2>&1 &
    PID=$!
    
    # 等待几秒确保进程启动
    sleep 5
    
    # 检查进程是否成功启动
    if ps -p $PID > /dev/null; then
        echo "发推系统已成功启动 (PID: $PID)"
        echo "可以通过以下命令查看运行日志："
        echo "tail -f logs/twitter_bot.log"
        
        # 显示最新的日志内容
        echo "最新日志内容："
        tail -n 5 logs/twitter_bot.log
    else
        echo "发推系统启动失败，请检查日志文件"
        cat logs/twitter_bot.log
    fi
fi

# 检查互动系统是否已经在运行
if pgrep -f "python3 engagement_system.py" > /dev/null; then
    echo "Engagement system is already running"
else
    # 启动互动系统
    nohup python3 engagement_system.py > engagement.log 2>&1 &
    echo "Engagement system started. Check engagement.log for details"
fi
