#!/usr/bin/env python3
"""
🗄️ Database Configuration - Scalable SQLAlchemy Implementation
CSV直接読み込みからスケーラブルなデータベース基盤への移行
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# SQLAlchemy imports with graceful fallback
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import create_engine, text, event
    from sqlalchemy.engine import Engine
    from sqlalchemy.pool import QueuePool, StaticPool
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import Integer, String, Text, DateTime, Boolean, Float, Index
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    SQLAlchemy = None

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Initialize SQLAlchemy
if SQLALCHEMY_AVAILABLE:
    db = SQLAlchemy(model_class=Base)
else:
    db = None
    logger.warning("⚠️ SQLAlchemy not available. Database features will be disabled.")

class DatabaseConfig:
    """Database configuration with connection pooling"""
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL with fallback options"""
        
        # Production database (PostgreSQL)
        if os.environ.get('DATABASE_URL'):
            url = os.environ.get('DATABASE_URL')
            # Fix Heroku postgres:// URL
            if url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql://', 1)
            return url
        
        # Development database options
        database_type = os.environ.get('DB_TYPE', 'sqlite').lower()
        
        if database_type == 'postgresql':
            # PostgreSQL configuration
            host = os.environ.get('DB_HOST', 'localhost')
            port = os.environ.get('DB_PORT', '5432')
            user = os.environ.get('DB_USER', 'rccm_user')
            password = os.environ.get('DB_PASSWORD', 'rccm_password')
            database = os.environ.get('DB_NAME', 'rccm_quiz')
            return f'postgresql://{user}:{password}@{host}:{port}/{database}'
        
        elif database_type == 'mysql':
            # MySQL configuration
            host = os.environ.get('DB_HOST', 'localhost')
            port = os.environ.get('DB_PORT', '3306')
            user = os.environ.get('DB_USER', 'rccm_user')
            password = os.environ.get('DB_PASSWORD', 'rccm_password')
            database = os.environ.get('DB_NAME', 'rccm_quiz')
            return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
        
        else:
            # SQLite (default for development)
            db_path = os.environ.get('DB_PATH', 'rccm_quiz.db')
            return f'sqlite:///{db_path}'
    
    @staticmethod
    def get_engine_config() -> Dict[str, Any]:
        """Get SQLAlchemy engine configuration with connection pooling"""
        
        database_url = DatabaseConfig.get_database_url()
        config = {}
        
        if database_url.startswith('sqlite'):
            # SQLite configuration
            config.update({
                'poolclass': StaticPool,
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 30
                }
            })
        else:
            # PostgreSQL/MySQL configuration with connection pooling
            config.update({
                'poolclass': QueuePool,
                'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10)),
                'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 20)),
                'pool_timeout': int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 30)),
                'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 3600)),
                'pool_pre_ping': True,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'rccm_quiz_app'
                }
            })
        
        # Echo SQL queries in development
        config['echo'] = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'
        
        return config

def configure_flask_app_database(app):
    """Configure Flask app with database settings"""
    if not SQLALCHEMY_AVAILABLE:
        logger.error("❌ SQLAlchemy not available. Cannot configure database.")
        return False
    
    try:
        # Database configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_url()
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = DatabaseConfig.get_engine_config()
        
        # SQLAlchemy settings
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_RECORD_QUERIES'] = os.environ.get('FLASK_ENV') == 'development'
        
        # Connection pool settings
        app.config['SQLALCHEMY_POOL_SIZE'] = int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10))
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 20))
        app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 30))
        app.config['SQLALCHEMY_POOL_RECYCLE'] = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 3600))
        
        # Initialize database
        db.init_app(app)
        
        # Configure connection pool events
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Configure SQLite-specific settings"""
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        logger.info("✅ Database configuration completed successfully")
        logger.info(f"🗄️ Database URL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}@***")
        logger.info(f"🔗 Pool Size: {app.config['SQLALCHEMY_POOL_SIZE']}")
        logger.info(f"📈 Max Overflow: {app.config['SQLALCHEMY_MAX_OVERFLOW']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database configuration failed: {e}")
        return False

class Question(db.Model if SQLALCHEMY_AVAILABLE else object):
    """Question model for database storage"""
    
    __tablename__ = 'questions'
    
    if SQLALCHEMY_AVAILABLE:
        # Primary key
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        
        # Question data
        question_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
        question_text: Mapped[str] = mapped_column(Text, nullable=False)
        
        # Answer options
        option_a: Mapped[str] = mapped_column(Text, nullable=False)
        option_b: Mapped[str] = mapped_column(Text, nullable=False)
        option_c: Mapped[str] = mapped_column(Text, nullable=False)
        option_d: Mapped[str] = mapped_column(Text, nullable=False)
        
        # Correct answer
        correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
        
        # Categorization
        department: Mapped[str] = mapped_column(String(100), nullable=False)
        category: Mapped[str] = mapped_column(String(100), nullable=False)
        difficulty: Mapped[Optional[str]] = mapped_column(String(20))
        
        # Metadata
        year: Mapped[Optional[int]] = mapped_column(Integer)
        source_file: Mapped[Optional[str]] = mapped_column(String(200))
        
        # Timestamps
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Performance tracking
        usage_count: Mapped[int] = mapped_column(Integer, default=0)
        correct_rate: Mapped[Optional[float]] = mapped_column(Float)
        
        # Indexes for performance
        __table_args__ = (
            Index('idx_department_category', 'department', 'category'),
            Index('idx_question_id', 'question_id'),
            Index('idx_difficulty', 'difficulty'),
            Index('idx_usage_count', 'usage_count'),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary (compatible with existing CSV format)"""
        if not SQLALCHEMY_AVAILABLE:
            return {}
        
        return {
            'id': self.question_id,
            'question': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_answer': self.correct_answer,
            'department': self.department,
            'category': self.category,
            'difficulty': self.difficulty,
            'year': self.year,
            'usage_count': self.usage_count,
            'correct_rate': self.correct_rate
        }
    
    @classmethod
    def from_csv_row(cls, row: Dict[str, str], department: str, source_file: str):
        """Create Question instance from CSV row"""
        if not SQLALCHEMY_AVAILABLE:
            return None
        
        return cls(
            question_id=row.get('id', ''),
            question_text=row.get('question', ''),
            option_a=row.get('option_a', ''),
            option_b=row.get('option_b', ''),
            option_c=row.get('option_c', ''),
            option_d=row.get('option_d', ''),
            correct_answer=row.get('correct_answer', ''),
            department=department,
            category=row.get('category', ''),
            difficulty=row.get('difficulty'),
            year=int(row['year']) if row.get('year', '').isdigit() else None,
            source_file=source_file
        )

class UserProgress(db.Model if SQLALCHEMY_AVAILABLE else object):
    """User progress tracking model"""
    
    __tablename__ = 'user_progress'
    
    if SQLALCHEMY_AVAILABLE:
        # Primary key
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        
        # User identification
        user_id: Mapped[str] = mapped_column(String(100), nullable=False)
        question_id: Mapped[str] = mapped_column(String(50), nullable=False)
        
        # Progress data
        attempts: Mapped[int] = mapped_column(Integer, default=0)
        correct_attempts: Mapped[int] = mapped_column(Integer, default=0)
        last_attempt_correct: Mapped[bool] = mapped_column(Boolean, default=False)
        
        # SRS data
        mastery_level: Mapped[int] = mapped_column(Integer, default=0)
        next_review: Mapped[Optional[datetime]] = mapped_column(DateTime)
        
        # Timestamps
        first_attempt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        last_attempt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_user_question', 'user_id', 'question_id'),
            Index('idx_user_review', 'user_id', 'next_review'),
            Index('idx_mastery_level', 'mastery_level'),
        )

def get_database_status() -> Dict[str, Any]:
    """Get current database status and metrics"""
    if not SQLALCHEMY_AVAILABLE:
        return {
            'available': False,
            'error': 'SQLAlchemy not installed'
        }
    
    try:
        engine = db.engine
        pool = engine.pool
        
        return {
            'available': True,
            'database_url': engine.url.database,
            'dialect': engine.dialect.name,
            'pool_class': pool.__class__.__name__,
            'pool_size': getattr(pool, 'size', lambda: 'N/A')(),
            'checked_out': getattr(pool, 'checkedout', lambda: 'N/A')(),
            'overflow': getattr(pool, 'overflow', lambda: 'N/A')(),
            'checked_in': getattr(pool, 'checkedin', lambda: 'N/A')(),
        }
    except Exception as e:
        return {
            'available': False,
            'error': str(e)
        }

def create_tables(app):
    """Create all database tables"""
    if not SQLALCHEMY_AVAILABLE:
        logger.error("❌ Cannot create tables: SQLAlchemy not available")
        return False
    
    try:
        with app.app_context():
            db.create_all()
            logger.info("✅ Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    # Test database configuration
    print("🗄️ Database Configuration Test")
    print("=" * 50)
    
    if SQLALCHEMY_AVAILABLE:
        print("✅ SQLAlchemy available")
        print(f"🔗 Database URL: {DatabaseConfig.get_database_url()}")
        print(f"⚙️ Engine Config: {DatabaseConfig.get_engine_config()}")
        print(f"📊 Status: {get_database_status()}")
    else:
        print("❌ SQLAlchemy not available")
        print("💡 Install with: pip install sqlalchemy flask-sqlalchemy")
    
    print("\nDatabase configuration test completed.")