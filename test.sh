#!/bin/bash

# Create logs directory
mkdir -p logs

# First stop any running instances
pkill -f "python3 posting_system_final.py"

# Set posting time to 5 minutes from now
current_hour=$(date -v+5M +%H)
current_minute=$(date -v+5M +%M)

# Format time display
formatted_time=$(printf "%02d:%02d" $current_hour $current_minute)

echo "Setting post time to 5 minutes from now: $formatted_time"

# Use sed to replace posting time
sed -i '' "s/self.posting_hour = .*/self.posting_hour = $current_hour  # Test time/" posting_system_final.py
sed -i '' "s/self.posting_minute = .*/self.posting_minute = $current_minute  # Test time/" posting_system_final.py
sed -i '' "s/schedule.every().day.at(\".*\").do/schedule.every().day.at(\"$formatted_time\").do/" posting_system_final.py

# Start posting system and output to log file
cd "$(dirname "$0")"  # Switch to script directory

# Clean old log files
rm -f logs/twitter_bot.log
rm -f logs/ai_posts.log

# Use full path to run Python script
PYTHON_PATH=$(which python3)
SCRIPT_PATH="$PWD/posting_system_final.py"

echo "Starting test posting system..."
nohup $PYTHON_PATH $SCRIPT_PATH >> logs/twitter_bot.log 2>&1 &
PID=$!

# Wait a few seconds to ensure process starts
sleep 5

# Check if process started successfully
if ps -p $PID > /dev/null; then
    echo "Test posting system started successfully (PID: $PID)"
    echo "System will attempt to post in 5 minutes ($formatted_time)"
    echo "You can view the running logs with:"
    echo "tail -f logs/twitter_bot.log"
    
    # Show latest log content
    echo "Latest log content:"
    tail -n 10 logs/twitter_bot.log
else
    echo "Test posting system failed to start, check log file"
    cat logs/twitter_bot.log
fi 