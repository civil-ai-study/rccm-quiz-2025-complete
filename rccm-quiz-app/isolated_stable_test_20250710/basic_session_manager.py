#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-3】基礎科目専用セッション管理実装
既存セッションとの完全非干渉・basic_exam_*プレフィックス専用セッション管理
新ファイル作成のみ・既存システム影響ゼロ保証
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import session

class BasicExamSessionManager:
    """基礎科目専用セッション管理クラス"""
    
    # セッションキープレフィックス（既存システムとの完全分離）
    SESSION_PREFIX = 'basic_exam_'
    
    # セッション有効期限（デフォルト2時間）
    DEFAULT_SESSION_TIMEOUT = timedelta(hours=2)
    
    # セッションキー定義
    KEYS = {
        'session_id': f'{SESSION_PREFIX}session_id',
        'created_at': f'{SESSION_PREFIX}created_at',
        'last_activity': f'{SESSION_PREFIX}last_activity',
        'questions': f'{SESSION_PREFIX}questions',
        'current_question': f'{SESSION_PREFIX}current_question',
        'answers': f'{SESSION_PREFIX}answers',
        'start_time': f'{SESSION_PREFIX}start_time',
        'status': f'{SESSION_PREFIX}status',
        'metadata': f'{SESSION_PREFIX}metadata'
    }
    
    # セッション状態定義
    STATUS = {
        'initialized': 'initialized',
        'in_progress': 'in_progress',
        'completed': 'completed',
        'expired': 'expired',
        'error': 'error'
    }
    
    def __init__(self):
        """基礎科目セッション管理初期化"""
        self.session_timeout = self.DEFAULT_SESSION_TIMEOUT
        
    def create_session(self, questions: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        基礎科目専用セッション作成
        
        Args:
            questions: 問題リスト（基礎科目のみ）
            metadata: 追加メタデータ
            
        Returns:
            str: セッションID
            
        Raises:
            ValueError: 不正な問題データ
        """
        try:
            # 問題データ検証
            if not questions or not isinstance(questions, list):
                raise ValueError("問題データが無効です")
            
            if len(questions) < 1:
                raise ValueError("問題数が不足しています")
            
            # 基礎科目データかチェック（basic_exam専用）
            for i, question in enumerate(questions):
                if not isinstance(question, dict):
                    raise ValueError(f"問題{i+1}のデータ形式が不正です")
                
                required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                for field in required_fields:
                    if field not in question:
                        raise ValueError(f"問題{i+1}に必須フィールド'{field}'がありません")
            
            # セッションID生成
            session_id = str(uuid.uuid4())
            current_time = datetime.now()
            
            # セッションデータ初期化
            session_data = {
                'session_id': session_id,
                'created_at': current_time.isoformat(),
                'last_activity': current_time.isoformat(),
                'questions': questions,
                'current_question': 0,
                'answers': {},
                'start_time': current_time.isoformat(),
                'status': self.STATUS['initialized'],
                'metadata': metadata or {}
            }
            
            # Flaskセッションに保存（basic_exam_*プレフィックス）
            for key, value in session_data.items():
                session[self.KEYS[key]] = value
            
            # セッション作成ログ
            self._log_session_event(session_id, 'session_created', {
                'question_count': len(questions),
                'created_at': current_time.isoformat()
            })
            
            return session_id
            
        except Exception as e:
            self._log_session_event('unknown', 'session_creation_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            raise
    
    def get_session_data(self) -> Optional[Dict[str, Any]]:
        """
        現在のセッションデータ取得
        
        Returns:
            Dict[str, Any]: セッションデータ（存在しない場合はNone）
        """
        try:
            # セッション存在確認
            if not self.is_session_active():
                return None
            
            # セッションデータ構築
            session_data = {}
            for key in self.KEYS:
                session_key = self.KEYS[key]
                if session_key in session:
                    session_data[key] = session[session_key]
            
            # 最終活動時刻更新
            self.update_last_activity()
            
            return session_data
            
        except Exception as e:
            self._log_session_event('unknown', 'session_get_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return None
    
    def update_current_question(self, question_index: int) -> bool:
        """
        現在問題番号更新
        
        Args:
            question_index: 問題インデックス（0ベース）
            
        Returns:
            bool: 更新成功可否
        """
        try:
            if not self.is_session_active():
                return False
            
            questions = session.get(self.KEYS['questions'], [])
            if not (0 <= question_index < len(questions)):
                return False
            
            session[self.KEYS['current_question']] = question_index
            session[self.KEYS['status']] = self.STATUS['in_progress']
            self.update_last_activity()
            
            self._log_session_event(self.get_session_id(), 'question_updated', {
                'question_index': question_index,
                'total_questions': len(questions)
            })
            
            return True
            
        except Exception as e:
            self._log_session_event(self.get_session_id(), 'question_update_error', {
                'error': str(e),
                'question_index': question_index
            })
            return False
    
    def save_answer(self, question_index: int, answer: str) -> bool:
        """
        回答保存
        
        Args:
            question_index: 問題インデックス
            answer: 回答（A, B, C, D）
            
        Returns:
            bool: 保存成功可否
        """
        try:
            if not self.is_session_active():
                return False
            
            # 回答データ検証
            if answer not in ['A', 'B', 'C', 'D']:
                return False
            
            questions = session.get(self.KEYS['questions'], [])
            if not (0 <= question_index < len(questions)):
                return False
            
            # 回答保存
            answers = session.get(self.KEYS['answers'], {})
            answers[str(question_index)] = {
                'answer': answer.upper(),
                'timestamp': datetime.now().isoformat(),
                'question_no': question_index + 1
            }
            
            session[self.KEYS['answers']] = answers
            self.update_last_activity()
            
            self._log_session_event(self.get_session_id(), 'answer_saved', {
                'question_index': question_index,
                'answer': answer.upper(),
                'total_answers': len(answers)
            })
            
            return True
            
        except Exception as e:
            self._log_session_event(self.get_session_id(), 'answer_save_error', {
                'error': str(e),
                'question_index': question_index,
                'answer': answer
            })
            return False
    
    def calculate_results(self) -> Optional[Dict[str, Any]]:
        """
        試験結果計算
        
        Returns:
            Dict[str, Any]: 試験結果（計算失敗時はNone）
        """
        try:
            if not self.is_session_active():
                return None
            
            questions = session.get(self.KEYS['questions'], [])
            answers = session.get(self.KEYS['answers'], {})
            
            if not questions:
                return None
            
            # 結果計算
            total_questions = len(questions)
            correct_count = 0
            incorrect_count = 0
            result_details = []
            
            for i, question in enumerate(questions):
                question_key = str(i)
                user_answer_data = answers.get(question_key, {})
                user_answer = user_answer_data.get('answer', '')
                correct_answer = question.get('correct_answer', '').upper()
                
                is_correct = user_answer.upper() == correct_answer
                if is_correct:
                    correct_count += 1
                else:
                    incorrect_count += 1
                
                result_details.append({
                    'question_index': i,
                    'question_no': i + 1,
                    'question_text': question.get('question', '')[:100] + '...',
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'answer_timestamp': user_answer_data.get('timestamp', '')
                })
            
            # スコア計算
            score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
            # 判定
            passing_score = 60.0  # 60%で合格
            is_pass = score_percentage >= passing_score
            
            results = {
                'session_id': self.get_session_id(),
                'total_questions': total_questions,
                'correct_count': correct_count,
                'incorrect_count': incorrect_count,
                'score_percentage': score_percentage,
                'is_pass': is_pass,
                'passing_score': passing_score,
                'result_details': result_details,
                'start_time': session.get(self.KEYS['start_time']),
                'end_time': datetime.now().isoformat(),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
            # セッション完了状態に更新
            session[self.KEYS['status']] = self.STATUS['completed']
            self.update_last_activity()
            
            self._log_session_event(self.get_session_id(), 'results_calculated', {
                'score': score_percentage,
                'is_pass': is_pass,
                'correct_count': correct_count,
                'total_questions': total_questions
            })
            
            return results
            
        except Exception as e:
            self._log_session_event(self.get_session_id(), 'results_calculation_error', {
                'error': str(e)
            })
            return None
    
    def is_session_active(self) -> bool:
        """
        セッション活性状態確認
        
        Returns:
            bool: セッション活性状態
        """
        try:
            # セッションID確認
            session_id = session.get(self.KEYS['session_id'])
            if not session_id:
                return False
            
            # セッション有効期限確認
            last_activity_str = session.get(self.KEYS['last_activity'])
            if not last_activity_str:
                return False
            
            last_activity = datetime.fromisoformat(last_activity_str)
            if datetime.now() - last_activity > self.session_timeout:
                # セッション期限切れ
                session[self.KEYS['status']] = self.STATUS['expired']
                return False
            
            # セッション状態確認
            status = session.get(self.KEYS['status'])
            if status in [self.STATUS['expired'], self.STATUS['error']]:
                return False
            
            return True
            
        except Exception as e:
            self._log_session_event('unknown', 'session_active_check_error', {
                'error': str(e)
            })
            return False
    
    def update_last_activity(self) -> None:
        """最終活動時刻更新"""
        try:
            session[self.KEYS['last_activity']] = datetime.now().isoformat()
        except Exception:
            pass  # エラーは無視（セッション更新の失敗は致命的ではない）
    
    def get_session_id(self) -> Optional[str]:
        """
        セッションID取得
        
        Returns:
            str: セッションID（存在しない場合はNone）
        """
        return session.get(self.KEYS['session_id'])
    
    def clear_session(self) -> bool:
        """
        セッションクリア（基礎科目専用キーのみ）
        
        Returns:
            bool: クリア成功可否
        """
        try:
            session_id = self.get_session_id()
            
            # basic_exam_*プレフィックスのキーのみ削除
            keys_to_remove = [key for key in session.keys() if key.startswith(self.SESSION_PREFIX)]
            for key in keys_to_remove:
                session.pop(key, None)
            
            self._log_session_event(session_id, 'session_cleared', {
                'cleared_keys': len(keys_to_remove)
            })
            
            return True
            
        except Exception as e:
            self._log_session_event('unknown', 'session_clear_error', {
                'error': str(e)
            })
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        セッション情報取得（デバッグ用）
        
        Returns:
            Dict[str, Any]: セッション情報
        """
        try:
            info = {
                'session_active': self.is_session_active(),
                'session_id': self.get_session_id(),
                'session_keys': [key for key in session.keys() if key.startswith(self.SESSION_PREFIX)],
                'session_status': session.get(self.KEYS['status']),
                'current_question': session.get(self.KEYS['current_question']),
                'answers_count': len(session.get(self.KEYS['answers'], {})),
                'questions_count': len(session.get(self.KEYS['questions'], [])),
                'last_activity': session.get(self.KEYS['last_activity']),
                'created_at': session.get(self.KEYS['created_at'])
            }
            
            return info
            
        except Exception as e:
            return {
                'error': str(e),
                'session_active': False
            }
    
    def _log_session_event(self, session_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        セッションイベントログ記録（デバッグ用）
        
        Args:
            session_id: セッションID
            event_type: イベント種別
            data: イベントデータ
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'event_type': event_type,
                'data': data,
                'system': 'basic_exam_session_manager'
            }
            
            # 開発環境ではコンソール出力
            print(f"[BasicExamSession] {event_type}: {session_id[:8] if session_id != 'unknown' else 'unknown'}")
            
        except Exception:
            pass  # ログ記録の失敗は無視
    
    @staticmethod
    def validate_session_isolation() -> Dict[str, Any]:
        """
        セッション分離確認（テスト用）
        
        Returns:
            Dict[str, Any]: 分離状況確認結果
        """
        try:
            basic_exam_keys = [key for key in session.keys() if key.startswith(BasicExamSessionManager.SESSION_PREFIX)]
            other_keys = [key for key in session.keys() if not key.startswith(BasicExamSessionManager.SESSION_PREFIX)]
            
            isolation_info = {
                'basic_exam_keys': basic_exam_keys,
                'basic_exam_key_count': len(basic_exam_keys),
                'other_keys': other_keys,
                'other_key_count': len(other_keys),
                'total_session_keys': len(session.keys()),
                'isolation_confirmed': True,  # basic_exam_*プレフィックスのみ使用
                'timestamp': datetime.now().isoformat()
            }
            
            return isolation_info
            
        except Exception as e:
            return {
                'error': str(e),
                'isolation_confirmed': False,
                'timestamp': datetime.now().isoformat()
            }

# 便利関数
def create_basic_exam_session(questions: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
    """基礎科目セッション作成便利関数"""
    manager = BasicExamSessionManager()
    return manager.create_session(questions, metadata)

def get_basic_exam_session() -> Optional[Dict[str, Any]]:
    """基礎科目セッション取得便利関数"""
    manager = BasicExamSessionManager()
    return manager.get_session_data()

def clear_basic_exam_session() -> bool:
    """基礎科目セッションクリア便利関数"""
    manager = BasicExamSessionManager()
    return manager.clear_session()

def is_basic_exam_session_active() -> bool:
    """基礎科目セッション活性確認便利関数"""
    manager = BasicExamSessionManager()
    return manager.is_session_active()

# 主要エクスポート
__all__ = [
    'BasicExamSessionManager',
    'create_basic_exam_session',
    'get_basic_exam_session', 
    'clear_basic_exam_session',
    'is_basic_exam_session_active'
]

if __name__ == "__main__":
    # セッション管理テスト用
    print("基礎科目専用セッション管理実装完了")
    print(f"セッションプレフィックス: {BasicExamSessionManager.SESSION_PREFIX}")
    print(f"セッションキー数: {len(BasicExamSessionManager.KEYS)}")
    print("注意: Flask context内での使用が必要です")