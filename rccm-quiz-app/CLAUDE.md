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