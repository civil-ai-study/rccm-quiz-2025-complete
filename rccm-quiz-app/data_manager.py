"""
RCCM学習アプリ - データ永続化管理
セッションデータの永続化とバックアップ
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """
    学習データの永続化管理
    セッション + ファイル保存のハイブリッド方式
    """
    
    def __init__(self, data_dir: str = 'user_data'):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """データディレクトリの作成"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"データディレクトリ作成: {self.data_dir}")
    
    def get_user_id(self, session_id: str, user_name: str = None) -> str:
        """
        セッションIDまたはユーザー名からユーザーIDを生成
        企業環境対応: ユーザー名優先でID生成
        """
        if user_name:
            # ユーザー名ベースのID生成（企業環境対応）
            clean_name = user_name.replace(' ', '_').replace('　', '_')
            return f"user_{hashlib.md5(clean_name.encode('utf-8')).hexdigest()[:8]}"
        else:
            # 従来のセッションIDベース（後方互換性）
            return hashlib.md5(session_id.encode()).hexdigest()[:12]
    
    def save_user_data(self, session_id: str, data: Dict[str, Any], user_name: str = None) -> bool:
        """
        ユーザーデータの保存（企業環境対応）
        """
        try:
            user_id = self.get_user_id(session_id, user_name)
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            # 既存データがあれば読み込み
            existing_data = {}
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"既存データ読み込みエラー: {e}")
            
            # データ更新
            existing_data.update(data)
            existing_data['last_updated'] = datetime.now().isoformat()
            existing_data['user_id'] = user_id
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"ユーザーデータ保存完了: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザーデータ保存エラー: {e}")
            return False
    
    def load_user_data(self, session_id: str, user_name: str = None) -> Dict[str, Any]:
        """
        ユーザーデータの読み込み（企業環境対応）
        """
        try:
            user_id = self.get_user_id(session_id, user_name)
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            if not os.path.exists(file_path):
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"ユーザーデータ読み込み完了: {user_id}")
            return data
            
        except Exception as e:
            logger.error(f"ユーザーデータ読み込みエラー: {e}")
            return {}
    
    def backup_user_data(self, session_id: str) -> bool:
        """
        ユーザーデータのバックアップ
        """
        try:
            user_id = self.get_user_id(session_id)
            source_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            if not os.path.exists(source_path):
                return True  # データがない場合は成功とみなす
            
            # バックアップディレクトリ
            backup_dir = os.path.join(self.data_dir, 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # バックアップファイル名（タイムスタンプ付き）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"{user_id}_{timestamp}.json")
            
            # バックアップ実行
            import shutil
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"ユーザーデータバックアップ完了: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザーデータバックアップエラー: {e}")
            return False
    
    def get_data_export(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        データエクスポート用
        """
        try:
            data = self.load_user_data(session_id)
            if not data:
                return None
            
            # エクスポート用データ構造
            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': self.get_user_id(session_id),
                'study_history': data.get('history', []),
                'srs_data': data.get('srs_data', {}),
                'category_stats': data.get('category_stats', {}),
                'bookmarks': data.get('bookmarks', []),
                'total_questions': len(data.get('history', [])),
                'study_days': len(set(h.get('date', '')[:10] for h in data.get('history', []) if h.get('date')))
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"データエクスポートエラー: {e}")
            return None

# Flask拡張: セッション + ファイル保存の統合
class SessionDataManager:
    """
    セッションとファイル保存を統合したデータ管理
    """
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def save_session_data(self, session, session_id: str, user_name: str = None):
        """
        セッションデータをファイルに保存（企業環境対応）
        """
        # 保存対象データの選択
        save_data = {
            'user_name': user_name or session.get('user_name', ''),
            'history': session.get('history', []),
            'srs_data': session.get('srs_data', {}),
            'category_stats': session.get('category_stats', {}),
            'bookmarks': session.get('bookmarks', []),
            'last_updated': datetime.now().isoformat()
        }
        
        # LocalStorageデータは含めない（クライアント側で管理）
        return self.data_manager.save_user_data(session_id, save_data, user_name)
    
    def load_session_data(self, session, session_id: str, user_name: str = None):
        """
        ファイルからセッションデータを復元（企業環境対応）
        """
        data = self.data_manager.load_user_data(session_id, user_name)
        
        if data:
            session['history'] = data.get('history', [])
            session['srs_data'] = data.get('srs_data', {})
            session['category_stats'] = data.get('category_stats', {})
            session['bookmarks'] = data.get('bookmarks', [])
            session.modified = True
            
            logger.info(f"セッションデータ復元完了 - ユーザー: {user_name or 'セッション'}")
            return True
        
        return False
    
    def auto_save_trigger(self, session, session_id: str, user_name: str = None):
        """
        自動保存のトリガー（企業環境対応）
        """
        # 一定の条件で自動保存
        history_count = len(session.get('history', []))
        
        # 10問ごと、または1時間ごとに自動保存
        if history_count > 0 and (history_count % 10 == 0):
            return self.save_session_data(session, session_id, user_name)
        
        return True

# 企業環境用ユーザー管理機能
class EnterpriseUserManager:
    """
    企業環境での複数ユーザー管理
    マルチユーザー対応、進捗管理、統計情報
    """
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """
        全ユーザーの一覧と基本統計を取得
        """
        try:
            users = {}
            data_dir = self.data_manager.data_dir
            
            if not os.path.exists(data_dir):
                return users
            
            # 全てのユーザーデータファイルを確認
            for filename in os.listdir(data_dir):
                if filename.endswith('.json') and not filename.startswith('backup'):
                    file_path = os.path.join(data_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        user_id = filename[:-5]  # .json を除去
                        user_name = data.get('user_name', f'ユーザー_{user_id[:8]}')
                        
                        # 基本統計計算
                        history = data.get('history', [])
                        total_questions = len(history)
                        correct_answers = sum(1 for h in history if h.get('is_correct', False))
                        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
                        
                        # 学習日数計算
                        study_dates = set()
                        for h in history:
                            if h.get('timestamp'):
                                date_str = h['timestamp'][:10]
                                study_dates.add(date_str)
                        
                        users[user_id] = {
                            'user_name': user_name,
                            'total_questions': total_questions,
                            'correct_answers': correct_answers,
                            'accuracy': round(accuracy, 1),
                            'study_days': len(study_dates),
                            'last_study': data.get('last_updated', '未記録'),
                            'srs_questions': len(data.get('srs_data', {})),
                            'bookmarks': len(data.get('bookmarks', []))
                        }
                        
                    except Exception as e:
                        logger.error(f"ユーザーファイル読み込みエラー {filename}: {e}")
                        continue
            
            return users
            
        except Exception as e:
            logger.error(f"全ユーザー取得エラー: {e}")
            return {}
    
    def get_user_progress_report(self, user_name: str) -> Dict[str, Any]:
        """
        特定ユーザーの詳細進捗レポート
        """
        try:
            # ユーザー名からuser_idを生成
            user_id = self.data_manager.get_user_id("", user_name)
            data = self.data_manager.load_user_data("", user_name)
            
            if not data:
                return {'error': 'ユーザーデータが見つかりません'}
            
            history = data.get('history', [])
            srs_data = data.get('srs_data', {})
            category_stats = data.get('category_stats', {})
            
            # 詳細統計計算
            total_questions = len(history)
            correct_answers = sum(1 for h in history if h.get('is_correct', False))
            accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # 部門別統計
            department_stats = {}
            for h in history:
                dept = h.get('department', '不明')
                if dept not in department_stats:
                    department_stats[dept] = {'total': 0, 'correct': 0}
                department_stats[dept]['total'] += 1
                if h.get('is_correct', False):
                    department_stats[dept]['correct'] += 1
            
            # 部門別正答率計算
            for dept in department_stats:
                total = department_stats[dept]['total']
                correct = department_stats[dept]['correct']
                department_stats[dept]['accuracy'] = (correct / total * 100) if total > 0 else 0
            
            # 学習パターン分析
            study_pattern = self._analyze_study_pattern(history)
            
            report = {
                'user_name': user_name,
                'user_id': user_id,
                'overview': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': round(accuracy, 1),
                    'study_days': len(set(h.get('timestamp', '')[:10] for h in history if h.get('timestamp'))),
                    'srs_questions': len(srs_data),
                    'bookmarks': len(data.get('bookmarks', []))
                },
                'department_performance': department_stats,
                'study_pattern': study_pattern,
                'recent_activity': history[-10:] if history else [],
                'srs_status': self._get_srs_status(srs_data),
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"ユーザー進捗レポートエラー: {e}")
            return {'error': str(e)}
    
    def _analyze_study_pattern(self, history: list) -> Dict[str, Any]:
        """学習パターンの分析"""
        if not history:
            return {}
        
        # 時間帯分析
        hour_distribution = {}
        for h in history:
            timestamp = h.get('timestamp', '')
            if len(timestamp) >= 13:
                hour = int(timestamp[11:13])
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        # 最も活発な時間帯
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None
        
        # 連続学習日数
        dates = sorted(set(h.get('timestamp', '')[:10] for h in history if h.get('timestamp')))
        streak = self._calculate_streak(dates)
        
        return {
            'peak_study_hour': peak_hour,
            'current_streak': streak,
            'total_study_sessions': len(dates),
            'avg_questions_per_session': len(history) / len(dates) if dates else 0
        }
    
    def _calculate_streak(self, dates: list) -> int:
        """連続学習日数の計算"""
        if not dates:
            return 0
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        streak = 0
        
        for i, date_str in enumerate(reversed(dates)):
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                expected_date = today - timedelta(days=i)
                if date == expected_date:
                    streak += 1
                else:
                    break
            except:
                break
        
        return streak
    
    def _get_srs_status(self, srs_data: dict) -> Dict[str, int]:
        """SRS問題の状態統計"""
        status = {'new': 0, 'learning': 0, 'review': 0, 'mastered': 0}
        
        for question_id, data in srs_data.items():
            level = data.get('level', 0)
            if level == 0:
                status['new'] += 1
            elif level <= 2:
                status['learning'] += 1
            elif level <= 4:
                status['review'] += 1
            else:
                status['mastered'] += 1
        
        return status 