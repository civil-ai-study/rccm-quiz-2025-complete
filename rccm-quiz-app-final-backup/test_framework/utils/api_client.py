#!/usr/bin/env python3
"""
🌐 API Client - Flask Application Testing Client
Provides HTTP client functionality for testing RCCM Quiz Application
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import urllib.parse

class FlaskTestClient:
    """HTTP client for testing Flask application endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Connection settings
        self.session.headers.update({
            'User-Agent': 'RCCM-Test-Framework/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Retry configuration
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 1,  # seconds
            'backoff_factor': 2
        }

    def validate_connection(self) -> bool:
        """Validate connection to Flask application"""
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Connection validated: {self.base_url}")
                return True
            else:
                self.logger.error(f"❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Connection error: Cannot connect to {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Connection timeout: {self.base_url}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Connection validation error: {e}")
            return False

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            follow_redirects: bool = True) -> Dict[str, Any]:
        """Perform GET request with error handling and retries"""
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.retry_config['max_retries']):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    allow_redirects=follow_redirects
                )
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'content': response.text,
                    'headers': dict(response.headers),
                    'url': response.url,
                    'cookies': dict(response.cookies),
                    'response_time': response.elapsed.total_seconds()
                }
                
            except requests.exceptions.Timeout:
                if attempt < self.retry_config['max_retries'] - 1:
                    delay = self.retry_config['retry_delay'] * (self.retry_config['backoff_factor'] ** attempt)
                    self.logger.warning(f"⚠️ GET timeout, retrying in {delay}s (attempt {attempt + 2})")
                    time.sleep(delay)
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Timeout after {self.retry_config['max_retries']} attempts",
                        'error_type': 'timeout'
                    }
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.retry_config['max_retries'] - 1:
                    delay = self.retry_config['retry_delay'] * (self.retry_config['backoff_factor'] ** attempt)
                    self.logger.warning(f"⚠️ Connection error, retrying in {delay}s (attempt {attempt + 2})")
                    time.sleep(delay)
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Connection error after {self.retry_config['max_retries']} attempts",
                        'error_type': 'connection_error'
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'error_type': 'unknown_error'
                }
        
        return {
            'success': False,
            'error': 'Maximum retries exceeded',
            'error_type': 'max_retries_exceeded'
        }

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             json_data: Optional[Dict[str, Any]] = None, 
             follow_redirects: bool = True) -> Dict[str, Any]:
        """Perform POST request with error handling and retries"""
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.retry_config['max_retries']):
            try:
                if json_data:
                    response = self.session.post(
                        url,
                        json=json_data,
                        timeout=self.timeout,
                        allow_redirects=follow_redirects
                    )
                else:
                    response = self.session.post(
                        url,
                        data=data,
                        timeout=self.timeout,
                        allow_redirects=follow_redirects
                    )
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'content': response.text,
                    'headers': dict(response.headers),
                    'url': response.url,
                    'cookies': dict(response.cookies),
                    'response_time': response.elapsed.total_seconds()
                }
                
            except requests.exceptions.Timeout:
                if attempt < self.retry_config['max_retries'] - 1:
                    delay = self.retry_config['retry_delay'] * (self.retry_config['backoff_factor'] ** attempt)
                    self.logger.warning(f"⚠️ POST timeout, retrying in {delay}s (attempt {attempt + 2})")
                    time.sleep(delay)
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Timeout after {self.retry_config['max_retries']} attempts",
                        'error_type': 'timeout'
                    }
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.retry_config['max_retries'] - 1:
                    delay = self.retry_config['retry_delay'] * (self.retry_config['backoff_factor'] ** attempt)
                    self.logger.warning(f"⚠️ Connection error, retrying in {delay}s (attempt {attempt + 2})")
                    time.sleep(delay)
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Connection error after {self.retry_config['max_retries']} attempts",
                        'error_type': 'connection_error'
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'error_type': 'unknown_error'
                }
        
        return {
            'success': False,
            'error': 'Maximum retries exceeded',
            'error_type': 'max_retries_exceeded'
        }

    def create_quiz_session(self, department: str, question_count: int) -> Dict[str, Any]:
        """Create a new quiz session"""
        # Map department to URL parameter
        department_mapping = {
            '基礎科目': 'basic',
            '道路部門': 'road',
            '河川・砂防部門': 'civil_planning',
            '都市計画部門': 'urban_planning',
            '造園部門': 'landscape',
            '建設環境部門': 'construction_env',
            '鋼構造・コンクリート部門': 'steel_concrete',
            '土質・基礎部門': 'soil_foundation',
            '施工計画部門': 'construction_planning',
            '上下水道部門': 'water_supply',
            '森林土木部門': 'forestry',
            '農業土木部門': 'agriculture',
            'トンネル部門': 'tunnel'
        }
        
        dept_param = department_mapping.get(department, 'basic')
        
        params = {
            'department': dept_param,
            'count': question_count
        }
        
        # Start quiz session
        result = self.get('/quiz', params=params)
        
        if result['success']:
            # Extract session information from response
            session_info = self._extract_session_info(result)
            return {
                'success': True,
                'session_info': session_info,
                'response': result
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to create quiz session'),
                'response': result
            }

    def submit_answer(self, answer: str, current_question: int) -> Dict[str, Any]:
        """Submit an answer for the current question"""
        data = {
            'answer': answer.lower(),
            'current': current_question
        }
        
        result = self.post('/exam', data=data)
        
        if result['success']:
            # Check if we're on feedback page or results page
            feedback_info = self._extract_feedback_info(result)
            return {
                'success': True,
                'feedback_info': feedback_info,
                'response': result
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to submit answer'),
                'response': result
            }

    def get_quiz_status(self) -> Dict[str, Any]:
        """Get current quiz session status"""
        result = self.get('/quiz')
        
        if result['success']:
            session_info = self._extract_session_info(result)
            return {
                'success': True,
                'session_info': session_info,
                'response': result
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to get quiz status'),
                'response': result
            }

    def get_results(self) -> Dict[str, Any]:
        """Get quiz results"""
        result = self.get('/results')
        
        if result['success']:
            results_info = self._extract_results_info(result)
            return {
                'success': True,
                'results_info': results_info,
                'response': result
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to get results'),
                'response': result
            }

    def reset_session(self) -> Dict[str, Any]:
        """Reset the current session"""
        result = self.get('/force_reset')
        
        return {
            'success': result['success'],
            'response': result
        }

    def _extract_session_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract session information from response"""
        content = response.get('content', '')
        
        session_info = {
            'has_quiz_session': False,
            'current_question': 0,
            'total_questions': 0,
            'progress_text': '',
            'question_text': '',
            'answer_options': [],
            'session_id': response.get('cookies', {}).get('session', 'unknown')
        }
        
        # Check if we're in a quiz session
        if 'quiz_current' in content or 'quiz-container' in content:
            session_info['has_quiz_session'] = True
            
            # Extract progress information
            # Look for patterns like "1/10", "2/20", etc.
            import re
            progress_match = re.search(r'(\d+)/(\d+)', content)
            if progress_match:
                session_info['current_question'] = int(progress_match.group(1))
                session_info['total_questions'] = int(progress_match.group(2))
                session_info['progress_text'] = progress_match.group(0)
            
            # Extract question text (simplified)
            if 'question-text' in content:
                # Find question text section
                question_start = content.find('question-text')
                if question_start != -1:
                    # Extract a portion of text around the question
                    question_section = content[question_start:question_start + 500]
                    session_info['question_text'] = 'Question found'
            
            # Extract answer options
            options = []
            for option in ['A', 'B', 'C', 'D']:
                if f'value="{option.lower()}"' in content:
                    options.append(option)
            session_info['answer_options'] = options
        
        return session_info

    def _extract_feedback_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract feedback information from response"""
        content = response.get('content', '')
        
        feedback_info = {
            'is_feedback_page': False,
            'is_results_page': False,
            'correct_answer': '',
            'user_answer': '',
            'explanation': '',
            'progress_text': '',
            'next_button_available': False,
            'results_button_available': False
        }
        
        # Check if we're on feedback page
        if 'feedback' in content.lower() or 'correct' in content.lower():
            feedback_info['is_feedback_page'] = True
            
            # Look for next button
            if '次の問題' in content or 'next' in content.lower():
                feedback_info['next_button_available'] = True
            
            # Look for results button
            if '結果' in content or 'results' in content.lower():
                feedback_info['results_button_available'] = True
        
        # Check if we're on results page
        if 'results' in content.lower() or 'score' in content.lower() or '点' in content:
            feedback_info['is_results_page'] = True
        
        return feedback_info

    def _extract_results_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract results information from response"""
        content = response.get('content', '')
        
        results_info = {
            'is_results_page': False,
            'score_text': '',
            'total_questions': 0,
            'correct_answers': 0,
            'percentage': 0,
            'completion_time': '',
            'has_score_breakdown': False
        }
        
        # Check if we're on results page
        if any(keyword in content.lower() for keyword in ['results', 'score', '結果', '点数', '正解']):
            results_info['is_results_page'] = True
            
            # Extract score information
            import re
            
            # Look for score patterns like "7/10", "15/20", etc.
            score_match = re.search(r'(\d+)/(\d+)', content)
            if score_match:
                results_info['correct_answers'] = int(score_match.group(1))
                results_info['total_questions'] = int(score_match.group(2))
                results_info['score_text'] = score_match.group(0)
                
                if results_info['total_questions'] > 0:
                    results_info['percentage'] = (results_info['correct_answers'] / results_info['total_questions']) * 100
            
            # Look for percentage patterns
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', content)
            if percentage_match:
                results_info['percentage'] = float(percentage_match.group(1))
        
        return results_info

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

if __name__ == "__main__":
    # Test the API client
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    with FlaskTestClient() as client:
        # Test connection
        if client.validate_connection():
            print("✅ Connection test passed")
            
            # Test quiz session creation
            session_result = client.create_quiz_session('基礎科目', 10)
            if session_result['success']:
                print("✅ Quiz session creation test passed")
                print(f"Session info: {session_result['session_info']}")
                
                # Test answer submission
                answer_result = client.submit_answer('a', 1)
                if answer_result['success']:
                    print("✅ Answer submission test passed")
                    print(f"Feedback info: {answer_result['feedback_info']}")
                else:
                    print(f"❌ Answer submission test failed: {answer_result['error']}")
            else:
                print(f"❌ Quiz session creation test failed: {session_result['error']}")
        else:
            print("❌ Connection test failed")
    
    print("API client test completed.")