#!/bin/bash

# Cron test script to verify cron is working
# This script will be run by cron to test if cron execution works properly

echo "=== CRON TEST EXECUTION ===" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
date >> /Users/yutaka/car_scraper_link/logs/cron_test.log
echo "Current directory: $(pwd)" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
echo "User: $(whoami)" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
echo "PATH: $PATH" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
echo "Python version:" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
/Users/yutaka/.pyenv/shims/python3 --version >> /Users/yutaka/car_scraper_link/logs/cron_test.log 2>&1
echo "Directory contents:" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
ls -la /Users/yutaka/car_scraper_link/scheduled_scraper.py >> /Users/yutaka/car_scraper_link/logs/cron_test.log 2>&1
echo "=========================" >> /Users/yutaka/car_scraper_link/logs/cron_test.log
echo "" >> /Users/yutaka/car_scraper_link/logs/cron_test.log 