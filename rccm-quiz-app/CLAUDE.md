# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development and Testing
```bash
# Start the Flask development server
python app.py

# Run AI features tests
python test_ai_features.py

# Run gamification tests  
python test_gamification.py

# Install dependencies
pip install -r requirements.txt

# Test with Flask test client (for debugging)
python3 -c "from app import app; with app.test_client() as client: print(client.get('/').status_code)"
```

### Data Management
```bash
# Check question data integrity
python data_check.py

# Clear application cache
curl -X POST http://localhost:5000/api/cache/clear

# Force reset application state
curl http://localhost:5000/force_reset
```

## Architecture

### Core Application Structure
This is a Flask-based RCCM (登録建設機械施工技術者) exam preparation application with advanced learning features:

**Main Application**: `app.py` (1,600+ lines) - Monolithic Flask app with 45+ routes
- Session-based quiz management with 10-question sessions
- File-based data persistence (no database)
- Modular architecture with separate feature modules

**Configuration Management**: `config.py`
- Environment-based configuration classes (Development/Production)
- QuizConfig.QUESTIONS_PER_SESSION = 10 (key constant)
- SRSConfig.INTERVALS defines spaced repetition timing

**Data Layer**:
- `data/questions.csv` - 100 RCCM exam questions (Shift_JIS encoding)
- `user_data/*.json` - Session-based user progress files
- `utils.py` - CSV loading with encoding detection
- `data_manager.py` - Data persistence and session management

### Feature Modules

**SRS (Spaced Repetition System)**: 
- Implements Ebbinghaus forgetting curve intervals
- Tracks question mastery levels (0-5)
- Mixes review questions with new questions in sessions

**AI Learning Engine**:
- `ai_analyzer.py` - Weakness detection and learning pattern analysis
- `adaptive_learning.py` - Adaptive question selection algorithms
- `advanced_analytics.py` - Performance analytics and insights

**Gamification**: `gamification.py`
- Badge system and learning streaks
- Study calendar and motivation features

**Exam Simulation**: `exam_simulator.py`
- Full exam environment with timing and navigation
- Question flagging and review capabilities

**Mobile/PWA Features**: `mobile_features.py`
- Offline data sync and caching
- Touch gestures and voice settings
- Service Worker integration

### Session Management Architecture
- File-based session persistence (no database)
- Session structure includes: quiz_question_ids, quiz_current, history, srs_data, bookmarks
- Critical session flow: quiz selection → question display → answer processing → feedback → navigation
- Session race condition handling with explicit locking mechanisms

### Template Architecture
- `templates/base.html` - Common layout with Bootstrap 5
- `templates/quiz_feedback.html` - Post-answer feedback with navigation logic
- Jinja2 templating with extensive conditional navigation logic
- Cache control headers to prevent browser caching issues

### Common Issues and Solutions

**Question Navigation Problem**: 
- Root cause: `is_last_question = (current_no + 1) >= len(quiz_question_ids)` calculation in app.py:379
- This determines when to show "次の問題へ" vs "結果を見る" buttons

**Session State Synchronization**:
- Sessions use 0-based indexing internally but 1-based display
- `quiz_current` tracks current question index
- Navigation uses URL parameters: `/quiz?next=1&current=N`

**Cache Management**:
- Question data cached for 1 hour (CACHE_TIMEOUT)
- Browser cache can cause stale UI - use `/force_reset` for debugging
- Template modifications require server restart + browser hard refresh

### Testing Strategy
- Flask test client for integration testing
- Simulated browser sessions to test question flow
- Manual testing required for session state edge cases
- Use debug information in quiz_feedback.html template for troubleshooting

### Key Configuration
- Questions per session: Controlled by QuizConfig.QUESTIONS_PER_SESSION
- SRS intervals: Defined in SRSConfig.INTERVALS (1, 3, 7, 21, 60, 180 days)
- Session timeout: 3600 seconds (1 hour)
- File encoding: Shift_JIS for CSV, UTF-8 for JSON user data

## API Integration & Professional Features

### New Professional Modules Added

**API Integration**: `api_integration.py` (900+ lines)
- RESTful API endpoints for external system integration
- API key authentication and authorization system
- Professional certification tracking and progress monitoring
- Enterprise reporting and analytics export
- Organization management for corporate/educational use

**Advanced Personalization**: `advanced_personalization.py` (764 lines) 
- ML-based learning recommendations and content personalization
- Adaptive UI customization based on learning styles
- Custom learning plan generation with biorhythm integration
- Real-time learning efficiency tracking and optimization

**Social Learning Features**: `social_learning.py` (1057 lines)
- Study group creation and management
- Peer comparison and leaderboard systems
- Discussion forums and collaborative learning
- Study partner recommendations based on learning patterns

**Admin Dashboard**: `admin_dashboard.py` (984 lines)
- Comprehensive system monitoring and analytics
- Question quality management and data integrity checks
- User progress oversight and performance metrics
- Content effectiveness analysis and recommendations

### API Endpoints

**Authentication Endpoints:**
- `POST /api/auth/generate_key` - Generate new API key
- `POST /api/auth/validate_key` - Validate API key
- `DELETE /api/auth/revoke_key` - Revoke API key

**User Management APIs:**
- `GET /api/users` - List all users with progress summary
- `GET /api/users/<user_id>/progress` - Individual progress report
- `GET /api/users/<user_id>/certifications` - User certification status

**Progress Reports:**
- `GET /api/reports/progress` - Generate progress reports
- `GET /api/reports/organization/<org_id>` - Organization reports
- `GET /api/reports/export/<format>` - Export analytics (JSON/PDF/Excel/CSV)

**Certification Management:**
- `GET /api/certifications` - List certification programs
- `POST /api/certifications` - Create certification program
- `GET /api/certifications/<cert_id>/progress` - Check certification progress

**Organization Management:**
- `GET /api/organizations` - List organizations
- `POST /api/organizations` - Create organization
- `GET /api/organizations/<org_id>/users` - Organization user list

**Personalization APIs:**
- `GET /api/personalization/profile/<user_id>` - User learning profile
- `GET /api/personalization/recommendations/<user_id>` - ML recommendations
- `GET /api/personalization/ui/<user_id>` - UI customization settings

### Professional Features Access

**Web Interfaces:**
- `/admin` - Administrative dashboard
- `/social_learning` - Social learning features
- `/api_integration` - API management and professional tools

**Authentication:**
- API key-based authentication with permission scoping
- Rate limiting (1000 requests/hour default)
- Organization-based access control

### Data Storage Structure

**API Data:**
- `api_data/api_keys.json` - API key storage and usage statistics
- `api_data/certifications.json` - Certification program definitions
- `api_data/organizations.json` - Organization data and user memberships
- `api_data/integration_settings.json` - External system integration configs

**Social Data:**
- `social_data/groups.json` - Study group information
- `social_data/discussions.json` - Discussion threads and replies
- `social_data/study_sessions.json` - Collaborative study sessions

**Personalization Data:**
- `personalization_data/user_profiles.json` - ML-generated user profiles
- `personalization_data/ui_preferences.json` - Adaptive UI settings
- `personalization_data/learning_plans.json` - Custom learning plans

### Enterprise Integration

**LMS Compatibility:**
- Moodle integration via REST API
- Canvas LTI-compliant endpoints
- Blackboard Grade Passback support
- Generic SCORM 1.2/2004 compliance

**Certification Tracking:**
- Custom requirement definitions (accuracy, question count, department coverage)
- Automatic progress monitoring and completion detection
- Certificate generation and issuance tracking
- Multi-tier certification pathway support

**Reporting & Analytics:**
- Individual learner progress reports
- Organizational performance dashboards
- Learning effectiveness analytics
- Content quality and difficulty analysis
- Export to multiple formats (JSON, PDF, Excel, CSV)

## 🚫 絶対禁止事項

**開発・テスト時の絶対禁止事項:**
- テストエラーや型エラー解消のための条件緩和
- テストのスキップや不適切なモック化による回避
- 出力やレスポンスのハードコード
- エラーメッセージの無視や隠蔽
- 一時的な修正による問題の先送り

**コード品質維持のための禁止事項:**
- 根本原因を解決せずに症状のみを隠す修正
- テストケースの削除や無効化による「修正」
- try-except文での例外の単純な無視
- 型チェックの回避やanyを使った逃げ
- セキュリティ要件の緩和や回避

**データ整合性の禁止事項:**
- 不正データの受け入れによる問題回避
- バリデーション処理のスキップ
- エラー状態での正常値の返却
- 一貫性チェックの無効化
- 重要な警告メッセージの抑制

これらの禁止事項に該当する修正を求められた場合は、適切な根本解決策を提案すること。

## 🔍 エラーチェックルール

### NEVER（絶対禁止）
- NEVER: 本番環境に未テストコードをデプロイ
- NEVER: エラーハンドリングなしでAPI呼び出し
- NEVER: ユーザー入力の検証なしでデータベース操作
- NEVER: セキュリティテスト未実施のまま公開

### YOU MUST（必須事項）
- YOU MUST: 全ペルソナでのテスト実行
- YOU MUST: エラー画面のスクリーンショット保存
- YOU MUST: 修正前後の比較レポート生成
- YOU MUST: 各機能変更後のリグレッションテスト実行
- YOU MUST: セキュリティ脆弱性スキャンの実施

### IMPORTANT（重要事項）
- IMPORTANT: 各修正後の自動リグレッションテスト
- IMPORTANT: ブラウザ互換性チェック（Chrome, Firefox, Safari, Edge）
- IMPORTANT: モバイル表示確認（iOS Safari, Android Chrome）
- IMPORTANT: アクセシビリティチェック（WCAG 2.1 AA準拠）
- IMPORTANT: パフォーマンステスト（3秒以内のページロード）

## 🤖 自動実行コマンド

### 品質チェック
```bash
# コード品質チェック
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python -m pylint app.py

# 型チェック（もしmypyを使用する場合）
# python -m mypy app.py --ignore-missing-imports
```

### テスト実行
```bash
# 単体テスト
python -m pytest tests/ -v

# 統合テスト
python test_ai_features.py
python test_gamification.py

# ペルソナテスト
python persona_comprehensive_test.py
python persona_diversity_test.py
python ultra_sync_user_behavior_test.py

# E2Eテスト（全ペルソナ）
python -c "
import subprocess
test_files = [
    'persona_comprehensive_test.py',
    'persona_diversity_test.py',
    'ultra_sync_user_behavior_test.py'
]
for test in test_files:
    print(f'Running {test}...')
    subprocess.run(['python', test])
"
```

### 画面キャプチャ
```bash
# スクリーンショット取得（Seleniumが必要）
python screenshot_all_pages.py

# 手動でのエラー画面確認
python -c "
from app import app
with app.test_client() as client:
    # エラーページの確認
    print('404 Error:', client.get('/nonexistent').status_code)
    print('Invalid data:', client.post('/exam', data={'invalid': 'data'}).status_code)
"
```

### レポート生成
```bash
# テスト結果レポート
python generate_test_report.py

# カバレッジレポート
python -m coverage run -m pytest
python -m coverage report
python -m coverage html

# パフォーマンスレポート
python performance_test.py
```

## 📋 チェックリスト

### デプロイ前チェックリスト
- [ ] 全ペルソナテスト合格（成功率95%以上）
- [ ] セキュリティテスト合格（SQLインジェクション、XSS、CSRF）
- [ ] アクセシビリティテスト合格（スクリーンリーダー対応）
- [ ] モバイル表示テスト合格
- [ ] パフォーマンステスト合格（3秒以内）
- [ ] エラーハンドリング確認
- [ ] ログ出力確認
- [ ] バックアップ作成

### 修正後チェックリスト
- [ ] 影響範囲の特定
- [ ] リグレッションテスト実行
- [ ] 修正前後の比較スクリーンショット
- [ ] パフォーマンス影響確認
- [ ] ドキュメント更新

# 🏆 MAXIMUM QUALITY STANDARDS - 最高品質基準

## 🚨 ABSOLUTE CRITICAL QUALITY RULES - 絶対的品質規則

### ❌ NEVER ALLOW - 絶対禁止事項（即座に作業停止）
1. **NEVER**: 構文エラー（SyntaxError）のあるコードを提出
2. **NEVER**: インデントエラー（IndentationError）のあるコードを提出  
3. **NEVER**: インポートエラー（ImportError）のあるコードを提出
4. **NEVER**: 実行時エラー（RuntimeError）のあるコードを提出
5. **NEVER**: 型エラー（TypeError）のあるコードを提出
6. **NEVER**: 名前エラー（NameError）のあるコードを提出
7. **NEVER**: テストしていないコードを提出
8. **NEVER**: 部分修正のみで全体チェックを怠る
9. **NEVER**: エラーログを無視して作業を続行
10. **NEVER**: 警告（Warning）を未解決のまま提出

### ✅ YOU MUST - 必須実行項目（100%実行義務）
1. **YOU MUST**: 修正前に必ず現在のコードの完全バックアップを作成
2. **YOU MUST**: 修正後に必ず `python3 -m py_compile app.py` で構文チェック
3. **YOU MUST**: 修正後に必ず `python3 -m flake8 app.py --max-line-length=200` で品質チェック
4. **YOU MUST**: 修正後に必ず `python3 -m pylint app.py --disable=C0114,C0115,C0116` でコード分析
5. **YOU MUST**: 修正後に必ず `python3 app.py` でローカル実行テスト（最低30秒間）
6. **YOU MUST**: 修正後に必ず `bash quality_check.sh` で総合品質チェック
7. **YOU MUST**: 修正後に必ず全エンドポイントのHTTPテスト実行
8. **YOU MUST**: 修正後に必ず10問完了テストを実行
9. **YOU MUST**: エラー修正時は影響範囲全体を再検証
10. **YOU MUST**: 全チェック合格後のみコードを提出

### MANDATORY CHECKS (必須チェック項目)

#### 1. 構文チェック (Syntax Check)
```bash
python -m py_compile app.py
# エラーが出た場合は絶対に修正完了まで作業継続
```

#### 2. インデントチェック (Indentation Check)  
```python
# Python構文として正しいインデントか確認
# if/elif/else/try/except/for/while の対応関係
# 4スペースまたは1タブの一貫性
```

#### 3. 実行テスト (Runtime Test)
```bash
python app.py
# 最低限の起動確認
# エラーログの完全確認
```

#### 4. 全体整合性チェック (Holistic Check)
```python
# 修正箇所が他の部分に影響していないか
# 変数名・関数名の一貫性
# import文の依存関係
```

## 🔧 CODE MODIFICATION PROTOCOL

### Step 1: 問題分析
- エラーログの完全解析
- 影響範囲の特定
- 根本原因の究明

### Step 2: 修正実装
- 最小限の変更で最大効果
- 副作用のない修正
- 可読性を維持した修正

### Step 3: 検証プロセス
```bash
# 必須実行コマンド
python -m py_compile app.py    # 構文チェック
python app.py                  # 実行チェック
curl http://localhost:5000     # 動作チェック
```

### Step 4: 品質確認
- ✅ 構文エラー: ゼロ
- ✅ インデントエラー: ゼロ  
- ✅ 実行エラー: ゼロ
- ✅ 機能テスト: 通過

## 🎯 QUALITY STANDARDS

### Acceptable Code Quality
- 構文エラー率: 0%
- インデントエラー率: 0%
- 実行成功率: 100%
- 機能テスト通過率: 100%

### Zero Tolerance Items
- SyntaxError
- IndentationError  
- ImportError
- 未テストコード

## 🚀 AUTOMATED QUALITY CHECKS

### Complete Quality Check Script (quality_check.sh)
```bash
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
python -m py_compile app.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax Check: PASSED${NC}"
else
    echo -e "${RED}❌ Syntax Check: FAILED${NC}"
    ((ERROR_COUNT++))
fi

# 2. インデントチェック
echo -e "${YELLOW}📋 Step 2: Indentation Check${NC}"
python -c "
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
python -c "
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
timeout 10s python app.py &
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
timeout 15s python app.py &
APP_PID=$!
sleep 5

# HTTP接続確認
curl -s http://localhost:5000 > /dev/null
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
```

### Quick Pre-Commit Check
```bash
# 簡易品質チェック
#!/bin/bash
echo "🔍 Quick Quality Check..."

# 構文チェック
python -m py_compile app.py
if [ $? -ne 0 ]; then
    echo "❌ Syntax Error Found"
    exit 1
fi

# 実行チェック  
timeout 10 python app.py &
PID=$!
sleep 5
kill $PID 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Runtime Error Found"
    exit 1
fi

echo "✅ Basic Quality Check Passed"
```

## 📋 DEPLOYMENT CHECKLIST

### Before Every Commit
- [ ] 構文チェック完了
- [ ] ローカル実行テスト完了
- [ ] 機能テスト完了
- [ ] エラーログ確認完了

### Before Every Deploy
- [ ] 全自動テスト通過
- [ ] 品質基準クリア
- [ ] バックアップ準備完了
- [ ] ロールバック計画準備完了

## 🎪 ERROR HANDLING PROTOCOL

### When Error Occurs
1. **STOP**: 即座に作業停止
2. **ANALYZE**: エラーの完全分析
3. **FIX**: 根本原因の修正
4. **VERIFY**: 3段階チェック実行
5. **CONFIRM**: 品質基準クリア確認

### Communication
- エラー発生時は必ず詳細報告
- 修正内容の明確な説明
- テスト結果の完全報告

## 💡 CONTINUOUS IMPROVEMENT

### Learning from Mistakes
- エラーパターンの記録
- 予防策の策定
- チェックリストの更新
- 自動化の強化

---

**Remember**: 品質は最優先事項。速度より正確性。完璧なコードのみ提出許可。