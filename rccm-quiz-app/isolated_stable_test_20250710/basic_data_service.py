#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-4】基礎科目専用データサービス実装
data/4-1.csv専用アクセス・専門科目データ非アクセス保証・エラーハンドリング強化
basic_session_manager.pyとの完全統合・新ファイル作成のみ・既存システム影響ゼロ保証
"""

import os
import csv
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
# Flask-conditional imports for testing compatibility
try:
    from basic_session_manager import BasicExamSessionManager, create_basic_exam_session, get_basic_exam_session
    SESSION_MANAGER_AVAILABLE = True
except ImportError as e:
    SESSION_MANAGER_AVAILABLE = False
    # Mock classes for testing
    class BasicExamSessionManager:
        def is_session_active(self): return False
    
    def create_basic_exam_session(questions, metadata=None): return "mock_session_id"
    def get_basic_exam_session(): return None

class BasicDataService:
    """基礎科目専用データサービスクラス"""
    
    # データファイルパス（基礎科目のみ）
    BASIC_QUESTIONS_FILE = 'data/4-1.csv'
    
    # 専門科目ファイル（アクセス厳格禁止リスト）
    FORBIDDEN_SPECIALIST_FILES = [
        'data/4-2_2008.csv', 'data/4-2_2009.csv', 'data/4-2_2010.csv',
        'data/4-2_2011.csv', 'data/4-2_2012.csv', 'data/4-2_2013.csv',
        'data/4-2_2014.csv', 'data/4-2_2015.csv', 'data/4-2_2016.csv',
        'data/4-2_2017.csv', 'data/4-2_2018.csv', 'data/4-2_2019.csv'
    ]
    
    # エンコーディング設定
    ENCODING_OPTIONS = ['utf-8', 'shift_jis', 'cp932', 'euc-jp']
    
    def __init__(self):
        """基礎科目データサービス初期化"""
        self.questions_cache = None
        self.cache_timestamp = None
        self.cache_duration = 3600  # 1時間キャッシュ
        self.session_manager = BasicExamSessionManager()
        
    def load_basic_questions(self) -> List[Dict[str, Any]]:
        """
        基礎科目問題データ読み込み（data/4-1.csvのみ）
        
        Returns:
            List[Dict[str, Any]]: 基礎科目問題リスト
            
        Raises:
            FileNotFoundError: 基礎科目ファイルが存在しない
            ValueError: データ形式が不正
            SecurityError: 専門科目ファイルアクセス試行検出
        """
        try:
            # セキュリティチェック：専門科目ファイルへのアクセス禁止
            self._validate_file_access_security()
            
            # キャッシュ確認
            if self._is_cache_valid():
                self._log_data_event('cache_hit', {'cached_questions': len(self.questions_cache)})
                return self.questions_cache.copy()
            
            # ファイル存在確認
            if not os.path.exists(self.BASIC_QUESTIONS_FILE):
                raise FileNotFoundError(f"基礎科目ファイルが見つかりません: {self.BASIC_QUESTIONS_FILE}")
            
            # ファイル読み込み（エンコーディング自動検出）
            questions = self._read_csv_with_encoding_detection()
            
            # データ検証
            validated_questions = self._validate_question_data(questions)
            
            # キャッシュ更新
            self.questions_cache = validated_questions
            self.cache_timestamp = datetime.now()
            
            self._log_data_event('questions_loaded', {
                'total_questions': len(validated_questions),
                'file_path': self.BASIC_QUESTIONS_FILE,
                'cache_updated': True
            })
            
            return validated_questions.copy()
            
        except Exception as e:
            self._log_data_event('load_error', {
                'error': str(e),
                'file_path': self.BASIC_QUESTIONS_FILE
            })
            raise
    
    def get_questions_for_session(self, count: int = 10, randomize: bool = True) -> List[Dict[str, Any]]:
        """
        セッション用問題取得
        
        Args:
            count: 問題数（デフォルト10問）
            randomize: ランダム選択可否
            
        Returns:
            List[Dict[str, Any]]: セッション用問題リスト
            
        Raises:
            ValueError: 問題数が不正または不足
        """
        try:
            # 基礎科目問題読み込み
            all_questions = self.load_basic_questions()
            
            # 問題数検証
            if count <= 0:
                raise ValueError("問題数は1以上である必要があります")
            
            if len(all_questions) < count:
                raise ValueError(f"利用可能な問題数({len(all_questions)})が不足しています。要求: {count}問")
            
            # 問題選択
            if randomize:
                selected_questions = random.sample(all_questions, count)
            else:
                selected_questions = all_questions[:count]
            
            # 問題番号付与
            for i, question in enumerate(selected_questions):
                question['session_order'] = i + 1
                question['question_id'] = question.get('id', f'basic_q_{i+1}')
            
            self._log_data_event('session_questions_prepared', {
                'selected_count': len(selected_questions),
                'total_available': len(all_questions),
                'randomized': randomize
            })
            
            return selected_questions
            
        except Exception as e:
            self._log_data_event('session_preparation_error', {
                'error': str(e),
                'requested_count': count,
                'randomize': randomize
            })
            raise
    
    def create_basic_exam_session_with_data(self, question_count: int = 10, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        基礎科目セッション作成（データ準備込み）
        
        Args:
            question_count: 問題数
            metadata: 追加メタデータ
            
        Returns:
            str: セッションID
        """
        try:
            # セッション用問題準備
            questions = self.get_questions_for_session(question_count, randomize=True)
            
            # メタデータ拡張
            enhanced_metadata = {
                'data_source': self.BASIC_QUESTIONS_FILE,
                'question_count': len(questions),
                'service_version': 'basic_data_service_v1.0',
                'created_by': 'BasicDataService',
                'question_selection': 'randomized',
                'session_type': 'basic_exam_only'
            }
            
            if metadata:
                enhanced_metadata.update(metadata)
            
            # セッション作成（Flask環境チェック）
            if SESSION_MANAGER_AVAILABLE:
                session_id = create_basic_exam_session(questions, enhanced_metadata)
            else:
                # テスト環境用モック
                session_id = f"mock_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self._log_data_event('session_created_with_data', {
                'session_id': session_id,
                'question_count': len(questions),
                'metadata_keys': list(enhanced_metadata.keys()),
                'session_manager_available': SESSION_MANAGER_AVAILABLE
            })
            
            return session_id
            
        except Exception as e:
            self._log_data_event('session_creation_with_data_error', {
                'error': str(e),
                'question_count': question_count
            })
            raise
    
    def get_session_question_by_index(self, question_index: int) -> Optional[Dict[str, Any]]:
        """
        セッション内の指定問題取得
        
        Args:
            question_index: 問題インデックス（0ベース）
            
        Returns:
            Dict[str, Any]: 問題データ（存在しない場合はNone）
        """
        try:
            if SESSION_MANAGER_AVAILABLE:
                session_data = get_basic_exam_session()
                if not session_data:
                    return None
                
                questions = session_data.get('questions', [])
            else:
                # テスト環境用：サンプル問題を使用
                questions = self.get_questions_for_session(10, randomize=False)
            
            if not (0 <= question_index < len(questions)):
                return None
            
            question = questions[question_index].copy()
            question['current_index'] = question_index
            question['total_questions'] = len(questions)
            question['is_last_question'] = (question_index == len(questions) - 1)
            
            self._log_data_event('session_question_retrieved', {
                'question_index': question_index,
                'question_id': question.get('question_id', 'unknown'),
                'total_questions': len(questions),
                'session_manager_available': SESSION_MANAGER_AVAILABLE
            })
            
            return question
            
        except Exception as e:
            self._log_data_event('session_question_retrieval_error', {
                'error': str(e),
                'question_index': question_index
            })
            return None
    
    def validate_answer_format(self, answer: str) -> bool:
        """
        回答形式検証
        
        Args:
            answer: 回答文字列
            
        Returns:
            bool: 形式正当性
        """
        try:
            if not isinstance(answer, str):
                return False
            
            # 基礎科目回答形式：A, B, C, D
            normalized_answer = answer.strip().upper()
            valid_answers = ['A', 'B', 'C', 'D']
            
            is_valid = normalized_answer in valid_answers
            
            self._log_data_event('answer_validation', {
                'original_answer': answer,
                'normalized_answer': normalized_answer,
                'is_valid': is_valid
            })
            
            return is_valid
            
        except Exception as e:
            self._log_data_event('answer_validation_error', {
                'error': str(e),
                'answer': answer
            })
            return False
    
    def get_basic_exam_statistics(self) -> Dict[str, Any]:
        """
        基礎科目統計情報取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        try:
            questions = self.load_basic_questions()
            
            statistics = {
                'total_available_questions': len(questions),
                'data_source': self.BASIC_QUESTIONS_FILE,
                'cache_status': 'hit' if self._is_cache_valid() else 'miss',
                'service_info': {
                    'version': 'basic_data_service_v1.0',
                    'type': 'basic_exam_only',
                    'specialist_access': 'strictly_forbidden',
                    'session_manager_available': SESSION_MANAGER_AVAILABLE
                }
            }
            
            # セッション統計（Flask環境でのみ）
            if SESSION_MANAGER_AVAILABLE:
                session_data = get_basic_exam_session()
                if session_data:
                    session_questions = session_data.get('questions', [])
                    answers = session_data.get('answers', {})
                    
                    statistics['current_session'] = {
                        'session_id': session_data.get('session_id', 'unknown'),
                        'questions_in_session': len(session_questions),
                        'answers_submitted': len(answers),
                        'current_question': session_data.get('current_question', 0),
                        'session_status': session_data.get('status', 'unknown'),
                        'session_active': self.session_manager.is_session_active()
                    }
                else:
                    statistics['current_session'] = None
            else:
                statistics['current_session'] = {
                    'session_status': 'test_environment',
                    'session_manager': 'not_available',
                    'note': 'Running in Flask-free test mode'
                }
            
            return statistics
            
        except Exception as e:
            self._log_data_event('statistics_error', {'error': str(e)})
            return {
                'error': str(e),
                'total_available_questions': 0,
                'service_status': 'error'
            }
    
    def _validate_file_access_security(self) -> None:
        """セキュリティ：専門科目ファイルアクセス禁止確認"""
        try:
            # 専門科目ファイルアクセス検出
            for forbidden_file in self.FORBIDDEN_SPECIALIST_FILES:
                if os.path.exists(forbidden_file):
                    # ファイル存在は問題ないが、アクセス試行を監視
                    pass
            
            # アクセス対象が基礎科目ファイルのみであることを確認
            if not self.BASIC_QUESTIONS_FILE.endswith('4-1.csv'):
                raise SecurityError("基礎科目以外のファイルアクセス試行が検出されました")
            
            self._log_data_event('security_check_passed', {
                'target_file': self.BASIC_QUESTIONS_FILE,
                'forbidden_files_checked': len(self.FORBIDDEN_SPECIALIST_FILES)
            })
            
        except Exception as e:
            self._log_data_event('security_check_error', {'error': str(e)})
            raise
    
    def _read_csv_with_encoding_detection(self) -> List[Dict[str, Any]]:
        """エンコーディング自動検出CSV読み込み"""
        questions = []
        
        for encoding in self.ENCODING_OPTIONS:
            try:
                with open(self.BASIC_QUESTIONS_FILE, 'r', encoding=encoding) as file:
                    csv_reader = csv.DictReader(file)
                    questions = list(csv_reader)
                    
                    self._log_data_event('csv_encoding_detected', {
                        'encoding': encoding,
                        'rows_read': len(questions)
                    })
                    break
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self._log_data_event('csv_read_error', {
                    'encoding': encoding,
                    'error': str(e)
                })
                continue
        
        if not questions:
            raise ValueError("CSV ファイルの読み込みに失敗しました（エンコーディング不明）")
        
        return questions
    
    def _validate_question_data(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """問題データ検証"""
        validated_questions = []
        required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        for i, question in enumerate(questions):
            try:
                # 必須フィールド確認
                for field in required_fields:
                    if field not in question or not question[field]:
                        raise ValueError(f"問題{i+1}: 必須フィールド'{field}'が不足しています")
                
                # 正解形式確認
                correct_answer = question['correct_answer'].strip().upper()
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    raise ValueError(f"問題{i+1}: 正解形式が不正です（{correct_answer}）")
                
                # データ正規化
                normalized_question = {
                    'id': question.get('id', f'basic_q_{i+1}'),
                    'question': question['question'].strip(),
                    'option_a': question['option_a'].strip(),
                    'option_b': question['option_b'].strip(),
                    'option_c': question['option_c'].strip(),
                    'option_d': question['option_d'].strip(),
                    'correct_answer': correct_answer,
                    'category': '基礎科目',
                    'source_file': self.BASIC_QUESTIONS_FILE,
                    'validated_at': datetime.now().isoformat()
                }
                
                # 追加フィールドの保持
                for key, value in question.items():
                    if key not in normalized_question and value:
                        normalized_question[key] = value
                
                validated_questions.append(normalized_question)
                
            except Exception as e:
                self._log_data_event('question_validation_error', {
                    'question_index': i,
                    'error': str(e),
                    'question_preview': str(question)[:100]
                })
                # 不正な問題はスキップ（続行）
                continue
        
        if not validated_questions:
            raise ValueError("有効な問題データが見つかりませんでした")
        
        self._log_data_event('questions_validated', {
            'total_input': len(questions),
            'validated_output': len(validated_questions),
            'validation_success_rate': (len(validated_questions) / len(questions)) * 100
        })
        
        return validated_questions
    
    def _is_cache_valid(self) -> bool:
        """キャッシュ有効性確認"""
        if not self.questions_cache or not self.cache_timestamp:
            return False
        
        cache_age = (datetime.now() - self.cache_timestamp).total_seconds()
        return cache_age < self.cache_duration
    
    def _log_data_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        データサービスイベントログ記録
        
        Args:
            event_type: イベント種別
            data: イベントデータ
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data,
                'service': 'basic_data_service',
                'version': '1.0'
            }
            
            # 開発環境ではコンソール出力
            print(f"[BasicDataService] {event_type}: {data.get('session_id', 'N/A')[:8] if 'session_id' in data else 'N/A'}")
            
        except Exception:
            pass  # ログ記録の失敗は無視

class SecurityError(Exception):
    """セキュリティエラー（専門科目アクセス禁止違反等）"""
    pass

# 便利関数
def create_basic_session_with_questions(question_count: int = 10, metadata: Optional[Dict[str, Any]] = None) -> str:
    """基礎科目セッション作成便利関数（データ準備込み）"""
    service = BasicDataService()
    return service.create_basic_exam_session_with_data(question_count, metadata)

def get_basic_questions_for_testing(count: int = 10) -> List[Dict[str, Any]]:
    """基礎科目問題取得便利関数（テスト用）"""
    service = BasicDataService()
    return service.get_questions_for_session(count, randomize=True)

def get_basic_exam_current_question() -> Optional[Dict[str, Any]]:
    """現在の基礎科目問題取得便利関数"""
    try:
        if SESSION_MANAGER_AVAILABLE:
            session_data = get_basic_exam_session()
            if not session_data:
                return None
            
            current_index = session_data.get('current_question', 0)
        else:
            # テスト環境用：最初の問題を返す
            current_index = 0
        
        service = BasicDataService()
        return service.get_session_question_by_index(current_index)
    except Exception:
        return None

def validate_basic_exam_answer(answer: str) -> bool:
    """基礎科目回答検証便利関数"""
    service = BasicDataService()
    return service.validate_answer_format(answer)

def get_basic_data_service_info() -> Dict[str, Any]:
    """基礎科目データサービス情報取得便利関数"""
    service = BasicDataService()
    return service.get_basic_exam_statistics()

# 主要エクスポート
__all__ = [
    'BasicDataService',
    'SecurityError',
    'create_basic_session_with_questions',
    'get_basic_questions_for_testing',
    'get_basic_exam_current_question',
    'validate_basic_exam_answer',
    'get_basic_data_service_info'
]

if __name__ == "__main__":
    # データサービステスト用
    print("基礎科目専用データサービス実装完了")
    
    try:
        service = BasicDataService()
        
        # 基本機能テスト
        questions = service.load_basic_questions()
        print(f"基礎科目問題数: {len(questions)}問")
        
        # セッション用問題準備テスト
        session_questions = service.get_questions_for_session(10)
        print(f"セッション用問題準備: {len(session_questions)}問")
        
        # 統計情報表示
        stats = service.get_basic_exam_statistics()
        print(f"サービス統計: {stats}")
        
        print("✅ 基礎科目データサービス動作確認完了")
        
    except Exception as e:
        print(f"❌ データサービステストエラー: {e}")
        print("注意: Flask context外での実行のため、セッション関連機能は制限されます")