#!/bin/bash
# Backup Script for Car Scraper Data

BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
echo "Creating backup in: $BACKUP_DIR"

mkdir -p "$BACKUP_DIR"

# Backup configuration files
if [ -d "config" ]; then
    cp -r config "$BACKUP_DIR/"
    echo "✓ Configuration backed up"
fi

# Backup recent output files (last 30 days)
if [ -d "output" ]; then
    mkdir -p "$BACKUP_DIR/output"
    find output -name "*.csv" -mtime -30 -exec cp {} "$BACKUP_DIR/output/" \;
    echo "✓ Recent output files backed up"
fi

# Backup recent logs (last 7 days)
if [ -d "logs" ]; then
    mkdir -p "$BACKUP_DIR/logs"
    find logs -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/logs/" \;
    echo "✓ Recent log files backed up"
fi

echo "Backup completed: $BACKUP_DIR"
echo "Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
