#!/bin/bash

# Security Fix Script for Car Scraper
# macOSセキュリティ問題の修正スクリプト

echo "🔧 Car Scraper Security Fix"
echo "==========================="
echo ""

# 1. 拡張属性の確認と削除
echo "🏷️  Fixing Extended Attributes:"

# Google Drive関連の属性をチェック
if xattr scheduled_scraper.py | grep -q "com.google.drivefs"; then
    echo "Found Google Drive attributes - removing non-essential ones..."
    
    # provenance属性を削除（ただしGoogle Driveの同期に影響しないもの）
    if xattr scheduled_scraper.py | grep -q "com.apple.provenance"; then
        echo "Removing com.apple.provenance..."
        xattr -d com.apple.provenance scheduled_scraper.py 2>/dev/null || echo "Failed to remove provenance attribute"
    fi
    
    # quarantine属性があれば削除
    if xattr scheduled_scraper.py | grep -q "com.apple.quarantine"; then
        echo "Removing quarantine attribute..."
        xattr -d com.apple.quarantine scheduled_scraper.py
        echo "✅ Quarantine removed"
    fi
else
    echo "No problematic attributes found"
fi

# 2. ディレクトリ全体の拡張属性をチェック
echo ""
echo "🗂️  Checking directory attributes:"
QUARANTINE_FILES=$(find . -name "*.py" -exec xattr {} \; 2>/dev/null | grep -l "com.apple.quarantine" | wc -l)
if [ "$QUARANTINE_FILES" -gt 0 ]; then
    echo "Found $QUARANTINE_FILES Python files with quarantine attributes"
    echo "Removing quarantine from all Python files..."
    find . -name "*.py" -exec xattr -d com.apple.quarantine {} \; 2>/dev/null
    echo "✅ Quarantine attributes removed from Python files"
else
    echo "No quarantine attributes found in Python files"
fi

# 3. 実行権限の確認と修正
echo ""
echo "📁 Checking execution permissions:"
if [ ! -x "scheduled_scraper.py" ]; then
    echo "Making scheduled_scraper.py executable..."
    chmod +x scheduled_scraper.py
    echo "✅ Execute permission granted"
else
    echo "✅ Execute permission already set"
fi

# 4. cronディレクトリのアクセス権限確認
echo ""
echo "⏰ Checking cron accessibility:"
if sudo -n true 2>/dev/null; then
    if sudo ls -la /usr/sbin/cron >/dev/null 2>&1; then
        echo "✅ cron executable accessible"
    else
        echo "❌ cron executable not found or inaccessible"
    fi
else
    echo "⚠️  Cannot check cron without sudo privileges"
fi

# 5. 最終テスト
echo ""
echo "🧪 Final Test:"
echo "Testing script execution with current settings..."
if /Users/yutaka/.pyenv/shims/python3 scheduled_scraper.py --dry-run >/dev/null 2>&1; then
    echo "✅ Script execution successful after fixes"
else
    echo "❌ Script execution still failing"
    echo "💡 Additional manual configuration may be required"
fi

echo ""
echo "🔧 Security fix completed!"
echo ""
echo "📋 Manual steps that may still be needed:"
echo "1. System Preferences > Privacy & Security > Full Disk Access"
echo "   - Add Terminal (/Applications/Utilities/Terminal.app)"
echo "   - Add cron (/usr/sbin/cron) if available"
echo ""
echo "2. System Preferences > Privacy & Security > Automation"
echo "   - Allow cursor.app or Terminal to control other apps if needed"
echo ""
echo "3. If using cursor.app, grant it necessary permissions:"
echo "   - Full Disk Access"
echo "   - Developer Tools (if available)"
echo "   - Automation (if needed)" 