# 車データスクレイピングモジュール定期実行仕様書

## 1. 概要

### 1.1 目的
kakaku.comから中古車データを定期的に収集し、価格予測分析を行うシステムの自動化仕様書。

### 1.2 対象システム
- **モジュール名**: CarDataScraper
- **ファイル**: `car_scraper.py`
- **プラットフォーム**: macOS (darwin 24.5.0)
- **Python版**: 3.12+

### 1.3 スコープ
- 定期実行の設定と管理
- ログ監視とアラート
- データ品質管理
- エラーハンドリング
- 運用監視

## 2. システム要件

### 2.1 実行環境
```bash
# 必要なシステム要件
- macOS 10.15以上
- Python 3.12+
- 最低8GB RAM（推奨16GB）
- 100GB以上の空きディスク容量
- 安定したインターネット接続
```

### 2.2 依存関係
```bash
# requirements.txtから
requests>=2.31.0
pandas>=2.0.0
beautifulsoup4>=4.12.0
scikit-learn>=1.3.0
tqdm>=4.65.0
retry>=0.9.2
mojimoji>=0.0.12
numpy>=1.24.0
```

## 3. 定期実行設計

### 3.1 実行頻度オプション

| 頻度 | 推奨用途 | 設定例 | 注意事項 |
|------|----------|---------|----------|
| 日次 | 価格変動追跡 | 毎日 AM 2:00 | サーバー負荷を考慮 |
| 週次 | 定期レポート | 毎週日曜 AM 3:00 | 推奨設定 |
| 月次 | 月次分析 | 毎月1日 AM 1:00 | データ蓄積向け |

### 3.2 cron設定例

```bash
# 週次実行（毎週日曜日 AM 3:00）
0 3 * * 0 cd /Users/yutaka/car_scraper && /usr/local/bin/python3 scheduled_scraper.py >> /var/log/car_scraper/cron.log 2>&1

# 日次実行（毎日 AM 2:00）
0 2 * * * cd /Users/yutaka/car_scraper && /usr/local/bin/python3 scheduled_scraper.py >> /var/log/car_scraper/cron.log 2>&1

# 月次実行（毎月1日 AM 1:00）
0 1 1 * * cd /Users/yutaka/car_scraper && /usr/local/bin/python3 scheduled_scraper.py >> /var/log/car_scraper/cron.log 2>&1
```

## 4. 実装ファイル構成

### 4.1 ディレクトリ構造
```
car_scraper/
├── car_scraper.py              # メインスクレイピングモジュール
├── scheduled_scraper.py        # 定期実行用スクリプト
├── scheduler_config.py         # 設定管理
├── monitoring.py               # 監視・アラート
├── data_validator.py           # データ品質チェック
├── backup_manager.py           # バックアップ管理
├── config/
│   ├── carmaker_selection.txt  # 車メーカー選択設定
│   ├── scheduler_config.yml    # スケジューラー設定
│   └── notification_config.yml # 通知設定
├── logs/
│   ├── scheduler.log          # スケジューラーログ
│   ├── scraper.log           # スクレイピングログ
│   └── error.log             # エラーログ
├── output/
│   ├── current/              # 最新データ
│   ├── archive/              # 過去データ
│   └── reports/              # レポート出力
└── scripts/
    ├── setup_scheduler.sh     # 初期設定スクリプト
    ├── health_check.sh       # ヘルスチェック
    └── backup.sh             # バックアップスクリプト
```

### 4.2 メインスケジューラーファイル

```python
# scheduled_scraper.py の仕様
class ScheduledScraper:
    """定期実行用のラッパークラス"""
    
    def __init__(self):
        self.load_config()
        self.setup_logging()
        self.setup_notifications()
    
    def run_scheduled_scraping(self):
        """スケジュールされたスクレイピング実行"""
        
    def handle_errors(self):
        """エラーハンドリングと通知"""
        
    def generate_reports(self):
        """実行結果レポート生成"""
        
    def cleanup_old_data(self):
        """古いデータのクリーンアップ"""
```

## 5. 設定管理

### 5.1 基本設定ファイル

```yaml
# config/scheduler_config.yml
scheduler:
  execution_mode: "auto"  # auto, manual, test
  target_carmakers: "config"  # config, all, interactive
  max_execution_time: 14400  # 4時間（秒）
  retry_attempts: 3
  retry_delay: 300  # 5分
  
data_management:
  output_retention_days: 90
  log_retention_days: 30
  backup_enabled: true
  backup_frequency: "weekly"
  
rate_limiting:
  requests_per_second: 0.5
  pages_per_batch: 100
  batch_delay: 60  # 秒
  
notifications:
  enabled: true
  email_alerts: true
  slack_webhook: false
  discord_webhook: false
```

### 5.2 通知設定

```yaml
# config/notification_config.yml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  username: "${EMAIL_USERNAME}"
  password: "${EMAIL_PASSWORD}"
  from_address: "car-scraper@yourdomain.com"
  to_addresses:
    - "admin@yourdom
.com"
    - "analyst@yourdomain.com"

alerts:
  success_notification: false
  error_notification: true
  completion_summary: true
  data_quality_alerts: true
  
thresholds:
  max_error_rate: 10  # パーセント
  min_success_rate: 90  # パーセント
  max_execution_time: 14400  # 秒
```

## 6. 監視とアラート

### 6.1 監視項目

| 項目 | 監視レベル | アラート条件 | 対応アクション |
|------|------------|--------------|----------------|
| 実行成功率 | Critical | < 90% | 即座にアラート |
| 実行時間 | Warning | > 4時間 | 調査が必要 |
| エラー率 | Warning | > 10% | パフォーマンス確認 |
| データ品質 | Info | 異常値検出 | データ検証 |
| ディスク容量 | Critical | < 10GB | クリーンアップ |

### 6.2 ヘルスチェック

```python
# monitoring.py の主要機能
class HealthMonitor:
    def check_system_resources(self):
        """システムリソース確認"""
        
    def check_data_quality(self):
        """データ品質確認"""
        
    def check_log_errors(self):
        """ログエラー確認"""
        
    def send_health_report(self):
        """ヘルスレポート送信"""
```

## 7. データ管理

### 7.1 データ保存戦略

```
output/
├── current/
│   └── 20241216_トヨタ_withexpectedPrice.csv
├── archive/
│   ├── 2024/
│   │   ├── 12/
│   │   │   ├── weekly/
│   │   │   └── daily/
│   │   └── 11/
│   └── 2023/
└── reports/
    ├── weekly_summary_20241216.pdf
    └── monthly_analysis_202412.xlsx
```

### 7.2 バックアップ戦略

```bash
# backup_manager.py の機能
- 日次: ローカルバックアップ
- 週次: クラウドストレージ同期
- 月次: 長期保存アーカイブ
```

## 8. エラーハンドリング

### 8.1 エラーレベル分類

| レベル | 説明 | 対応 |
|--------|------|------|
| CRITICAL | システム停止 | 即座に管理者通知 |
| ERROR | 処理失敗 | リトライ後通知 |
| WARNING | 性能劣化 | ログ記録 |
| INFO | 正常処理 | 統計記録 |

### 8.2 リカバリー戦略

```python
# エラー別リカバリー手順
recovery_strategies = {
    "network_timeout": "exponential_backoff_retry",
    "rate_limit": "delay_and_retry",
    "data_validation_error": "skip_and_continue",
    "disk_full": "cleanup_and_retry",
    "memory_error": "reduce_batch_size"
}
```

## 9. セキュリティ考慮事項

### 9.1 アクセス制御
- 実行権限の最小化
- ログファイルのアクセス制限
- 設定ファイルの暗号化

### 9.2 レート制限
```python
# サイトに負荷をかけないための制限
rate_limits = {
    "requests_per_second": 0.5,
    "concurrent_connections": 1,
    "user_agent_rotation": True,
    "respect_robots_txt": True
}
```

## 10. 運用手順

### 10.1 初期セットアップ

```bash
# 1. 環境準備
./scripts/setup_scheduler.sh

# 2. 設定ファイル作成
cp config/scheduler_config.yml.template config/scheduler_config.yml

# 3. cron設定
crontab -e

# 4. 初回テスト実行
python scheduled_scraper.py --test-mode
```

### 10.2 日常運用

```bash
# 日次チェック
./scripts/health_check.sh

# ログ確認
tail -f logs/scheduler.log

# 手動実行（テスト）
python scheduled_scraper.py --dry-run

# 設定変更反映
sudo systemctl reload cron
```

### 10.3 トラブルシューティング

| 問題 | 確認箇所 | 解決策 |
|------|----------|---------|
| 実行されない | cron設定、権限 | 設定見直し、権限修正 |
| データが古い | 実行ログ、エラーログ | エラー修正、再実行 |
| 性能劣化 | システムリソース | リソース追加、最適化 |
| 通知が来ない | 通知設定、ネットワーク | 設定確認、接続テスト |

## 11. パフォーマンス最適化

### 11.1 推奨設定

```python
# 最適化パラメータ
optimization_settings = {
    "batch_size": 50,
    "worker_threads": 2,
    "connection_pool_size": 5,
    "request_timeout": 30,
    "memory_limit": "8GB",
    "temp_cleanup": True
}
```

### 11.2 監視メトリクス

- CPU使用率
- メモリ使用量
- ネットワーク帯域幅
- ディスクI/O
- 応答時間

## 12. 今後の拡張予定

### 12.1 機能拡張
- AI価格予測モデルの統合
- リアルタイムデータ更新
- Web UIダッシュボード
- APIエンドポイント提供

### 12.2 技術改善
- Dockerコンテナ化
- Kubernetes対応
- マイクロサービス化
- CI/CD パイプライン統合

## 13. 付録

### 13.1 設定例ファイル
- 各設定ファイルのテンプレート
- 環境変数設定例
- cron設定の詳細例

### 13.2 コマンドリファレンス
```bash
# 主要コマンド一覧
python scheduled_scraper.py --help
./scripts/setup_scheduler.sh --help
./scripts/health_check.sh --verbose
```

---

**作成日**: 2024年12月16日  
**バージョン**: 1.0  
**作成者**: AI Assistant  
**レビュー**: 定期更新予定 