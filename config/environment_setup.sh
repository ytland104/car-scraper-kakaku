#!/bin/bash
# Environment Setup Script for Car Scraper
# 車データスクレイピング環境変数設定スクリプト

# このスクリプトは実行せず、必要な環境変数を設定するための参考として使用してください
# source this file or copy the export commands to your shell profile

# Email notification settings (optional)
# メール通知設定（オプション）
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"  # Gmail App Passwordを使用

# Slack notification settings (optional)
# Slack通知設定（オプション）
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Discord notification settings (optional)
# Discord通知設定（オプション）
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"

# Database settings (if using database storage)
# データベース設定（データベース保存を使用する場合）
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="car_scraper"
export DB_USER="car_scraper_user"
export DB_PASSWORD="your-db-password"

# API keys (if needed for future integrations)
# APIキー（将来の統合で必要な場合）
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_CLOUD_API_KEY="your-google-cloud-api-key"

# Cloud storage settings (optional)
# クラウドストレージ設定（オプション）
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="ap-northeast-1"
export S3_BUCKET_NAME="car-scraper-data"

# Custom output directory (optional)
# カスタム出力ディレクトリ（オプション）
export CAR_SCRAPER_OUTPUT_DIR="/path/to/custom/output"

# Logging level override (optional)
# ログレベル上書き（オプション）
export CAR_SCRAPER_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR

# Rate limiting override (optional)
# レート制限上書き（オプション）
export CAR_SCRAPER_REQUESTS_PER_SECOND="0.5"

# Proxy settings (if needed)
# プロキシ設定（必要な場合）
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

echo "Environment variables template loaded."
echo "Please modify these values according to your setup and add them to your shell profile."
echo ""
echo "To add to your shell profile (choose one):"
echo "  # For bash users:"
echo "  echo 'export EMAIL_USERNAME=\"your-email@gmail.com\"' >> ~/.bashrc"
echo "  echo 'export EMAIL_PASSWORD=\"your-app-password\"' >> ~/.bashrc"
echo ""
echo "  # For zsh users:"
echo "  echo 'export EMAIL_USERNAME=\"your-email@gmail.com\"' >> ~/.zshrc" 
echo "  echo 'export EMAIL_PASSWORD=\"your-app-password\"' >> ~/.zshrc"
echo ""
echo "Remember to reload your shell or run 'source ~/.bashrc' (or ~/.zshrc) after making changes." 