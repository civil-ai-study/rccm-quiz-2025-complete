"""
RCCM学習アプリ - プロフェッショナルAPI統合機能
外部システム連携、認定追跡、企業/教育機関向け進捗レポート
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from functools import wraps
from collections import defaultdict
import secrets
import uuid

logger = logging.getLogger(__name__)

class APIManager:
    """API管理とプロフェッショナル統合機能"""
    
    def __init__(self, user_data_dir: str = 'user_data', api_data_dir: str = 'api_data'):
        self.user_data_dir = user_data_dir
        self.api_data_dir = api_data_dir
        self.api_keys_file = os.path.join(api_data_dir, 'api_keys.json')
        self.certifications_file = os.path.join(api_data_dir, 'certifications.json')
        self.organization_data_file = os.path.join(api_data_dir, 'organizations.json')
        self.integration_settings_file = os.path.join(api_data_dir, 'integration_settings.json')
        
        # ディレクトリ作成
        os.makedirs(api_data_dir, exist_ok=True)
        
        # APIエンドポイント定義
        self.api_endpoints = {
            # 認証エンドポイント
            'auth': {
                '/api/auth/generate_key': 'POST',
                '/api/auth/validate_key': 'POST',
                '/api/auth/revoke_key': 'DELETE'
            },
            # ユーザー管理
            'users': {
                '/api/users': 'GET',
                '/api/users/<user_id>': 'GET',
                '/api/users/<user_id>/progress': 'GET',
                '/api/users/<user_id>/certifications': 'GET'
            },
            # 進捗レポート
            'reports': {
                '/api/reports/progress': 'GET',
                '/api/reports/organization/<org_id>': 'GET',
                '/api/reports/certification/<cert_id>': 'GET',
                '/api/reports/export/<format>': 'GET'
            },
            # 認定管理
            'certifications': {
                '/api/certifications': 'GET',
                '/api/certifications': 'POST',
                '/api/certifications/<cert_id>': 'GET',
                '/api/certifications/<cert_id>/progress': 'GET'
            },
            # 組織管理
            'organizations': {
                '/api/organizations': 'GET',
                '/api/organizations': 'POST',
                '/api/organizations/<org_id>': 'GET',
                '/api/organizations/<org_id>/users': 'GET',
                '/api/organizations/<org_id>/reports': 'GET'
            },
            # 学習データ連携
            'learning': {
                '/api/learning/sessions': 'GET',
                '/api/learning/sessions': 'POST',
                '/api/learning/analytics': 'GET',
                '/api/learning/recommendations': 'GET'
            }
        }
        
        logger.info("プロフェッショナルAPI統合機能初期化完了")
    
    # === API認証管理 ===
    
    def generate_api_key(self, organization: str, permissions: List[str], 
                        expires_in_days: int = 365) -> Dict[str, Any]:
        """APIキー生成"""
        try:
            api_keys = self._load_api_keys()
            
            # APIキー生成
            api_key = f"rccm_{secrets.token_urlsafe(32)}"
            api_secret = secrets.token_urlsafe(64)
            
            # キー情報
            key_info = {
                'api_key': api_key,
                'api_secret': api_secret,
                'organization': organization,
                'permissions': permissions,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
                'is_active': True,
                'usage_stats': {
                    'total_requests': 0,
                    'last_used': None,
                    'rate_limit': 1000,  # 1時間あたりのリクエスト上限
                    'current_usage': 0
                }
            }
            
            api_keys[api_key] = key_info
            self._save_api_keys(api_keys)
            
            logger.info(f"APIキー生成: {organization}")
            return {
                'success': True,
                'api_key': api_key,
                'api_secret': api_secret,
                'permissions': permissions,
                'expires_at': key_info['expires_at']
            }
            
        except Exception as e:
            logger.error(f"APIキー生成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_api_key(self, api_key: str, required_permission: str = None) -> Dict[str, Any]:
        """APIキー検証"""
        try:
            api_keys = self._load_api_keys()
            
            if api_key not in api_keys:
                return {'valid': False, 'error': 'Invalid API key'}
            
            key_info = api_keys[api_key]
            
            # アクティブ状態チェック
            if not key_info['is_active']:
                return {'valid': False, 'error': 'API key is deactivated'}
            
            # 有効期限チェック
            try:
                expires_at = datetime.fromisoformat(key_info['expires_at'])
                if datetime.now() > expires_at:
                    return {'valid': False, 'error': 'API key has expired'}
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"有効期限の日付パースエラー: {e}")
                return {'valid': False, 'error': 'Invalid expiration date format'}
            
            # 権限チェック
            if required_permission and required_permission not in key_info['permissions']:
                return {'valid': False, 'error': 'Insufficient permissions'}
            
            # 使用統計更新
            key_info['usage_stats']['total_requests'] += 1
            key_info['usage_stats']['last_used'] = datetime.now().isoformat()
            
            # レート制限チェック（簡略化）
            if key_info['usage_stats']['current_usage'] >= key_info['usage_stats']['rate_limit']:
                return {'valid': False, 'error': 'Rate limit exceeded'}
            
            api_keys[api_key] = key_info
            self._save_api_keys(api_keys)
            
            return {
                'valid': True,
                'organization': key_info['organization'],
                'permissions': key_info['permissions']
            }
            
        except Exception as e:
            logger.error(f"APIキー検証エラー: {e}")
            return {'valid': False, 'error': 'Validation failed'}
    
    def revoke_api_key(self, api_key: str) -> Dict[str, Any]:
        """APIキー無効化"""
        try:
            api_keys = self._load_api_keys()
            
            if api_key not in api_keys:
                return {'success': False, 'error': 'API key not found'}
            
            api_keys[api_key]['is_active'] = False
            api_keys[api_key]['revoked_at'] = datetime.now().isoformat()
            
            self._save_api_keys(api_keys)
            
            logger.info(f"APIキー無効化: {api_key}")
            return {'success': True, 'message': 'API key revoked successfully'}
            
        except Exception as e:
            logger.error(f"APIキー無効化エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    # === 認定追跡機能 ===
    
    def create_certification_program(self, name: str, description: str, 
                                   requirements: Dict[str, Any], 
                                   organization: str = None) -> Dict[str, Any]:
        """認定プログラム作成"""
        try:
            certifications = self._load_certifications()
            
            cert_id = str(uuid.uuid4())
            
            certification = {
                'id': cert_id,
                'name': name,
                'description': description,
                'organization': organization,
                'requirements': requirements,
                'created_at': datetime.now().isoformat(),
                'is_active': True,
                'statistics': {
                    'total_participants': 0,
                    'completed': 0,
                    'in_progress': 0,
                    'completion_rate': 0.0
                }
            }
            
            certifications[cert_id] = certification
            self._save_certifications(certifications)
            
            logger.info(f"認定プログラム作成: {name}")
            return {
                'success': True,
                'certification_id': cert_id,
                'certification': certification
            }
            
        except Exception as e:
            logger.error(f"認定プログラム作成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def enroll_user_in_certification(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """ユーザーの認定プログラム登録"""
        try:
            certifications = self._load_certifications()
            
            if cert_id not in certifications:
                return {'success': False, 'error': 'Certification program not found'}
            
            user_data = self._load_user_data(user_id)
            
            # ユーザーの認定情報を初期化
            if 'certifications' not in user_data:
                user_data['certifications'] = {}
            
            enrollment = {
                'enrolled_at': datetime.now().isoformat(),
                'status': 'in_progress',
                'progress': 0.0,
                'requirements_met': {},
                'completion_date': None,
                'certificate_issued': False
            }
            
            user_data['certifications'][cert_id] = enrollment
            self._save_user_data(user_id, user_data)
            
            # 認定プログラム統計更新
            certifications[cert_id]['statistics']['total_participants'] += 1
            certifications[cert_id]['statistics']['in_progress'] += 1
            self._save_certifications(certifications)
            
            logger.info(f"認定プログラム登録: ユーザー{user_id} → 認定{cert_id}")
            return {
                'success': True,
                'enrollment': enrollment
            }
            
        except Exception as e:
            logger.error(f"認定プログラム登録エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_certification_progress(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """認定進捗チェック"""
        try:
            user_data = self._load_user_data(user_id)
            certifications = self._load_certifications()
            
            if cert_id not in certifications:
                return {'error': 'Certification program not found'}
            
            if 'certifications' not in user_data or cert_id not in user_data['certifications']:
                return {'error': 'User not enrolled in this certification'}
            
            certification = certifications[cert_id]
            enrollment = user_data['certifications'][cert_id]
            requirements = certification['requirements']
            
            # 進捗計算
            progress_data = self._calculate_certification_progress(user_data, requirements)
            
            # 完了チェック
            if progress_data['completion_percentage'] >= 100 and enrollment['status'] != 'completed':
                enrollment['status'] = 'completed'
                enrollment['completion_date'] = datetime.now().isoformat()
                enrollment['certificate_issued'] = True
                
                # 統計更新
                certifications[cert_id]['statistics']['completed'] += 1
                certifications[cert_id]['statistics']['in_progress'] -= 1
                certifications[cert_id]['statistics']['completion_rate'] = (
                    certifications[cert_id]['statistics']['completed'] / 
                    certifications[cert_id]['statistics']['total_participants']
                )
                
                self._save_user_data(user_id, user_data)
                self._save_certifications(certifications)
            
            return {
                'certification_id': cert_id,
                'certification_name': certification['name'],
                'enrollment_status': enrollment['status'],
                'progress': progress_data,
                'requirements_status': self._check_requirements_status(user_data, requirements),
                'completion_date': enrollment.get('completion_date'),
                'certificate_issued': enrollment.get('certificate_issued', False)
            }
            
        except Exception as e:
            logger.error(f"認定進捗チェックエラー: {e}")
            return {'error': str(e)}
    
    # === 進捗レポート機能 ===
    
    def generate_progress_report(self, user_id: str = None, organization: str = None, 
                               time_period: str = 'month', format: str = 'json') -> Dict[str, Any]:
        """進捗レポート生成"""
        try:
            if user_id:
                return self._generate_individual_report(user_id, time_period, format)
            elif organization:
                return self._generate_organization_report(organization, time_period, format)
            else:
                return self._generate_global_report(time_period, format)
            
        except Exception as e:
            logger.error(f"進捗レポート生成エラー: {e}")
            return {'error': str(e)}
    
    def _generate_individual_report(self, user_id: str, time_period: str, format: str) -> Dict[str, Any]:
        """個人進捗レポート"""
        user_data = self._load_user_data(user_id)
        history = user_data.get('history', [])
        
        # 期間フィルタ
        cutoff_date = self._get_time_cutoff(time_period)
        if cutoff_date:
            history = [h for h in history if 
                      datetime.fromisoformat(h.get('date', '')) >= cutoff_date]
        
        # レポートデータ生成
        report = {
            'report_type': 'individual',
            'user_id': user_id,
            'time_period': time_period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_questions_attempted': len(history),
                'correct_answers': sum(1 for h in history if h.get('is_correct', False)),
                'accuracy_rate': 0,
                'study_sessions': len(set(h.get('date', '')[:10] for h in history)),
                'time_spent_minutes': sum(h.get('elapsed', 0) for h in history) // 60
            },
            'performance_analytics': self._calculate_performance_analytics(history),
            'learning_progress': self._calculate_learning_progress(user_data),
            'weak_areas': self._identify_weak_areas_for_report(history),
            'strengths': self._identify_strengths_for_report(history),
            'recommendations': self._generate_learning_recommendations(user_data),
            'certifications': self._get_user_certifications_status(user_id)
        }
        
        # 正答率計算
        if len(history) > 0:
            report['summary']['accuracy_rate'] = report['summary']['correct_answers'] / len(history)
        
        if format == 'pdf':
            return self._convert_to_pdf(report)
        elif format == 'excel':
            return self._convert_to_excel(report)
        else:
            return report
    
    def _generate_organization_report(self, organization: str, time_period: str, format: str) -> Dict[str, Any]:
        """組織進捗レポート"""
        organizations = self._load_organizations()
        
        if organization not in organizations:
            return {'error': 'Organization not found'}
        
        org_data = organizations[organization]
        users = org_data.get('users', [])
        
        # 全ユーザーのデータ集計
        all_users_data = []
        total_questions = 0
        total_correct = 0
        total_time = 0
        
        for user_id in users:
            user_data = self._load_user_data(user_id)
            history = user_data.get('history', [])
            
            # 期間フィルタ
            cutoff_date = self._get_time_cutoff(time_period)
            if cutoff_date:
                history = [h for h in history if 
                          datetime.fromisoformat(h.get('date', '')) >= cutoff_date]
            
            user_stats = {
                'user_id': user_id,
                'questions_attempted': len(history),
                'correct_answers': sum(1 for h in history if h.get('is_correct', False)),
                'accuracy_rate': 0,
                'time_spent': sum(h.get('elapsed', 0) for h in history)
            }
            
            if len(history) > 0:
                user_stats['accuracy_rate'] = user_stats['correct_answers'] / len(history)
            
            all_users_data.append(user_stats)
            total_questions += user_stats['questions_attempted']
            total_correct += user_stats['correct_answers']
            total_time += user_stats['time_spent']
        
        # 組織レポート
        report = {
            'report_type': 'organization',
            'organization': organization,
            'time_period': time_period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_users': len(users),
                'active_users': len([u for u in all_users_data if u['questions_attempted'] > 0]),
                'total_questions_attempted': total_questions,
                'total_correct_answers': total_correct,
                'organization_accuracy_rate': total_correct / total_questions if total_questions > 0 else 0,
                'total_study_time_hours': total_time // 3600
            },
            'user_performance': all_users_data,
            'department_breakdown': self._calculate_department_breakdown(users),
            'learning_trends': self._calculate_learning_trends(users, time_period),
            'certification_progress': self._get_organization_certification_progress(users),
            'recommendations': self._generate_organization_recommendations(all_users_data)
        }
        
        if format == 'pdf':
            return self._convert_to_pdf(report)
        elif format == 'excel':
            return self._convert_to_excel(report)
        else:
            return report
    
    def export_learning_analytics(self, format: str = 'json', 
                                include_personal_data: bool = False) -> Dict[str, Any]:
        """学習分析データエクスポート"""
        try:
            # 全ユーザーデータ読み込み
            all_users = self._load_all_user_data()
            
            analytics_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_users': len(all_users),
                'format': format,
                'includes_personal_data': include_personal_data,
                'aggregate_statistics': {},
                'learning_patterns': {},
                'performance_metrics': {},
                'content_analytics': {}
            }
            
            # 集計統計
            all_histories = []
            for user_data in all_users.values():
                all_histories.extend(user_data.get('history', []))
            
            analytics_data['aggregate_statistics'] = {
                'total_questions_attempted': len(all_histories),
                'unique_questions': len(set(h.get('question_id') for h in all_histories)),
                'overall_accuracy': sum(1 for h in all_histories if h.get('is_correct', False)) / len(all_histories) if all_histories else 0,
                'average_response_time': sum(h.get('elapsed', 0) for h in all_histories) / len(all_histories) if all_histories else 0
            }
            
            # 学習パターン分析
            analytics_data['learning_patterns'] = self._analyze_global_learning_patterns(all_users)
            
            # パフォーマンス指標
            analytics_data['performance_metrics'] = self._calculate_global_performance_metrics(all_histories)
            
            # コンテンツ分析
            analytics_data['content_analytics'] = self._analyze_content_effectiveness(all_histories)
            
            # 個人データ含める場合
            if include_personal_data:
                analytics_data['user_data'] = {}
                for user_id, user_data in all_users.items():
                    analytics_data['user_data'][user_id] = {
                        'total_questions': len(user_data.get('history', [])),
                        'accuracy': self._calculate_user_accuracy(user_data),
                        'learning_level': self._assess_learning_level(user_data),
                        'primary_departments': self._get_user_primary_departments(user_data)
                    }
            
            # フォーマット変換
            if format == 'csv':
                return self._convert_analytics_to_csv(analytics_data)
            elif format == 'excel':
                return self._convert_analytics_to_excel(analytics_data)
            else:
                return analytics_data
            
        except Exception as e:
            logger.error(f"学習分析エクスポートエラー: {e}")
            return {'error': str(e)}
    
    # === 組織管理機能 ===
    
    def create_organization(self, name: str, description: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """組織作成"""
        try:
            organizations = self._load_organizations()
            
            org_id = str(uuid.uuid4())
            
            organization = {
                'id': org_id,
                'name': name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'settings': settings or {},
                'users': [],
                'administrators': [],
                'statistics': {
                    'total_users': 0,
                    'active_users': 0,
                    'total_questions_attempted': 0,
                    'average_accuracy': 0.0
                }
            }
            
            organizations[org_id] = organization
            self._save_organizations(organizations)
            
            logger.info(f"組織作成: {name}")
            return {
                'success': True,
                'organization_id': org_id,
                'organization': organization
            }
            
        except Exception as e:
            logger.error(f"組織作成エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_user_to_organization(self, user_id: str, org_id: str, role: str = 'member') -> Dict[str, Any]:
        """ユーザーの組織追加"""
        try:
            organizations = self._load_organizations()
            
            if org_id not in organizations:
                return {'success': False, 'error': 'Organization not found'}
            
            organization = organizations[org_id]
            
            if user_id not in organization['users']:
                organization['users'].append(user_id)
                organization['statistics']['total_users'] += 1
                
                if role == 'admin':
                    organization['administrators'].append(user_id)
                
                organizations[org_id] = organization
                self._save_organizations(organizations)
                
                # ユーザーデータに組織情報追加
                user_data = self._load_user_data(user_id)
                if 'organizations' not in user_data:
                    user_data['organizations'] = []
                
                user_data['organizations'].append({
                    'organization_id': org_id,
                    'role': role,
                    'joined_at': datetime.now().isoformat()
                })
                
                self._save_user_data(user_id, user_data)
                
                logger.info(f"ユーザー組織追加: {user_id} → {org_id}")
                return {'success': True, 'message': 'User added to organization'}
            else:
                return {'success': False, 'error': 'User already in organization'}
            
        except Exception as e:
            logger.error(f"ユーザー組織追加エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    # === 外部システム連携 ===
    
    def setup_lms_integration(self, lms_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """LMS(学習管理システム)連携設定"""
        try:
            integration_settings = self._load_integration_settings()
            
            integration_id = str(uuid.uuid4())
            
            integration = {
                'id': integration_id,
                'type': 'lms',
                'lms_type': lms_type,  # 'moodle', 'canvas', 'blackboard', etc.
                'config': config,
                'created_at': datetime.now().isoformat(),
                'is_active': True,
                'sync_settings': {
                    'sync_frequency': 'daily',
                    'sync_data_types': ['progress', 'scores', 'completion'],
                    'last_sync': None
                }
            }
            
            integration_settings[integration_id] = integration
            self._save_integration_settings(integration_settings)
            
            logger.info(f"LMS連携設定: {lms_type}")
            return {
                'success': True,
                'integration_id': integration_id,
                'integration': integration
            }
            
        except Exception as e:
            logger.error(f"LMS連携設定エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_with_external_system(self, integration_id: str) -> Dict[str, Any]:
        """外部システムとの同期"""
        try:
            integration_settings = self._load_integration_settings()
            
            if integration_id not in integration_settings:
                return {'success': False, 'error': 'Integration not found'}
            
            integration = integration_settings[integration_id]
            
            # 同期処理（実装は統合対象システムに依存）
            sync_result = self._perform_external_sync(integration)
            
            # 同期結果を記録
            integration['sync_settings']['last_sync'] = datetime.now().isoformat()
            integration_settings[integration_id] = integration
            self._save_integration_settings(integration_settings)
            
            logger.info(f"外部システム同期完了: {integration_id}")
            return {
                'success': True,
                'sync_result': sync_result,
                'last_sync': integration['sync_settings']['last_sync']
            }
            
        except Exception as e:
            logger.error(f"外部システム同期エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    # === プライベートメソッド ===
    
    def _load_api_keys(self) -> Dict[str, Any]:
        """APIキーデータ読み込み"""
        return self._load_json_file(self.api_keys_file, {})
    
    def _save_api_keys(self, api_keys: Dict[str, Any]):
        """APIキーデータ保存"""
        self._save_json_file(self.api_keys_file, api_keys)
    
    def _load_certifications(self) -> Dict[str, Any]:
        """認定データ読み込み"""
        return self._load_json_file(self.certifications_file, {})
    
    def _save_certifications(self, certifications: Dict[str, Any]):
        """認定データ保存"""
        self._save_json_file(self.certifications_file, certifications)
    
    def _load_organizations(self) -> Dict[str, Any]:
        """組織データ読み込み"""
        return self._load_json_file(self.organization_data_file, {})
    
    def _save_organizations(self, organizations: Dict[str, Any]):
        """組織データ保存"""
        self._save_json_file(self.organization_data_file, organizations)
    
    def _load_integration_settings(self) -> Dict[str, Any]:
        """統合設定読み込み"""
        return self._load_json_file(self.integration_settings_file, {})
    
    def _save_integration_settings(self, settings: Dict[str, Any]):
        """統合設定保存"""
        self._save_json_file(self.integration_settings_file, settings)
    
    def _load_json_file(self, filepath: str, default: Any) -> Any:
        """JSONファイル読み込み"""
        try:
            if not os.path.exists(filepath):
                return default
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError) as e:
            logger.warning(f"ファイルアクセスエラー {filepath}: {e}")
            return default
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"データ読み込みエラー {filepath}: {e}")
            return default
        except Exception as e:
            logger.error(f"予期しないエラー {filepath}: {e}")
            return default
    
    def _save_json_file(self, filepath: str, data: Any):
        """JSONファイル保存"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"JSONファイル保存エラー {filepath}: {e}")
    
    def _load_user_data(self, user_id: str) -> Dict[str, Any]:
        """ユーザーデータ読み込み"""
        filepath = os.path.join(self.user_data_dir, f"{user_id}.json")
        return self._load_json_file(filepath, {})
    
    def _save_user_data(self, user_id: str, user_data: Dict[str, Any]):
        """ユーザーデータ保存"""
        filepath = os.path.join(self.user_data_dir, f"{user_id}.json")
        self._save_json_file(filepath, user_data)
    
    def _load_all_user_data(self) -> Dict[str, Dict[str, Any]]:
        """全ユーザーデータ読み込み"""
        all_users = {}
        
        if not os.path.exists(self.user_data_dir):
            return all_users
        
        for filename in os.listdir(self.user_data_dir):
            if filename.endswith('.json'):
                user_id = filename[:-5]
                all_users[user_id] = self._load_user_data(user_id)
        
        return all_users
    
    def _calculate_certification_progress(self, user_data: Dict, requirements: Dict) -> Dict[str, Any]:
        """認定進捗計算"""
        history = user_data.get('history', [])
        
        progress = {
            'completion_percentage': 0,
            'requirements_met': {},
            'total_requirements': len(requirements),
            'met_requirements': 0
        }
        
        for req_name, req_config in requirements.items():
            if req_config['type'] == 'accuracy':
                target_accuracy = req_config['target']
                current_accuracy = sum(1 for h in history if h.get('is_correct', False)) / len(history) if len(history) > 0 else 0
                progress['requirements_met'][req_name] = current_accuracy >= target_accuracy
            
            elif req_config['type'] == 'question_count':
                target_count = req_config['target']
                current_count = len(history)
                progress['requirements_met'][req_name] = current_count >= target_count
            
            elif req_config['type'] == 'department_coverage':
                required_departments = req_config['departments']
                user_departments = set(h.get('department') for h in history)
                coverage = len(user_departments.intersection(required_departments)) / len(required_departments)
                progress['requirements_met'][req_name] = coverage >= req_config['coverage_threshold']
        
        progress['met_requirements'] = sum(1 for met in progress['requirements_met'].values() if met)
        progress['completion_percentage'] = (progress['met_requirements'] / progress['total_requirements']) * 100
        
        return progress
    
    def _check_requirements_status(self, user_data: Dict, requirements: Dict) -> Dict[str, Any]:
        """要件ステータスチェック"""
        status = {}
        history = user_data.get('history', [])
        
        for req_name, req_config in requirements.items():
            if req_config['type'] == 'accuracy':
                current_accuracy = sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0
                status[req_name] = {
                    'current': current_accuracy,
                    'target': req_config['target'],
                    'met': current_accuracy >= req_config['target'],
                    'progress_percentage': (current_accuracy / req_config['target']) * 100
                }
        
        return status
    
    def _get_time_cutoff(self, time_period: str) -> Optional[datetime]:
        """時間期間のカットオフ日取得"""
        now = datetime.now()
        
        if time_period == 'week':
            return now - timedelta(weeks=1)
        elif time_period == 'month':
            return now - timedelta(days=30)
        elif time_period == 'quarter':
            return now - timedelta(days=90)
        elif time_period == 'year':
            return now - timedelta(days=365)
        else:
            return None
    
    def _calculate_performance_analytics(self, history: List[Dict]) -> Dict[str, Any]:
        """パフォーマンス分析計算"""
        if not history:
            return {}
        
        # 時系列分析
        daily_performance = defaultdict(list)
        for entry in history:
            try:
                date = datetime.fromisoformat(entry.get('date', '')).date()
                daily_performance[date.isoformat()].append(entry.get('is_correct', False))
            except:
                continue
        
        # 部門別分析
        department_performance = defaultdict(list)
        for entry in history:
            dept = entry.get('department', 'unknown')
            department_performance[dept].append(entry.get('is_correct', False))
        
        return {
            'daily_accuracy': {
                date: sum(results) / len(results) 
                for date, results in daily_performance.items()
            },
            'department_accuracy': {
                dept: sum(results) / len(results) 
                for dept, results in department_performance.items()
            },
            'learning_velocity': len(history) / max(len(daily_performance), 1),
            'consistency_score': self._calculate_consistency_score(daily_performance)
        }
    
    def _calculate_learning_progress(self, user_data: Dict) -> Dict[str, Any]:
        """学習進捗計算"""
        history = user_data.get('history', [])
        
        if not history:
            return {}
        
        # 進捗指標
        total_questions = len(history)
        correct_answers = sum(1 for h in history if h.get('is_correct', False))
        
        # 時間軸での改善度
        if len(history) >= 20:
            early_accuracy = sum(1 for h in history[:10] if h.get('is_correct', False)) / 10
            recent_accuracy = sum(1 for h in history[-10:] if h.get('is_correct', False)) / 10
            improvement = recent_accuracy - early_accuracy
        else:
            improvement = 0
        
        return {
            'total_progress': min(total_questions / 100, 1.0),  # 100問で100%
            'accuracy_progress': correct_answers / total_questions,
            'improvement_rate': improvement,
            'mastery_level': self._calculate_mastery_level(history),
            'study_consistency': self._calculate_study_consistency(history)
        }
    
    # その他のヘルパーメソッドは簡略化実装
    def _identify_weak_areas_for_report(self, history: List[Dict]) -> List[str]:
        """レポート用弱点分野特定"""
        return ["構造計算", "土質力学"]  # 簡略化
    
    def _identify_strengths_for_report(self, history: List[Dict]) -> List[str]:
        """レポート用強み分野特定"""
        return ["基礎知識", "法規"]  # 簡略化
    
    def _generate_learning_recommendations(self, user_data: Dict) -> List[str]:
        """学習推奨生成"""
        return ["毎日30分の学習継続を推奨", "弱点分野の集中学習"]  # 簡略化
    
    def _get_user_certifications_status(self, user_id: str) -> List[Dict]:
        """ユーザー認定ステータス取得"""
        user_data = self._load_user_data(user_id)
        return user_data.get('certifications', {})
    
    def _convert_to_pdf(self, report: Dict) -> Dict[str, Any]:
        """PDF変換（簡略化）"""
        return {'format': 'pdf', 'data': report, 'message': 'PDF conversion would be implemented here'}
    
    def _convert_to_excel(self, report: Dict) -> Dict[str, Any]:
        """Excel変換（簡略化）"""
        return {'format': 'excel', 'data': report, 'message': 'Excel conversion would be implemented here'}
    
    def _calculate_department_breakdown(self, users: List[str]) -> Dict[str, Any]:
        """部門別分析"""
        return {"道路": 45, "河川": 30, "建設環境": 25}  # 簡略化
    
    def _calculate_learning_trends(self, users: List[str], time_period: str) -> Dict[str, Any]:
        """学習トレンド分析"""
        return {"trend": "improving", "growth_rate": 0.15}  # 簡略化
    
    def _get_organization_certification_progress(self, users: List[str]) -> Dict[str, Any]:
        """組織認定進捗"""
        return {"in_progress": 20, "completed": 5}  # 簡略化
    
    def _generate_organization_recommendations(self, user_data: List[Dict]) -> List[str]:
        """組織推奨生成"""
        return ["グループ学習セッションの実施を推奨"]  # 簡略化
    
    def _perform_external_sync(self, integration: Dict) -> Dict[str, Any]:
        """外部同期実行（簡略化）"""
        return {"synced_users": 50, "status": "success"}
    
    def _calculate_consistency_score(self, daily_performance: Dict) -> float:
        """一貫性スコア計算"""
        return 0.8  # 簡略化
    
    def _calculate_mastery_level(self, history: List[Dict]) -> str:
        """習熟度レベル計算"""
        accuracy = sum(1 for h in history if h.get('is_correct', False)) / len(history)
        if accuracy >= 0.9:
            return "expert"
        elif accuracy >= 0.7:
            return "advanced"
        elif accuracy >= 0.5:
            return "intermediate"
        else:
            return "beginner"
    
    def _calculate_study_consistency(self, history: List[Dict]) -> float:
        """学習一貫性計算"""
        return 0.75  # 簡略化
    
    def _analyze_global_learning_patterns(self, all_users: Dict) -> Dict[str, Any]:
        """グローバル学習パターン分析"""
        return {"pattern": "evening_preference", "peak_hours": [19, 20, 21]}
    
    def _calculate_global_performance_metrics(self, all_histories: List[Dict]) -> Dict[str, Any]:
        """グローバルパフォーマンス指標"""
        return {"global_accuracy": 0.72, "average_session_length": 25}
    
    def _analyze_content_effectiveness(self, all_histories: List[Dict]) -> Dict[str, Any]:
        """コンテンツ効果分析"""
        return {"most_difficult": [101, 205, 378], "most_effective": [45, 67, 89]}
    
    def _calculate_user_accuracy(self, user_data: Dict) -> float:
        """ユーザー正答率計算"""
        history = user_data.get('history', [])
        if not history:
            return 0.0
        return sum(1 for h in history if h.get('is_correct', False)) / len(history)
    
    def _assess_learning_level(self, user_data: Dict) -> str:
        """学習レベル評価"""
        history = user_data.get('history', [])
        if len(history) < 10:
            return "beginner"
        elif len(history) < 50:
            return "intermediate"
        else:
            return "advanced"
    
    def _get_user_primary_departments(self, user_data: Dict) -> List[str]:
        """ユーザー主要部門取得"""
        history = user_data.get('history', [])
        departments = [h.get('department', 'unknown') for h in history]
        from collections import Counter
        dept_counts = Counter(departments)
        return [dept for dept, count in dept_counts.most_common(3)]
    
    def _convert_analytics_to_csv(self, analytics_data: Dict) -> Dict[str, Any]:
        """分析データCSV変換"""
        return {'format': 'csv', 'data': analytics_data, 'message': 'CSV conversion would be implemented here'}
    
    def _convert_analytics_to_excel(self, analytics_data: Dict) -> Dict[str, Any]:
        """分析データExcel変換"""
        return {'format': 'excel', 'data': analytics_data, 'message': 'Excel conversion would be implemented here'}

# APIキー検証デコレータ
def require_api_key(permission: str = None):
    """APIキー認証デコレータ"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 実際の実装では、FlaskのrequestからAPIキーを取得
            # ここでは簡略化
            api_key = "dummy_api_key"  # request.headers.get('X-API-Key')
            
            api_manager = APIManager()
            validation_result = api_manager.validate_api_key(api_key, permission)
            
            if not validation_result['valid']:
                return {'error': 'Unauthorized', 'message': validation_result['error']}, 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# グローバルインスタンス
api_manager = APIManager()