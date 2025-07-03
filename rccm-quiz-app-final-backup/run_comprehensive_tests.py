#!/usr/bin/env python3
"""
🎯 Comprehensive Test Execution Script
Execute all 39 test cases (13 departments × 3 question counts) with full validation
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add test framework to Python path
sys.path.insert(0, str(Path(__file__).parent / "test_framework"))

try:
    from core.test_runner import ComprehensiveTestRunner
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    print(f"❌ Test framework import error: {e}")
    FRAMEWORK_AVAILABLE = False

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="RCCM Quiz Comprehensive Test Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_comprehensive_tests.py --all                    # Run all 39 test cases
  python run_comprehensive_tests.py --department 基礎科目      # Test one department
  python run_comprehensive_tests.py --questions 10           # Test 10-question config
  python run_comprehensive_tests.py --parallel --workers 4   # Parallel execution
        """
    )
    
    # Test execution options
    parser.add_argument("--all", action="store_true", 
                       help="Run all 39 test cases (13 departments × 3 question counts)")
    parser.add_argument("--department", type=str, 
                       help="Run tests for specific department")
    parser.add_argument("--questions", type=int, choices=[10, 20, 30],
                       help="Run tests for specific question count")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of parallel workers (default: 4)")
    
    # Output options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    parser.add_argument("--no-reports", action="store_true",
                       help="Skip report generation")
    
    # Validation options
    parser.add_argument("--validate-environment", action="store_true",
                       help="Only validate test environment")
    parser.add_argument("--validate-data", action="store_true",
                       help="Only validate department data")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Check framework availability
    if not FRAMEWORK_AVAILABLE:
        logger.error("❌ Test framework not available. Please check imports.")
        return 1
    
    # Print framework banner
    print_banner()
    
    try:
        # Initialize test runner
        logger.info("🚀 Initializing Comprehensive Test Runner...")
        runner = ComprehensiveTestRunner()
        
        # Validation-only modes
        if args.validate_environment:
            logger.info("🔍 Validating test environment...")
            if runner._validate_test_environment():
                logger.info("✅ Test environment validation passed")
                return 0
            else:
                logger.error("❌ Test environment validation failed")
                return 1
        
        if args.validate_data:
            logger.info("🔍 Validating department data...")
            if runner._validate_all_department_data():
                logger.info("✅ Department data validation passed")
                return 0
            else:
                logger.error("❌ Department data validation failed")
                return 1
        
        # Test execution modes
        success = False
        
        if args.all:
            logger.info("🎯 Executing comprehensive test suite (39 test cases)...")
            success = runner.execute_comprehensive_suite(
                parallel=args.parallel, 
                max_workers=args.workers
            )
        elif args.department:
            logger.info(f"🏢 Executing department suite: {args.department}")
            success = runner.execute_department_suite(args.department)
        elif args.questions:
            logger.info(f"🔢 Executing question count suite: {args.questions} questions")
            success = runner.execute_configuration_suite(args.questions)
        else:
            parser.print_help()
            return 1
        
        # Print final results
        if success:
            logger.info("🎉 All tests completed successfully!")
            print_success_summary(runner.get_test_results())
            return 0
        else:
            logger.error("❌ Some tests failed!")
            print_failure_summary(runner.get_test_results())
            return 1
            
    except KeyboardInterrupt:
        logger.warning("⚠️ Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"🚨 Unexpected error: {e}")
        return 1

def print_banner():
    """Print framework banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎯 RCCM Quiz Comprehensive Test Framework                  ║
║                                                                              ║
║  📊 Test Matrix: 13 Departments × 3 Question Counts = 39 Total Test Cases   ║
║  🏢 Departments: 基礎科目 + 12 Specialist Departments                         ║
║  🔢 Question Counts: 10, 20, 30 questions per session                       ║
║  ✅ Validation: Complete flow from start to results                          ║
║                                                                              ║
║  🎖️ Success Criteria: 100% test case success rate                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_success_summary(test_results: dict):
    """Print success summary"""
    stats = test_results.get('execution_stats', {})
    
    summary = f"""
🎉 COMPREHENSIVE TEST EXECUTION COMPLETED SUCCESSFULLY!

📊 Test Statistics:
├── Total Tests: {stats.get('total_tests', 0)}
├── Completed: {stats.get('completed_tests', 0)}
├── Passed: {stats.get('passed_tests', 0)} ✅
├── Failed: {stats.get('failed_tests', 0)} ❌
├── Errors: {stats.get('error_tests', 0)} 🚨
└── Success Rate: {(stats.get('passed_tests', 0) / max(stats.get('completed_tests', 1), 1) * 100):.1f}%

🎯 All quality gates passed! System ready for production.
    """
    print(summary)

def print_failure_summary(test_results: dict):
    """Print failure summary"""
    stats = test_results.get('execution_stats', {})
    
    summary = f"""
❌ TEST EXECUTION COMPLETED WITH FAILURES

📊 Test Statistics:
├── Total Tests: {stats.get('total_tests', 0)}
├── Completed: {stats.get('completed_tests', 0)}
├── Passed: {stats.get('passed_tests', 0)} ✅
├── Failed: {stats.get('failed_tests', 0)} ❌
├── Errors: {stats.get('error_tests', 0)} 🚨
└── Success Rate: {(stats.get('passed_tests', 0) / max(stats.get('completed_tests', 1), 1) * 100):.1f}%

🚨 Quality gates not met. Review failed tests before proceeding.
    """
    print(summary)

if __name__ == "__main__":
    sys.exit(main())