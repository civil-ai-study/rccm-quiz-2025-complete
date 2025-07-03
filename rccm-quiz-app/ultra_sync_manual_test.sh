#!/bin/bash
# 🔥 Ultra Sync Department Test Script
# Generated: 2025-07-01T17:20:06.139339

echo "🔥 Ultra Sync Department Test - Manual Verification"
echo "=================================================="
echo ""
echo "🎯 このスクリプトは手動テストをガイドします"
echo ""

# カラー定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# テスト対象部門
departments=(
    "土質基礎:soil_foundation:CRITICAL"
    "道路:road:HIGH"
    "河川・砂防:civil_planning:HIGH"
    "都市計画:urban_planning:MEDIUM"
    "造園:landscape:MEDIUM"
    "建設環境:construction_env:MEDIUM"
    "鋼構造:steel_concrete:MEDIUM"
    "施工計画:construction_planning:MEDIUM"
    "上水道:water_supply:MEDIUM"
    "森林土木:forestry:MEDIUM"
    "農業土木:agriculture:MEDIUM"
    "トンネル:tunnel:MEDIUM"
    "基礎科目:basic:MEDIUM"
)

echo "📋 テスト手順:"
echo "1. ブラウザでRCCM学習アプリを開く (http://localhost:5000)"
echo "2. 各部門のボタンをクリック"
echo "3. 結果を記録"
echo ""
echo "Press Enter to start testing..."
read

# 結果記録ファイル
result_file="test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "Test Results - $(date)" > $result_file
echo "========================" >> $result_file

passed=0
failed=0

for dept in "${departments[@]}"
do
    IFS=':' read -r name url priority <<< "$dept"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ "$priority" = "CRITICAL" ]; then
        echo -e "${RED}🚨 CRITICAL TEST${NC}: $name"
    else
        echo "🧪 Testing: $name"
    fi
    
    echo "URL: /department_study/$url"
    echo ""
    echo "手順:"
    echo "1. 「$name」ボタンをクリック"
    echo "2. 結果を確認:"
    echo "   - エラーなし → 's' を入力"
    echo "   - エラーあり → 'f' を入力"
    echo ""
    echo -n "結果を入力 (s/f): "
    read result
    
    if [ "$result" = "s" ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $name"
        echo "✅ PASSED: $name" >> $result_file
        ((passed++))
    else
        echo -e "${RED}❌ FAILED${NC}: $name"
        echo -n "エラー内容を入力: "
        read error_msg
        echo "❌ FAILED: $name - $error_msg" >> $result_file
        ((failed++))
        
        if [ "$priority" = "CRITICAL" ]; then
            echo -e "${RED}🚨 CRITICAL FAILURE DETECTED!${NC}"
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 テスト結果サマリー"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "成功: ${GREEN}$passed${NC}"
echo -e "失敗: ${RED}$failed${NC}"
echo "成功率: $(( passed * 100 / (passed + failed) ))%"
echo ""
echo "詳細結果: $result_file"

# 最終判定
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "✅ デプロイ準備完了"
else
    echo -e "${RED}❌ FAILURES DETECTED${NC}"
    echo "🚨 修正が必要です"
fi
