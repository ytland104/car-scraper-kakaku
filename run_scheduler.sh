#!/bin/bash
set -e
# cron では .zshrc が読まれないため、PATH を明示
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# === ここをあなたの環境に合わせて変更してください ===
PROJECT_DIR="/Users/yutaka/Documents/Myapp/car_scraper"
VENV_PYTHON="/Users/yutaka/myenv/venv/bin/python"

cd "$PROJECT_DIR" || exit 1

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# cron 実行かどうかログに残す（crontab で CRON_INVOKED=1 を付けて呼ぶと判別できる）
if [ -n "${CRON_INVOKED:-}" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CRON] run_scheduler.sh started (pid=$$)"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] run_scheduler.sh started (pid=$$)"
fi

# 第1引数があれば「選択していないメーカー」用の設定ファイルとして渡す（例: config/carmaker_selection_other.txt）
if [ -n "$1" ]; then
  if "$VENV_PYTHON" scheduled_scraper.py --carmaker-config "$1"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] run_scheduler.sh finished successfully (carmaker-config=$1)"
    exit 0
  else
    EXIT=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] run_scheduler.sh finished with exit code $EXIT"
    exit $EXIT
  fi
else
  if "$VENV_PYTHON" scheduled_scraper.py; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] run_scheduler.sh finished successfully"
    exit 0
  else
    EXIT=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] run_scheduler.sh finished with exit code $EXIT"
    exit $EXIT
  fi
fi
