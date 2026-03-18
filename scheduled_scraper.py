#!/usr/bin/env python3
"""
Scheduled Car Scraper
定期実行用の車データスクレイピングスクリプト

このスクリプトはcar_scraperモジュールをラップし、
定期実行、エラーハンドリング、通知、監視機能を提供します。
"""

import os
import sys
import yaml
import json
import logging
import argparse
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import signal

# psutilは必須ではないので、インポートエラーを処理
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Add current directory to Python path to import car_scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from car_scraper import CarDataScraper, ScrapingError, DataValidationError
except ImportError as e:
    print(f"Error importing car_scraper: {e}")
    print("Please ensure car_scraper.py is in the same directory")
    sys.exit(1)


class ScheduledScraper:
    """定期実行用のラッパークラス"""
    
    def __init__(self, config_path: str = "config/scheduler_config.yml", carmaker_config_path: Optional[str] = None):
        """
        Initialize ScheduledScraper
        
        Args:
            config_path: Path to scheduler configuration file
            carmaker_config_path: Path to car maker selection file (default: config/carmaker_selection.txt).
                                   Used when target_carmakers is "config".
        """
        self.config_path = config_path
        self.carmaker_config_path = carmaker_config_path or "config/carmaker_selection.txt"
        self.config = {}
        self.start_time = datetime.now()
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'success': False,
            'errors': [],
            'warnings': [],
            'data_files_created': [],
            'records_processed': 0
        }
        
        # Initialize components
        self.load_config()
        self.setup_logging()
        self.scraper = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def load_config(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                    
                # Apply environment variable substitutions
                self._substitute_env_vars(self.config)
                
            else:
                # Default configuration
                self.config = self._get_default_config()
                self._save_default_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._get_default_config()
            
    def _substitute_env_vars(self, obj):
        """環境変数の置換処理"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._substitute_env_vars(item)
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を返却"""
        return {
            'scheduler': {
                'execution_mode': 'auto',
                'target_carmakers': 'config',
                'max_execution_time': 14400,  # 4時間
                'retry_attempts': 3,
                'retry_delay': 300  # 5分
            },
            'data_management': {
                'output_dir': 'output',
                'output_retention_days': 90,
                'log_retention_days': 30,
                'backup_enabled': True,
                'backup_frequency': 'weekly'
            },
            'rate_limiting': {
                'requests_per_second': 0.5,
                'pages_per_batch': 100,
                'batch_delay': 60
            },
            'notifications': {
                'enabled': True,
                'email_alerts': False,
                'success_notification': False,
                'error_notification': True,
                'completion_summary': True
            },
            'monitoring': {
                'max_error_rate': 10,
                'min_success_rate': 90,
                'max_execution_time': 14400,
                'disk_space_threshold': 10  # GB
            }
        }
    
    def _save_default_config(self):
        """デフォルト設定ファイルの保存"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            print(f"Default configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving default config: {e}")
    
    def setup_logging(self):
        """ログ設定のセットアップ"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_level = getattr(logging, self.config.get('logging', {}).get('level', 'INFO'))
        
        # File handler for scheduler logs
        file_handler = logging.FileHandler(
            log_dir / "scheduler.log", 
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger('ScheduledScraper')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
    def check_system_resources(self) -> Dict[str, Any]:
        """システムリソースの確認"""
        try:
            resources = {
                'timestamp': datetime.now().isoformat(),
                'warnings': []
            }
            
            if PSUTIL_AVAILABLE:
                # CPU情報
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # メモリ情報
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_available_gb = memory.available / (1024**3)
                
                # ディスク情報
                disk = psutil.disk_usage(os.getcwd())
                disk_free_gb = disk.free / (1024**3)
                disk_percent = (disk.used / disk.total) * 100
                
                resources.update({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_available_gb': round(memory_available_gb, 2),
                    'disk_free_gb': round(disk_free_gb, 2),
                    'disk_used_percent': round(disk_percent, 2)
                })
                
                # Check thresholds
                if disk_free_gb < self.config.get('monitoring', {}).get('disk_space_threshold', 10):
                    resources['warnings'].append(f"Low disk space: {disk_free_gb:.2f}GB remaining")
                    
                if memory_percent > 85:
                    resources['warnings'].append(f"High memory usage: {memory_percent:.1f}%")
                    
                if cpu_percent > 80:
                    resources['warnings'].append(f"High CPU usage: {cpu_percent:.1f}%")
            else:
                resources['note'] = 'psutil not available - resource monitoring limited'
                
                # Basic disk space check using os.statvfs (Unix-like systems)
                try:
                    if hasattr(os, 'statvfs'):
                        statvfs = os.statvfs('.')
                        disk_free_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
                        resources['disk_free_gb'] = round(disk_free_gb, 2)
                        
                        if disk_free_gb < self.config.get('monitoring', {}).get('disk_space_threshold', 10):
                            resources['warnings'].append(f"Low disk space: {disk_free_gb:.2f}GB remaining")
                except Exception:
                    pass
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            return {'error': str(e), 'warnings': []}
    
    def run_scheduled_scraping(self, dry_run: bool = False, test_mode: bool = False) -> bool:
        """
        スケジュールされたスクレイピングの実行
        
        Args:
            dry_run: ドライラン（実際の処理は実行しない）
            test_mode: テストモード（少量データで実行）
            
        Returns:
            実行成功可否
        """
        self.execution_stats['start_time'] = datetime.now()
        success = False
        
        try:
            self.logger.info("=== Scheduled scraping started ===")
            
            # System resource check
            resources = self.check_system_resources()
            self.logger.info(f"System resources: {resources}")
            
            if resources.get('warnings'):
                for warning in resources['warnings']:
                    self.logger.warning(warning)
                    self.execution_stats['warnings'].append(warning)
            
            # Check disk space before starting
            if resources.get('disk_free_gb', float('inf')) < 5:  # Less than 5GB
                raise Exception("Insufficient disk space to proceed")
            
            if dry_run:
                self.logger.info("DRY RUN MODE - No actual scraping will be performed")
                return True
            
            # Initialize scraper
            self.scraper = CarDataScraper(
                csv_path="allmaker_url1016.csv",
                output_dir=self.config.get('data_management', {}).get('output_dir', 'output')
            )
            
            # Load and filter data
            filtered_df = self.scraper.load_and_filter_data()
            if filtered_df.empty:
                raise DataValidationError("No data available after filtering")
            
            # Determine car makers to process
            target_carmakers = self._get_target_carmakers()
            
            if test_mode:
                # Limit to first car maker for testing
                target_carmakers = target_carmakers[:1] if target_carmakers else []
                self.logger.info("TEST MODE - Processing only first car maker")
            
            if not target_carmakers:
                raise Exception("No car makers selected for processing")
            
            self.logger.info(f"Processing {len(target_carmakers)} car makers: {target_carmakers}")
            
            # Process car makers
            self.scraper.process_by_carmaker(carmaker_indices=target_carmakers)
            
            # Update statistics
            stats = self.scraper.get_error_statistics()
            self.execution_stats['records_processed'] = stats['successful_requests']
            self.execution_stats['success'] = True
            
            # Generate reports
            self._generate_execution_report()
            
            # Cleanup old data
            self._cleanup_old_data()
            
            success = True
            self.logger.info("=== Scheduled scraping completed successfully ===")
            
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.execution_stats['errors'].append(error_msg)
            success = False
            
        finally:
            self.execution_stats['end_time'] = datetime.now()
            self.execution_stats['duration_seconds'] = (
                self.execution_stats['end_time'] - self.execution_stats['start_time']
            ).total_seconds()
            
            # Send notifications
            if self.config.get('notifications', {}).get('enabled', True):
                self._send_notifications(success)
            
        return success
    
    def _get_target_carmakers(self) -> List[int]:
        """処理対象の車メーカーを取得"""
        target_mode = self.config.get('scheduler', {}).get('target_carmakers', 'config')
        
        if target_mode == 'all':
            # Process all car makers
            carmaker_info = self.scraper.list_available_carmakers()
            return carmaker_info['Index'].tolist()
            
        elif target_mode == 'config':
            # Load from configuration file（--carmaker-config で別ファイル指定可能）
            config_file = self.carmaker_config_path
            if os.path.exists(config_file):
                return self.scraper.load_carmaker_config(config_file)
            else:
                self.logger.warning(f"Config file not found: {config_file}")
                return []
                
        else:
            self.logger.warning(f"Unknown target mode: {target_mode}")
            return []
    
    def _generate_execution_report(self):
        """実行レポートの生成"""
        try:
            out_dir = self.config.get('data_management', {}).get('output_dir', 'output')
            report_dir = Path(out_dir) / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_data = {
                'execution_time': self.execution_stats['start_time'].isoformat(),
                'duration_minutes': round(self.execution_stats['duration_seconds'] / 60, 2),
                'success': self.execution_stats['success'],
                'records_processed': self.execution_stats['records_processed'],
                'errors': self.execution_stats['errors'],
                'warnings': self.execution_stats['warnings'],
                'system_resources': self.check_system_resources()
            }
            
            # Save JSON report
            report_file = report_dir / f"execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Execution report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating execution report: {e}")
    
    def _cleanup_old_data(self):
        """古いデータのクリーンアップ"""
        try:
            retention_days = self.config.get('data_management', {}).get('output_retention_days', 3650)
            
            # 0以下の場合はクリーンアップしない
            if retention_days <= 0:
                return

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Clean up old output files（config の output_dir を使用）
            output_dir = Path(self.config.get('data_management', {}).get('output_dir', 'output'))
            if output_dir.exists():
                for file_path in output_dir.rglob("*.csv"):
                    try:
                        if file_path.stat().st_mtime < cutoff_date.timestamp():
                            file_path.unlink()
                            self.logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {file_path}: {e}")
            
            # Clean up old logs
            log_retention_days = self.config.get('data_management', {}).get('log_retention_days', 30)
            log_cutoff_date = datetime.now() - timedelta(days=log_retention_days)
            
            log_dir = Path("logs")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    try:
                        if log_file.stat().st_mtime < log_cutoff_date.timestamp():
                            log_file.unlink()
                            self.logger.info(f"Deleted old log: {log_file}")
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {log_file}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _send_notifications(self, success: bool):
        """通知の送信"""
        try:
            notification_config = self.config.get('notifications', {})
            
            if not notification_config.get('enabled', True):
                return
            
            # Determine if notification should be sent
            should_notify = False
            if success and notification_config.get('success_notification', False):
                should_notify = True
            elif not success and notification_config.get('error_notification', True):
                should_notify = True
            elif notification_config.get('completion_summary', True):
                should_notify = True
            
            if not should_notify:
                return
            
            # Send email notification
            if notification_config.get('email_alerts', False):
                self._send_email_notification(success)
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
    
    def _send_email_notification(self, success: bool):
        """メール通知の送信"""
        try:
            # Load notification config
            notification_config_path = "config/notification_config.yml"
            if not os.path.exists(notification_config_path):
                self.logger.warning("Notification config file not found")
                return
            
            with open(notification_config_path, 'r', encoding='utf-8') as f:
                notification_config = yaml.safe_load(f)
            
            email_config = notification_config.get('email', {})
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_address', 'car-scraper@localhost')
            msg['To'] = ', '.join(email_config.get('to_addresses', []))
            
            # Subject and body
            status = "SUCCESS" if success else "FAILED"
            msg['Subject'] = f"Car Scraper Execution {status} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = self._create_email_body(success)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(email_config.get('smtp_server', 'smtp.gmail.com'), 
                                email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config.get('username'), email_config.get('password'))
            
            text = msg.as_string()
            server.sendmail(msg['From'], email_config.get('to_addresses', []), text)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
    
    def _create_email_body(self, success: bool) -> str:
        """メール本文の作成"""
        status = "成功" if success else "失敗"
        
        body = f"""
車データスクレイピング実行結果

実行状態: {status}
開始時間: {self.execution_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
終了時間: {self.execution_stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
実行時間: {self.execution_stats['duration_seconds'] / 60:.1f} 分
処理レコード数: {self.execution_stats['records_processed']}

"""
        
        if self.execution_stats['warnings']:
            body += "警告:\n"
            for warning in self.execution_stats['warnings']:
                body += f"  - {warning}\n"
            body += "\n"
        
        if self.execution_stats['errors']:
            body += "エラー:\n"
            for error in self.execution_stats['errors']:
                body += f"  - {error}\n"
            body += "\n"
        
        # System resources
        resources = self.check_system_resources()
        body += f"""
システムリソース:
  - CPU使用率: {resources.get('cpu_percent', 'N/A')}%
  - メモリ使用率: {resources.get('memory_percent', 'N/A')}%
  - 空きディスク容量: {resources.get('disk_free_gb', 'N/A')}GB

---
Car Data Scraper - Automated Execution
"""
        
        return body
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー（優雅な停止）"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        
        if self.scraper:
            self.scraper.safe_shutdown()
        
        self.execution_stats['end_time'] = datetime.now()
        self.execution_stats['duration_seconds'] = (
            self.execution_stats['end_time'] - self.execution_stats['start_time']
        ).total_seconds() if self.execution_stats['start_time'] else 0
        
        self.logger.info("Graceful shutdown completed")
        sys.exit(0)
    
    def health_check(self) -> Dict[str, Any]:
        """ヘルスチェックの実行"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'checks': {}
            }
            
            # System resources check
            resources = self.check_system_resources()
            health_status['checks']['system_resources'] = {
                'status': 'ok' if not resources.get('warnings') else 'warning',
                'details': resources
            }
            
            # Configuration check
            try:
                self.load_config()
                health_status['checks']['configuration'] = {'status': 'ok'}
            except Exception as e:
                health_status['checks']['configuration'] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['status'] = 'unhealthy'
            
            # CSV file check
            csv_path = "allmaker_url1016.csv"
            if os.path.exists(csv_path):
                health_status['checks']['data_file'] = {'status': 'ok'}
            else:
                health_status['checks']['data_file'] = {
                    'status': 'error',
                    'error': f'CSV file not found: {csv_path}'
                }
                health_status['status'] = 'unhealthy'
            
            # Output directory check（config の output_dir を使用）
            output_dir = Path(self.config.get('data_management', {}).get('output_dir', 'output'))
            if output_dir.exists() and output_dir.is_dir():
                health_status['checks']['output_directory'] = {'status': 'ok'}
            else:
                health_status['checks']['output_directory'] = {
                    'status': 'warning',
                    'details': 'Output directory does not exist'
                }
            
            return health_status
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='Scheduled Car Data Scraper')
    parser.add_argument('--config', '-c', 
                       default='config/scheduler_config.yml',
                       help='Scheduler configuration file path')
    parser.add_argument('--carmaker-config',
                       default=None,
                       metavar='PATH',
                       help='Car maker selection file (default: config/carmaker_selection.txt). Use for second cron with other makers.')
    parser.add_argument('--dry-run', '-d', 
                       action='store_true',
                       help='Dry run mode (no actual scraping)')
    parser.add_argument('--test-mode', '-t', 
                       action='store_true',
                       help='Test mode (process limited data)')
    parser.add_argument('--health-check', 
                       action='store_true',
                       help='Run health check only')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        # Initialize scheduler
        scheduler = ScheduledScraper(
            config_path=args.config,
            carmaker_config_path=args.carmaker_config
        )
        
        if args.health_check:
            # Run health check
            health_status = scheduler.health_check()
            print(json.dumps(health_status, indent=2, ensure_ascii=False))
            return 0 if health_status['status'] != 'error' else 1
        else:
            # Run scheduled scraping
            success = scheduler.run_scheduled_scraping(
                dry_run=args.dry_run,
                test_mode=args.test_mode
            )
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 