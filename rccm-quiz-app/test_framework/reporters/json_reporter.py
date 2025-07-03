#!/usr/bin/env python3
"""
📊 JSON Reporter - Generate Structured JSON Test Reports
Creates machine-readable JSON reports for automated processing and integration
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class JSONReporter:
    """Generate structured JSON test reports"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.reports_dir = self.base_dir / "results" / "reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> str:
        """Generate comprehensive JSON test report"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"test_report_{timestamp}.json"
        
        try:
            # Build comprehensive report data
            report_data = self._build_report_data(test_results, execution_stats)
            
            # Write JSON file with proper formatting
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            return str(report_path)
            
        except Exception as e:
            raise Exception(f"Failed to generate JSON report: {e}")

    def _build_report_data(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive report data structure"""
        # Generate metadata
        metadata = self._generate_metadata(execution_stats)
        
        # Generate summary statistics
        summary = self._generate_summary_statistics(test_results, execution_stats)
        
        # Generate detailed analysis
        analysis = self._generate_detailed_analysis(test_results)
        
        # Generate quality metrics
        quality_metrics = self._generate_quality_metrics(test_results, execution_stats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, quality_metrics)
        
        return {
            "metadata": metadata,
            "summary": summary,
            "analysis": analysis,
            "quality_metrics": quality_metrics,
            "recommendations": recommendations,
            "detailed_results": test_results,
            "raw_execution_stats": execution_stats
        }

    def _generate_metadata(self, execution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            "report_version": "1.0",
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": "comprehensive_test_report",
            "framework_version": "RCCM Test Framework v1.0",
            "test_session": {
                "start_time": execution_stats.get('start_time'),
                "end_time": execution_stats.get('end_time'),
                "duration_seconds": self._calculate_duration_seconds(execution_stats),
                "session_id": execution_stats.get('session_id', 'unknown')
            },
            "environment": {
                "platform": "RCCM Quiz Application",
                "testing_mode": "comprehensive",
                "departments_tested": 13,
                "question_count_variations": [10, 20, 30],
                "total_test_matrix": "13 departments × 3 question counts"
            }
        }

    def _generate_summary_statistics(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = execution_stats.get('total_tests', 0)
        completed = execution_stats.get('completed_tests', 0)
        passed = execution_stats.get('passed_tests', 0)
        failed = execution_stats.get('failed_tests', 0)
        errors = execution_stats.get('error_tests', 0)
        skipped = execution_stats.get('skipped_tests', 0)
        
        # Calculate rates
        completion_rate = (completed / total * 100) if total > 0 else 0
        success_rate = (passed / completed * 100) if completed > 0 else 0
        failure_rate = (failed / completed * 100) if completed > 0 else 0
        error_rate = (errors / completed * 100) if completed > 0 else 0
        
        # Determine overall status
        if success_rate >= 95:
            overall_status = "EXCELLENT"
            status_level = "success"
        elif success_rate >= 80:
            overall_status = "GOOD"
            status_level = "warning"
        elif success_rate >= 60:
            overall_status = "ACCEPTABLE"
            status_level = "warning"
        else:
            overall_status = "NEEDS_ATTENTION"
            status_level = "error"
        
        return {
            "overall_status": overall_status,
            "status_level": status_level,
            "test_counts": {
                "total": total,
                "completed": completed,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped
            },
            "rates": {
                "completion_rate": round(completion_rate, 2),
                "success_rate": round(success_rate, 2),
                "failure_rate": round(failure_rate, 2),
                "error_rate": round(error_rate, 2)
            },
            "performance": {
                "average_execution_time": self._calculate_average_execution_time(test_results),
                "fastest_test": self._find_fastest_test(test_results),
                "slowest_test": self._find_slowest_test(test_results),
                "total_execution_time": self._calculate_total_execution_time(test_results)
            }
        }

    def _generate_detailed_analysis(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analysis breakdown"""
        # Analyze by department
        department_analysis = self._analyze_by_department(test_results)
        
        # Analyze by question count
        question_count_analysis = self._analyze_by_question_count(test_results)
        
        # Analyze failure patterns
        failure_analysis = self._analyze_failures(test_results)
        
        # Analyze performance patterns
        performance_analysis = self._analyze_performance(test_results)
        
        return {
            "department_breakdown": department_analysis,
            "question_count_breakdown": question_count_analysis,
            "failure_patterns": failure_analysis,
            "performance_patterns": performance_analysis
        }

    def _generate_quality_metrics(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quality metrics and indicators"""
        # Test coverage metrics
        coverage_metrics = self._calculate_coverage_metrics(test_results)
        
        # Reliability metrics
        reliability_metrics = self._calculate_reliability_metrics(test_results, execution_stats)
        
        # Performance metrics
        performance_metrics = self._calculate_performance_metrics(test_results)
        
        # Consistency metrics
        consistency_metrics = self._calculate_consistency_metrics(test_results)
        
        return {
            "coverage": coverage_metrics,
            "reliability": reliability_metrics,
            "performance": performance_metrics,
            "consistency": consistency_metrics,
            "overall_quality_score": self._calculate_overall_quality_score(
                coverage_metrics, reliability_metrics, performance_metrics, consistency_metrics
            )
        }

    def _generate_recommendations(self, analysis: Dict[str, Any], quality_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Performance recommendations
        if quality_metrics["performance"]["average_execution_time"] > 5.0:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "title": "Optimize Test Execution Time",
                "description": "Average test execution time exceeds 5 seconds",
                "action": "Review and optimize slow test cases, consider parallel execution",
                "impact": "Reduce overall test suite execution time"
            })
        
        # Reliability recommendations
        if quality_metrics["reliability"]["failure_rate"] > 5.0:
            recommendations.append({
                "type": "reliability",
                "priority": "high",
                "title": "Address Test Failures",
                "description": f"Failure rate of {quality_metrics['reliability']['failure_rate']:.1f}% needs attention",
                "action": "Investigate and fix failing test cases",
                "impact": "Improve overall test suite reliability"
            })
        
        # Coverage recommendations
        if quality_metrics["coverage"]["department_coverage"] < 100.0:
            recommendations.append({
                "type": "coverage",
                "priority": "medium",
                "title": "Complete Department Coverage",
                "description": "Not all departments have been fully tested",
                "action": "Ensure all 13 departments are tested with all question count variations",
                "impact": "Achieve 100% department coverage"
            })
        
        # Consistency recommendations
        if quality_metrics["consistency"]["cross_department_consistency"] < 80.0:
            recommendations.append({
                "type": "consistency",
                "priority": "medium",
                "title": "Improve Cross-Department Consistency",
                "description": "Test results vary significantly across departments",
                "action": "Investigate department-specific issues and standardize test procedures",
                "impact": "Achieve consistent test results across all departments"
            })
        
        return recommendations

    def _analyze_by_department(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results by department"""
        department_stats = {}
        
        for test_id, result in test_results.items():
            department = result.get('department', self._extract_department_from_test_id(test_id))
            
            if department not in department_stats:
                department_stats[department] = {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "error_tests": 0,
                    "execution_times": [],
                    "question_counts_tested": set()
                }
            
            stats = department_stats[department]
            stats["total_tests"] += 1
            
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                stats["passed_tests"] += 1
            elif status == 'FAIL':
                stats["failed_tests"] += 1
            elif status == 'ERROR':
                stats["error_tests"] += 1
            
            stats["execution_times"].append(result.get('execution_time', 0))
            stats["question_counts_tested"].add(result.get('question_count', 0))
        
        # Calculate derived metrics for each department
        for dept, stats in department_stats.items():
            stats["success_rate"] = (stats["passed_tests"] / stats["total_tests"] * 100) if stats["total_tests"] > 0 else 0
            stats["average_execution_time"] = sum(stats["execution_times"]) / len(stats["execution_times"]) if stats["execution_times"] else 0
            stats["question_counts_tested"] = sorted(list(stats["question_counts_tested"]))
        
        return department_stats

    def _analyze_by_question_count(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results by question count"""
        question_count_stats = {}
        
        for test_id, result in test_results.items():
            question_count = result.get('question_count', self._extract_question_count_from_test_id(test_id))
            
            if question_count not in question_count_stats:
                question_count_stats[question_count] = {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "error_tests": 0,
                    "execution_times": [],
                    "departments_tested": set()
                }
            
            stats = question_count_stats[question_count]
            stats["total_tests"] += 1
            
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                stats["passed_tests"] += 1
            elif status == 'FAIL':
                stats["failed_tests"] += 1
            elif status == 'ERROR':
                stats["error_tests"] += 1
            
            stats["execution_times"].append(result.get('execution_time', 0))
            stats["departments_tested"].add(result.get('department', 'Unknown'))
        
        # Calculate derived metrics for each question count
        for count, stats in question_count_stats.items():
            stats["success_rate"] = (stats["passed_tests"] / stats["total_tests"] * 100) if stats["total_tests"] > 0 else 0
            stats["average_execution_time"] = sum(stats["execution_times"]) / len(stats["execution_times"]) if stats["execution_times"] else 0
            stats["departments_tested"] = sorted(list(stats["departments_tested"]))
        
        return question_count_stats

    def _analyze_failures(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze failure patterns"""
        failure_patterns = {
            "common_errors": {},
            "failure_by_step": {},
            "department_specific_failures": {},
            "question_count_specific_failures": {}
        }
        
        for test_id, result in test_results.items():
            if result.get('status') in ['FAIL', 'ERROR']:
                error = result.get('error', 'Unknown error')
                step_failed = result.get('step_failed', 'unknown')
                department = result.get('department', 'unknown')
                question_count = result.get('question_count', 0)
                
                # Track common errors
                if error not in failure_patterns["common_errors"]:
                    failure_patterns["common_errors"][error] = 0
                failure_patterns["common_errors"][error] += 1
                
                # Track failures by step
                if step_failed not in failure_patterns["failure_by_step"]:
                    failure_patterns["failure_by_step"][step_failed] = 0
                failure_patterns["failure_by_step"][step_failed] += 1
                
                # Track department-specific failures
                if department not in failure_patterns["department_specific_failures"]:
                    failure_patterns["department_specific_failures"][department] = []
                failure_patterns["department_specific_failures"][department].append({
                    "test_id": test_id,
                    "error": error,
                    "step_failed": step_failed
                })
                
                # Track question count specific failures
                if question_count not in failure_patterns["question_count_specific_failures"]:
                    failure_patterns["question_count_specific_failures"][question_count] = []
                failure_patterns["question_count_specific_failures"][question_count].append({
                    "test_id": test_id,
                    "error": error,
                    "department": department
                })
        
        return failure_patterns

    def _analyze_performance(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance patterns"""
        execution_times = [result.get('execution_time', 0) for result in test_results.values()]
        
        if not execution_times:
            return {"error": "No execution time data available"}
        
        execution_times.sort()
        n = len(execution_times)
        
        return {
            "average_execution_time": sum(execution_times) / n,
            "median_execution_time": execution_times[n // 2],
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "percentile_90": execution_times[int(n * 0.9)] if n > 0 else 0,
            "percentile_95": execution_times[int(n * 0.95)] if n > 0 else 0,
            "total_execution_time": sum(execution_times),
            "performance_distribution": {
                "fast_tests": len([t for t in execution_times if t < 2.0]),
                "medium_tests": len([t for t in execution_times if 2.0 <= t < 5.0]),
                "slow_tests": len([t for t in execution_times if t >= 5.0])
            }
        }

    def _calculate_coverage_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        departments_tested = set()
        question_counts_tested = set()
        
        for result in test_results.values():
            departments_tested.add(result.get('department', 'Unknown'))
            question_counts_tested.add(result.get('question_count', 0))
        
        expected_departments = 13
        expected_question_counts = 3  # [10, 20, 30]
        expected_total_combinations = expected_departments * expected_question_counts
        
        return {
            "department_coverage": (len(departments_tested) / expected_departments * 100) if expected_departments > 0 else 0,
            "question_count_coverage": (len(question_counts_tested) / expected_question_counts * 100) if expected_question_counts > 0 else 0,
            "combination_coverage": (len(test_results) / expected_total_combinations * 100) if expected_total_combinations > 0 else 0,
            "departments_tested": len(departments_tested),
            "question_counts_tested": len(question_counts_tested),
            "total_combinations_tested": len(test_results)
        }

    def _calculate_reliability_metrics(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate reliability metrics"""
        completed = execution_stats.get('completed_tests', 0)
        passed = execution_stats.get('passed_tests', 0)
        failed = execution_stats.get('failed_tests', 0)
        errors = execution_stats.get('error_tests', 0)
        
        return {
            "success_rate": (passed / completed * 100) if completed > 0 else 0,
            "failure_rate": (failed / completed * 100) if completed > 0 else 0,
            "error_rate": (errors / completed * 100) if completed > 0 else 0,
            "reliability_score": (passed / completed * 100) if completed > 0 else 0
        }

    def _calculate_performance_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        execution_times = [result.get('execution_time', 0) for result in test_results.values()]
        
        if not execution_times:
            return {"average_execution_time": 0, "performance_score": 0}
        
        avg_time = sum(execution_times) / len(execution_times)
        
        # Performance score based on average execution time (lower is better)
        if avg_time <= 2.0:
            performance_score = 100
        elif avg_time <= 5.0:
            performance_score = 80
        elif avg_time <= 10.0:
            performance_score = 60
        else:
            performance_score = 40
        
        return {
            "average_execution_time": avg_time,
            "performance_score": performance_score
        }

    def _calculate_consistency_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate consistency metrics"""
        department_success_rates = {}
        
        # Calculate success rates by department
        for test_id, result in test_results.items():
            department = result.get('department', 'Unknown')
            if department not in department_success_rates:
                department_success_rates[department] = {"total": 0, "passed": 0}
            
            department_success_rates[department]["total"] += 1
            if result.get('status') == 'PASS':
                department_success_rates[department]["passed"] += 1
        
        # Calculate success rates
        success_rates = []
        for dept, stats in department_success_rates.items():
            if stats["total"] > 0:
                success_rate = stats["passed"] / stats["total"] * 100
                success_rates.append(success_rate)
        
        if not success_rates:
            return {"cross_department_consistency": 0}
        
        # Calculate consistency (lower standard deviation = higher consistency)
        avg_success_rate = sum(success_rates) / len(success_rates)
        variance = sum((rate - avg_success_rate) ** 2 for rate in success_rates) / len(success_rates)
        std_dev = variance ** 0.5
        
        # Consistency score (100 - normalized standard deviation)
        consistency_score = max(0, 100 - std_dev)
        
        return {
            "cross_department_consistency": consistency_score,
            "average_success_rate": avg_success_rate,
            "success_rate_std_dev": std_dev
        }

    def _calculate_overall_quality_score(self, coverage: Dict[str, Any], reliability: Dict[str, Any], 
                                       performance: Dict[str, Any], consistency: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality score"""
        # Weight factors for different aspects
        weights = {
            "coverage": 0.3,
            "reliability": 0.4,
            "performance": 0.2,
            "consistency": 0.1
        }
        
        scores = {
            "coverage": coverage.get("combination_coverage", 0),
            "reliability": reliability.get("reliability_score", 0),
            "performance": performance.get("performance_score", 0),
            "consistency": consistency.get("cross_department_consistency", 0)
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        # Determine grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(overall_score, 2),
            "grade": grade,
            "component_scores": scores,
            "weights_used": weights
        }

    def _calculate_duration_seconds(self, execution_stats: Dict[str, Any]) -> Optional[float]:
        """Calculate test duration in seconds"""
        start_time = execution_stats.get('start_time')
        end_time = execution_stats.get('end_time')
        
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                return (end_dt - start_dt).total_seconds()
            except:
                return None
        return None

    def _calculate_average_execution_time(self, test_results: Dict[str, Any]) -> float:
        """Calculate average execution time"""
        times = [result.get('execution_time', 0) for result in test_results.values()]
        return sum(times) / len(times) if times else 0

    def _calculate_total_execution_time(self, test_results: Dict[str, Any]) -> float:
        """Calculate total execution time"""
        return sum(result.get('execution_time', 0) for result in test_results.values())

    def _find_fastest_test(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Find the fastest test"""
        if not test_results:
            return {"test_id": None, "execution_time": 0}
        
        fastest = min(test_results.items(), key=lambda x: x[1].get('execution_time', float('inf')))
        return {
            "test_id": fastest[0],
            "execution_time": fastest[1].get('execution_time', 0)
        }

    def _find_slowest_test(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Find the slowest test"""
        if not test_results:
            return {"test_id": None, "execution_time": 0}
        
        slowest = max(test_results.items(), key=lambda x: x[1].get('execution_time', 0))
        return {
            "test_id": slowest[0],
            "execution_time": slowest[1].get('execution_time', 0)
        }

    def _extract_department_from_test_id(self, test_id: str) -> str:
        """Extract department from test ID"""
        return test_id.split('_')[0] if '_' in test_id else test_id

    def _extract_question_count_from_test_id(self, test_id: str) -> int:
        """Extract question count from test ID"""
        parts = test_id.split('_')
        for part in parts:
            if part.endswith('q') and part[:-1].isdigit():
                return int(part[:-1])
        return 0

if __name__ == "__main__":
    # Test the JSON reporter
    reporter = JSONReporter()
    
    # Sample test data
    test_results = {
        "basic_10q": {
            "status": "PASS",
            "execution_time": 2.5,
            "department": "基礎科目",
            "question_count": 10
        },
        "road_20q": {
            "status": "FAIL",
            "execution_time": 3.2,
            "department": "道路部門",
            "question_count": 20,
            "error": "Session initialization failed",
            "step_failed": "session_initialization"
        }
    }
    
    execution_stats = {
        "total_tests": 39,
        "completed_tests": 2,
        "passed_tests": 1,
        "failed_tests": 1,
        "error_tests": 0,
        "skipped_tests": 0,
        "start_time": "2025-06-30T12:00:00Z",
        "end_time": "2025-06-30T12:05:00Z"
    }
    
    report_path = reporter.generate_report(test_results, execution_stats)
    print(f"JSON report generated: {report_path}")
    
    # Print a sample of the generated data
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("\nReport Summary:")
        print(f"Overall Status: {data['summary']['overall_status']}")
        print(f"Success Rate: {data['summary']['rates']['success_rate']}%")
        print(f"Quality Score: {data['quality_metrics']['overall_quality_score']['overall_score']}")