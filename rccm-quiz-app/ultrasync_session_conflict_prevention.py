#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC タスク4: セッション競合解決機構
副作用ゼロでセッション競合を根本的に解決する独立モジュール
"""

import threading
import time
import logging
from datetime import datetime

# セッションロック（グローバル）
session_lock = threading.Lock()

class UltraSyncSessionConflictPrevention:
    """🔥 ULTRA SYNC: セッション競合を根本的に防ぐ管理クラス"""
    
    def __init__(self, session):
        self.session = session
        self.conflict_count = 0
        self.repair_count = 0
        self.last_check = time.time()
    
    def safe_batch_update(self, updates):
        """セッションの安全な一括更新 - 競合防止"""
        with session_lock:
            try:
                # 更新前のバックアップ
                backup = {}
                for key in updates.keys():
                    if key in self.session:
                        backup[key] = self.session[key]
                
                # 一括更新実行
                for key, value in updates.items():
                    self.session[key] = value
                
                # 必須: session.modified設定
                self.session.modified = True
                
                # 更新検証
                for key, value in updates.items():
                    if self.session.get(key) != value:
                        # 復元処理
                        for restore_key, restore_value in backup.items():
                            self.session[restore_key] = restore_value
                        self.session.modified = True
                        raise ValueError(f"セッション更新検証失敗: {key}")
                
                logging.info(f"🔥 ULTRA SYNC 一括更新成功: {len(updates)}キー")
                return True
                
            except Exception as e:
                logging.error(f"🔥 ULTRA SYNC 一括更新エラー: {e}")
                return False
    
    def detect_session_conflicts(self):
        """セッション競合の検出"""
        conflicts = []
        
        # 必須キーの存在チェック
        required_keys = ['exam_current', 'exam_question_ids', 'selected_question_type']
        for key in required_keys:
            if key not in self.session:
                conflicts.append(f"必須キー不足: {key}")
        
        # データ整合性チェック
        current = self.session.get('exam_current', 0)
        question_ids = self.session.get('exam_question_ids', [])
        
        if question_ids and current >= len(question_ids):
            conflicts.append(f"インデックス範囲外: current={current}, max={len(question_ids)-1}")
        
        # データ型チェック
        if not isinstance(current, int):
            conflicts.append(f"exam_current型エラー: {type(current)}")
        
        if not isinstance(question_ids, list):
            conflicts.append(f"exam_question_ids型エラー: {type(question_ids)}")
        
        if conflicts:
            self.conflict_count += 1
            logging.warning(f"🔥 ULTRA SYNC セッション競合検出: {conflicts}")
        
        return conflicts
    
    def repair_session_conflicts(self):
        """セッション競合の自動修復"""
        with session_lock:
            repairs = []
            
            # 必須キーの補完
            if 'exam_current' not in self.session:
                self.session['exam_current'] = 0
                repairs.append("exam_current補完")
            
            if 'exam_question_ids' not in self.session:
                self.session['exam_question_ids'] = []
                repairs.append("exam_question_ids補完")
            
            if 'selected_question_type' not in self.session:
                self.session['selected_question_type'] = 'basic'
                repairs.append("selected_question_type補完")
            
            # データ型修復
            current = self.session.get('exam_current', 0)
            if not isinstance(current, int):
                try:
                    self.session['exam_current'] = int(current)
                    repairs.append(f"exam_current型修復: {type(current)} → int")
                except (ValueError, TypeError):
                    self.session['exam_current'] = 0
                    repairs.append("exam_current型修復失敗→0設定")
            
            # インデックス修復
            question_ids = self.session.get('exam_question_ids', [])
            if question_ids and current >= len(question_ids):
                self.session['exam_current'] = len(question_ids) - 1
                repairs.append(f"exam_currentインデックス修復: {current} → {len(question_ids) - 1}")
            
            # 修復完了処理
            if repairs:
                self.session.modified = True
                self.repair_count += 1
                logging.info(f"🔥 ULTRA SYNC セッション修復完了: {repairs}")
            
            return repairs
    
    def comprehensive_session_check(self):
        """包括的なセッション整合性チェック"""
        start_time = time.time()
        
        # 競合検出
        conflicts = self.detect_session_conflicts()
        
        # 修復実行
        repairs = []
        if conflicts:
            repairs = self.repair_session_conflicts()
        
        # 結果レポート
        check_time = time.time() - start_time
        result = {
            'conflicts_detected': len(conflicts),
            'repairs_made': len(repairs),
            'check_time': check_time,
            'session_healthy': len(conflicts) == 0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.last_check = time.time()
        
        if conflicts or repairs:
            logging.info(f"🔥 ULTRA SYNC セッションチェック完了: {result}")
        
        return result
    
    def get_session_stats(self):
        """セッション統計情報の取得"""
        return {
            'conflict_count': self.conflict_count,
            'repair_count': self.repair_count,
            'last_check': self.last_check,
            'session_keys': len(self.session.keys()) if hasattr(self.session, 'keys') else 0
        }

def create_ultrasync_session_manager(session):
    """🔥 ULTRA SYNC: セッション管理クラスのファクトリー"""
    return UltraSyncSessionConflictPrevention(session)

def safe_session_operation(session, operation_func):
    """セッション操作の安全な実行"""
    with session_lock:
        try:
            result = operation_func()
            session.modified = True
            return result
        except Exception as e:
            logging.error(f"🔥 ULTRA SYNC セッション操作エラー: {e}")
            raise

def ultrasync_session_middleware(session, request_path):
    """🔥 ULTRA SYNC: セッション競合防止ミドルウェア"""
    manager = create_ultrasync_session_manager(session)
    
    # 高リスクルートでの強制チェック
    high_risk_routes = ['/exam', '/exam_question', '/start_exam']
    if any(route in request_path for route in high_risk_routes):
        result = manager.comprehensive_session_check()
        if not result['session_healthy']:
            logging.warning(f"🔥 ULTRA SYNC 高リスクルート検出: {request_path}, 修復実行")
    
    return manager

# 使用例とテスト関数
def test_ultrasync_session_conflict_prevention():
    """テスト用の模擬セッション競合解決"""
    
    # 模擬セッションの作成
    class MockSession:
        def __init__(self):
            self.data = {}
            self.modified = False
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
        
        def keys(self):
            return self.data.keys()
    
    # テスト実行
    mock_session = MockSession()
    manager = create_ultrasync_session_manager(mock_session)
    
    # 競合状態の作成
    mock_session.data = {
        'exam_current': 15,  # 範囲外
        'exam_question_ids': [1, 2, 3],  # 3問のみ
        'selected_question_type': 'basic'
    }
    
    # 競合検出テスト
    conflicts = manager.detect_session_conflicts()
    print(f"検出された競合: {conflicts}")
    
    # 修復テスト
    repairs = manager.repair_session_conflicts()
    print(f"実行された修復: {repairs}")
    
    # 最終状態確認
    final_state = {
        'exam_current': mock_session.get('exam_current'),
        'exam_question_ids': mock_session.get('exam_question_ids'),
        'selected_question_type': mock_session.get('selected_question_type')
    }
    print(f"修復後の状態: {final_state}")
    
    return len(conflicts) == 0

if __name__ == '__main__':
    print("🔥 ULTRA SYNC セッション競合解決機構テスト開始")
    success = test_ultrasync_session_conflict_prevention()
    print(f"テスト結果: {'成功' if success else '失敗'}")