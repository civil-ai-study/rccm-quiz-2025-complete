#!/usr/bin/env python3
"""
🎯 Comprehensive Test Runner - Main Execution Engine
39 Test Cases: 13 Departments × 3 Question Configurations
"""

import sys
import os
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Add test framework to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.department_validator import DepartmentValidator
from validators.data_validator import DataValidator
from validators.flow_validator import FlowValidator
from reporters.logger import TestLogger
from reporters.html_reporter import HTMLReporter
from reporters.json_reporter import JSONReporter
from utils.api_client import FlaskTestClient

class ComprehensiveTestRunner:
    """Main test execution engine for 39 test cases"""
    
    def __init__(self):
        self.departments = [
            '基礎科目',
            '道路部門', '河川・砂防部門', '都市計画部門', '造園部門',
            '建設環境部門', '鋼構造・コンクリート部門', '土質・基礎部門',
            '施工計画部門', '上下水道部門', '森林土木部門',
            '農業土木部門', 'トンネル部門'
        ]
        
        self.question_counts = [10, 20, 30]
        self.total_tests = len(self.departments) * len(self.question_counts)  # 39 tests
        
        # Initialize components
        self.logger = TestLogger()
        self.data_validator = DataValidator()
        self.department_validator = DepartmentValidator()
        self.flow_validator = FlowValidator()
        self.html_reporter = HTMLReporter()
        self.json_reporter = JSONReporter()
        self.api_client = FlaskTestClient()
        
        # Test execution state
        self.test_results = {}
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'total_tests': self.total_tests,
            'completed_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'skipped_tests': 0
        }
        
        # Error handling configuration
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 5,  # seconds
            'timeout_limit': 300  # 5 minutes per test
        }
        
        self.logger.info("🎯 Comprehensive Test Runner initialized")
        self.logger.info(f"📊 Total test cases: {self.total_tests}")
        self.logger.info(f"🏢 Departments: {len(self.departments)}")
        self.logger.info(f"🔢 Question counts: {self.question_counts}")

    def execute_comprehensive_suite(self, parallel=False, max_workers=4):
        """Execute all 39 test cases with comprehensive logging and error handling"""
        self.logger.info("🚀 Starting comprehensive test suite execution")
        self.execution_stats['start_time'] = datetime.utcnow()
        
        try:
            # Phase 1: Environment validation
            if not self._validate_test_environment():
                self.logger.error("❌ Test environment validation failed")
                return False
            
            # Phase 2: Data validation
            if not self._validate_all_department_data():
                self.logger.error("❌ Department data validation failed")
                return False
            
            # Phase 3: Execute test matrix
            if parallel:
                success = self._execute_parallel_tests(max_workers)
            else:
                success = self._execute_sequential_tests()
            
            # Phase 4: Generate comprehensive reports
            self._generate_final_reports()
            
            self.execution_stats['end_time'] = datetime.utcnow()
            self._log_execution_summary()
            
            return success
            
        except Exception as e:
            self.logger.error(f"🚨 Critical error in test suite execution: {e}")
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return False

    def _validate_test_environment(self) -> bool:
        """Validate test environment prerequisites"""
        self.logger.info("🔍 Validating test environment...")
        
        try:
            # Check Flask application availability
            if not self.api_client.validate_connection():
                self.logger.error("❌ Flask application not accessible")
                return False
            
            # Check data directory
            data_dir = "../data"
            if not os.path.exists(data_dir):
                self.logger.error(f"❌ Data directory not found: {data_dir}")
                return False
            
            # Check write permissions for results
            results_dir = "results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            self.logger.info("✅ Test environment validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Environment validation error: {e}")
            return False

    def _validate_all_department_data(self) -> bool:
        """Validate data availability for all departments"""
        self.logger.info("🔍 Validating department data availability...")
        
        validation_results = {}
        
        for department in self.departments:
            try:
                self.logger.info(f"🔍 Validating {department}...")
                
                # Validate department data
                validation_result = self.data_validator.validate_department_data(
                    department, self.question_counts
                )
                
                validation_results[department] = validation_result
                
                if validation_result['valid']:
                    self.logger.info(f"✅ {department}: {validation_result['total_questions']} questions available")
                else:
                    self.logger.error(f"❌ {department}: {validation_result['error']}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error validating {department}: {e}")
                validation_results[department] = {'valid': False, 'error': str(e)}
        
        # Check overall validation status
        valid_departments = sum(1 for result in validation_results.values() if result['valid'])
        
        self.logger.info(f"📊 Department validation: {valid_departments}/{len(self.departments)} valid")
        
        if valid_departments == len(self.departments):
            self.logger.info("✅ All department data validation passed")
            return True
        else:
            self.logger.error(f"❌ Department data validation failed: {len(self.departments) - valid_departments} departments invalid")
            return False

    def _execute_sequential_tests(self) -> bool:
        """Execute all test cases sequentially"""
        self.logger.info("🔄 Executing tests sequentially...")
        
        success_count = 0
        
        for department in self.departments:
            for question_count in self.question_counts:
                test_id = f"{department}_{question_count}q"
                
                try:
                    self.logger.info(f"🧪 Executing test: {test_id}")
                    
                    result = self._execute_single_test(department, question_count)
                    self.test_results[test_id] = result
                    
                    self._update_execution_stats(result)
                    
                    if result['status'] == 'PASS':
                        success_count += 1
                        self.logger.info(f"✅ Test passed: {test_id}")
                    else:
                        self.logger.error(f"❌ Test failed: {test_id} - {result.get('error', 'Unknown error')}")
                    
                    # Progress reporting
                    progress = (self.execution_stats['completed_tests'] / self.total_tests) * 100
                    self.logger.info(f"📊 Progress: {self.execution_stats['completed_tests']}/{self.total_tests} ({progress:.1f}%)")
                    
                except Exception as e:
                    self.logger.error(f"🚨 Critical error in test {test_id}: {e}")
                    self.test_results[test_id] = {
                        'status': 'ERROR',
                        'error': str(e),
                        'execution_time': 0
                    }
                    self._update_execution_stats({'status': 'ERROR'})
        
        success_rate = (success_count / self.total_tests) * 100
        self.logger.info(f"📈 Sequential execution completed: {success_count}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        return success_count == self.total_tests

    def _execute_parallel_tests(self, max_workers=4) -> bool:
        """Execute tests in parallel"""
        self.logger.info(f"🔄 Executing tests in parallel (max_workers={max_workers})...")
        
        success_count = 0
        test_futures = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test cases
            for department in self.departments:
                for question_count in self.question_counts:
                    test_id = f"{department}_{question_count}q"
                    future = executor.submit(self._execute_single_test_with_retry, department, question_count)
                    test_futures.append((test_id, future))
            
            # Collect results as they complete
            for test_id, future in test_futures:
                try:
                    result = future.result(timeout=self.retry_config['timeout_limit'])
                    self.test_results[test_id] = result
                    
                    self._update_execution_stats(result)
                    
                    if result['status'] == 'PASS':
                        success_count += 1
                        self.logger.info(f"✅ Test passed: {test_id}")
                    else:
                        self.logger.error(f"❌ Test failed: {test_id} - {result.get('error', 'Unknown error')}")
                    
                    # Progress reporting
                    progress = (self.execution_stats['completed_tests'] / self.total_tests) * 100
                    self.logger.info(f"📊 Progress: {self.execution_stats['completed_tests']}/{self.total_tests} ({progress:.1f}%)")
                    
                except Exception as e:
                    self.logger.error(f"🚨 Critical error in test {test_id}: {e}")
                    self.test_results[test_id] = {
                        'status': 'ERROR',
                        'error': str(e),
                        'execution_time': 0
                    }
                    self._update_execution_stats({'status': 'ERROR'})
        
        success_rate = (success_count / self.total_tests) * 100
        self.logger.info(f"📈 Parallel execution completed: {success_count}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        return success_count == self.total_tests

    def _execute_single_test_with_retry(self, department: str, question_count: int) -> Dict[str, Any]:
        """Execute single test with retry logic"""
        for attempt in range(self.retry_config['max_retries']):
            try:
                result = self._execute_single_test(department, question_count)
                
                if result['status'] in ['PASS', 'FAIL']:
                    return result
                elif attempt < self.retry_config['max_retries'] - 1:
                    self.logger.warning(f"⚠️ Test {department}_{question_count}q failed, retrying (attempt {attempt + 2})...")
                    time.sleep(self.retry_config['retry_delay'])
                    
            except Exception as e:
                if attempt < self.retry_config['max_retries'] - 1:
                    self.logger.warning(f"⚠️ Test {department}_{question_count}q error, retrying: {e}")
                    time.sleep(self.retry_config['retry_delay'])
                else:
                    return {
                        'status': 'ERROR',
                        'error': f"Max retries exceeded: {e}",
                        'execution_time': 0,
                        'attempts': attempt + 1
                    }
        
        return {
            'status': 'ERROR',
            'error': 'Max retries exceeded',
            'execution_time': 0,
            'attempts': self.retry_config['max_retries']
        }

    def _execute_single_test(self, department: str, question_count: int) -> Dict[str, Any]:
        """Execute a single test case"""
        start_time = time.time()
        test_id = f"{department}_{question_count}q"
        
        try:
            self.logger.debug(f"🧪 Starting test: {test_id}")
            
            # Step 1: Department loading validation
            dept_result = self.department_validator.validate_department_loading(department)
            if not dept_result['valid']:
                return {
                    'status': 'FAIL',
                    'error': f"Department loading failed: {dept_result['error']}",
                    'execution_time': time.time() - start_time,
                    'step_failed': 'department_loading'
                }
            
            # Step 2: Question count configuration validation
            config_result = self.department_validator.validate_question_count_config(department, question_count)
            if not config_result['valid']:
                return {
                    'status': 'FAIL',
                    'error': f"Question count config failed: {config_result['error']}",
                    'execution_time': time.time() - start_time,
                    'step_failed': 'question_count_config'
                }
            
            # Step 3: Complete flow validation
            flow_result = self.flow_validator.validate_complete_flow(department, question_count)
            if not flow_result['valid']:
                return {
                    'status': 'FAIL',
                    'error': f"Complete flow failed: {flow_result['error']}",
                    'execution_time': time.time() - start_time,
                    'step_failed': 'complete_flow'
                }
            
            execution_time = time.time() - start_time
            
            self.logger.debug(f"✅ Test completed successfully: {test_id} ({execution_time:.2f}s)")
            
            return {
                'status': 'PASS',
                'execution_time': execution_time,
                'department': department,
                'question_count': question_count,
                'steps_completed': ['department_loading', 'question_count_config', 'complete_flow'],
                'details': {
                    'department_result': dept_result,
                    'config_result': config_result,
                    'flow_result': flow_result
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Test execution error {test_id}: {e}")
            
            return {
                'status': 'ERROR',
                'error': str(e),
                'execution_time': execution_time,
                'traceback': traceback.format_exc()
            }

    def _update_execution_stats(self, result: Dict[str, Any]):
        """Update execution statistics"""
        self.execution_stats['completed_tests'] += 1
        
        if result['status'] == 'PASS':
            self.execution_stats['passed_tests'] += 1
        elif result['status'] == 'FAIL':
            self.execution_stats['failed_tests'] += 1
        elif result['status'] == 'ERROR':
            self.execution_stats['error_tests'] += 1
        elif result['status'] == 'SKIP':
            self.execution_stats['skipped_tests'] += 1

    def _generate_final_reports(self):
        """Generate comprehensive test reports"""
        self.logger.info("📋 Generating comprehensive test reports...")
        
        try:
            # Generate HTML report
            html_report_path = self.html_reporter.generate_report(
                self.test_results, self.execution_stats
            )
            self.logger.info(f"📄 HTML report generated: {html_report_path}")
            
            # Generate JSON report
            json_report_path = self.json_reporter.generate_report(
                self.test_results, self.execution_stats
            )
            self.logger.info(f"📄 JSON report generated: {json_report_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating reports: {e}")

    def _log_execution_summary(self):
        """Log comprehensive execution summary"""
        duration = self.execution_stats['end_time'] - self.execution_stats['start_time']
        success_rate = (self.execution_stats['passed_tests'] / self.total_tests) * 100
        
        self.logger.info("=" * 80)
        self.logger.info("📊 COMPREHENSIVE TEST EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"⏱️  Total execution time: {duration}")
        self.logger.info(f"📋 Total test cases: {self.total_tests}")
        self.logger.info(f"✅ Passed tests: {self.execution_stats['passed_tests']}")
        self.logger.info(f"❌ Failed tests: {self.execution_stats['failed_tests']}")
        self.logger.info(f"🚨 Error tests: {self.execution_stats['error_tests']}")
        self.logger.info(f"⏭️  Skipped tests: {self.execution_stats['skipped_tests']}")
        self.logger.info(f"📈 Success rate: {success_rate:.1f}%")
        self.logger.info("=" * 80)

    def execute_department_suite(self, department: str) -> bool:
        """Execute all 3 configurations for specific department"""
        self.logger.info(f"🏢 Executing department suite: {department}")
        
        if department not in self.departments:
            self.logger.error(f"❌ Invalid department: {department}")
            return False
        
        success_count = 0
        
        for question_count in self.question_counts:
            test_id = f"{department}_{question_count}q"
            
            try:
                result = self._execute_single_test(department, question_count)
                self.test_results[test_id] = result
                
                if result['status'] == 'PASS':
                    success_count += 1
                    self.logger.info(f"✅ Test passed: {test_id}")
                else:
                    self.logger.error(f"❌ Test failed: {test_id}")
                    
            except Exception as e:
                self.logger.error(f"🚨 Error in test {test_id}: {e}")
        
        success_rate = (success_count / len(self.question_counts)) * 100
        self.logger.info(f"📈 Department suite completed: {success_count}/{len(self.question_counts)} tests passed ({success_rate:.1f}%)")
        
        return success_count == len(self.question_counts)

    def execute_configuration_suite(self, question_count: int) -> bool:
        """Execute specific question count across all departments"""
        self.logger.info(f"🔢 Executing configuration suite: {question_count} questions")
        
        if question_count not in self.question_counts:
            self.logger.error(f"❌ Invalid question count: {question_count}")
            return False
        
        success_count = 0
        
        for department in self.departments:
            test_id = f"{department}_{question_count}q"
            
            try:
                result = self._execute_single_test(department, question_count)
                self.test_results[test_id] = result
                
                if result['status'] == 'PASS':
                    success_count += 1
                    self.logger.info(f"✅ Test passed: {test_id}")
                else:
                    self.logger.error(f"❌ Test failed: {test_id}")
                    
            except Exception as e:
                self.logger.error(f"🚨 Error in test {test_id}: {e}")
        
        success_rate = (success_count / len(self.departments)) * 100
        self.logger.info(f"📈 Configuration suite completed: {success_count}/{len(self.departments)} tests passed ({success_rate:.1f}%)")
        
        return success_count == len(self.departments)

    def get_test_results(self) -> Dict[str, Any]:
        """Get current test results"""
        return {
            'test_results': self.test_results,
            'execution_stats': self.execution_stats
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all 39 test cases")
    parser.add_argument("--department", type=str, help="Run tests for specific department")
    parser.add_argument("--questions", type=int, choices=[10, 20, 30], help="Run tests for specific question count")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.all:
        success = runner.execute_comprehensive_suite(parallel=args.parallel, max_workers=args.workers)
    elif args.department:
        success = runner.execute_department_suite(args.department)
    elif args.questions:
        success = runner.execute_configuration_suite(args.questions)
    else:
        print("Please specify --all, --department, or --questions")
        sys.exit(1)
    
    sys.exit(0 if success else 1)