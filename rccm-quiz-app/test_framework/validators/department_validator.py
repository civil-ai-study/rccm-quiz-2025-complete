#!/usr/bin/env python3
"""
🏢 Department Validator - Department Loading and Configuration Validation
Validates department loading and question count configuration functionality
"""

import sys
import os
import time
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class DepartmentValidator:
    """Validates department loading and configuration functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Department configuration mapping
        self.department_config = {
            '基礎科目': {
                'type': 'basic',
                'file_pattern': '4-1.csv',
                'category_filter': '共通',
                'expected_route': '/exam',
                'url_params': {'question_type': 'basic'}
            },
            '道路部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '道路',
                'expected_route': '/exam',
                'url_params': {'department': 'road', 'question_type': 'specialist'}
            },
            '河川・砂防部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '河川、砂防及び海岸・海洋',
                'expected_route': '/exam',
                'url_params': {'department': 'civil_planning', 'question_type': 'specialist'}
            },
            '都市計画部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '都市計画及び地方計画',
                'expected_route': '/exam',
                'url_params': {'department': 'urban_planning', 'question_type': 'specialist'}
            },
            '造園部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '造園',
                'expected_route': '/exam',
                'url_params': {'department': 'landscape', 'question_type': 'specialist'}
            },
            '建設環境部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '建設環境',
                'expected_route': '/exam',
                'url_params': {'department': 'construction_env', 'question_type': 'specialist'}
            },
            '鋼構造・コンクリート部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '鋼構造及びコンクリート',
                'expected_route': '/exam',
                'url_params': {'department': 'steel_concrete', 'question_type': 'specialist'}
            },
            '土質・基礎部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '土質及び基礎',
                'expected_route': '/exam',
                'url_params': {'department': 'soil_foundation', 'question_type': 'specialist'}
            },
            '施工計画部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '施工計画、施工設備及び積算',
                'expected_route': '/exam',
                'url_params': {'department': 'construction_planning', 'question_type': 'specialist'}
            },
            '上下水道部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '上水道及び工業用水道',
                'expected_route': '/exam',
                'url_params': {'department': 'water_supply', 'question_type': 'specialist'}
            },
            '森林土木部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '森林土木',
                'expected_route': '/exam',
                'url_params': {'department': 'forestry', 'question_type': 'specialist'}
            },
            '農業土木部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': '農業土木',
                'expected_route': '/exam',
                'url_params': {'department': 'agriculture', 'question_type': 'specialist'}
            },
            'トンネル部門': {
                'type': 'specialist',
                'file_pattern': '4-2_*.csv',
                'category_filter': 'トンネル',
                'expected_route': '/exam',
                'url_params': {'department': 'tunnel', 'question_type': 'specialist'}
            }
        }
        
        # Question count configurations
        self.question_count_configs = {
            10: {
                'session_type': 'quick',
                'time_limit': None,
                'description': 'Quick practice session'
            },
            20: {
                'session_type': 'standard',
                'time_limit': 1800,  # 30 minutes
                'description': 'Standard practice session'
            },
            30: {
                'session_type': 'intensive',
                'time_limit': 2700,  # 45 minutes
                'description': 'Intensive exam simulation'
            }
        }

    def validate_department_loading(self, department: str) -> Dict[str, Any]:
        """Validate department loading functionality"""
        start_time = time.time()
        
        try:
            self.logger.debug(f"🔍 Validating department loading: {department}")
            
            if department not in self.department_config:
                return {
                    'valid': False,
                    'error': f"Unknown department: {department}",
                    'execution_time': time.time() - start_time
                }
            
            config = self.department_config[department]
            
            # Validation steps
            validation_results = {}
            
            # Step 1: Validate department configuration
            config_validation = self._validate_department_config(department, config)
            validation_results['config_validation'] = config_validation
            
            if not config_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Department configuration invalid: {config_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            # Step 2: Validate data availability
            data_validation = self._validate_department_data_availability(department, config)
            validation_results['data_validation'] = data_validation
            
            if not data_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Department data validation failed: {data_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            # Step 3: Validate category filtering
            category_validation = self._validate_category_filtering(department, config)
            validation_results['category_validation'] = category_validation
            
            if not category_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Category filtering validation failed: {category_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            execution_time = time.time() - start_time
            
            self.logger.debug(f"✅ Department loading validation passed: {department} ({execution_time:.2f}s)")
            
            return {
                'valid': True,
                'department': department,
                'execution_time': execution_time,
                'validation_results': validation_results,
                'config': config
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Department loading validation error for {department}: {e}")
            
            return {
                'valid': False,
                'error': str(e),
                'execution_time': execution_time,
                'department': department
            }

    def validate_question_count_config(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate question count configuration for department"""
        start_time = time.time()
        
        try:
            self.logger.debug(f"🔢 Validating question count config: {department} - {question_count} questions")
            
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
            
            dept_config = self.department_config[department]
            count_config = self.question_count_configs[question_count]
            
            # Validation steps
            validation_results = {}
            
            # Step 1: Validate question availability
            availability_validation = self._validate_question_availability(department, question_count)
            validation_results['availability_validation'] = availability_validation
            
            if not availability_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Insufficient questions available: {availability_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            # Step 2: Validate session configuration
            session_validation = self._validate_session_configuration(department, question_count)
            validation_results['session_validation'] = session_validation
            
            if not session_validation['valid']:
                return {
                    'valid': False,
                    'error': f"Session configuration invalid: {session_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            # Step 3: Validate URL parameter generation
            url_validation = self._validate_url_parameters(department, question_count)
            validation_results['url_validation'] = url_validation
            
            if not url_validation['valid']:
                return {
                    'valid': False,
                    'error': f"URL parameter validation failed: {url_validation['error']}",
                    'execution_time': time.time() - start_time,
                    'validation_results': validation_results
                }
            
            execution_time = time.time() - start_time
            
            self.logger.debug(f"✅ Question count config validation passed: {department} - {question_count}q ({execution_time:.2f}s)")
            
            return {
                'valid': True,
                'department': department,
                'question_count': question_count,
                'execution_time': execution_time,
                'validation_results': validation_results,
                'dept_config': dept_config,
                'count_config': count_config
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Question count config validation error: {department} - {question_count}q: {e}")
            
            return {
                'valid': False,
                'error': str(e),
                'execution_time': execution_time,
                'department': department,
                'question_count': question_count
            }

    def _validate_department_config(self, department: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate department configuration structure"""
        try:
            required_fields = ['type', 'file_pattern', 'category_filter', 'expected_route', 'url_params']
            
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                return {
                    'valid': False,
                    'error': f"Missing configuration fields: {missing_fields}"
                }
            
            # Validate type
            if config['type'] not in ['basic', 'specialist']:
                return {
                    'valid': False,
                    'error': f"Invalid department type: {config['type']}"
                }
            
            # Validate URL parameters
            if not isinstance(config['url_params'], dict):
                return {
                    'valid': False,
                    'error': "URL parameters must be a dictionary"
                }
            
            return {
                'valid': True,
                'config_fields': required_fields,
                'department_type': config['type']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Configuration validation error: {e}"
            }

    def _validate_department_data_availability(self, department: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that department data files exist and are accessible"""
        try:
            data_dir = Path(__file__).parent.parent.parent / "data"
            
            if not data_dir.exists():
                return {
                    'valid': False,
                    'error': f"Data directory not found: {data_dir}"
                }
            
            file_pattern = config['file_pattern']
            
            if file_pattern == '4-1.csv':
                # Basic subject file
                file_path = data_dir / file_pattern
                if not file_path.exists():
                    return {
                        'valid': False,
                        'error': f"Basic subject file not found: {file_path}"
                    }
                files_found = [file_path]
            else:
                # Specialist subject files
                files_found = list(data_dir.glob(file_pattern))
                if not files_found:
                    return {
                        'valid': False,
                        'error': f"No specialist files found matching pattern: {file_pattern}"
                    }
            
            # Validate file accessibility
            for file_path in files_found:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Try to read first line to ensure file is readable
                        f.readline()
                except UnicodeDecodeError:
                    # Try shift_jis encoding
                    try:
                        with open(file_path, 'r', encoding='shift_jis') as f:
                            f.readline()
                    except:
                        return {
                            'valid': False,
                            'error': f"File encoding error: {file_path}"
                        }
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f"File access error: {file_path} - {e}"
                    }
            
            return {
                'valid': True,
                'files_found': len(files_found),
                'file_paths': [str(f) for f in files_found]
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Data availability validation error: {e}"
            }

    def _validate_category_filtering(self, department: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate category filtering logic"""
        try:
            category_filter = config['category_filter']
            
            # This is a logical validation - in a real implementation,
            # we would load actual data and verify filtering works
            if not category_filter:
                return {
                    'valid': False,
                    'error': "Category filter is empty"
                }
            
            # Validate category filter format
            if not isinstance(category_filter, str):
                return {
                    'valid': False,
                    'error': "Category filter must be a string"
                }
            
            return {
                'valid': True,
                'category_filter': category_filter,
                'filter_type': 'string_match'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Category filtering validation error: {e}"
            }

    def _validate_question_availability(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate sufficient questions are available for the requested count"""
        try:
            # Import data validator to check question availability
            sys.path.append(str(Path(__file__).parent))
            from data_validator import DataValidator
            
            data_validator = DataValidator()
            validation_result = data_validator.validate_department_data(department, [question_count])
            
            if not validation_result['valid']:
                return {
                    'valid': False,
                    'error': f"Data validation failed: {validation_result.get('error', 'Unknown error')}"
                }
            
            # Check specific question count availability
            question_validations = validation_result.get('question_validations', {})
            count_key = f'{question_count}_questions'
            
            if count_key not in question_validations:
                return {
                    'valid': False,
                    'error': f"Question count validation missing for {question_count} questions"
                }
            
            count_validation = question_validations[count_key]
            
            if not count_validation['sufficient']:
                return {
                    'valid': False,
                    'error': f"Insufficient questions: need {count_validation['required']}, have {count_validation['available']}"
                }
            
            return {
                'valid': True,
                'available_questions': count_validation['available'],
                'required_questions': count_validation['required'],
                'total_department_questions': validation_result.get('total_questions', 0)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Question availability validation error: {e}"
            }

    def _validate_session_configuration(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate session can be configured correctly"""
        try:
            dept_config = self.department_config[department]
            count_config = self.question_count_configs[question_count]
            
            # Validate session type compatibility
            if dept_config['type'] == 'basic' and count_config['session_type'] == 'intensive':
                # Check if basic subject has enough questions for intensive sessions
                pass  # This would be implemented based on business rules
            
            # Validate time limits
            if count_config['time_limit'] is not None:
                if count_config['time_limit'] <= 0:
                    return {
                        'valid': False,
                        'error': f"Invalid time limit: {count_config['time_limit']}"
                    }
            
            return {
                'valid': True,
                'session_type': count_config['session_type'],
                'time_limit': count_config['time_limit'],
                'description': count_config['description']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Session configuration validation error: {e}"
            }

    def _validate_url_parameters(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate URL parameters can be generated correctly"""
        try:
            dept_config = self.department_config[department]
            count_config = self.question_count_configs[question_count]
            
            # Build URL parameters
            url_params = dept_config['url_params'].copy()
            url_params['count'] = question_count
            url_params['session_type'] = count_config['session_type']
            
            # Validate required parameters
            if dept_config['type'] == 'specialist':
                if 'department' not in url_params:
                    return {
                        'valid': False,
                        'error': "Specialist department missing 'department' parameter"
                    }
            
            # Validate parameter values
            for key, value in url_params.items():
                if value is None or value == '':
                    return {
                        'valid': False,
                        'error': f"Empty URL parameter: {key}"
                    }
            
            return {
                'valid': True,
                'url_params': url_params,
                'expected_route': dept_config['expected_route']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"URL parameter validation error: {e}"
            }

    def validate_all_departments_loading(self) -> Dict[str, Any]:
        """Validate loading for all departments"""
        self.logger.info("🔍 Validating loading for all departments...")
        
        results = {}
        stats = {
            'total_departments': len(self.department_config),
            'valid_departments': 0,
            'invalid_departments': 0
        }
        
        for department in self.department_config.keys():
            result = self.validate_department_loading(department)
            results[department] = result
            
            if result['valid']:
                stats['valid_departments'] += 1
            else:
                stats['invalid_departments'] += 1
        
        validation_rate = (stats['valid_departments'] / stats['total_departments']) * 100
        
        return {
            'overall_valid': validation_rate == 100.0,
            'validation_rate': validation_rate,
            'stats': stats,
            'department_results': results
        }

    def validate_all_question_count_configs(self) -> Dict[str, Any]:
        """Validate all question count configurations across all departments"""
        self.logger.info("🔢 Validating all question count configurations...")
        
        results = {}
        stats = {
            'total_combinations': len(self.department_config) * len(self.question_count_configs),
            'valid_combinations': 0,
            'invalid_combinations': 0
        }
        
        for department in self.department_config.keys():
            dept_results = {}
            for question_count in self.question_count_configs.keys():
                result = self.validate_question_count_config(department, question_count)
                dept_results[f'{question_count}_questions'] = result
                
                if result['valid']:
                    stats['valid_combinations'] += 1
                else:
                    stats['invalid_combinations'] += 1
            
            results[department] = dept_results
        
        validation_rate = (stats['valid_combinations'] / stats['total_combinations']) * 100
        
        return {
            'overall_valid': validation_rate == 100.0,
            'validation_rate': validation_rate,
            'stats': stats,
            'combination_results': results
        }

if __name__ == "__main__":
    # Standalone validation execution
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    validator = DepartmentValidator()
    
    print("🔍 Testing department validator...")
    
    # Test single department
    result = validator.validate_department_loading('基礎科目')
    print(f"Basic subject validation: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
    
    # Test question count config
    result = validator.validate_question_count_config('基礎科目', 10)
    print(f"Question count config validation: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
    
    print("Department validator test completed.")