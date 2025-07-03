#!/usr/bin/env python3
"""
🔍 Data Validator - Department Data Integrity Validation
Validates data availability and integrity for all 13 departments
"""

import os
import csv
import json
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path

class DataValidator:
    """Validates department data integrity and availability"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        
        # Department mapping to file patterns
        self.department_mappings = {
            '基礎科目': {'file_pattern': '4-1.csv', 'category': '共通'},
            '道路部門': {'file_pattern': '4-2_*.csv', 'category': '道路'},
            '河川・砂防部門': {'file_pattern': '4-2_*.csv', 'category': '河川、砂防及び海岸・海洋'},
            '都市計画部門': {'file_pattern': '4-2_*.csv', 'category': '都市計画及び地方計画'},
            '造園部門': {'file_pattern': '4-2_*.csv', 'category': '造園'},
            '建設環境部門': {'file_pattern': '4-2_*.csv', 'category': '建設環境'},
            '鋼構造・コンクリート部門': {'file_pattern': '4-2_*.csv', 'category': '鋼構造及びコンクリート'},
            '土質・基礎部門': {'file_pattern': '4-2_*.csv', 'category': '土質及び基礎'},
            '施工計画部門': {'file_pattern': '4-2_*.csv', 'category': '施工計画、施工設備及び積算'},
            '上下水道部門': {'file_pattern': '4-2_*.csv', 'category': '上水道及び工業用水道'},
            '森林土木部門': {'file_pattern': '4-2_*.csv', 'category': '森林土木'},
            '農業土木部門': {'file_pattern': '4-2_*.csv', 'category': '農業土木'},
            'トンネル部門': {'file_pattern': '4-2_*.csv', 'category': 'トンネル'}
        }
        
        # Question count requirements
        self.question_requirements = {
            10: 15,  # Need 15+ questions for 10-question session
            20: 25,  # Need 25+ questions for 20-question session
            30: 35   # Need 35+ questions for 30-question session
        }
        
        # Supported encodings
        self.encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
        
        self.logger = logging.getLogger(__name__)

    def validate_department_data(self, department: str, question_counts: List[int]) -> Dict[str, Any]:
        """Validate data availability for specific department"""
        try:
            if department not in self.department_mappings:
                return {
                    'valid': False,
                    'error': f"Unknown department: {department}",
                    'department': department
                }
            
            mapping = self.department_mappings[department]
            
            # Find and analyze data files
            questions = self._load_department_questions(department, mapping)
            
            if not questions:
                return {
                    'valid': False,
                    'error': f"No questions found for department: {department}",
                    'department': department
                }
            
            total_questions = len(questions)
            
            # Validate sufficient questions for each configuration
            validation_results = {}
            overall_valid = True
            
            for count in question_counts:
                required = self.question_requirements.get(count, count + 5)
                sufficient = total_questions >= required
                
                validation_results[f'{count}_questions'] = {
                    'required': required,
                    'available': total_questions,
                    'sufficient': sufficient
                }
                
                if not sufficient:
                    overall_valid = False
            
            return {
                'valid': overall_valid,
                'department': department,
                'total_questions': total_questions,
                'question_validations': validation_results,
                'sample_questions': questions[:3] if questions else [],
                'data_integrity': self._validate_question_integrity(questions)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating department {department}: {e}")
            return {
                'valid': False,
                'error': str(e),
                'department': department
            }

    def _load_department_questions(self, department: str, mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Load questions for specific department from CSV files"""
        questions = []
        
        try:
            if department == '基礎科目':
                # Load basic subject questions
                basic_file = self.data_dir / "4-1.csv"
                if basic_file.exists():
                    file_questions = self._load_csv_file(basic_file)
                    questions.extend(file_questions)
            else:
                # Load specialist questions from all year files
                specialist_files = list(self.data_dir.glob("4-2_*.csv"))
                category = mapping['category']
                
                for file_path in specialist_files:
                    file_questions = self._load_csv_file(file_path)
                    # Filter by department category
                    dept_questions = [q for q in file_questions if q.get('category') == category]
                    questions.extend(dept_questions)
            
            self.logger.debug(f"Loaded {len(questions)} questions for {department}")
            return questions
            
        except Exception as e:
            self.logger.error(f"Error loading questions for {department}: {e}")
            return []

    def _load_csv_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load CSV file with multiple encoding support"""
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    questions = list(reader)
                    
                    # Validate basic structure
                    if questions and all(key in questions[0] for key in ['id', 'question', 'correct_answer']):
                        return questions
                        
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                self.logger.warning(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        self.logger.error(f"Could not read {file_path} with any supported encoding")
        return []

    def _validate_question_integrity(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate question data integrity"""
        if not questions:
            return {'valid': False, 'error': 'No questions to validate'}
        
        integrity_issues = []
        valid_questions = 0
        
        required_fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        for i, question in enumerate(questions):
            # Check required fields
            missing_fields = [field for field in required_fields if not question.get(field)]
            if missing_fields:
                integrity_issues.append(f"Question {i+1}: Missing fields {missing_fields}")
                continue
            
            # Check correct answer validity
            correct_answer = question.get('correct_answer', '').lower()
            if correct_answer not in ['a', 'b', 'c', 'd']:
                integrity_issues.append(f"Question {i+1}: Invalid correct answer '{correct_answer}'")
                continue
            
            # Check option availability
            option_key = f'option_{correct_answer}'
            if not question.get(option_key):
                integrity_issues.append(f"Question {i+1}: Missing option for correct answer '{correct_answer}'")
                continue
            
            valid_questions += 1
        
        integrity_rate = (valid_questions / len(questions)) * 100 if questions else 0
        
        return {
            'valid': integrity_rate >= 95.0,  # 95% integrity threshold
            'total_questions': len(questions),
            'valid_questions': valid_questions,
            'integrity_rate': integrity_rate,
            'issues': integrity_issues[:10],  # Limit to first 10 issues
            'total_issues': len(integrity_issues)
        }

    def validate_all_departments(self, question_counts: List[int]) -> Dict[str, Any]:
        """Validate all departments comprehensively"""
        self.logger.info("🔍 Starting comprehensive department data validation...")
        
        validation_results = {}
        overall_stats = {
            'total_departments': len(self.department_mappings),
            'valid_departments': 0,
            'invalid_departments': 0,
            'total_questions': 0,
            'departments_by_status': {'valid': [], 'invalid': []}
        }
        
        for department in self.department_mappings.keys():
            self.logger.debug(f"Validating {department}...")
            
            result = self.validate_department_data(department, question_counts)
            validation_results[department] = result
            
            if result['valid']:
                overall_stats['valid_departments'] += 1
                overall_stats['total_questions'] += result.get('total_questions', 0)
                overall_stats['departments_by_status']['valid'].append(department)
                self.logger.debug(f"✅ {department}: {result.get('total_questions', 0)} questions")
            else:
                overall_stats['invalid_departments'] += 1
                overall_stats['departments_by_status']['invalid'].append(department)
                self.logger.warning(f"❌ {department}: {result.get('error', 'Unknown error')}")
        
        # Calculate overall validation rate
        validation_rate = (overall_stats['valid_departments'] / overall_stats['total_departments']) * 100
        
        return {
            'overall_valid': validation_rate >= 100.0,  # All departments must be valid
            'validation_rate': validation_rate,
            'stats': overall_stats,
            'department_results': validation_results,
            'summary': self._generate_validation_summary(validation_results, overall_stats)
        }

    def _generate_validation_summary(self, results: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generate human-readable validation summary"""
        summary_lines = []
        summary_lines.append("📊 Department Data Validation Summary")
        summary_lines.append("=" * 50)
        summary_lines.append(f"Total departments: {stats['total_departments']}")
        summary_lines.append(f"Valid departments: {stats['valid_departments']}")
        summary_lines.append(f"Invalid departments: {stats['invalid_departments']}")
        summary_lines.append(f"Total questions: {stats['total_questions']}")
        summary_lines.append("")
        
        if stats['departments_by_status']['valid']:
            summary_lines.append("✅ Valid departments:")
            for dept in stats['departments_by_status']['valid']:
                questions = results[dept].get('total_questions', 0)
                summary_lines.append(f"   - {dept}: {questions} questions")
        
        if stats['departments_by_status']['invalid']:
            summary_lines.append("\n❌ Invalid departments:")
            for dept in stats['departments_by_status']['invalid']:
                error = results[dept].get('error', 'Unknown error')
                summary_lines.append(f"   - {dept}: {error}")
        
        return "\n".join(summary_lines)

    def export_validation_results(self, results: Dict[str, Any], output_path: str = None) -> str:
        """Export validation results to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/department_validation_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 Validation results exported to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting validation results: {e}")
            return ""

if __name__ == "__main__":
    # Standalone validation execution
    import logging
    from datetime import datetime
    
    logging.basicConfig(level=logging.INFO)
    
    validator = DataValidator()
    question_counts = [10, 20, 30]
    
    print("🔍 Starting department data validation...")
    
    # Validate all departments
    results = validator.validate_all_departments(question_counts)
    
    # Print summary
    print(results['summary'])
    
    # Export results
    output_file = validator.export_validation_results(results)
    
    if results['overall_valid']:
        print("\n✅ All departments validation passed!")
    else:
        print(f"\n❌ Validation failed: {results['validation_rate']:.1f}% departments valid")
        
    print(f"📄 Detailed results: {output_file}")