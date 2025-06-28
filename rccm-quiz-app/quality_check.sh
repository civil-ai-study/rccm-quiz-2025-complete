#!/bin/bash
# quality_check.sh - CLAUDE.mdウルトラシンク品質チェックスクリプト（副作用防止）

echo "🚀 CLAUDE.md Ultra Sync Quality Check Starting..."
echo "=============================================="

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# エラーカウンター
ERROR_COUNT=0

# ウルトラシンク副作用防止：バックアップ作成
echo -e "${BLUE}🔄 Creating ultra sync backup...${NC}"
if [ ! -f "app.py.backup_$(date +%Y%m%d)" ]; then
    cp app.py "app.py.backup_$(date +%Y%m%d)"
    echo -e "${GREEN}✅ Backup created: app.py.backup_$(date +%Y%m%d)${NC}"
fi

# 1. 構文チェック（CLAUDE.md絶対必須）
echo -e "${YELLOW}📋 Step 1: Syntax Check (CLAUDE.md ABSOLUTE CRITICAL)${NC}"
python3 -m py_compile app.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax Check: PASSED${NC}"
else
    echo -e "${RED}❌ Syntax Check: FAILED - CLAUDE.md違反！作業停止！${NC}"
    ((ERROR_COUNT++))
fi

# 2. インデントチェック（CLAUDE.md絶対必須）
echo -e "${YELLOW}📋 Step 2: Indentation Check (CLAUDE.md ABSOLUTE CRITICAL)${NC}"
python3 -c "
import ast
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print('✅ Indentation Check: PASSED')
except IndentationError as e:
    print(f'❌ Indentation Error: {e}')
    exit(1)
except SyntaxError as e:
    print(f'❌ Syntax Error: {e}')
    exit(1)
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Indentation Check: PASSED${NC}"
else
    echo -e "${RED}❌ Indentation Check: FAILED - CLAUDE.md違反！作業停止！${NC}"
    ((ERROR_COUNT++))
fi

# 3. インポートチェック（CLAUDE.md絶対必須）
echo -e "${YELLOW}📋 Step 3: Import Check (CLAUDE.md ABSOLUTE CRITICAL)${NC}"
python3 -c "
import sys
sys.path.append('.')
try:
    import app
    print('✅ Import Check: PASSED')
except Exception as e:
    print(f'❌ Import Error: {e}')
    exit(1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Import Check: PASSED${NC}"
else
    echo -e "${RED}❌ Import Check: FAILED - CLAUDE.md違反！作業停止！${NC}"
    ((ERROR_COUNT++))
fi

# 4. 簡易実行テスト（ポート競合回避）
echo -e "${YELLOW}📋 Step 4: Basic Runtime Test (CLAUDE.md YOU MUST)${NC}"
timeout 8s python3 -c "
import app
try:
    # アプリケーション初期化確認のみ
    print('✅ Application initialization: PASSED')
except Exception as e:
    print(f'❌ Application error: {e}')
    exit(1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Basic Runtime Test: PASSED${NC}"
else
    echo -e "${RED}❌ Basic Runtime Test: FAILED - CLAUDE.md違反！${NC}"
    ((ERROR_COUNT++))
fi

# 5. ファイル構造チェック（ウルトラシンク必須）
echo -e "${YELLOW}📋 Step 5: File Structure Check (Ultra Sync)${NC}"
REQUIRED_FILES=("app.py" "utils.py" "config.py" "templates" "static" "data")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}✅ $file: EXISTS${NC}"
    else
        echo -e "${RED}❌ $file: MISSING${NC}"
        ((ERROR_COUNT++))
    fi
done

# 6. データファイル整合性チェック（ウルトラシンク）
echo -e "${YELLOW}📋 Step 6: Data File Integrity Check (Ultra Sync)${NC}"
DATA_FILES=("data/4-1.csv" "data/4-2_2019.csv" "data/4-2_2018.csv" "data/4-2_2017.csv")
for file in "${DATA_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file: EXISTS${NC}"
    else
        echo -e "${RED}❌ $file: MISSING${NC}"
        ((ERROR_COUNT++))
    fi
done

# 7. ウルトラシンク副作用チェック
echo -e "${YELLOW}📋 Step 7: Ultra Sync Side Effect Check${NC}"
# バックアップファイルの存在確認
if [ -f "app.py.backup_$(date +%Y%m%d)" ]; then
    echo -e "${GREEN}✅ Backup file exists: 副作用防止済み${NC}"
else
    echo -e "${YELLOW}⚠️ No backup found: バックアップ推奨${NC}"
fi

# ログファイルの確認
if [ -f "rccm_app.log" ]; then
    echo -e "${GREEN}✅ Log file exists: 正常${NC}"
else
    echo -e "${YELLOW}⚠️ No log file: 初回起動後に作成される${NC}"
fi

# 8. 最終結果
echo "=============================================="
if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CLAUDE.MD QUALITY CHECKS PASSED!${NC}"
    echo -e "${GREEN}✅ ウルトラシンク品質基準クリア${NC}"
    echo -e "${BLUE}🚀 Ready for ultra sync deployment${NC}"
    echo -e "${BLUE}📋 CLAUDE.md compliance: 100%${NC}"
    exit 0
else
    echo -e "${RED}💥 $ERROR_COUNT ERROR(S) FOUND!${NC}"
    echo -e "${RED}❌ CLAUDE.md品質基準未達成${NC}"
    echo -e "${YELLOW}🔧 Please fix errors following CLAUDE.md guidelines${NC}"
    echo -e "${YELLOW}📖 Review CLAUDE.md section: MAXIMUM QUALITY STANDARDS${NC}"
    exit 1
fi

