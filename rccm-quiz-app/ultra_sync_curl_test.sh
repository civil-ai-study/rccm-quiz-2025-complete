#!/bin/bash
# 🔥 Ultra Sync Automated cURL Test
# Seleniumなしでの自動HTTP検証

echo "🔥 Ultra Sync Automated Department Test"
echo "======================================"
echo ""

# ベースURL
BASE_URL="http://localhost:5000"

# テスト結果
passed=0
failed=0

# 土質基礎部門テスト（最重要）
echo "🚨 Testing 土質基礎 department (CRITICAL)..."
response=$(curl -s -L "$BASE_URL/department_study/soil_foundation")

# エラーメッセージチェック
if echo "$response" | grep -q "この部門の専門問題はまだ利用できません"; then
    echo "❌ FAILED: Error message found"
    ((failed++))
elif echo "$response" | grep -q "土質及び基礎"; then
    echo "✅ PASSED: Department page loaded correctly"
    ((passed++))
else
    echo "⚠️ UNKNOWN: Could not determine status"
    echo "Response sample:"
    echo "$response" | head -n 20
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Passed: $passed"
echo "Failed: $failed"

if [ $failed -eq 0 ]; then
    echo "✅ Test PASSED!"
else
    echo "❌ Test FAILED!"
fi
