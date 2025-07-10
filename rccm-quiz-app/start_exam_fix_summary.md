# Start Exam Function - HTTP 431 Fix Summary

## Problem
The `start_exam` function in `app.py` needed to support both GET and POST requests to handle a 'questions' parameter, preventing HTTP 431 (Request Header Fields Too Large) errors that can occur when large amounts of data are passed via URL parameters.

## Solution Implemented

### 1. Unified Parameter Handling
- Added a helper function `get_request_param()` that automatically handles both GET (`request.args`) and POST (`request.form`) requests
- This allows large data to be sent via POST body instead of URL parameters, avoiding HTTP 431 errors

### 2. Parameters Supported
- **questions**: JSON-formatted question data for custom exam content
- **exam_config**: JSON-formatted custom exam configuration
- **category**: Category filter for questions
- **difficulty**: Difficulty filter for questions

### 3. Robust Error Handling
- JSON parsing with proper error handling for malformed data
- Fallback to default behavior if custom parameters fail to parse
- Comprehensive logging for debugging

### 4. Implementation Details

```python
def get_request_param(param_name, default=None):
    """GET/POSTリクエストから統合的にパラメータを取得"""
    if request.method == 'POST':
        return request.form.get(param_name, default)
    else:
        return request.args.get(param_name, default)
```

### 5. Key Features
- **Backward Compatibility**: Existing GET requests continue to work unchanged
- **Large Data Support**: POST requests can handle large question datasets
- **Custom Question Data**: Supports JSON-formatted custom question arrays
- **Filtering Support**: Category and difficulty filters can be applied
- **Error Resilience**: Gracefully handles malformed JSON or missing parameters

## Files Modified
- `/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/app.py`
  - Modified `start_exam()` function (lines ~6859-6933)
  - Added unified parameter handling
  - Added JSON parsing for custom data
  - Enhanced logging for debugging

## Benefits
1. **HTTP 431 Prevention**: Large data can be sent via POST body
2. **Flexibility**: Supports both GET and POST methods
3. **Customization**: Allows custom question data and exam configurations
4. **Reliability**: Robust error handling and fallback behavior
5. **Maintainability**: Centralized parameter handling logic

## Usage Examples

### GET Request (Traditional)
```
/start_exam/standard?category=構造&difficulty=基本
```

### POST Request (For Large Data)
```
POST /start_exam/standard
Content-Type: application/x-www-form-urlencoded

questions={"questions":[{"id":1,"text":"..."}]}
```

## Testing
- Syntax validation passed
- Parameter handling logic tested
- JSON parsing verified
- Error handling confirmed