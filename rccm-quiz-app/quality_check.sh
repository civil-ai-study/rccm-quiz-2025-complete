#!/bin/bash
# quality_check.sh - 完全自動品質チェックスクリプト

echo "🚀 Complete Quality Check Starting..."
echo "=================================="

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# エラーカウンター
ERROR_COUNT=0

# 1. 構文チェック
echo -e "${YELLOW}📋 Step 1: Syntax Check${NC}"
python3 -m py_compile app.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax Check: PASSED${NC}"
else
    echo -e "${RED}❌ Syntax Check: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 2. インデントチェック
echo -e "${YELLOW}📋 Step 2: Indentation Check${NC}"
python3 -c "
import ast
try:
    with open('app.py', 'r') as f:
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
    echo -e "${RED}❌ Indentation Check: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 3. インポートチェック
echo -e "${YELLOW}📋 Step 3: Import Check${NC}"
python3 -c "
import sys
sys.path.append('.')
try:
    import app
    print('✅ Import Check: PASSED')
except Exception as e:
    print(f'❌ Import Error: {e}')
    exit(1)
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Import Check: PASSED${NC}"
else
    echo -e "${RED}❌ Import Check: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 4. 実行テスト
echo -e "${YELLOW}📋 Step 4: Runtime Test${NC}"
timeout 10s python3 app.py &
APP_PID=$!
sleep 3

# プロセス確認
if kill -0 $APP_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Runtime Test: PASSED${NC}"
    kill $APP_PID 2>/dev/null
else
    echo -e "${RED}❌ Runtime Test: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 5. HTTP接続テスト
echo -e "${YELLOW}📋 Step 5: HTTP Connection Test${NC}"
timeout 15s python3 app.py &
APP_PID=$!
sleep 8  # 起動に時間がかかるため、待機時間を延長

# HTTP接続確認（ポート5003を使用）
curl -s http://localhost:5003 > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ HTTP Test: PASSED${NC}"
else
    echo -e "${RED}❌ HTTP Test: FAILED${NC}"
    ((ERROR_COUNT++))
fi
kill $APP_PID 2>/dev/null

# 6. ファイル構造チェック
echo -e "${YELLOW}📋 Step 6: File Structure Check${NC}"
REQUIRED_FILES=("app.py" "requirements.txt" "templates" "static")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}✅ $file: EXISTS${NC}"
    else
        echo -e "${RED}❌ $file: MISSING${NC}"
        ((ERROR_COUNT++))
    fi
done

# 最終結果
echo "=================================="
if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL QUALITY CHECKS PASSED!${NC}"
    echo -e "${GREEN}✅ Ready for deployment${NC}"
    exit 0
else
    echo -e "${RED}💥 $ERROR_COUNT ERROR(S) FOUND!${NC}"
    echo -e "${RED}❌ NOT ready for deployment${NC}"
    echo -e "${YELLOW}🔧 Please fix errors before committing${NC}"
    exit 1
fi