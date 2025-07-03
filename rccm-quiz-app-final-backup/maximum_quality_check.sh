#!/bin/bash
# maximum_quality_check.sh - 最高レベル品質チェックスクリプト

echo "🏆 MAXIMUM QUALITY CHECK STARTING..."
echo "===================================="
echo "⚠️  このチェックは最高レベルの品質基準を適用します"
echo ""

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# エラーカウンター
ERROR_COUNT=0
WARNING_COUNT=0

# タイムスタンプ
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "${CYAN}実行時刻: $TIMESTAMP${NC}"
echo ""

# 0. バックアップ確認
echo -e "${YELLOW}📋 Step 0: Backup Check${NC}"
if [ -f "app.py.backup" ]; then
    echo -e "${GREEN}✅ Backup exists${NC}"
else
    cp app.py app.py.backup
    echo -e "${GREEN}✅ Backup created: app.py.backup${NC}"
fi

# 1. 構文チェック（詳細版）
echo -e "${YELLOW}📋 Step 1: Advanced Syntax Check${NC}"
python3 -m py_compile app.py 2>&1 | tee syntax_check.log
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax Check: PASSED${NC}"
else
    echo -e "${RED}❌ Syntax Check: FAILED${NC}"
    echo -e "${RED}詳細はsyntax_check.logを確認してください${NC}"
    ((ERROR_COUNT++))
fi

# 2. Flake8品質チェック
echo -e "${YELLOW}📋 Step 2: Flake8 Quality Check${NC}"
if command -v flake8 &> /dev/null; then
    flake8 app.py --max-line-length=200 --count --statistics 2>&1 | tee flake8_check.log
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ Flake8 Check: PASSED${NC}"
    else
        echo -e "${YELLOW}⚠️  Flake8 Warnings Found${NC}"
        ((WARNING_COUNT++))
    fi
else
    echo -e "${MAGENTA}📌 Flake8 not installed - Installing...${NC}"
    pip3 install flake8
fi

# 3. Pylintコード分析
echo -e "${YELLOW}📋 Step 3: Pylint Code Analysis${NC}"
if command -v pylint &> /dev/null; then
    pylint app.py --disable=C0114,C0115,C0116,R0903,R0902,R0913,R0914,R0915,W0703 --score=y 2>&1 | tee pylint_check.log
    PYLINT_SCORE=$(grep "Your code has been rated at" pylint_check.log | sed 's/.*rated at \([0-9.]*\).*/\1/')
    if (( $(echo "$PYLINT_SCORE >= 7.0" | bc -l) )); then
        echo -e "${GREEN}✅ Pylint Score: $PYLINT_SCORE/10.00${NC}"
    else
        echo -e "${YELLOW}⚠️  Pylint Score: $PYLINT_SCORE/10.00 (推奨: 7.0以上)${NC}"
        ((WARNING_COUNT++))
    fi
else
    echo -e "${MAGENTA}📌 Pylint not installed - Installing...${NC}"
    pip3 install pylint
fi

# 4. インポートチェック（詳細版）
echo -e "${YELLOW}📋 Step 4: Comprehensive Import Check${NC}"
python3 -c "
import sys
import traceback
sys.path.append('.')
try:
    import app
    print('✅ All imports successful')
    
    # モジュール依存関係チェック
    import importlib
    modules = ['flask', 'logging', 'datetime', 'os', 'random']
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            print(f'❌ Missing module: {module}')
            sys.exit(1)
    
except Exception as e:
    print(f'❌ Import Error: {e}')
    traceback.print_exc()
    sys.exit(1)
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Import Check: PASSED${NC}"
else
    echo -e "${RED}❌ Import Check: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 5. 実行時テスト（30秒間）
echo -e "${YELLOW}📋 Step 5: Extended Runtime Test (30 seconds)${NC}"
timeout 35s python3 app.py > runtime_test.log 2>&1 &
APP_PID=$!
sleep 5

# プロセス監視
for i in {1..6}; do
    if kill -0 $APP_PID 2>/dev/null; then
        echo -e "${BLUE}   Running... ($((i*5))/30 seconds)${NC}"
        sleep 5
    else
        echo -e "${RED}❌ Application crashed after $((i*5)) seconds${NC}"
        cat runtime_test.log
        ((ERROR_COUNT++))
        break
    fi
done

if kill -0 $APP_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Runtime Test: PASSED (30 seconds stable)${NC}"
    kill $APP_PID 2>/dev/null
fi

# 6. HTTPエンドポイントテスト
echo -e "${YELLOW}📋 Step 6: HTTP Endpoint Tests${NC}"
python3 app.py > /dev/null 2>&1 &
APP_PID=$!
sleep 8

# テストするエンドポイント
ENDPOINTS=("/" "/quiz" "/exam" "/result" "/api/health")
HTTP_ERRORS=0

for endpoint in "${ENDPOINTS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5003$endpoint)
    if [[ "$response" =~ ^[23][0-9][0-9]$ ]]; then
        echo -e "${GREEN}   ✅ $endpoint: HTTP $response${NC}"
    else
        echo -e "${RED}   ❌ $endpoint: HTTP $response${NC}"
        ((HTTP_ERRORS++))
    fi
done

kill $APP_PID 2>/dev/null

if [ $HTTP_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All HTTP Endpoints: PASSED${NC}"
else
    echo -e "${RED}❌ HTTP Endpoint Test: $HTTP_ERRORS errors${NC}"
    ((ERROR_COUNT++))
fi

# 7. メモリリークチェック
echo -e "${YELLOW}📋 Step 7: Memory Leak Check${NC}"
python3 -c "
import tracemalloc
import app
tracemalloc.start()

# 簡易メモリテスト
for i in range(10):
    with app.app.test_client() as client:
        client.get('/')

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

if peak < 100 * 1024 * 1024:  # 100MB未満
    print(f'✅ Memory usage: {peak / 1024 / 1024:.2f} MB (Good)')
else:
    print(f'⚠️  Memory usage: {peak / 1024 / 1024:.2f} MB (High)')
"

# 8. セキュリティチェック
echo -e "${YELLOW}📋 Step 8: Security Check${NC}"
python3 -c "
import re

with open('app.py', 'r') as f:
    content = f.read()

security_issues = []

# SQLインジェクション脆弱性チェック
if re.search(r'\.format\(.*request\.|f\".*request\.', content):
    security_issues.append('Potential SQL injection vulnerability')

# XSS脆弱性チェック
if re.search(r'Markup\(.*request\.', content):
    security_issues.append('Potential XSS vulnerability')

# ハードコードされた秘密情報チェック
if re.search(r'(password|secret|key)\s*=\s*[\"\']\w+[\"\']', content, re.IGNORECASE):
    security_issues.append('Hardcoded secrets detected')

if security_issues:
    print('⚠️  Security warnings:')
    for issue in security_issues:
        print(f'   - {issue}')
else:
    print('✅ No critical security issues found')
"

# 9. 10問完了保証テスト
echo -e "${YELLOW}📋 Step 9: 10-Question Completion Test${NC}"
if [ -f "test_10_questions_guarantee.py" ]; then
    python3 test_10_questions_guarantee.py > 10q_test.log 2>&1
    if grep -q "10問完了: ✅ 成功" 10q_test.log; then
        echo -e "${GREEN}✅ 10-Question Test: PASSED${NC}"
    else
        echo -e "${RED}❌ 10-Question Test: FAILED${NC}"
        ((ERROR_COUNT++))
    fi
else
    echo -e "${YELLOW}⚠️  10-Question test script not found${NC}"
    ((WARNING_COUNT++))
fi

# 10. ファイル構造チェック（詳細版）
echo -e "${YELLOW}📋 Step 10: Comprehensive File Structure Check${NC}"
REQUIRED_FILES=(
    "app.py"
    "requirements.txt"
    "templates"
    "static"
    "data"
    "CLAUDE.md"
    "config.py"
    "utils.py"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}   ✅ $file: EXISTS${NC}"
    else
        echo -e "${RED}   ❌ $file: MISSING${NC}"
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo -e "${GREEN}✅ File Structure: COMPLETE${NC}"
else
    echo -e "${RED}❌ File Structure: $MISSING_FILES files missing${NC}"
    ((ERROR_COUNT++))
fi

# 最終レポート
echo ""
echo "===================================="
echo -e "${CYAN}📊 QUALITY REPORT SUMMARY${NC}"
echo "===================================="
echo -e "実行時刻: $TIMESTAMP"
echo -e "エラー数: ${RED}$ERROR_COUNT${NC}"
echo -e "警告数: ${YELLOW}$WARNING_COUNT${NC}"

if [ $ERROR_COUNT -eq 0 ] && [ $WARNING_COUNT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🏆 PERFECT QUALITY ACHIEVED!${NC}"
    echo -e "${GREEN}✅ All quality standards met${NC}"
    echo -e "${GREEN}✅ Ready for production deployment${NC}"
    exit 0
elif [ $ERROR_COUNT -eq 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  GOOD QUALITY (with $WARNING_COUNT warnings)${NC}"
    echo -e "${YELLOW}✅ No critical errors found${NC}"
    echo -e "${YELLOW}📌 Consider fixing warnings before deployment${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ QUALITY CHECK FAILED!${NC}"
    echo -e "${RED}💥 $ERROR_COUNT CRITICAL ERROR(S) FOUND!${NC}"
    echo -e "${RED}🚫 NOT ready for deployment${NC}"
    echo -e "${YELLOW}🔧 Fix all errors before proceeding${NC}"
    
    echo ""
    echo -e "${CYAN}📝 Check these log files for details:${NC}"
    echo "   - syntax_check.log"
    echo "   - flake8_check.log"
    echo "   - pylint_check.log"
    echo "   - runtime_test.log"
    echo "   - 10q_test.log"
    
    exit 1
fi