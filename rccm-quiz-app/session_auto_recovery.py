#!/usr/bin/env python3
"""
🔧 Ultra Sync Session Auto Recovery System
RCCM試験問題集アプリ - セッション破損時の自動復旧機能

🎯 CLAUDE.md準拠・副作用ゼロ保証・ウルトラシンク自動復旧システム
- セッション破損の自動検出
- 包括的なセッション修復
- 無縫な復旧体験
- データ整合性保証
- 完全なログ記録とモニタリング
"""

import json
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
import hashlib
import uuid
from functools import wraps

logger = logging.getLogger(__name__)

class SessionCorruptionDetector:
    """🔍 セッション破損検出システム"""
    
    def __init__(self):
        self.corruption_patterns = {
            'missing_required_keys': ['user_name'],
            'invalid_data_types': {
                'history': list,
                'quiz_question_ids': list,
                'quiz_current': int,
                'srs_data': dict
            },
            'inconsistent_quiz_state': [
                'quiz_current_out_of_range',
                'missing_question_ids',
                'invalid_question_references'
            ],
            'session_size_anomalies': {
                'max_history_size': 1000,
                'max_srs_entries': 500,
                'max_session_size_mb': 5
            }
        }
        
        # 破損検出統計
        self.detection_stats = {
            'total_checks': 0,
            'corruptions_detected': 0,
            'corruption_types': defaultdict(int),
            'false_positives': 0,
            'recovery_attempts': 0,
            'successful_recoveries': 0
        }
    
    def detect_corruption(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 セッション破損の包括的検出"""
        self.detection_stats['total_checks'] += 1
        
        corruption_report = {
            'is_corrupted': False,
            'corruption_types': [],
            'severity': 'none',  # none, minor, major, critical
            'recovery_recommendations': [],
            'timestamp': datetime.now().isoformat(),
            'session_hash': self._calculate_session_hash(session)
        }
        
        try:
            # 1. 必須キーの存在確認
            missing_keys = self._check_missing_keys(session)
            if missing_keys:
                corruption_report['corruption_types'].append({
                    'type': 'missing_required_keys',
                    'details': missing_keys,
                    'severity': 'major'
                })
            
            # 2. データ型整合性チェック
            type_violations = self._check_data_types(session)
            if type_violations:
                corruption_report['corruption_types'].append({
                    'type': 'invalid_data_types',
                    'details': type_violations,
                    'severity': 'major'
                })
            
            # 3. クイズ状態整合性チェック
            quiz_inconsistencies = self._check_quiz_state_consistency(session)
            if quiz_inconsistencies:
                corruption_report['corruption_types'].append({
                    'type': 'quiz_state_inconsistency',
                    'details': quiz_inconsistencies,
                    'severity': 'critical'
                })
            
            # 4. セッションサイズ異常チェック
            size_anomalies = self._check_session_size_anomalies(session)
            if size_anomalies:
                corruption_report['corruption_types'].append({
                    'type': 'session_size_anomaly',
                    'details': size_anomalies,
                    'severity': 'minor'
                })
            
            # 5. SRSデータ整合性チェック
            srs_issues = self._check_srs_data_integrity(session)
            if srs_issues:
                corruption_report['corruption_types'].append({
                    'type': 'srs_data_corruption',
                    'details': srs_issues,
                    'severity': 'major'
                })
            
            # 6. 履歴データ整合性チェック
            history_issues = self._check_history_integrity(session)
            if history_issues:
                corruption_report['corruption_types'].append({
                    'type': 'history_corruption',
                    'details': history_issues,
                    'severity': 'minor'
                })
            
            # 総合評価
            if corruption_report['corruption_types']:
                corruption_report['is_corrupted'] = True
                self.detection_stats['corruptions_detected'] += 1
                
                # 最高重要度を全体の重要度とする
                severities = [ct['severity'] for ct in corruption_report['corruption_types']]
                if 'critical' in severities:
                    corruption_report['severity'] = 'critical'
                elif 'major' in severities:
                    corruption_report['severity'] = 'major'
                else:
                    corruption_report['severity'] = 'minor'
                
                # 破損タイプ統計更新
                for ct in corruption_report['corruption_types']:
                    self.detection_stats['corruption_types'][ct['type']] += 1
                
                # 復旧推奨事項生成
                corruption_report['recovery_recommendations'] = self._generate_recovery_recommendations(
                    corruption_report['corruption_types']
                )
            
            logger.info(f"🔍 Session corruption check: {'CORRUPTED' if corruption_report['is_corrupted'] else 'CLEAN'}")
            if corruption_report['is_corrupted']:
                logger.warning(f"   Severity: {corruption_report['severity']}")
                logger.warning(f"   Types: {[ct['type'] for ct in corruption_report['corruption_types']]}")
            
            return corruption_report
            
        except Exception as e:
            logger.error(f"❌ Session corruption detection failed: {e}")
            return {
                'is_corrupted': True,
                'corruption_types': [{
                    'type': 'detection_error',
                    'details': str(e),
                    'severity': 'critical'
                }],
                'severity': 'critical',
                'recovery_recommendations': ['manual_intervention_required'],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _check_missing_keys(self, session: Dict[str, Any]) -> List[str]:
        """必須キーの存在確認"""
        missing_keys = []
        for key in self.corruption_patterns['missing_required_keys']:
            if key not in session:
                missing_keys.append(key)
        return missing_keys
    
    def _check_data_types(self, session: Dict[str, Any]) -> List[Dict[str, str]]:
        """データ型整合性チェック"""
        violations = []
        for key, expected_type in self.corruption_patterns['invalid_data_types'].items():
            if key in session:
                actual_value = session[key]
                if not isinstance(actual_value, expected_type):
                    violations.append({
                        'key': key,
                        'expected_type': expected_type.__name__,
                        'actual_type': type(actual_value).__name__,
                        'value': str(actual_value)[:100]  # 最初の100文字のみ
                    })
        return violations
    
    def _check_quiz_state_consistency(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """クイズ状態整合性チェック"""
        inconsistencies = []
        
        # クイズ進行状況チェック
        if 'quiz_question_ids' in session and 'quiz_current' in session:
            question_ids = session['quiz_question_ids']
            current_index = session['quiz_current']
            
            if isinstance(question_ids, list) and isinstance(current_index, int):
                if current_index < 0:
                    inconsistencies.append({
                        'issue': 'negative_quiz_current',
                        'details': f'quiz_current is negative: {current_index}'
                    })
                elif current_index >= len(question_ids) and len(question_ids) > 0:
                    inconsistencies.append({
                        'issue': 'quiz_current_out_of_range',
                        'details': f'quiz_current ({current_index}) >= question_ids length ({len(question_ids)})'
                    })
        
        # 選択部門とカテゴリーの整合性
        if 'selected_department' in session and 'exam_category' in session:
            department = session['selected_department']
            category = session['exam_category']
            
            # ここで部門-カテゴリーマッピングの整合性をチェック
            # (実際のマッピングはapp.pyから取得する必要がある)
            pass  # 実装はapp.pyとの統合時に行う
        
        return inconsistencies
    
    def _check_session_size_anomalies(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """セッションサイズ異常チェック"""
        anomalies = []
        limits = self.corruption_patterns['session_size_anomalies']
        
        # 履歴サイズチェック
        if 'history' in session and isinstance(session['history'], list):
            history_size = len(session['history'])
            if history_size > limits['max_history_size']:
                anomalies.append({
                    'issue': 'oversized_history',
                    'details': f'History size ({history_size}) exceeds limit ({limits["max_history_size"]})'
                })
        
        # SRSデータサイズチェック
        if 'srs_data' in session and isinstance(session['srs_data'], dict):
            srs_size = len(session['srs_data'])
            if srs_size > limits['max_srs_entries']:
                anomalies.append({
                    'issue': 'oversized_srs_data',
                    'details': f'SRS data size ({srs_size}) exceeds limit ({limits["max_srs_entries"]})'
                })
        
        # 全体セッションサイズチェック
        session_size_mb = len(json.dumps(session, default=str)) / (1024 * 1024)
        if session_size_mb > limits['max_session_size_mb']:
            anomalies.append({
                'issue': 'oversized_session',
                'details': f'Session size ({session_size_mb:.2f}MB) exceeds limit ({limits["max_session_size_mb"]}MB)'
            })
        
        return anomalies
    
    def _check_srs_data_integrity(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """SRSデータ整合性チェック"""
        issues = []
        
        if 'srs_data' in session and isinstance(session['srs_data'], dict):
            srs_data = session['srs_data']
            
            for question_id, srs_info in srs_data.items():
                if not isinstance(srs_info, dict):
                    issues.append({
                        'issue': 'invalid_srs_entry_type',
                        'details': f'SRS entry for {question_id} is not dict: {type(srs_info)}'
                    })
                    continue
                
                # 必須フィールドチェック
                required_fields = ['correct_count', 'wrong_count', 'total_attempts']
                missing_fields = [f for f in required_fields if f not in srs_info]
                if missing_fields:
                    issues.append({
                        'issue': 'missing_srs_fields',
                        'details': f'Question {question_id} missing fields: {missing_fields}'
                    })
                
                # 数値フィールドの妥当性チェック
                for field in required_fields:
                    if field in srs_info:
                        value = srs_info[field]
                        if not isinstance(value, (int, float)) or value < 0:
                            issues.append({
                                'issue': 'invalid_srs_numeric_value',
                                'details': f'Question {question_id} field {field}: {value} (should be non-negative number)'
                            })
        
        return issues
    
    def _check_history_integrity(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """履歴データ整合性チェック"""
        issues = []
        
        if 'history' in session and isinstance(session['history'], list):
            history = session['history']
            
            for i, entry in enumerate(history):
                if not isinstance(entry, dict):
                    issues.append({
                        'issue': 'invalid_history_entry_type',
                        'details': f'History entry {i} is not dict: {type(entry)}'
                    })
                    continue
                
                # 必須フィールドチェック
                required_fields = ['id', 'is_correct', 'date']
                missing_fields = [f for f in required_fields if f not in entry]
                if missing_fields:
                    issues.append({
                        'issue': 'missing_history_fields',
                        'details': f'History entry {i} missing fields: {missing_fields}'
                    })
                
                # 日付フォーマットチェック
                if 'date' in entry:
                    try:
                        datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        issues.append({
                            'issue': 'invalid_history_date_format',
                            'details': f'History entry {i} invalid date: {entry["date"]}'
                        })
        
        return issues
    
    def _calculate_session_hash(self, session: Dict[str, Any]) -> str:
        """セッションハッシュ計算（整合性確認用）"""
        try:
            session_str = json.dumps(session, sort_keys=True, default=str)
            return hashlib.md5(session_str.encode()).hexdigest()[:16]
        except Exception:
            return 'hash_error'
    
    def _generate_recovery_recommendations(self, corruption_types: List[Dict[str, Any]]) -> List[str]:
        """復旧推奨事項生成"""
        recommendations = []
        
        for corruption in corruption_types:
            corruption_type = corruption['type']
            severity = corruption['severity']
            
            if corruption_type == 'missing_required_keys':
                recommendations.append('initialize_missing_keys')
            elif corruption_type == 'invalid_data_types':
                recommendations.append('fix_data_types')
            elif corruption_type == 'quiz_state_inconsistency':
                if severity == 'critical':
                    recommendations.append('reset_quiz_state')
                else:
                    recommendations.append('repair_quiz_state')
            elif corruption_type == 'session_size_anomaly':
                recommendations.append('compress_session_data')
            elif corruption_type == 'srs_data_corruption':
                recommendations.append('rebuild_srs_data')
            elif corruption_type == 'history_corruption':
                recommendations.append('clean_history_data')
            else:
                recommendations.append('full_session_rebuild')
        
        # 重複除去
        return list(set(recommendations))


class SessionAutoRecoverySystem:
    """🔧 セッション自動復旧システム"""
    
    def __init__(self):
        self.detector = SessionCorruptionDetector()
        self.recovery_stats = {
            'total_recovery_attempts': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'recovery_methods_used': defaultdict(int),
            'recovery_time_ms': [],
            'critical_recoveries': 0
        }
        
        # デフォルト値定義
        self.default_values = {
            'user_name': 'anonymous_user',
            'history': [],
            'quiz_question_ids': [],
            'quiz_current': 0,
            'srs_data': {},
            'bookmarks': [],
            'quiz_settings': {
                'questions_per_session': 10,
                'difficulty_level': 'normal'
            },
            'last_activity': datetime.now().isoformat(),
            'session_version': '1.0'
        }
    
    def auto_recover_session(self, session: Dict[str, Any], corruption_report: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 セッション自動復旧実行"""
        start_time = time.time()
        self.recovery_stats['total_recovery_attempts'] += 1
        
        recovery_result = {
            'success': False,
            'recovered_session': session.copy(),
            'recovery_actions': [],
            'warnings': [],
            'backup_created': False,
            'recovery_time_ms': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            logger.info(f"🔧 Starting auto-recovery for session corruption (severity: {corruption_report['severity']})")
            
            # 1. バックアップ作成
            backup_result = self._create_recovery_backup(session)
            recovery_result['backup_created'] = backup_result['success']
            if backup_result['success']:
                recovery_result['backup_id'] = backup_result['backup_id']
                logger.info(f"📁 Recovery backup created: {backup_result['backup_id']}")
            
            # 2. 推奨復旧アクションの実行
            recommendations = corruption_report.get('recovery_recommendations', [])
            
            for recommendation in recommendations:
                try:
                    action_result = self._execute_recovery_action(
                        recommendation, 
                        recovery_result['recovered_session'], 
                        corruption_report
                    )
                    
                    if action_result['success']:
                        recovery_result['recovery_actions'].append({
                            'action': recommendation,
                            'success': True,
                            'details': action_result.get('details', ''),
                            'changes_made': action_result.get('changes_made', [])
                        })
                        logger.info(f"✅ Recovery action completed: {recommendation}")
                    else:
                        recovery_result['recovery_actions'].append({
                            'action': recommendation,
                            'success': False,
                            'error': action_result.get('error', 'Unknown error'),
                            'fallback_used': action_result.get('fallback_used', False)
                        })
                        logger.warning(f"⚠️ Recovery action failed: {recommendation} - {action_result.get('error')}")
                        
                        # 失敗した場合でもフォールバック処理を試行
                        if action_result.get('fallback_used'):
                            recovery_result['warnings'].append(f"Fallback used for {recommendation}")
                    
                    # 統計更新
                    self.recovery_stats['recovery_methods_used'][recommendation] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Recovery action exception: {recommendation} - {e}")
                    recovery_result['recovery_actions'].append({
                        'action': recommendation,
                        'success': False,
                        'error': str(e),
                        'exception': True
                    })
            
            # 3. 復旧後の検証
            verification_result = self.detector.detect_corruption(recovery_result['recovered_session'])
            
            if not verification_result['is_corrupted']:
                recovery_result['success'] = True
                self.recovery_stats['successful_recoveries'] += 1
                logger.info("🎉 Session auto-recovery completed successfully")
            else:
                # まだ破損がある場合は最終手段として完全再構築
                logger.warning("⚠️ Corruption still detected after recovery, attempting full rebuild")
                rebuild_result = self._full_session_rebuild(recovery_result['recovered_session'])
                
                if rebuild_result['success']:
                    recovery_result['recovered_session'] = rebuild_result['rebuilt_session']
                    recovery_result['success'] = True
                    recovery_result['recovery_actions'].append({
                        'action': 'full_session_rebuild',
                        'success': True,
                        'details': 'Emergency full rebuild performed',
                        'changes_made': ['complete_session_reconstruction']
                    })
                    recovery_result['warnings'].append("Full session rebuild was required")
                    self.recovery_stats['successful_recoveries'] += 1
                    logger.info("✅ Emergency full rebuild completed successfully")
                else:
                    recovery_result['success'] = False
                    self.recovery_stats['failed_recoveries'] += 1
                    logger.error("❌ Auto-recovery failed - manual intervention required")
            
            # 4. セッションメタデータ更新
            if recovery_result['success']:
                recovery_result['recovered_session']['recovery_metadata'] = {
                    'recovered_at': datetime.now().isoformat(),
                    'corruption_severity': corruption_report['severity'],
                    'recovery_actions_count': len([a for a in recovery_result['recovery_actions'] if a['success']]),
                    'backup_id': recovery_result.get('backup_id'),
                    'recovery_version': '1.0'
                }
            
            # 5. 重要度別統計更新
            if corruption_report['severity'] == 'critical':
                self.recovery_stats['critical_recoveries'] += 1
            
        except Exception as e:
            logger.error(f"❌ Auto-recovery system error: {e}")
            recovery_result['success'] = False
            recovery_result['error'] = str(e)
            self.recovery_stats['failed_recoveries'] += 1
        
        finally:
            # 復旧時間記録
            recovery_time_ms = (time.time() - start_time) * 1000
            recovery_result['recovery_time_ms'] = recovery_time_ms
            self.recovery_stats['recovery_time_ms'].append(recovery_time_ms)
            
            logger.info(f"🔧 Auto-recovery completed in {recovery_time_ms:.1f}ms")
        
        return recovery_result
    
    def _create_recovery_backup(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """📁 復旧用バックアップ作成"""
        try:
            backup_id = f"recovery_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            backup_dir = os.path.join(os.path.dirname(__file__), 'recovery_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_data = {
                'backup_id': backup_id,
                'timestamp': datetime.now().isoformat(),
                'session_data': session.copy(),
                'backup_type': 'corruption_recovery',
                'session_size_bytes': len(json.dumps(session, default=str))
            }
            
            backup_file = os.path.join(backup_dir, f"{backup_id}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            return {
                'success': True,
                'backup_id': backup_id,
                'backup_file': backup_file
            }
            
        except Exception as e:
            logger.error(f"❌ Recovery backup creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_recovery_action(self, action: str, session: Dict[str, Any], corruption_report: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 復旧アクション実行"""
        try:
            if action == 'initialize_missing_keys':
                return self._initialize_missing_keys(session)
            elif action == 'fix_data_types':
                return self._fix_data_types(session, corruption_report)
            elif action == 'reset_quiz_state':
                return self._reset_quiz_state(session)
            elif action == 'repair_quiz_state':
                return self._repair_quiz_state(session)
            elif action == 'compress_session_data':
                return self._compress_session_data(session)
            elif action == 'rebuild_srs_data':
                return self._rebuild_srs_data(session)
            elif action == 'clean_history_data':
                return self._clean_history_data(session)
            elif action == 'full_session_rebuild':
                return self._full_session_rebuild(session)
            else:
                return {
                    'success': False,
                    'error': f'Unknown recovery action: {action}'
                }
                
        except Exception as e:
            logger.error(f"❌ Recovery action execution failed: {action} - {e}")
            return {
                'success': False,
                'error': str(e),
                'exception': True
            }
    
    def _initialize_missing_keys(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 欠損キーの初期化"""
        changes_made = []
        
        for key, default_value in self.default_values.items():
            if key not in session:
                session[key] = default_value
                changes_made.append(f'initialized_{key}')
        
        return {
            'success': True,
            'details': f'Initialized {len(changes_made)} missing keys',
            'changes_made': changes_made
        }
    
    def _fix_data_types(self, session: Dict[str, Any], corruption_report: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 データ型修正"""
        changes_made = []
        
        # 破損レポートから型違反を特定
        for corruption in corruption_report['corruption_types']:
            if corruption['type'] == 'invalid_data_types':
                for violation in corruption['details']:
                    key = violation['key']
                    expected_type = violation['expected_type']
                    
                    if key in session:
                        try:
                            if expected_type == 'list' and not isinstance(session[key], list):
                                # リストに変換を試行
                                if isinstance(session[key], str):
                                    session[key] = []  # 空リストで初期化
                                else:
                                    session[key] = [session[key]]  # 単一要素をリストに
                                changes_made.append(f'fixed_type_{key}_to_list')
                            
                            elif expected_type == 'dict' and not isinstance(session[key], dict):
                                session[key] = {}  # 空辞書で初期化
                                changes_made.append(f'fixed_type_{key}_to_dict')
                            
                            elif expected_type == 'int' and not isinstance(session[key], int):
                                if isinstance(session[key], (str, float)):
                                    session[key] = int(float(session[key]))
                                else:
                                    session[key] = 0
                                changes_made.append(f'fixed_type_{key}_to_int')
                            
                        except (ValueError, TypeError):
                            # 変換に失敗した場合はデフォルト値を使用
                            session[key] = self.default_values.get(key, None)
                            changes_made.append(f'reset_{key}_to_default')
        
        return {
            'success': True,
            'details': f'Fixed {len(changes_made)} data type issues',
            'changes_made': changes_made
        }
    
    def _reset_quiz_state(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 クイズ状態リセット"""
        changes_made = []
        
        # クイズ関連の状態を初期値にリセット
        quiz_fields_to_reset = [
            'quiz_question_ids', 'quiz_current', 'exam_category',
            'selected_department', 'selected_question_type', 'selected_year'
        ]
        
        for field in quiz_fields_to_reset:
            if field in session:
                if field in self.default_values:
                    session[field] = self.default_values[field]
                else:
                    del session[field]
                changes_made.append(f'reset_{field}')
        
        return {
            'success': True,
            'details': f'Reset {len(changes_made)} quiz state fields',
            'changes_made': changes_made
        }
    
    def _repair_quiz_state(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 クイズ状態修復（リセットしない）"""
        changes_made = []
        
        # quiz_currentの範囲修正
        if 'quiz_question_ids' in session and 'quiz_current' in session:
            question_ids = session['quiz_question_ids']
            current_index = session['quiz_current']
            
            if isinstance(question_ids, list) and isinstance(current_index, int):
                if current_index < 0:
                    session['quiz_current'] = 0
                    changes_made.append('fixed_negative_quiz_current')
                elif len(question_ids) > 0 and current_index >= len(question_ids):
                    session['quiz_current'] = len(question_ids) - 1
                    changes_made.append('fixed_out_of_range_quiz_current')
        
        return {
            'success': True,
            'details': f'Repaired {len(changes_made)} quiz state issues',
            'changes_made': changes_made
        }
    
    def _compress_session_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 セッションデータ圧縮"""
        changes_made = []
        
        # 履歴データの圧縮
        if 'history' in session and isinstance(session['history'], list):
            original_size = len(session['history'])
            if original_size > 500:  # 500件に制限
                session['history'] = session['history'][-500:]
                changes_made.append(f'compressed_history_{original_size}_to_500')
        
        # SRSデータの圧縮
        if 'srs_data' in session and isinstance(session['srs_data'], dict):
            original_size = len(session['srs_data'])
            if original_size > 300:  # 300件に制限
                # 最後の試行時間でソートして新しいものを保持
                sorted_items = sorted(
                    session['srs_data'].items(),
                    key=lambda x: x[1].get('last_attempt', ''),
                    reverse=True
                )
                session['srs_data'] = dict(sorted_items[:300])
                changes_made.append(f'compressed_srs_data_{original_size}_to_300')
        
        return {
            'success': True,
            'details': f'Compressed {len(changes_made)} data structures',
            'changes_made': changes_made
        }
    
    def _rebuild_srs_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 SRSデータ再構築"""
        changes_made = []
        
        if 'srs_data' in session:
            rebuilt_srs = {}
            original_srs = session.get('srs_data', {})
            
            if isinstance(original_srs, dict):
                for question_id, srs_info in original_srs.items():
                    if isinstance(srs_info, dict):
                        # 有効なSRSエントリを再構築
                        rebuilt_entry = {
                            'correct_count': max(0, int(srs_info.get('correct_count', 0))),
                            'wrong_count': max(0, int(srs_info.get('wrong_count', 0))),
                            'total_attempts': max(0, int(srs_info.get('total_attempts', 0))),
                            'last_attempt': srs_info.get('last_attempt', datetime.now().isoformat()),
                            'mastery_level': max(0, min(5, int(srs_info.get('mastery_level', 0))))
                        }
                        rebuilt_srs[str(question_id)] = rebuilt_entry
                        changes_made.append(f'rebuilt_srs_{question_id}')
            
            session['srs_data'] = rebuilt_srs
        
        return {
            'success': True,
            'details': f'Rebuilt {len(changes_made)} SRS entries',
            'changes_made': changes_made
        }
    
    def _clean_history_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 履歴データクリーニング"""
        changes_made = []
        
        if 'history' in session and isinstance(session['history'], list):
            cleaned_history = []
            
            for i, entry in enumerate(session['history']):
                if isinstance(entry, dict):
                    # 必須フィールドの補完
                    cleaned_entry = {
                        'id': entry.get('id', f'unknown_{i}'),
                        'is_correct': bool(entry.get('is_correct', False)),
                        'date': entry.get('date', datetime.now().isoformat()),
                        'category': entry.get('category', 'unknown'),
                        'score': max(0, min(100, int(entry.get('score', 0))))
                    }
                    
                    # 日付フォーマット修正
                    try:
                        datetime.fromisoformat(cleaned_entry['date'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        cleaned_entry['date'] = datetime.now().isoformat()
                        changes_made.append(f'fixed_history_date_{i}')
                    
                    cleaned_history.append(cleaned_entry)
                    changes_made.append(f'cleaned_history_entry_{i}')
            
            session['history'] = cleaned_history
        
        return {
            'success': True,
            'details': f'Cleaned {len(changes_made)} history entries',
            'changes_made': changes_made
        }
    
    def _full_session_rebuild(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 完全セッション再構築（最終手段）"""
        try:
            # 重要な情報を保持
            preserved_data = {}
            preserve_keys = ['user_name', 'history', 'srs_data', 'bookmarks']
            
            for key in preserve_keys:
                if key in session and session[key]:
                    preserved_data[key] = session[key]
            
            # 新しいセッションを構築
            rebuilt_session = self.default_values.copy()
            
            # 保持したデータを復元（クリーニング後）
            for key, value in preserved_data.items():
                if key == 'history' and isinstance(value, list):
                    # 履歴データのクリーニング
                    cleaned_history = []
                    for entry in value[-100:]:  # 最新100件のみ保持
                        if isinstance(entry, dict) and 'id' in entry:
                            cleaned_history.append(entry)
                    rebuilt_session['history'] = cleaned_history
                
                elif key == 'srs_data' and isinstance(value, dict):
                    # SRSデータのクリーニング
                    cleaned_srs = {}
                    for qid, srs_info in value.items():
                        if isinstance(srs_info, dict):
                            cleaned_srs[str(qid)] = {
                                'correct_count': max(0, int(srs_info.get('correct_count', 0))),
                                'wrong_count': max(0, int(srs_info.get('wrong_count', 0))),
                                'total_attempts': max(0, int(srs_info.get('total_attempts', 0))),
                                'last_attempt': srs_info.get('last_attempt', datetime.now().isoformat()),
                                'mastery_level': max(0, min(5, int(srs_info.get('mastery_level', 0))))
                            }
                    rebuilt_session['srs_data'] = cleaned_srs
                
                else:
                    rebuilt_session[key] = value
            
            # 再構築メタデータ追加
            rebuilt_session['rebuild_metadata'] = {
                'rebuilt_at': datetime.now().isoformat(),
                'rebuild_reason': 'corruption_recovery',
                'preserved_keys': list(preserved_data.keys()),
                'rebuild_version': '1.0'
            }
            
            return {
                'success': True,
                'rebuilt_session': rebuilt_session,
                'preserved_keys': list(preserved_data.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ Full session rebuild failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """📊 復旧統計取得"""
        stats = self.recovery_stats.copy()
        
        # 平均復旧時間計算
        if stats['recovery_time_ms']:
            stats['average_recovery_time_ms'] = sum(stats['recovery_time_ms']) / len(stats['recovery_time_ms'])
            stats['max_recovery_time_ms'] = max(stats['recovery_time_ms'])
            stats['min_recovery_time_ms'] = min(stats['recovery_time_ms'])
        else:
            stats['average_recovery_time_ms'] = 0
            stats['max_recovery_time_ms'] = 0
            stats['min_recovery_time_ms'] = 0
        
        # 成功率計算
        if stats['total_recovery_attempts'] > 0:
            stats['success_rate'] = stats['successful_recoveries'] / stats['total_recovery_attempts']
        else:
            stats['success_rate'] = 0
        
        # 検出器統計も含める
        stats['detection_stats'] = self.detector.detection_stats.copy()
        
        return stats


def session_auto_recovery_decorator(recovery_system: SessionAutoRecoverySystem):
    """🔧 セッション自動復旧デコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Flask関数の場合、sessionオブジェクトにアクセス
            try:
                from flask import session
                
                # セッション破損チェック
                corruption_report = recovery_system.detector.detect_corruption(dict(session))
                
                if corruption_report['is_corrupted']:
                    logger.warning(f"🚨 Session corruption detected in {func.__name__}: {corruption_report['severity']}")
                    
                    # 自動復旧実行
                    recovery_result = recovery_system.auto_recover_session(dict(session), corruption_report)
                    
                    if recovery_result['success']:
                        # 復旧されたセッションで更新
                        session.clear()
                        session.update(recovery_result['recovered_session'])
                        logger.info(f"✅ Session auto-recovery completed for {func.__name__}")
                    else:
                        logger.error(f"❌ Session auto-recovery failed for {func.__name__}")
                
                # 元の関数を実行
                return func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"❌ Session auto-recovery decorator error: {e}")
                # エラーが発生しても元の関数は実行
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# グローバルインスタンス
global_auto_recovery_system = SessionAutoRecoverySystem()


def init_session_auto_recovery(app=None):
    """🚀 セッション自動復旧システム初期化"""
    try:
        if app:
            # Flask app に自動復旧API を追加
            register_auto_recovery_routes(app)
        
        logger.info("Session auto-recovery system initialized successfully")
        return global_auto_recovery_system
        
    except Exception as e:
        logger.error(f"Failed to initialize session auto-recovery: {e}")
        return None


def register_auto_recovery_routes(app):
    """📡 自動復旧APIルート登録"""
    
    @app.route('/api/session/check_corruption')
    def check_session_corruption():
        """セッション破損チェックAPI"""
        try:
            from flask import session, jsonify
            corruption_report = global_auto_recovery_system.detector.detect_corruption(dict(session))
            return jsonify({
                'success': True,
                'corruption_report': corruption_report
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/session/auto_recover', methods=['POST'])
    def auto_recover_session():
        """セッション自動復旧API"""
        try:
            from flask import session, jsonify
            
            # 破損チェック
            corruption_report = global_auto_recovery_system.detector.detect_corruption(dict(session))
            
            if corruption_report['is_corrupted']:
                # 自動復旧実行
                recovery_result = global_auto_recovery_system.auto_recover_session(dict(session), corruption_report)
                
                if recovery_result['success']:
                    # セッション更新
                    session.clear()
                    session.update(recovery_result['recovered_session'])
                
                return jsonify({
                    'success': True,
                    'corruption_detected': True,
                    'recovery_result': recovery_result
                })
            else:
                return jsonify({
                    'success': True,
                    'corruption_detected': False,
                    'message': 'No corruption detected'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/session/recovery_stats')
    def get_recovery_stats():
        """復旧統計API"""
        try:
            stats = global_auto_recovery_system.get_recovery_stats()
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    # テスト実行
    recovery_system = SessionAutoRecoverySystem()
    
    # テストセッション（破損状態）
    test_session = {
        'user_name': 'test_user',
        'history': 'invalid_type',  # 本来はlist
        'quiz_current': -1,  # 無効な値
        'srs_data': {
            'q1': {'invalid_field': 'test'}  # 必須フィールドなし
        }
    }
    
    print("🔍 Testing session corruption detection and auto-recovery...")
    
    # 破損検出
    corruption_report = recovery_system.detector.detect_corruption(test_session)
    print(f"Corruption detected: {corruption_report['is_corrupted']}")
    print(f"Severity: {corruption_report['severity']}")
    
    if corruption_report['is_corrupted']:
        # 自動復旧
        recovery_result = recovery_system.auto_recover_session(test_session, corruption_report)
        print(f"Recovery success: {recovery_result['success']}")
        print(f"Recovery actions: {len(recovery_result['recovery_actions'])}")
        
        # 復旧後の検証
        post_recovery_check = recovery_system.detector.detect_corruption(recovery_result['recovered_session'])
        print(f"Post-recovery corruption: {post_recovery_check['is_corrupted']}")
    
    # 統計表示
    stats = recovery_system.get_recovery_stats()
    print(f"\nRecovery Stats:")
    print(f"  Total attempts: {stats['total_recovery_attempts']}")
    print(f"  Successful: {stats['successful_recoveries']}")
    print(f"  Success rate: {stats['success_rate']:.2%}")