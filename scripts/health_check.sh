#!/bin/bash
# Health Check Script for Car Scraper

echo "=== Car Scraper Health Check ==="
echo "Timestamp: $(date)"
echo

# Check if Python script exists
if [ -f "scheduled_scraper.py" ]; then
    echo "✓ Main script found"
else
    echo "✗ Main script not found"
    exit 1
fi

# Check configuration files
if [ -f "config/scheduler_config.yml" ]; then
    echo "✓ Scheduler configuration found"
else
    echo "✗ Scheduler configuration missing"
fi

# Check data file
if [ -f "allmaker_url1016.csv" ]; then
    echo "✓ Data file found"
else
    echo "✗ Data file missing"
fi

# Check directories
required_dirs=("logs" "output" "config")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ Directory exists: $dir"
    else
        echo "✗ Directory missing: $dir"
    fi
done

# Run Python health check
echo
echo "Running Python health check..."
python3 scheduled_scraper.py --health-check

echo
echo "=== Health Check Complete ==="
