#!/bin/bash

# Create logs directory
mkdir -p logs

# Check if posting system is already running
if pgrep -f "python3 posting_system_final.py" > /dev/null; then
    echo "Posting system is already running"
else
    # Start posting system and redirect logs to file
    cd "$(dirname "$0")"  # Change to script directory
    
    echo "Starting posting system..."
    nohup python3 "./posting_system_final.py" >> "./logs/twitter_bot.log" 2>&1 &
    PID=$!
    
    # Wait a few seconds to ensure process starts
    sleep 5
    
    # Check if process started successfully
    if ps -p $PID > /dev/null; then
        echo "Posting system started successfully (PID: $PID)"
        echo "You can view the logs using:"
        echo "tail -f logs/twitter_bot.log"
        
        # Show latest log entries
        echo "Latest log entries:"
        tail -n 5 logs/twitter_bot.log
    else
        echo "Failed to start posting system, please check logs"
        cat logs/twitter_bot.log
    fi
fi
