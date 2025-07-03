#!/usr/bin/env python3
"""
🔄 Flow Validator - Complete Quiz Flow Validation
Validates complete quiz flow from start to results for all question counts
"""

import sys
import os
import time
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
import urllib.parse

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class FlowValidator:
    """Validates complete quiz flow from start to results"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        
        # Department configuration mapping
        self.department_config = {
            '基礎科目': {
                'url_param': 'basic',
                'category_filter': '共通',
                'expected_questions': 'basic_subject'
            },
            '道路部門': {
                'url_param': 'road',
                'category_filter': '道路',
                'expected_questions': 'specialist'
            },
            '河川・砂防部門': {
                'url_param': 'civil_planning',
                'category_filter': '河川、砂防及び海岸・海洋',
                'expected_questions': 'specialist'
            },
            '都市計画部門': {
                'url_param': 'urban_planning',
                'category_filter': '都市計画及び地方計画',
                'expected_questions': 'specialist'
            },
            '造園部門': {
                'url_param': 'landscape',
                'category_filter': '造園',
                'expected_questions': 'specialist'
            },
            '建設環境部門': {
                'url_param': 'construction_env',
                'category_filter': '建設環境',
                'expected_questions': 'specialist'
            },
            '鋼構造・コンクリート部門': {
                'url_param': 'steel_concrete',
                'category_filter': '鋼構造及びコンクリート',
                'expected_questions': 'specialist'
            },
            '土質・基礎部門': {
                'url_param': 'soil_foundation',
                'category_filter': '土質及び基礎',
                'expected_questions': 'specialist'
            },
            '施工計画部門': {
                'url_param': 'construction_planning',
                'category_filter': '施工計画、施工設備及び積算',
                'expected_questions': 'specialist'
            },
            '上下水道部門': {
                'url_param': 'water_supply',
                'category_filter': '上水道及び工業用水道',
                'expected_questions': 'specialist'
            },
            '森林土木部門': {
                'url_param': 'forestry',
                'category_filter': '森林土木',
                'expected_questions': 'specialist'
            },
            '農業土木部門': {
                'url_param': 'agriculture',
                'category_filter': '農業土木',
                'expected_questions': 'specialist'
            },
            'トンネル部門': {
                'url_param': 'tunnel',
                'category_filter': 'トンネル',
                'expected_questions': 'specialist'
            }
        }
        
        # Question count configurations
        self.question_count_configs = [10, 20, 30]
        
        # Flow validation steps
        self.flow_steps = [
            'session_initialization',
            'first_question_display',
            'answer_submission',
            'progress_navigation',
            'session_persistence',
            'final_results_calculation'
        ]
        
        # Request timeout settings
        self.timeout_config = {
            'connection_timeout': 10,  # seconds
            'read_timeout': 30,        # seconds
            'total_timeout': 60        # seconds for complete flow
        }

    def validate_complete_flow(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate complete quiz flow for specific department and question count"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🔄 Validating complete flow: {department} - {question_count} questions")
            
            if department not in self.department_config:
                return {
                    'valid': False,
                    'error': f"Unknown department: {department}",
                    'execution_time': time.time() - start_time
                }
            
            if question_count not in self.question_count_configs:
                return {
                    'valid': False,
                    'error': f"Unsupported question count: {question_count}",
                    'execution_time': time.time() - start_time
                }
            
            # Execute flow validation steps
            flow_results = {}
            session_data = {}
            
            # Step 1: Session initialization
            init_result = self._validate_session_initialization(department, question_count, session_data)
            flow_results['session_initialization'] = init_result
            
            if not init_result['valid']:
                return {
                    'valid': False,
                    'error': f"Session initialization failed: {init_result['error']}",
                    'execution_time': time.time() - start_time,
                    'flow_results': flow_results
                }
            
            # Step 2: First question display
            question_result = self._validate_first_question_display(session_data)
            flow_results['first_question_display'] = question_result
            
            if not question_result['valid']:
                return {
                    'valid': False,
                    'error': f"First question display failed: {question_result['error']}",
                    'execution_time': time.time() - start_time,
                    'flow_results': flow_results
                }
            
            # Step 3: Answer submission and navigation
            navigation_result = self._validate_answer_submission_flow(session_data, question_count)
            flow_results['answer_submission_navigation'] = navigation_result
            
            if not navigation_result['valid']:
                return {
                    'valid': False,
                    'error': f"Answer submission/navigation failed: {navigation_result['error']}",
                    'execution_time': time.time() - start_time,
                    'flow_results': flow_results
                }
            
            # Step 4: Session persistence validation
            persistence_result = self._validate_session_persistence(session_data)
            flow_results['session_persistence'] = persistence_result
            
            if not persistence_result['valid']:
                return {
                    'valid': False,
                    'error': f"Session persistence failed: {persistence_result['error']}",
                    'execution_time': time.time() - start_time,
                    'flow_results': flow_results
                }
            
            # Step 5: Final results validation
            results_validation = self._validate_final_results(session_data, question_count)
            flow_results['final_results'] = results_validation
            
            if not results_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Final results validation failed: {results_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'flow_results': flow_results
                }
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"✅ Complete flow validation passed: {department} - {question_count}q ({execution_time:.2f}s)")
            
            return {
                'valid': True,
                'department': department,
                'question_count': question_count,
                'execution_time': execution_time,
                'flow_results': flow_results,
                'session_summary': {
                    'session_id': session_data.get('session_id'),
                    'questions_answered': session_data.get('questions_answered', 0),
                    'final_score': session_data.get('final_score'),
                    'completion_rate': session_data.get('completion_rate', 0)
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Complete flow validation error: {department} - {question_count}q: {e}")
            
            return {
                'valid': False,
                'error': str(e),
                'execution_time': execution_time,
                'department': department,
                'question_count': question_count
            }

    def _validate_session_initialization(self, department: str, question_count: int, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate session initialization step"""
        try:
            config = self.department_config[department]
            
            # Build quiz start URL
            params = {
                'department': config['url_param'],
                'count': question_count
            }
            
            quiz_url = f"{self.base_url}/quiz?" + urllib.parse.urlencode(params)
            
            # Create session and make initial request
            session = requests.Session()
            session_data['requests_session'] = session
            
            response = session.get(
                quiz_url,
                timeout=(self.timeout_config['connection_timeout'], self.timeout_config['read_timeout'])
            )
            
            if response.status_code != 200:
                return {
                    'valid': False,
                    'error': f"Quiz initialization failed with status {response.status_code}"
                }
            
            # Check for quiz session data in response
            if 'quiz_current' not in response.text or 'quiz_total' not in response.text:
                return {
                    'valid': False,
                    'error': "Quiz session data not found in response"
                }
            
            # Validate question count in response
            if f"/{question_count}" not in response.text:
                return {
                    'valid': False,
                    'error': f"Expected question count {question_count} not found in response"
                }
            
            # Store session information
            session_data.update({
                'session_id': session.cookies.get('session', 'unknown'),
                'department': department,
                'question_count': question_count,
                'initialization_response': response.text,
                'current_question': 1,
                'questions_answered': 0
            })
            
            return {
                'valid': True,
                'session_id': session_data['session_id'],
                'response_status': response.status_code,
                'department_verified': department in response.text,
                'question_count_verified': str(question_count) in response.text
            }
            
        except requests.exceptions.Timeout:
            return {
                'valid': False,
                'error': "Session initialization timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                'valid': False,
                'error': "Connection error during session initialization"
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Session initialization error: {e}"
            }

    def _validate_first_question_display(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate first question display"""
        try:
            session = session_data['requests_session']
            
            # The session should already be on the first question from initialization
            response_text = session_data['initialization_response']
            
            # Check for essential question elements
            required_elements = [
                'question-text',  # Question content
                'options',        # Answer options
                'submit-btn',     # Submit button
                'progress'        # Progress indicator
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in response_text:
                    missing_elements.append(element)
            
            if missing_elements:
                return {
                    'valid': False,
                    'error': f"Missing required elements: {missing_elements}"
                }
            
            # Check for progress display (1/N format)
            if f"1/{session_data['question_count']}" not in response_text:
                return {
                    'valid': False,
                    'error': f"Progress indicator not showing 1/{session_data['question_count']}"
                }
            
            # Check for answer options (A, B, C, D)
            option_count = 0
            for option in ['A', 'B', 'C', 'D']:
                if f'value="{option.lower()}"' in response_text:
                    option_count += 1
            
            if option_count < 4:
                return {
                    'valid': False,
                    'error': f"Expected 4 answer options, found {option_count}"
                }
            
            return {
                'valid': True,
                'question_elements_found': len(required_elements) - len(missing_elements),
                'progress_display_correct': True,
                'answer_options_count': option_count,
                'response_length': len(response_text)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"First question display validation error: {e}"
            }

    def _validate_answer_submission_flow(self, session_data: Dict[str, Any], question_count: int) -> Dict[str, Any]:
        """Validate answer submission and navigation flow"""
        try:
            session = session_data['requests_session']
            
            # Simulate answering first few questions to test flow
            test_questions = min(3, question_count)  # Test first 3 questions or all if less
            
            for question_num in range(1, test_questions + 1):
                # Submit answer for current question
                answer_data = {
                    'answer': 'a',  # Always choose option A for testing
                    'current': question_num
                }
                
                submit_response = session.post(
                    f"{self.base_url}/exam",
                    data=answer_data,
                    timeout=(self.timeout_config['connection_timeout'], self.timeout_config['read_timeout'])
                )
                
                if submit_response.status_code not in [200, 302]:
                    return {
                        'valid': False,
                        'error': f"Answer submission failed for question {question_num}: status {submit_response.status_code}"
                    }
                
                # Check for feedback page or next question
                if question_num < question_count:
                    # Should redirect to feedback or next question
                    if submit_response.status_code == 302:
                        # Follow redirect
                        redirect_response = session.get(submit_response.headers.get('Location', '/quiz'))
                        response_text = redirect_response.text
                    else:
                        response_text = submit_response.text
                    
                    # Verify progress updated
                    expected_progress = f"{question_num + 1}/{question_count}"
                    if expected_progress not in response_text and question_num < question_count:
                        # For last question, we might be on results page
                        if question_num + 1 < question_count:
                            return {
                                'valid': False,
                                'error': f"Progress not updated correctly after question {question_num}. Expected: {expected_progress}"
                            }
                
                session_data['questions_answered'] = question_num
                time.sleep(0.1)  # Brief pause between submissions
            
            return {
                'valid': True,
                'questions_tested': test_questions,
                'answers_submitted': test_questions,
                'navigation_successful': True,
                'final_question_tested': session_data['questions_answered']
            }
            
        except requests.exceptions.Timeout:
            return {
                'valid': False,
                'error': f"Timeout during answer submission flow at question {session_data.get('questions_answered', 0) + 1}"
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Answer submission flow error: {e}"
            }

    def _validate_session_persistence(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate session persistence across requests"""
        try:
            session = session_data['requests_session']
            
            # Make a status request to check session persistence
            status_response = session.get(
                f"{self.base_url}/quiz",
                timeout=(self.timeout_config['connection_timeout'], self.timeout_config['read_timeout'])
            )
            
            if status_response.status_code != 200:
                return {
                    'valid': False,
                    'error': f"Session persistence check failed: status {status_response.status_code}"
                }
            
            response_text = status_response.text
            
            # Check if session data is maintained
            department = session_data['department']
            if department not in response_text and session_data['department'] != '基礎科目':
                # For specialist departments, check if department context is maintained
                if 'quiz_current' not in response_text:
                    return {
                        'valid': False,
                        'error': "Session data lost - no quiz context found"
                    }
            
            # Check if progress is maintained
            questions_answered = session_data.get('questions_answered', 0)
            if questions_answered > 0:
                # Should show current progress
                current_question = questions_answered + 1
                if f"{current_question}/" not in response_text and current_question <= session_data['question_count']:
                    return {
                        'valid': False,
                        'error': f"Session progress not maintained - expected question {current_question}"
                    }
            
            return {
                'valid': True,
                'session_maintained': True,
                'progress_preserved': True,
                'response_status': status_response.status_code
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Session persistence validation error: {e}"
            }

    def _validate_final_results(self, session_data: Dict[str, Any], question_count: int) -> Dict[str, Any]:
        """Validate final results calculation and display"""
        try:
            session = session_data['requests_session']
            
            # Submit answers for remaining questions to reach results
            current_question = session_data.get('questions_answered', 0) + 1
            
            for question_num in range(current_question, question_count + 1):
                answer_data = {
                    'answer': 'a',  # Always choose option A for testing
                    'current': question_num
                }
                
                submit_response = session.post(
                    f"{self.base_url}/exam",
                    data=answer_data,
                    timeout=(self.timeout_config['connection_timeout'], self.timeout_config['read_timeout'])
                )
                
                if submit_response.status_code not in [200, 302]:
                    return {
                        'valid': False,
                        'error': f"Failed to submit answer for question {question_num}"
                    }
                
                # Brief pause between submissions
                time.sleep(0.1)
            
            # Should now be on results page - get final response
            if submit_response.status_code == 302:
                # Follow redirect to results
                final_response = session.get(
                    submit_response.headers.get('Location', '/results'),
                    timeout=(self.timeout_config['connection_timeout'], self.timeout_config['read_timeout'])
                )
            else:
                final_response = submit_response
            
            if final_response.status_code != 200:
                return {
                    'valid': False,
                    'error': f"Results page not accessible: status {final_response.status_code}"
                }
            
            results_text = final_response.text
            
            # Validate results page elements
            required_results_elements = [
                'score',      # Score display
                'total',      # Total questions
                'results'     # Results section
            ]
            
            found_elements = []
            for element in required_results_elements:
                if element in results_text.lower():
                    found_elements.append(element)
            
            # Check for score calculation
            score_found = False
            for i in range(question_count + 1):
                if f"{i}/{question_count}" in results_text or f"{i} / {question_count}" in results_text:
                    score_found = True
                    session_data['final_score'] = f"{i}/{question_count}"
                    break
            
            if not score_found:
                return {
                    'valid': False,
                    'error': "Score calculation not found in results"
                }
            
            # Calculate completion rate
            session_data['completion_rate'] = 100.0  # All questions were answered
            
            return {
                'valid': True,
                'results_elements_found': len(found_elements),
                'score_calculation_valid': score_found,
                'final_score': session_data.get('final_score'),
                'completion_rate': session_data.get('completion_rate'),
                'results_page_length': len(results_text)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Final results validation error: {e}"
            }

    def validate_all_departments_flow(self, question_count: int) -> Dict[str, Any]:
        """Validate complete flow for all departments with specific question count"""
        self.logger.info(f"🔄 Validating complete flow for all departments: {question_count} questions")
        
        results = {}
        stats = {
            'total_departments': len(self.department_config),
            'valid_flows': 0,
            'invalid_flows': 0,
            'question_count': question_count
        }
        
        for department in self.department_config.keys():
            result = self.validate_complete_flow(department, question_count)
            results[department] = result
            
            if result['valid']:
                stats['valid_flows'] += 1
            else:
                stats['invalid_flows'] += 1
        
        validation_rate = (stats['valid_flows'] / stats['total_departments']) * 100
        
        return {
            'overall_valid': validation_rate == 100.0,
            'validation_rate': validation_rate,
            'stats': stats,
            'department_results': results
        }

    def validate_all_question_counts_flow(self, department: str) -> Dict[str, Any]:
        """Validate complete flow for all question counts with specific department"""
        self.logger.info(f"🔄 Validating complete flow for all question counts: {department}")
        
        if department not in self.department_config:
            return {
                'overall_valid': False,
                'error': f"Unknown department: {department}"
            }
        
        results = {}
        stats = {
            'total_question_counts': len(self.question_count_configs),
            'valid_flows': 0,
            'invalid_flows': 0,
            'department': department
        }
        
        for question_count in self.question_count_configs:
            result = self.validate_complete_flow(department, question_count)
            results[f'{question_count}_questions'] = result
            
            if result['valid']:
                stats['valid_flows'] += 1
            else:
                stats['invalid_flows'] += 1
        
        validation_rate = (stats['valid_flows'] / stats['total_question_counts']) * 100
        
        return {
            'overall_valid': validation_rate == 100.0,
            'validation_rate': validation_rate,
            'stats': stats,
            'question_count_results': results
        }

if __name__ == "__main__":
    # Standalone flow validation execution
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    validator = FlowValidator()
    
    print("🔄 Testing flow validator...")
    
    # Test single flow
    result = validator.validate_complete_flow('基礎科目', 10)
    print(f"Basic subject flow validation: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
    
    if not result['valid']:
        print(f"Error: {result['error']}")
    
    print("Flow validator test completed.")