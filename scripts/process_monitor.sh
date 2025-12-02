#!/bin/bash

# Process Monitor Script for Car Scraper
# 実行中プロセスの監視スクリプト

PID=${1:-60007}  # デフォルトPID、引数で変更可能
LOG_FILE="logs/cron.log"

echo "🔍 Car Scraper Process Monitor"
echo "=============================="
echo "Monitoring PID: $PID"
echo "Log file: $LOG_FILE"
echo ""

# プロセス存在確認
if ! kill -0 $PID 2>/dev/null; then
    echo "❌ Process $PID not found or already completed"
    exit 1
fi

echo "✅ Process is running"
echo ""

# 基本情報表示
echo "📊 Process Information:"
ps -p $PID -o pid,etime,pcpu,pmem,stat,wchan
echo ""

# ログ情報
echo "📝 Log Information:"
echo "- Last modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" $LOG_FILE)"
echo "- Current time:  $(date "+%Y-%m-%d %H:%M:%S")"
echo "- File size:     $(ls -lh $LOG_FILE | awk '{print $5}')"
echo ""

# 最新ログ行
echo "📋 Latest Log Entries:"
tail -5 $LOG_FILE
echo ""

# 時間経過チェック
LAST_MOD=$(stat -f "%m" $LOG_FILE)
CURRENT_TIME=$(date +%s)
DIFF=$((CURRENT_TIME - LAST_MOD))

echo "⏱️  Time Analysis:"
echo "- Time since last log update: ${DIFF} seconds"

if [ $DIFF -gt 300 ]; then  # 5分以上
    echo "⚠️  WARNING: No log update for over 5 minutes"
    echo ""
    echo "💡 Recommended Actions:"
    echo "1. Wait a bit longer (network delays are common)"
    echo "2. Check if process is stuck: kill -USR1 $PID (if supported)"
    echo "3. Graceful termination: kill -TERM $PID"
    echo "4. Force termination: kill -KILL $PID (last resort)"
elif [ $DIFF -gt 180 ]; then  # 3分以上
    echo "⚠️  CAUTION: No log update for over 3 minutes"
    echo "Process may be processing a difficult URL"
else
    echo "✅ Recent activity detected"
fi

echo ""
echo "🔄 To continue monitoring: watch -n 30 '$0 $PID'" 