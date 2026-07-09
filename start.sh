#!/bin/sh
# Forwardbot Management Script

case "$1" in
    start)
        echo "Starting forwardbot..."
        cd /root/forwardbot
        
        if [ -f bot.pid ]; then
            PID=$(cat bot.pid)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Bot is already running (PID: $PID)"
                exit 0
            fi
        fi
        
        # Run in a loop in the background and save PID of the loop
        (
            while true; do
                python3 -m forwardbot
                sleep 2
            done
        ) > bot.log 2>&1 &
        
        echo $! > bot.pid
        echo "Forwardbot started. PID: $(cat bot.pid)"
        echo "View logs: tail -f /root/forwardbot/bot.log"
        ;;
    stop)
        echo "Stopping forwardbot..."
        if [ -f bot.pid ]; then
            PID=$(cat bot.pid)
            kill $PID >/dev/null 2>&1
            rm -f bot.pid
        fi
        pkill -9 -f "python3.*forwardbot"
        echo "Forwardbot stopped."
        ;;
    restart)
        echo "Restarting forwardbot..."
        # Stop
        if [ -f bot.pid ]; then
            PID=$(cat bot.pid)
            kill $PID >/dev/null 2>&1
            rm -f bot.pid
        fi
        pkill -9 -f "python3.*forwardbot"
        sleep 2
        
        # Start
        (
            while true; do
                python3 -m forwardbot
                sleep 2
            done
        ) > bot.log 2>&1 &
        
        echo $! > bot.pid
        echo "Forwardbot restarted. PID: $(cat bot.pid)"
        ;;
    status)
        echo "Forwardbot status:"
        if [ -f bot.pid ]; then
            PID=$(cat bot.pid)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Running (Loop PID: $PID)"
                ps aux | grep "python3 -m forwardbot" | grep -v grep
                exit 0
            fi
        fi
        echo "Not running"
        ;;
    logs)
        tail -f /root/forwardbot/bot.log
        ;;
    *)
        echo "Starting forwardbot in foreground loop..."
        cd /root/forwardbot
        while true; do
            python3 -m forwardbot
            sleep 2
        done
        ;;
esac
