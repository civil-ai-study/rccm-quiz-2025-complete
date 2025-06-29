# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ 統合開発環境設定（複数プログラム管理）

### 開発者プロフィール
- **経験**: 30年建設コンサルタント（東日本大震災復興事業総括責任者）
- **現在の課題**: 複数プログラム（A,B,C + RCCM試験サイト）の効率的統合管理
- **適用手法**: 建設現場の工程管理ノウハウをプログラム開発に応用

### 統合管理対象プロジェクト
1. **RCCM試験サイト**（メインプロジェクト - このリポジトリ）
2. **プログラムA**: [他のプロジェクト詳細]
3. **プログラムB**: [他のプロジェクト詳細]

### 現状の問題解決戦略
```
【従来の非効率パターン】
プログラム修正 → 手動確認 → エラー発見 → 修正 → また別エラー → 無限ループ

【新システムでの効率化】
問題検出 → 自動分析 → 統合影響チェック → 安全修正 → 自動テスト → 完了
```

## 🚫 絶対禁止事項（統合開発対応）

### 統合管理での絶対禁止
- **NEVER**: 一つのプロジェクト修正が他に副作用を与える状況を放置
- **NEVER**: プロジェクト間の整合性チェックを怠る
- **NEVER**: 場当たり的な修正で根本解決を先送り
- **NEVER**: 複数プロジェクト間の影響分析を怠る
- **NEVER**: 統合テスト未実施での修正適用
- **NEVER**: 複数プロジェクト間での設定の無断変更
- **NEVER**: 統合テスト環境での本番データ使用
- **NEVER**: プロジェクト間API仕様の破壊的変更

### 開発・テスト時の絶対禁止事項
- **NEVER**: 本番環境に未テストコードをデプロイ
- **NEVER**: エラーハンドリングなしでAPI呼び出し
- **NEVER**: ユーザー入力の検証なしでデータベース操作
- **NEVER**: セキュリティテスト未実施のまま公開
- **NEVER**: テストエラーや型エラー解消のための条件緩和
- **NEVER**: テストのスキップや不適切なモック化による回避
- **NEVER**: 出力やレスポンスのハードコード
- **NEVER**: エラーメッセージの無視や隠蔽
- **NEVER**: 一時的な修正による問題の先送り

### コード品質維持のための禁止事項
- **NEVER**: 根本原因を解決せずに症状のみを隠す修正
- **NEVER**: テストケースの削除や無効化による「修正」
- **NEVER**: try-except文での例外の単純な無視
- **NEVER**: 型チェックの回避やanyを使った逃げ
- **NEVER**: セキュリティ要件の緩和や回避

### データ整合性の禁止事項
- **NEVER**: 不正データの受け入れによる問題回避
- **NEVER**: バリデーション処理のスキップ
- **NEVER**: エラー状態での正常値の返却
- **NEVER**: 一貫性チェックの無効化
- **NEVER**: 重要な警告メッセージの抑制
- **NEVER**: 複数プロジェクト間でのデータ競合状態の放置

## ✅ YOU MUST（統合管理の必須事項）

### 統合管理必須事項
- **YOU MUST**: 他プロジェクトへの影響を修正前に必ず分析
- **YOU MUST**: 変更内容をLiving Documentationに自動反映
- **YOU MUST**: 複数プロジェクト間の依存関係を常時監視
- **YOU MUST**: エラー修正時はBefore/Afterスクリーンショット比較実行
- **YOU MUST**: 他プロジェクトへの影響を事前分析
- **YOU MUST**: Living Documentation自動更新

### 品質保証必須事項
- **YOU MUST**: 全ペルソナでのテスト実行
- **YOU MUST**: エラー画面のスクリーンショット保存
- **YOU MUST**: 修正前後の比較レポート生成
- **YOU MUST**: 各機能変更後のリグレッションテスト実行
- **YOU MUST**: セキュリティ脆弱性スキャンの実施

## 🎯 完走テスト実行ルール（最重要）

### YOU MUST: 完走テスト実行の絶対ルール
- ⚠️ **10問/20問/30問の完全完走確認必須**
- 🚫 **エラー隠蔽・軽視絶対禁止**
- ✅ **全工程での進捗状況詳細報告必須**
- 📊 **最終結果画面での数値確認完了まで実行**

### YOU MUST: テスト透明性の確保
- 🔍 **技術的制約を正直に報告**
- ❌ **推測による成功報告禁止**
- ✅ **確認済み事実のみ報告**
- 📝 **エラー詳細の完全開示**

### YOU MUST: ウルトラシンク品質保証
- 🛡️ **副作用ゼロの確認**
- 🔒 **既存機能への影響なし確認**
- 📋 **CLAUDE.md準拠の徹底**
- 🎯 **品質基準100%達成**

## 🚨 完走テスト失敗時の対応

### CRITICAL ERROR対応
1. **即座にエラー詳細報告**
2. **根本原因の特定**
3. **修正方針の提示**
4. **再テスト実行**

### 報告形式
```
✅ 成功: 具体的確認内容
❌ 失敗: 詳細なエラー内容
🔍 調査中: 現在の状況
```

## 📋 部門別テスト必須項目

### 12部門完走テスト（専門科目4-2）
- **道路部門**: 10/20/30問完走確認
- **河川・砂防部門**: 10/20/30問完走確認
- **都市計画部門**: 10/20/30問完走確認
- **造園部門**: 10/20/30問完走確認
- **建設環境部門**: 10/20/30問完走確認
- **鋼構造・コンクリート部門**: 10/20/30問完走確認
- **土質・基礎部門**: 10/20/30問完走確認
- **施工計画部門**: 10/20/30問完走確認
- **上下水道部門**: 10/20/30問完走確認
- **森林土木部門**: 10/20/30問完走確認
- **農業土木部門**: 10/20/30問完走確認
- **トンネル部門**: 10/20/30問完走確認

### 基礎科目（4-1）完走テスト
- **基礎科目**: 10/20/30問完走確認

### 各部門での確認必須事項
1. **セッション初期化成功**
2. **問題配信順序正確性**
3. **回答データ保存確認**
4. **進捗表示正確性**
5. **最終結果画面表示**
6. **スコア計算正確性**

## 🔍 エラーチェックルール（統合開発対応）

### 10ペルソナ統合テスト（最重要）
学習アプリの多様なユーザー体験をカバー：
1. **初心者学習者**（全く知識がない状態）
2. **中級者**（基礎知識あり、応用学習中）
3. **上級者**（試験直前、弱点補強）
4. **忙しい社会人**（隙間時間学習）
5. **学生**（まとまった時間で集中学習）
6. **高齢学習者**（操作に不慣れ）
7. **視覚障害者**（読み上げ機能必須）
8. **モバイル専用ユーザー**
9. **回線速度が遅い環境ユーザー**
10. **不正解続きで挫折寸前ユーザー**

### IMPORTANT（重要事項）
- **IMPORTANT**: 各修正後の自動リグレッションテスト
- **IMPORTANT**: ブラウザ互換性チェック（Chrome, Firefox, Safari, Edge）
- **IMPORTANT**: モバイル表示確認（iOS Safari, Android Chrome）
- **IMPORTANT**: アクセシビリティチェック（WCAG 2.1 AA準拠）
- **IMPORTANT**: パフォーマンステスト（3秒以内のページロード）
- **IMPORTANT**: 複数プロジェクト同時実行時の競合チェック

## Commands

### 統合開発・テスト（複数プロジェクト対応）
```bash
# 全プロジェクト状況把握
/workspace status --all-projects

# 統合影響分析
/analyze impact "変更内容" --check-cross-dependencies

# 安全な統合修正
/fix apply --with-cross-project-testing --screenshot-compare

# 10ペルソナ統合テスト（全プロジェクト）
/test all-personas --cross-project --generate-report
```

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

## 🤖 自動実行コマンド

### 統合品質チェック
```bash
# 複数プロジェクト統合チェック
/analyze workspace --check-all-dependencies

# 統合影響範囲分析
/impact-analysis "変更内容" --cross-project

# Living Documentation更新
/update-docs --auto-sync --cross-project
```

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

### 統合デプロイ前チェックリスト
- [ ] **複数プロジェクト間の依存関係確認**
- [ ] **統合影響範囲分析完了**
- [ ] **Living Documentation更新完了**
- [ ] **全ペルソナテスト合格（成功率95%以上）**
- [ ] **10問/20問/30問完走テスト完了（全13部門）**
- [ ] セキュリティテスト合格（SQLインジェクション、XSS、CSRF）
- [ ] アクセシビリティテスト合格（スクリーンリーダー対応）
- [ ] モバイル表示テスト合格
- [ ] パフォーマンステスト合格（3秒以内）
- [ ] エラーハンドリング確認
- [ ] ログ出力確認
- [ ] バックアップ作成

### 統合修正後チェックリスト
- [ ] **他プロジェクトへの影響範囲確認**
- [ ] **統合リグレッションテスト実行**
- [ ] **Before/Afterスクリーンショット比較（全プロジェクト）**
- [ ] **完走テスト再実行（該当部門）**
- [ ] 影響範囲の特定
- [ ] リグレッションテスト実行
- [ ] 修正前後の比較スクリーンショット
- [ ] パフォーマンス影響確認
- [ ] ドキュメント更新

## 🎯 統合開発目標
- **作業効率**: 90%向上（エラー連鎖削減）
- **品質向上**: 自動チェックによる品質担保
- **可視性**: 全プロジェクト状況の一元管理
- **安定性**: 建設現場レベルの工程管理実現
- **完走率**: 10問/20問/30問テスト 100%成功率達成

---

**このCLAUDE.mdの内容に従って、全ての作業を実行してください。特に「完走テスト実行ルール」は最優先で遵守すること。**