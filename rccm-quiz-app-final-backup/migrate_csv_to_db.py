#!/usr/bin/env python3
"""
🔄 CSV to Database Migration Tool
CSV直接読み込みからスケーラブルなデータベースへの移行ツール
"""

import os
import sys
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

# Add application directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import application modules
from database import db, Question, UserProgress, configure_flask_app_database, create_tables, SQLALCHEMY_AVAILABLE
from app import app
from utils import load_rccm_data_files, DataLoadError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class CSVToDBMigrator:
    """CSV data migration to SQLAlchemy database"""
    
    def __init__(self):
        self.departments = [
            '基礎科目',
            '道路部門', '河川・砂防部門', '都市計画部門', '造園部門',
            '建設環境部門', '鋼構造・コンクリート部門', '土質・基礎部門',
            '施工計画部門', '上下水道部門', '森林土木部門',
            '農業土木部門', 'トンネル部門'
        ]
        self.migration_stats = {
            'departments_processed': 0,
            'questions_imported': 0,
            'questions_skipped': 0,
            'errors': 0,
            'duplicate_ids': set(),
            'missing_files': []
        }
    
    def validate_prerequisites(self) -> bool:
        """Validate migration prerequisites"""
        logger.info("🔍 Validating migration prerequisites...")
        
        if not SQLALCHEMY_AVAILABLE:
            logger.error("❌ SQLAlchemy not available. Cannot perform migration.")
            return False
        
        # Check if Flask app is configured
        try:
            with app.app_context():
                if not hasattr(app, 'config') or not app.config.get('SQLALCHEMY_DATABASE_URI'):
                    logger.error("❌ Flask app database not configured")
                    return False
        except Exception as e:
            logger.error(f"❌ Flask app configuration error: {e}")
            return False
        
        logger.info("✅ Prerequisites validated successfully")
        return True
    
    def setup_database(self) -> bool:
        """Setup database connection and create tables"""
        logger.info("🗄️ Setting up database...")
        
        try:
            with app.app_context():
                # Configure database
                if not configure_flask_app_database(app):
                    logger.error("❌ Database configuration failed")
                    return False
                
                # Create tables
                if not create_tables(app):
                    logger.error("❌ Table creation failed")
                    return False
                
                logger.info("✅ Database setup completed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            return False
    
    def load_csv_data(self, department: str) -> List[Dict]:
        """Load CSV data for a specific department"""
        logger.info(f"📖 Loading CSV data for {department}...")
        
        try:
            # Use existing utility function to load data
            questions = load_rccm_data_files(department)
            if not questions:
                self.migration_stats['missing_files'].append(department)
                logger.warning(f"⚠️ No data found for {department}")
                return []
            
            logger.info(f"📊 Loaded {len(questions)} questions for {department}")
            return questions
            
        except DataLoadError as e:
            logger.error(f"❌ Data load error for {department}: {e}")
            self.migration_stats['errors'] += 1
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error loading {department}: {e}")
            self.migration_stats['errors'] += 1
            return []
    
    def validate_question_data(self, question_data: Dict, department: str) -> bool:
        """Validate individual question data"""
        required_fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        for field in required_fields:
            if not question_data.get(field, '').strip():
                logger.warning(f"⚠️ Missing required field '{field}' in question {question_data.get('id', 'unknown')} for {department}")
                return False
        
        # Validate correct answer format
        correct_answer = question_data.get('correct_answer', '').upper()
        if correct_answer not in ['A', 'B', 'C', 'D']:
            logger.warning(f"⚠️ Invalid correct answer '{correct_answer}' in question {question_data.get('id', 'unknown')} for {department}")
            return False
        
        return True
    
    def check_duplicate_question_id(self, question_id: str) -> bool:
        """Check if question ID already exists in database"""
        try:
            with app.app_context():
                existing = Question.query.filter_by(question_id=question_id).first()
                return existing is not None
        except Exception as e:
            logger.error(f"❌ Error checking duplicate ID {question_id}: {e}")
            return False
    
    def import_questions_for_department(self, department: str) -> int:
        """Import questions for a specific department"""
        logger.info(f"🔄 Importing questions for {department}...")
        
        # Load CSV data
        csv_questions = self.load_csv_data(department)
        if not csv_questions:
            return 0
        
        imported_count = 0
        skipped_count = 0
        
        try:
            with app.app_context():
                for question_data in csv_questions:
                    # Validate question data
                    if not self.validate_question_data(question_data, department):
                        skipped_count += 1
                        continue
                    
                    question_id = question_data.get('id', '').strip()
                    
                    # Check for duplicates
                    if self.check_duplicate_question_id(question_id):
                        logger.warning(f"⚠️ Duplicate question ID: {question_id} (skipping)")
                        self.migration_stats['duplicate_ids'].add(question_id)
                        skipped_count += 1
                        continue
                    
                    # Determine source file name
                    source_file = f"{department.replace('部門', '').replace('科目', '')}_questions.csv"
                    
                    # Create Question object
                    question = Question.from_csv_row(
                        row=question_data,
                        department=department,
                        source_file=source_file
                    )
                    
                    if question:
                        db.session.add(question)
                        imported_count += 1
                    else:
                        skipped_count += 1
                
                # Commit changes for this department
                db.session.commit()
                logger.info(f"✅ {department}: {imported_count} imported, {skipped_count} skipped")
                
        except Exception as e:
            logger.error(f"❌ Import error for {department}: {e}")
            try:
                db.session.rollback()
            except:
                pass
            self.migration_stats['errors'] += 1
            return 0
        
        return imported_count
    
    def generate_migration_report(self) -> Dict:
        """Generate comprehensive migration report"""
        total_questions = self.migration_stats['questions_imported'] + self.migration_stats['questions_skipped']
        success_rate = (self.migration_stats['questions_imported'] / max(total_questions, 1)) * 100
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'migration_summary': {
                'departments_processed': self.migration_stats['departments_processed'],
                'total_departments': len(self.departments),
                'questions_imported': self.migration_stats['questions_imported'],
                'questions_skipped': self.migration_stats['questions_skipped'],
                'success_rate': round(success_rate, 2),
                'errors': self.migration_stats['errors']
            },
            'data_quality': {
                'duplicate_ids_count': len(self.migration_stats['duplicate_ids']),
                'duplicate_ids': list(self.migration_stats['duplicate_ids']),
                'missing_files': self.migration_stats['missing_files']
            },
            'database_status': self.get_database_status()
        }
    
    def get_database_status(self) -> Dict:
        """Get post-migration database status"""
        try:
            with app.app_context():
                total_questions = Question.query.count()
                departments_in_db = db.session.query(Question.department).distinct().count()
                
                return {
                    'total_questions': total_questions,
                    'departments_in_database': departments_in_db,
                    'connection_status': 'active'
                }
        except Exception as e:
            return {
                'total_questions': 0,
                'departments_in_database': 0,
                'connection_status': f'error: {e}'
            }
    
    def run_migration(self, departments: Optional[List[str]] = None) -> Dict:
        """Run complete migration process"""
        logger.info("🚀 Starting CSV to Database Migration")
        logger.info("=" * 80)
        
        # Use all departments if none specified
        if departments is None:
            departments = self.departments
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            return {'success': False, 'error': 'Prerequisites validation failed'}
        
        # Setup database
        if not self.setup_database():
            return {'success': False, 'error': 'Database setup failed'}
        
        # Import data for each department
        for department in departments:
            logger.info(f"🔄 Processing department: {department}")
            imported_count = self.import_questions_for_department(department)
            
            self.migration_stats['departments_processed'] += 1
            self.migration_stats['questions_imported'] += imported_count
            
            # Add skipped count (calculated in import method)
            # The actual skipped count is tracked within the import method
        
        # Generate final report
        report = self.generate_migration_report()
        
        logger.info("✅ Migration completed successfully")
        logger.info("=" * 80)
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   Departments: {report['migration_summary']['departments_processed']}/{report['migration_summary']['total_departments']}")
        logger.info(f"   Questions: {report['migration_summary']['questions_imported']} imported")
        logger.info(f"   Success Rate: {report['migration_summary']['success_rate']}%")
        logger.info(f"   Errors: {report['migration_summary']['errors']}")
        
        return {
            'success': True,
            'report': report
        }

def main():
    """Main migration execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RCCM Quiz CSV to Database Migration Tool')
    parser.add_argument('--department', '-d', help='Migrate specific department only')
    parser.add_argument('--dry-run', action='store_true', help='Validate only, do not import')
    parser.add_argument('--force', action='store_true', help='Force migration even if database exists')
    parser.add_argument('--report-file', '-r', help='Save report to file')
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = CSVToDBMigrator()
    
    # Determine departments to migrate
    departments = None
    if args.department:
        if args.department in migrator.departments:
            departments = [args.department]
        else:
            logger.error(f"❌ Invalid department: {args.department}")
            logger.info(f"💡 Available departments: {', '.join(migrator.departments)}")
            sys.exit(1)
    
    # Dry run validation
    if args.dry_run:
        logger.info("🧪 Running migration validation (dry run)...")
        
        if not migrator.validate_prerequisites():
            logger.error("❌ Prerequisites validation failed")
            sys.exit(1)
        
        # Test data loading for all departments
        total_questions = 0
        for dept in departments or migrator.departments:
            questions = migrator.load_csv_data(dept)
            total_questions += len(questions)
            logger.info(f"📊 {dept}: {len(questions)} questions available")
        
        logger.info(f"✅ Dry run completed. {total_questions} questions ready for migration.")
        return
    
    # Run actual migration
    try:
        result = migrator.run_migration(departments)
        
        if not result['success']:
            logger.error(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Save report if requested
        if args.report_file:
            import json
            with open(args.report_file, 'w', encoding='utf-8') as f:
                json.dump(result['report'], f, ensure_ascii=False, indent=2)
            logger.info(f"📄 Report saved to: {args.report_file}")
        
        logger.info("🎉 Migration completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected migration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()