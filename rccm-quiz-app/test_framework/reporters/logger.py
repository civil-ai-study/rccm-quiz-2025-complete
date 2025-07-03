#!/usr/bin/env python3
"""
📝 Test Logger - Comprehensive Test Logging and Reporting
Provides detailed logging for all 39 test cases with real-time monitoring
"""

import os
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading

class TestLogger:
    """Comprehensive test logging system with real-time monitoring"""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper())
        self.base_dir = Path(__file__).parent.parent.parent
        self.logs_dir = self.base_dir / "results" / "logs"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging components
        self.session_id = self._generate_session_id()
        self.log_file_path = self.logs_dir / f"test_session_{self.session_id}.log"
        self.json_log_path = self.logs_dir / f"test_session_{self.session_id}.json"
        
        # Test execution tracking
        self.test_events = []
        self.test_stats = {
            'session_id': self.session_id,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'total_tests': 0,
            'completed_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'skipped_tests': 0,
            'departments_tested': set(),
            'question_counts_tested': set()
        }
        
        # Real-time monitoring
        self.monitoring_enabled = True
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(f"TestRunner.{self.session_id}")
        self.logger.info(f"🚀 Test logging session initialized: {self.session_id}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{int(time.time() * 1000) % 10000:04d}"

    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        """Log info message with test context"""
        self._log_event('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with test context"""
        self._log_event('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with test context"""
        self._log_event('ERROR', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with test context"""
        self._log_event('DEBUG', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with test context"""
        self._log_event('CRITICAL', message, **kwargs)

    def _log_event(self, level: str, message: str, **kwargs):
        """Log event with structured data"""
        timestamp = datetime.utcnow()
        
        # Create event record
        event = {
            'timestamp': timestamp.isoformat(),
            'level': level,
            'message': message,
            'session_id': self.session_id,
            **kwargs
        }
        
        with self.lock:
            self.test_events.append(event)
            self._write_json_log()
        
        # Log to standard logger
        logger = logging.getLogger(f"TestRunner.{self.session_id}")
        log_method = getattr(logger, level.lower())
        log_method(message)

    def log_test_start(self, department: str, question_count: int, test_id: str):
        """Log test start event"""
        with self.lock:
            self.test_stats['total_tests'] += 1
            self.test_stats['departments_tested'].add(department)
            self.test_stats['question_counts_tested'].add(question_count)
        
        self.info(
            f"🧪 Starting test: {test_id}",
            event_type='test_start',
            test_id=test_id,
            department=department,
            question_count=question_count
        )

    def log_test_completion(self, test_id: str, result: Dict[str, Any]):
        """Log test completion event"""
        status = result.get('status', 'UNKNOWN')
        execution_time = result.get('execution_time', 0)
        
        with self.lock:
            self.test_stats['completed_tests'] += 1
            
            if status == 'PASS':
                self.test_stats['passed_tests'] += 1
            elif status == 'FAIL':
                self.test_stats['failed_tests'] += 1
            elif status == 'ERROR':
                self.test_stats['error_tests'] += 1
            elif status == 'SKIP':
                self.test_stats['skipped_tests'] += 1
        
        if status == 'PASS':
            self.info(
                f"✅ Test completed successfully: {test_id} ({execution_time:.2f}s)",
                event_type='test_completion',
                test_id=test_id,
                status=status,
                execution_time=execution_time,
                result=result
            )
        else:
            self.error(
                f"❌ Test failed: {test_id} - {result.get('error', 'Unknown error')} ({execution_time:.2f}s)",
                event_type='test_completion',
                test_id=test_id,
                status=status,
                execution_time=execution_time,
                result=result
            )

    def log_test_step(self, test_id: str, step: str, result: Dict[str, Any]):
        """Log individual test step"""
        status = 'PASS' if result.get('valid', False) else 'FAIL'
        
        if status == 'PASS':
            self.debug(
                f"  ✅ Step completed: {step}",
                event_type='test_step',
                test_id=test_id,
                step=step,
                status=status,
                result=result
            )
        else:
            self.warning(
                f"  ❌ Step failed: {step} - {result.get('error', 'Unknown error')}",
                event_type='test_step',
                test_id=test_id,
                step=step,
                status=status,
                result=result
            )

    def log_progress_update(self):
        """Log current progress status"""
        with self.lock:
            stats = self.test_stats.copy()
            stats['departments_tested'] = list(stats['departments_tested'])
            stats['question_counts_tested'] = list(stats['question_counts_tested'])
        
        if stats['total_tests'] > 0:
            progress_percentage = (stats['completed_tests'] / stats['total_tests']) * 100
            success_rate = (stats['passed_tests'] / stats['completed_tests']) * 100 if stats['completed_tests'] > 0 else 0
            
            self.info(
                f"📊 Progress Update: {stats['completed_tests']}/{stats['total_tests']} tests ({progress_percentage:.1f}%) - Success: {success_rate:.1f}%",
                event_type='progress_update',
                progress_percentage=progress_percentage,
                success_rate=success_rate,
                stats=stats
            )

    def log_session_start(self, total_tests: int):
        """Log test session start"""
        with self.lock:
            self.test_stats['total_tests'] = total_tests
            self.test_stats['start_time'] = datetime.utcnow().isoformat()
        
        self.info(
            f"🚀 Test session started: {total_tests} total tests scheduled",
            event_type='session_start',
            total_tests=total_tests,
            session_id=self.session_id
        )

    def log_session_end(self):
        """Log test session end"""
        end_time = datetime.utcnow()
        
        with self.lock:
            self.test_stats['end_time'] = end_time.isoformat()
            stats = self.test_stats.copy()
            stats['departments_tested'] = list(stats['departments_tested'])
            stats['question_counts_tested'] = list(stats['question_counts_tested'])
        
        # Calculate session duration
        start_time = datetime.fromisoformat(stats['start_time'])
        duration = end_time - start_time
        
        success_rate = (stats['passed_tests'] / stats['completed_tests']) * 100 if stats['completed_tests'] > 0 else 0
        
        self.info(
            f"🏁 Test session completed: {stats['completed_tests']}/{stats['total_tests']} tests - Success: {success_rate:.1f}% - Duration: {duration}",
            event_type='session_end',
            duration_seconds=duration.total_seconds(),
            success_rate=success_rate,
            stats=stats
        )

    def log_error_recovery(self, test_id: str, error: str, recovery_action: str, success: bool):
        """Log error recovery attempt"""
        if success:
            self.info(
                f"🔄 Error recovery successful: {test_id} - {recovery_action}",
                event_type='error_recovery',
                test_id=test_id,
                error=error,
                recovery_action=recovery_action,
                success=success
            )
        else:
            self.error(
                f"🚨 Error recovery failed: {test_id} - {recovery_action}",
                event_type='error_recovery',
                test_id=test_id,
                error=error,
                recovery_action=recovery_action,
                success=success
            )

    def log_environment_info(self, environment_data: Dict[str, Any]):
        """Log test environment information"""
        self.info(
            "🔍 Test environment initialized",
            event_type='environment_info',
            environment=environment_data
        )

    def log_department_validation(self, department: str, validation_result: Dict[str, Any]):
        """Log department data validation result"""
        if validation_result.get('valid', False):
            self.info(
                f"✅ Department validation passed: {department} - {validation_result.get('total_questions', 0)} questions",
                event_type='department_validation',
                department=department,
                result=validation_result
            )
        else:
            self.error(
                f"❌ Department validation failed: {department} - {validation_result.get('error', 'Unknown error')}",
                event_type='department_validation',
                department=department,
                result=validation_result
            )

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current test statistics"""
        with self.lock:
            stats = self.test_stats.copy()
            stats['departments_tested'] = list(stats['departments_tested'])
            stats['question_counts_tested'] = list(stats['question_counts_tested'])
        
        return stats

    def get_test_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get test events, optionally filtered by type"""
        with self.lock:
            if event_type:
                return [event for event in self.test_events if event.get('event_type') == event_type]
            return self.test_events.copy()

    def _write_json_log(self):
        """Write events to JSON log file"""
        log_data = {
            'session_info': self.test_stats,
            'events': self.test_events
        }
        
        try:
            with open(self.json_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            # Use standard logger to avoid recursion
            logging.getLogger().error(f"Failed to write JSON log: {e}")

    def generate_summary_report(self) -> str:
        """Generate text summary report"""
        with self.lock:
            stats = self.test_stats.copy()
            stats['departments_tested'] = list(stats['departments_tested'])
            stats['question_counts_tested'] = list(stats['question_counts_tested'])
        
        # Calculate metrics
        success_rate = (stats['passed_tests'] / stats['completed_tests']) * 100 if stats['completed_tests'] > 0 else 0
        completion_rate = (stats['completed_tests'] / stats['total_tests']) * 100 if stats['total_tests'] > 0 else 0
        
        # Calculate duration
        if stats['end_time']:
            start_time = datetime.fromisoformat(stats['start_time'])
            end_time = datetime.fromisoformat(stats['end_time'])
            duration = end_time - start_time
            duration_str = str(duration)
        else:
            duration_str = "In progress"
        
        report_lines = [
            "=" * 80,
            "📊 COMPREHENSIVE TEST SESSION SUMMARY",
            "=" * 80,
            f"Session ID: {stats['session_id']}",
            f"Start Time: {stats['start_time']}",
            f"End Time: {stats['end_time'] or 'In progress'}",
            f"Duration: {duration_str}",
            "",
            "📈 TEST EXECUTION STATISTICS:",
            f"├── Total Tests: {stats['total_tests']}",
            f"├── Completed: {stats['completed_tests']} ({completion_rate:.1f}%)",
            f"├── Passed: {stats['passed_tests']} ({success_rate:.1f}%)",
            f"├── Failed: {stats['failed_tests']}",
            f"├── Errors: {stats['error_tests']}",
            f"└── Skipped: {stats['skipped_tests']}",
            "",
            "🏢 DEPARTMENT COVERAGE:",
            f"├── Departments Tested: {len(stats['departments_tested'])}",
            f"└── Question Counts: {sorted(stats['question_counts_tested'])}",
            "",
            "📄 LOG FILES:",
            f"├── Text Log: {self.log_file_path}",
            f"└── JSON Log: {self.json_log_path}",
            "=" * 80
        ]
        
        return "\n".join(report_lines)

    def cleanup(self):
        """Cleanup logger resources"""
        self.monitoring_enabled = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Final JSON log write
        self._write_json_log()

if __name__ == "__main__":
    # Test the logger
    logger = TestLogger()
    
    # Simulate test session
    logger.log_session_start(39)
    logger.log_test_start("基礎科目", 10, "basic_10q")
    
    test_result = {
        'status': 'PASS',
        'execution_time': 2.5,
        'department': '基礎科目',
        'question_count': 10
    }
    
    logger.log_test_completion("basic_10q", test_result)
    logger.log_progress_update()
    logger.log_session_end()
    
    # Generate summary
    print(logger.generate_summary_report())
    
    logger.cleanup()
    print(f"Logger test completed. Check logs in: {logger.logs_dir}")