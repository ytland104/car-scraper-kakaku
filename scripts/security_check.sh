#!/bin/bash

# Security Check Script for Car Scraper
# macOSセキュリティ機能との互換性確認スクリプト

echo "🔒 Car Scraper Security Check"
echo "============================="
echo ""

# 1. 実行権限の確認
echo "📁 File Permissions:"
echo "- scheduled_scraper.py: $(ls -la scheduled_scraper.py | cut -d' ' -f1)"
echo "- Python executable: $(ls -la /Users/yutaka/.pyenv/shims/python3 | cut -d' ' -f1)"
echo ""

# 2. 拡張属性の確認
echo "🏷️  Extended Attributes:"
XATTRS=$(xattr scheduled_scraper.py 2>/dev/null)
if [ -n "$XATTRS" ]; then
    echo "Found extended attributes:"
    echo "$XATTRS"
    
    # Google Drive関連の属性を確認
    if echo "$XATTRS" | grep -q "com.google.drivefs"; then
        echo "⚠️  File is from Google Drive - may need security clearance"
    fi
    
    # quarantine属性を確認
    if echo "$XATTRS" | grep -q "com.apple.quarantine"; then
        echo "⚠️  File is quarantined - may need to be cleared"
        echo "💡 To remove quarantine: xattr -r -d com.apple.quarantine scheduled_scraper.py"
    fi
else
    echo "No extended attributes found"
fi
echo ""

# 3. システムセキュリティ設定
echo "🛡️  System Security:"
echo "- Gatekeeper: $(spctl --status)"
echo "- SIP: $(csrutil status)"
echo ""

# 4. cron実行テスト
echo "⏰ Cron Execution Test:"
echo "Testing dry-run execution..."
if /Users/yutaka/.pyenv/shims/python3 scheduled_scraper.py --dry-run >/dev/null 2>&1; then
    echo "✅ Script execution successful"
else
    echo "❌ Script execution failed"
    echo "💡 This may indicate a permissions issue"
fi
echo ""

# 5. ネットワークアクセステスト
echo "🌐 Network Access Test:"
if /Users/yutaka/.pyenv/shims/python3 -c "import requests; requests.get('https://kakaku.com', timeout=5)" >/dev/null 2>&1; then
    echo "✅ Network access successful"
else
    echo "❌ Network access may be restricted"
    echo "💡 Check Privacy & Security settings for network access"
fi
echo ""

# 6. ファイル書き込みテスト
echo "📝 File Write Test:"
TEST_FILE="/Users/yutaka/car_scraper_link/logs/security_test.tmp"
if echo "test" > "$TEST_FILE" 2>/dev/null; then
    echo "✅ File write access successful"
    rm -f "$TEST_FILE"
else
    echo "❌ File write access failed"
    echo "💡 Check Full Disk Access permissions"
fi
echo ""

# 7. 推奨対策
echo "💡 Recommended Actions:"
echo "1. If quarantine attributes exist, remove them:"
echo "   xattr -r -d com.apple.quarantine /Users/yutaka/car_scraper_link/"
echo ""
echo "2. Grant Terminal/cron Full Disk Access:"
echo "   System Preferences > Privacy & Security > Full Disk Access"
echo "   Add: /usr/sbin/cron"
echo ""
echo "3. Allow network access for Python:"
echo "   System Preferences > Privacy & Security > Network"
echo "   Ensure Python is allowed"
echo ""
echo "4. If using cursor.app, grant necessary permissions:"
echo "   System Preferences > Privacy & Security"
echo "   Add cursor.app to relevant categories"
echo ""

echo "🔍 Security check completed!" 