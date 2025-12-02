#!/bin/bash

# Power Monitoring Script for Car Scraper
# PCの電源状態を監視・確認するためのスクリプト

LOG_FILE="/Users/yutaka/car_scraper_link/logs/power_status.log"

echo "=== Power Status Check - $(date) ===" >> "$LOG_FILE"

# System uptime
echo "System Uptime:" >> "$LOG_FILE"
uptime >> "$LOG_FILE"

# Last boot time
echo "Last Boot Time:" >> "$LOG_FILE"
who -b >> "$LOG_FILE"

# Recent reboots
echo "Recent Reboots:" >> "$LOG_FILE"
last | grep reboot | head -5 >> "$LOG_FILE"

# Power management settings
echo "Power Management Settings:" >> "$LOG_FILE"
pmset -g >> "$LOG_FILE"

# Scheduled power events
echo "Scheduled Power Events:" >> "$LOG_FILE"
pmset -g sched >> "$LOG_FILE"

echo "=======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Also display to console
echo "✅ Power status logged to: $LOG_FILE"
echo "📊 Recent status:"
echo "- Uptime: $(uptime | cut -d',' -f1 | cut -d' ' -f4-)"
echo "- Last boot: $(who -b | cut -d' ' -f12-)"
echo "- Sleep setting: $(pmset -g | grep -E '^\s*sleep' | head -1 | tr -s ' ')" 