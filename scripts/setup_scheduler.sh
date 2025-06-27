#!/bin/bash
# Car Scraper Scheduler Setup Script
# 車データスクレイピング定期実行のセットアップスクリプト

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_info "Python version: $PYTHON_VERSION"
        
        # Check if version is 3.12 or higher
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 12) else 1)'; then
            print_success "Python version is compatible"
        else
            print_warning "Python 3.12+ recommended, but continuing with $PYTHON_VERSION"
        fi
    else
        print_error "Python 3 not found. Please install Python 3.12+"
        exit 1
    fi
}

# Function to create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    directories=(
        "config"
        "logs"
        "output/current"
        "output/archive"
        "output/reports"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_info "Directory already exists: $dir"
        fi
    done
}

# Function to install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        
        # Additional dependencies for scheduled execution
        python3 -m pip install pyyaml psutil
        
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found. Installing basic dependencies..."
        python3 -m pip install --upgrade pip
        python3 -m pip install requests pandas beautifulsoup4 scikit-learn tqdm retry mojimoji numpy pyyaml psutil
        print_success "Basic dependencies installed"
    fi
}

# Function to create configuration files
create_config_files() {
    print_info "Creating configuration files..."
    
    # Scheduler configuration
    cat > config/scheduler_config.yml << 'EOF'
# Car Scraper Scheduler Configuration
# 車データスクレイピングスケジューラー設定

scheduler:
  execution_mode: "auto"          # auto, manual, test
  target_carmakers: "config"      # config, all, interactive
  max_execution_time: 14400       # 4時間（秒）
  retry_attempts: 3
  retry_delay: 300                # 5分（秒）

data_management:
  output_dir: "output"
  output_retention_days: 90       # 3ヶ月
  log_retention_days: 30          # 1ヶ月
  backup_enabled: true
  backup_frequency: "weekly"      # daily, weekly, monthly

rate_limiting:
  requests_per_second: 0.5        # サイトに負荷をかけないため
  pages_per_batch: 100
  batch_delay: 60                 # 秒

notifications:
  enabled: true
  email_alerts: false             # メール設定後にtrueに変更
  success_notification: false
  error_notification: true
  completion_summary: true

monitoring:
  max_error_rate: 10              # パーセント
  min_success_rate: 90            # パーセント
  max_execution_time: 14400       # 4時間（秒）
  disk_space_threshold: 10        # GB

logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR
  max_file_size: "10MB"
  backup_count: 5
EOF
    
    # Notification configuration template
    cat > config/notification_config.yml.template << 'EOF'
# Notification Configuration Template
# 通知設定テンプレート
# 実際の設定を行う場合は、このファイルをnotification_config.ymlにコピーして編集してください

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  username: "${EMAIL_USERNAME}"      # 環境変数から取得
  password: "${EMAIL_PASSWORD}"      # 環境変数から取得
  from_address: "car-scraper@yourdomain.com"
  to_addresses:
    - "admin@yourdomain.com"
    - "analyst@yourdomain.com"

alerts:
  success_notification: false
  error_notification: true
  completion_summary: true
  data_quality_alerts: true

thresholds:
  max_error_rate: 10              # パーセント
  min_success_rate: 90            # パーセント
  max_execution_time: 14400       # 秒
EOF
    
    # Car maker selection template
    cat > config/carmaker_selection.txt.template << 'EOF'
# Car Maker Selection Configuration
# 車メーカー選択設定
# 
# 設定方法:
# - 1行に1つのメーカーインデックスを記載
# - 範囲指定: 0-5 (0から5まで)
# - コメント行: # で始める
# - 空行は無視されます

# Example: Process first 3 car makers
0
1
2

# Example: Process specific range
# 5-10

# Example: Process specific makers
# 0  # トヨタ
# 2  # ホンダ
# 5  # 日産
EOF
    
    print_success "Configuration files created"
    print_info "Please edit config files as needed:"
    print_info "  - config/scheduler_config.yml"
    print_info "  - config/notification_config.yml.template -> config/notification_config.yml"
    print_info "  - config/carmaker_selection.txt.template -> config/carmaker_selection.txt"
}

# Function to create helper scripts
create_helper_scripts() {
    print_info "Creating helper scripts..."
    
    # Health check script
    cat > scripts/health_check.sh << 'EOF'
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
EOF
    
    # Backup script
    cat > scripts/backup.sh << 'EOF'
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
EOF
    
    # Make scripts executable
    chmod +x scripts/health_check.sh
    chmod +x scripts/backup.sh
    
    print_success "Helper scripts created"
}

# Function to setup cron job
setup_cron() {
    print_info "Setting up cron job..."
    
    SCRIPT_DIR="$(pwd)"
    PYTHON_PATH="$(which python3)"
    
    # Create cron job template
    cat > scripts/cron_template.txt << EOF
# Car Scraper Cron Jobs
# 車データスクレイピング定期実行設定
#
# 使用方法:
# 1. 以下の設定をコピーして crontab -e で編集
# 2. パスとスケジュールを必要に応じて変更
# 3. 初回はテストモードで実行することを推奨

# Weekly execution (Sundays at 3:00 AM)
# 週次実行（日曜日 午前3時）
0 3 * * 0 cd $SCRIPT_DIR && $PYTHON_PATH scheduled_scraper.py >> logs/cron.log 2>&1

# Daily execution (2:00 AM)
# 日次実行（午前2時）
# 0 2 * * * cd $SCRIPT_DIR && $PYTHON_PATH scheduled_scraper.py >> logs/cron.log 2>&1

# Monthly execution (1st day of month at 1:00 AM)
# 月次実行（毎月1日 午前1時）
# 0 1 1 * * cd $SCRIPT_DIR && $PYTHON_PATH scheduled_scraper.py >> logs/cron.log 2>&1

# Health check (daily at 6:00 AM)
# ヘルスチェック（毎日 午前6時）
0 6 * * * cd $SCRIPT_DIR && $PYTHON_PATH scheduled_scraper.py --health-check >> logs/health_check.log 2>&1
EOF
    
    print_success "Cron template created: scripts/cron_template.txt"
    print_info "To set up cron job:"
    print_info "  1. Run: crontab -e"
    print_info "  2. Add lines from scripts/cron_template.txt"
    print_info "  3. Save and exit"
}

# Function to run initial test
run_initial_test() {
    print_info "Running initial test..."
    
    if [ -f "allmaker_url1016.csv" ]; then
        print_info "Running dry-run test..."
        python3 scheduled_scraper.py --dry-run --test-mode
        
        if [ $? -eq 0 ]; then
            print_success "Initial test passed"
        else
            print_warning "Initial test had issues, check logs"
        fi
    else
        print_warning "Data file (allmaker_url1016.csv) not found, skipping test"
    fi
}

# Function to show post-setup instructions
show_post_setup_instructions() {
    print_success "Setup completed successfully!"
    echo
    print_info "Next steps:"
    print_info "1. Edit configuration files:"
    print_info "   - config/scheduler_config.yml"
    print_info "   - Copy config/carmaker_selection.txt.template to config/carmaker_selection.txt and edit"
    print_info "   - (Optional) Copy config/notification_config.yml.template to config/notification_config.yml and edit"
    echo
    print_info "2. Test the setup:"
    print_info "   python3 scheduled_scraper.py --test-mode --dry-run"
    echo
    print_info "3. Set up cron job:"
    print_info "   crontab -e"
    print_info "   Add lines from scripts/cron_template.txt"
    echo
    print_info "4. Run health check:"
    print_info "   ./scripts/health_check.sh"
    echo
    print_info "5. Monitor logs:"
    print_info "   tail -f logs/scheduler.log"
    echo
    print_success "Car Scraper Scheduler is ready to use!"
}

# Main execution
main() {
    echo "================================================================"
    echo "Car Scraper Scheduler Setup"
    echo "車データスクレイピング定期実行セットアップ"
    echo "================================================================"
    echo
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root is not recommended"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Run setup steps
    check_python_version
    create_directories
    install_dependencies
    create_config_files
    create_helper_scripts
    setup_cron
    run_initial_test
    show_post_setup_instructions
}

# Handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Car Scraper Scheduler Setup Script"
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo "  --skip-test    Skip initial test"
            echo "  --force        Force overwrite existing files"
            exit 0
            ;;
        --skip-test)
            SKIP_TEST=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main 