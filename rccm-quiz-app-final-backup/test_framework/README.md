# 🧪 RCCM Quiz Comprehensive Test Framework

## Overview

This comprehensive testing framework validates the RCCM Quiz Application across **13 departments** with **3 question count variations** (10, 20, 30 questions), resulting in **39 total test cases**.

## Architecture

```
test_framework/
├── core/
│   └── test_runner.py          # Main test execution engine
├── validators/
│   ├── data_validator.py       # Department data validation
│   ├── department_validator.py # Department loading validation
│   └── flow_validator.py       # Complete quiz flow validation
├── reporters/
│   ├── logger.py              # Comprehensive test logging
│   ├── html_reporter.py       # HTML report generation
│   └── json_reporter.py       # JSON report generation
└── utils/
    ├── api_client.py          # HTTP client for API testing
    └── browser_automation.py  # Selenium-based UI testing
```

## Test Matrix

### Departments (13 total)
- **基礎科目** (Basic Subject)
- **道路部門** (Road Department)
- **河川・砂防部門** (River & Erosion Control)
- **都市計画部門** (Urban Planning)
- **造園部門** (Landscape)
- **建設環境部門** (Construction Environment)
- **鋼構造・コンクリート部門** (Steel & Concrete)
- **土質・基礎部門** (Soil & Foundation)
- **施工計画部門** (Construction Planning)
- **上下水道部門** (Water Supply & Drainage)
- **森林土木部門** (Forestry Civil Engineering)
- **農業土木部門** (Agricultural Civil Engineering)
- **トンネル部門** (Tunnel Department)

### Question Counts (3 variations)
- **10 questions**: Quick practice session
- **20 questions**: Standard practice session (30 min)
- **30 questions**: Intensive exam simulation (45 min)

### Total Test Cases: 13 × 3 = 39

## Validation Steps

Each test case validates:

1. **Department Loading**: Validates department configuration and data availability
2. **Question Count Configuration**: Validates question count settings and session setup
3. **Complete Flow Validation**: Tests entire quiz flow from start to results:
   - Session initialization
   - First question display
   - Answer submission and navigation
   - Session persistence
   - Final results calculation

## Usage

### Run All Tests
```bash
python run_comprehensive_tests.py --all
```

### Run Tests for Specific Department
```bash
python run_comprehensive_tests.py --department 基礎科目
```

### Run Tests for Specific Question Count
```bash
python run_comprehensive_tests.py --questions 10
```

### Parallel Execution
```bash
python run_comprehensive_tests.py --all --parallel --workers 4
```

### Validation Only
```bash
# Validate test environment
python run_comprehensive_tests.py --validate-environment

# Validate department data
python run_comprehensive_tests.py --validate-data
```

## Test Framework Components

### Core Test Runner
The `ComprehensiveTestRunner` coordinates all test execution:
- Manages 39 test cases systematically
- Supports both sequential and parallel execution
- Provides real-time progress tracking
- Implements retry logic with exponential backoff
- Generates comprehensive reports

### Validators

#### Data Validator
- Validates question availability for all departments
- Checks data integrity and encoding support
- Verifies minimum question requirements (15+ for 10q, 25+ for 20q, 35+ for 30q)

#### Department Validator
- Validates department loading and configuration
- Tests URL parameter generation
- Verifies session configuration for each question count

#### Flow Validator
- Tests complete quiz flow end-to-end
- Simulates user interactions via HTTP requests
- Validates session persistence and state management
- Confirms final results calculation

### Reporters

#### Logger
- Structured logging with real-time monitoring
- Session tracking and progress reporting
- Error recovery logging
- JSON and text log output

#### HTML Reporter
- Interactive HTML reports with charts
- Department and question count analysis
- Performance metrics and trends
- Bootstrap-based responsive design

#### JSON Reporter
- Machine-readable structured reports
- Quality metrics and recommendations
- Integration-ready format for CI/CD
- Comprehensive analysis data

### Utilities

#### API Client
- HTTP client with retry logic and error handling
- Session management and cookie handling
- Request/response validation
- Timeout and connection error recovery

#### Browser Automation
- Selenium-based UI testing (optional)
- Screenshot capture for visual validation
- Cross-browser compatibility testing
- Headless and GUI modes

## Quality Gates

The framework enforces the following quality gates:

- **100% Department Coverage**: All 13 departments must be tested
- **100% Question Count Coverage**: All 3 question counts must work
- **95%+ Success Rate**: At least 95% of test cases must pass
- **Error Recovery**: All error scenarios must recover within 60 seconds
- **Performance**: Response times must be within acceptable limits

## Reports and Output

### Generated Reports
- `results/reports/test_report_YYYYMMDD_HHMMSS.html` - Interactive HTML report
- `results/reports/test_report_YYYYMMDD_HHMMSS.json` - Structured JSON report
- `results/logs/test_session_YYYYMMDD_HHMMSS.log` - Detailed text logs
- `results/logs/test_session_YYYYMMDD_HHMMSS.json` - Structured log data

### Screenshots (if browser automation enabled)
- `results/screenshots/` - Visual validation screenshots

## Success Criteria

For the testing framework to pass, the following criteria must be met:

1. **Complete Test Execution**: All 39 test cases executed
2. **100% Success Rate**: All test cases must pass
3. **Quality Gates**: All quality gates must be satisfied
4. **Performance**: All tests complete within acceptable time limits
5. **Error Recovery**: All error scenarios properly handled

## Error Handling

The framework implements comprehensive error handling:

- **Network Timeouts**: Automatic retry with exponential backoff
- **Session Failures**: Session recovery and state restoration
- **Data Issues**: Fallback mechanisms and error reporting
- **Connection Errors**: Retry logic with configurable limits

## Integration

### CI/CD Integration
```bash
# Example CI/CD pipeline step
python run_comprehensive_tests.py --all --parallel --log-level INFO
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed - deployment approved"
else
    echo "❌ Tests failed - deployment blocked"
    exit 1
fi
```

### Custom Extensions
The framework is designed for extensibility:
- Add new validators by extending base classes
- Create custom reporters for specific formats
- Implement additional utilities for specialized testing

## Dependencies

### Required
- Python 3.7+
- requests library
- Standard library modules (json, logging, datetime, etc.)

### Optional
- selenium (for browser automation)
- webdriver (Chrome/Firefox) for UI testing

## Installation

```bash
# Install required dependencies
pip install requests

# Optional: Install Selenium for browser automation
pip install selenium
```

## Configuration

The framework uses configuration in the test components:
- API endpoints and timeouts in `api_client.py`
- Browser settings in `browser_automation.py`
- Department mappings in validators
- Question count requirements in data validator

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure Flask application is running on `http://localhost:5000`
2. **Import Errors**: Check Python path and test framework installation
3. **Selenium Issues**: Install appropriate WebDriver for browser automation
4. **Timeout Errors**: Increase timeout values in configuration

### Debug Mode
```bash
python run_comprehensive_tests.py --all --log-level DEBUG
```

---

**Framework Version**: 1.0.0  
**Compatible with**: RCCM Quiz Application  
**Test Coverage**: 13 departments × 3 question counts = 39 test cases  
**Success Requirement**: 100% test case success rate