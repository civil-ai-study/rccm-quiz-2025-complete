#!/usr/bin/env python3
"""
📄 HTML Reporter - Generate Comprehensive HTML Test Reports
Creates detailed HTML reports with charts and interactive elements
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class HTMLReporter:
    """Generate comprehensive HTML test reports"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.reports_dir = self.base_dir / "results" / "reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # HTML template components
        self.html_template = self._get_html_template()

    def generate_report(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> str:
        """Generate comprehensive HTML test report"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"test_report_{timestamp}.html"
        
        try:
            # Generate report content
            html_content = self._build_html_report(test_results, execution_stats)
            
            # Write HTML file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(report_path)
            
        except Exception as e:
            raise Exception(f"Failed to generate HTML report: {e}")

    def _build_html_report(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> str:
        """Build complete HTML report content"""
        # Generate report sections
        header_section = self._generate_header_section(execution_stats)
        summary_section = self._generate_summary_section(execution_stats)
        charts_section = self._generate_charts_section(test_results, execution_stats)
        department_section = self._generate_department_section(test_results)
        detailed_results_section = self._generate_detailed_results_section(test_results)
        footer_section = self._generate_footer_section()
        
        # Combine all sections
        html_content = self.html_template.format(
            title="RCCM Quiz Test Report",
            header=header_section,
            summary=summary_section,
            charts=charts_section,
            departments=department_section,
            detailed_results=detailed_results_section,
            footer=footer_section
        )
        
        return html_content

    def _generate_header_section(self, execution_stats: Dict[str, Any]) -> str:
        """Generate report header section"""
        start_time = execution_stats.get('start_time', 'Unknown')
        end_time = execution_stats.get('end_time', 'Unknown')
        
        if start_time != 'Unknown' and end_time != 'Unknown':
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end_dt - start_dt
                duration_str = str(duration)
            except:
                duration_str = "Unknown"
        else:
            duration_str = "Unknown"
        
        return f"""
        <div class="header-section">
            <h1>🎯 RCCM Quiz Comprehensive Test Report</h1>
            <div class="header-info">
                <div class="info-item">
                    <strong>📅 Start Time:</strong> {start_time}
                </div>
                <div class="info-item">
                    <strong>🏁 End Time:</strong> {end_time}
                </div>
                <div class="info-item">
                    <strong>⏱️ Duration:</strong> {duration_str}
                </div>
                <div class="info-item">
                    <strong>📊 Total Tests:</strong> {execution_stats.get('total_tests', 0)}
                </div>
            </div>
        </div>
        """

    def _generate_summary_section(self, execution_stats: Dict[str, Any]) -> str:
        """Generate summary statistics section"""
        total = execution_stats.get('total_tests', 0)
        completed = execution_stats.get('completed_tests', 0)
        passed = execution_stats.get('passed_tests', 0)
        failed = execution_stats.get('failed_tests', 0)
        errors = execution_stats.get('error_tests', 0)
        skipped = execution_stats.get('skipped_tests', 0)
        
        success_rate = (passed / completed * 100) if completed > 0 else 0
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Determine overall status
        if success_rate >= 95:
            status_class = "status-excellent"
            status_icon = "🟢"
            status_text = "EXCELLENT"
        elif success_rate >= 80:
            status_class = "status-good"
            status_icon = "🟡"
            status_text = "GOOD"
        else:
            status_class = "status-poor"
            status_icon = "🔴"
            status_text = "NEEDS ATTENTION"
        
        return f"""
        <div class="summary-section">
            <h2>📊 Test Execution Summary</h2>
            <div class="summary-grid">
                <div class="summary-card overall-status {status_class}">
                    <h3>{status_icon} Overall Status</h3>
                    <div class="status-value">{status_text}</div>
                    <div class="status-detail">Success Rate: {success_rate:.1f}%</div>
                </div>
                <div class="summary-card">
                    <h3>✅ Passed Tests</h3>
                    <div class="card-value">{passed}</div>
                    <div class="card-percentage">{(passed/total*100) if total > 0 else 0:.1f}%</div>
                </div>
                <div class="summary-card">
                    <h3>❌ Failed Tests</h3>
                    <div class="card-value">{failed}</div>
                    <div class="card-percentage">{(failed/total*100) if total > 0 else 0:.1f}%</div>
                </div>
                <div class="summary-card">
                    <h3>🚨 Error Tests</h3>
                    <div class="card-value">{errors}</div>
                    <div class="card-percentage">{(errors/total*100) if total > 0 else 0:.1f}%</div>
                </div>
                <div class="summary-card">
                    <h3>⏭️ Skipped Tests</h3>
                    <div class="card-value">{skipped}</div>
                    <div class="card-percentage">{(skipped/total*100) if total > 0 else 0:.1f}%</div>
                </div>
                <div class="summary-card">
                    <h3>📈 Completion Rate</h3>
                    <div class="card-value">{completion_rate:.1f}%</div>
                    <div class="card-detail">{completed}/{total} completed</div>
                </div>
            </div>
        </div>
        """

    def _generate_charts_section(self, test_results: Dict[str, Any], execution_stats: Dict[str, Any]) -> str:
        """Generate charts and visualizations section"""
        # Analyze results by department and question count
        department_stats = self._analyze_by_department(test_results)
        question_count_stats = self._analyze_by_question_count(test_results)
        
        # Generate chart data
        dept_chart_data = self._generate_department_chart_data(department_stats)
        question_chart_data = self._generate_question_count_chart_data(question_count_stats)
        
        return f"""
        <div class="charts-section">
            <h2>📊 Test Results Visualization</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>🏢 Results by Department</h3>
                    <div class="chart-placeholder">
                        <canvas id="departmentChart" width="400" height="300"></canvas>
                    </div>
                    <div class="chart-data" style="display: none;">{json.dumps(dept_chart_data)}</div>
                </div>
                <div class="chart-container">
                    <h3>🔢 Results by Question Count</h3>
                    <div class="chart-placeholder">
                        <canvas id="questionCountChart" width="400" height="300"></canvas>
                    </div>
                    <div class="chart-data" style="display: none;">{json.dumps(question_chart_data)}</div>
                </div>
            </div>
        </div>
        """

    def _generate_department_section(self, test_results: Dict[str, Any]) -> str:
        """Generate department-by-department breakdown"""
        department_stats = self._analyze_by_department(test_results)
        
        department_rows = []
        for dept, stats in department_stats.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            if success_rate >= 95:
                status_class = "status-excellent"
                status_icon = "✅"
            elif success_rate >= 80:
                status_class = "status-good"
                status_icon = "⚠️"
            else:
                status_class = "status-poor"
                status_icon = "❌"
            
            department_rows.append(f"""
                <tr class="{status_class}">
                    <td>{status_icon} {dept}</td>
                    <td>{stats['total']}</td>
                    <td>{stats['passed']}</td>
                    <td>{stats['failed']}</td>
                    <td>{stats['errors']}</td>
                    <td>{success_rate:.1f}%</td>
                    <td>{stats['avg_execution_time']:.2f}s</td>
                </tr>
            """)
        
        return f"""
        <div class="departments-section">
            <h2>🏢 Department Analysis</h2>
            <div class="table-container">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Department</th>
                            <th>Total Tests</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Errors</th>
                            <th>Success Rate</th>
                            <th>Avg Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(department_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _generate_detailed_results_section(self, test_results: Dict[str, Any]) -> str:
        """Generate detailed test results section"""
        result_rows = []
        
        for test_id, result in test_results.items():
            status = result.get('status', 'UNKNOWN')
            execution_time = result.get('execution_time', 0)
            error = result.get('error', '')
            
            if status == 'PASS':
                status_class = "status-pass"
                status_icon = "✅"
            elif status == 'FAIL':
                status_class = "status-fail"
                status_icon = "❌"
            elif status == 'ERROR':
                status_class = "status-error"
                status_icon = "🚨"
            else:
                status_class = "status-unknown"
                status_icon = "❓"
            
            # Extract department and question count from test_id
            parts = test_id.split('_')
            if len(parts) >= 2:
                department = parts[0]
                question_info = parts[1] if len(parts) > 1 else ''
            else:
                department = test_id
                question_info = ''
            
            error_display = error[:100] + '...' if len(error) > 100 else error
            
            result_rows.append(f"""
                <tr class="{status_class}">
                    <td>{test_id}</td>
                    <td>{department}</td>
                    <td>{question_info}</td>
                    <td>{status_icon} {status}</td>
                    <td>{execution_time:.2f}s</td>
                    <td title="{error}">{error_display}</td>
                </tr>
            """)
        
        return f"""
        <div class="detailed-results-section">
            <h2>📋 Detailed Test Results</h2>
            <div class="table-container">
                <table class="results-table detailed-table">
                    <thead>
                        <tr>
                            <th>Test ID</th>
                            <th>Department</th>
                            <th>Questions</th>
                            <th>Status</th>
                            <th>Execution Time</th>
                            <th>Error Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(result_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _generate_footer_section(self) -> str:
        """Generate report footer"""
        return f"""
        <div class="footer-section">
            <div class="footer-info">
                <p>📄 Report generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p>🎯 RCCM Quiz Application Test Framework v1.0</p>
                <p>🏗️ Comprehensive Testing Strategy Implementation</p>
            </div>
        </div>
        """

    def _analyze_by_department(self, test_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze test results by department"""
        department_stats = {}
        
        for test_id, result in test_results.items():
            # Extract department from test_id
            department = result.get('department', test_id.split('_')[0])
            
            if department not in department_stats:
                department_stats[department] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'errors': 0,
                    'execution_times': []
                }
            
            stats = department_stats[department]
            stats['total'] += 1
            
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                stats['passed'] += 1
            elif status == 'FAIL':
                stats['failed'] += 1
            elif status == 'ERROR':
                stats['errors'] += 1
            
            execution_time = result.get('execution_time', 0)
            stats['execution_times'].append(execution_time)
        
        # Calculate average execution times
        for stats in department_stats.values():
            if stats['execution_times']:
                stats['avg_execution_time'] = sum(stats['execution_times']) / len(stats['execution_times'])
            else:
                stats['avg_execution_time'] = 0
        
        return department_stats

    def _analyze_by_question_count(self, test_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze test results by question count"""
        question_count_stats = {}
        
        for test_id, result in test_results.items():
            # Extract question count from test_id or result
            question_count = result.get('question_count', 'Unknown')
            if question_count == 'Unknown':
                # Try to extract from test_id (e.g., "dept_10q")
                parts = test_id.split('_')
                for part in parts:
                    if part.endswith('q') and part[:-1].isdigit():
                        question_count = int(part[:-1])
                        break
            
            key = f"{question_count}_questions"
            
            if key not in question_count_stats:
                question_count_stats[key] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'errors': 0,
                    'execution_times': []
                }
            
            stats = question_count_stats[key]
            stats['total'] += 1
            
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                stats['passed'] += 1
            elif status == 'FAIL':
                stats['failed'] += 1
            elif status == 'ERROR':
                stats['errors'] += 1
            
            execution_time = result.get('execution_time', 0)
            stats['execution_times'].append(execution_time)
        
        # Calculate average execution times
        for stats in question_count_stats.values():
            if stats['execution_times']:
                stats['avg_execution_time'] = sum(stats['execution_times']) / len(stats['execution_times'])
            else:
                stats['avg_execution_time'] = 0
        
        return question_count_stats

    def _generate_department_chart_data(self, department_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate chart data for department analysis"""
        labels = list(department_stats.keys())
        passed_data = [stats['passed'] for stats in department_stats.values()]
        failed_data = [stats['failed'] for stats in department_stats.values()]
        error_data = [stats['errors'] for stats in department_stats.values()]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Passed',
                    'data': passed_data,
                    'backgroundColor': '#28a745'
                },
                {
                    'label': 'Failed',
                    'data': failed_data,
                    'backgroundColor': '#dc3545'
                },
                {
                    'label': 'Errors',
                    'data': error_data,
                    'backgroundColor': '#ffc107'
                }
            ]
        }

    def _generate_question_count_chart_data(self, question_count_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate chart data for question count analysis"""
        labels = list(question_count_stats.keys())
        passed_data = [stats['passed'] for stats in question_count_stats.values()]
        failed_data = [stats['failed'] for stats in question_count_stats.values()]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Passed',
                    'data': passed_data,
                    'backgroundColor': '#28a745'
                },
                {
                    'label': 'Failed',
                    'data': failed_data,
                    'backgroundColor': '#dc3545'
                }
            ]
        }

    def _get_html_template(self) -> str:
        """Get HTML template with CSS and JavaScript"""
        return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header-section h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .header-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
        }}
        
        .summary-section {{
            margin-bottom: 30px;
        }}
        
        .summary-section h2 {{
            color: #495057;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-2px);
        }}
        
        .summary-card h3 {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .card-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #495057;
            margin-bottom: 5px;
        }}
        
        .card-percentage {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .card-detail {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .overall-status {{
            grid-column: span 2;
        }}
        
        .overall-status .status-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .status-excellent {{
            border-left: 5px solid #28a745;
        }}
        
        .status-excellent .status-value {{
            color: #28a745;
        }}
        
        .status-good {{
            border-left: 5px solid #ffc107;
        }}
        
        .status-good .status-value {{
            color: #ffc107;
        }}
        
        .status-poor {{
            border-left: 5px solid #dc3545;
        }}
        
        .status-poor .status-value {{
            color: #dc3545;
        }}
        
        .charts-section {{
            margin-bottom: 30px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-container h3 {{
            color: #495057;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .table-container {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .results-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .results-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .results-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .results-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .status-pass {{
            border-left: 3px solid #28a745;
        }}
        
        .status-fail {{
            border-left: 3px solid #dc3545;
        }}
        
        .status-error {{
            border-left: 3px solid #ffc107;
        }}
        
        .detailed-table {{
            font-size: 0.9em;
        }}
        
        .footer-section {{
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            color: #6c757d;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .overall-status {{
                grid-column: span 1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {header}
        {summary}
        {charts}
        {departments}
        {detailed_results}
        {footer}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {{
            // Department Chart
            const deptChartElement = document.getElementById('departmentChart');
            if (deptChartElement) {{
                const deptChartData = JSON.parse(document.querySelector('#departmentChart').parentElement.nextElementSibling.textContent);
                new Chart(deptChartElement, {{
                    type: 'bar',
                    data: deptChartData,
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // Question Count Chart
            const qcChartElement = document.getElementById('questionCountChart');
            if (qcChartElement) {{
                const qcChartData = JSON.parse(document.querySelector('#questionCountChart').parentElement.nextElementSibling.textContent);
                new Chart(qcChartElement, {{
                    type: 'doughnut',
                    data: qcChartData,
                    options: {{
                        responsive: true
                    }}
                }});
            }}
        }}
    </script>
</body>
</html>
        """

if __name__ == "__main__":
    # Test the HTML reporter
    reporter = HTMLReporter()
    
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
            "error": "Session initialization failed"
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
    print(f"HTML report generated: {report_path}")