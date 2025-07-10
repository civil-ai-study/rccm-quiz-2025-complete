#!/usr/bin/env python3
"""
ULTRATHIN土質及び基礎部門問題の詳細原因分析
- 既存ファイルを変更しない安全な診断ツール
- 段階的な原因特定に集中
"""

import os
import json
import logging
from datetime import datetime
from utils import load_specialist_questions_only, validate_file_path, monitored_file_open

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SoilFoundationDebugAnalyzer:
    """土質及び基礎部門問題の詳細分析クラス"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.analysis_results = {}
        
    def analyze_soil_foundation_issue(self):
        """土質及び基礎部門の問題を段階的に分析"""
        logger.info("=== ULTRATHIN土質及び基礎部門問題分析開始 ===")
        
        # 段階1: CSVファイルの存在確認
        self._check_csv_files()
        
        # 段階2: 2019年データの直接読み込み確認
        self._check_2019_data_direct()
        
        # 段階3: カテゴリマッピング確認
        self._check_category_mapping()
        
        # 段階4: load_specialist_questions_only関数の動作確認
        self._check_load_specialist_function()
        
        # 段階5: 年度空指定時の処理確認
        self._check_empty_year_handling()
        
        # 結果をファイルに保存
        self._save_analysis_results()
        
        return self.analysis_results
    
    def _check_csv_files(self):
        """CSVファイルの存在確認"""
        logger.info("段階1: CSVファイルの存在確認")
        
        csv_files = {}
        for year in range(2008, 2020):
            csv_file = os.path.join(self.data_dir, f'4-2_{year}.csv')
            exists = os.path.exists(csv_file)
            csv_files[year] = {
                'file': csv_file,
                'exists': exists,
                'size': os.path.getsize(csv_file) if exists else 0
            }
            if exists:
                logger.info(f"✓ 4-2_{year}.csv 存在確認 - サイズ: {csv_files[year]['size']} bytes")
        
        self.analysis_results['csv_files'] = csv_files
    
    def _check_2019_data_direct(self):
        """2019年データの直接読み込み確認"""
        logger.info("段階2: 2019年データの直接読み込み確認")
        
        csv_file = os.path.join(self.data_dir, '4-2_2019.csv')
        
        try:
            validated_path = validate_file_path(csv_file)
            
            # CSVファイルの直接読み込み
            soil_foundation_questions = []
            all_categories = set()
            
            with monitored_file_open(validated_path, 'r', encoding='utf-8') as f:
                import csv
                reader = csv.DictReader(f)
                
                for row in reader:
                    category = row.get('category', '').strip()
                    all_categories.add(category)
                    
                    # 土質及び基礎カテゴリの問題を抽出
                    if category == '土質及び基礎':
                        soil_foundation_questions.append({
                            'id': row.get('id'),
                            'category': category,
                            'question': row.get('question', '')[:100] + '...' if len(row.get('question', '')) > 100 else row.get('question', '')
                        })
            
            self.analysis_results['2019_data_direct'] = {
                'total_soil_foundation_questions': len(soil_foundation_questions),
                'all_categories': sorted(list(all_categories)),
                'sample_questions': soil_foundation_questions[:5],
                'category_contains_soil': any('土質' in cat for cat in all_categories)
            }
            
            logger.info(f"✓ 2019年データ直接読み込み完了: 土質及び基礎問題数 = {len(soil_foundation_questions)}")
            logger.info(f"✓ 全カテゴリ: {sorted(list(all_categories))}")
            
        except Exception as e:
            logger.error(f"✗ 2019年データ直接読み込み失敗: {e}")
            self.analysis_results['2019_data_direct'] = {'error': str(e)}
    
    def _check_category_mapping(self):
        """カテゴリマッピング確認"""
        logger.info("段階3: カテゴリマッピング確認")
        
        # app.pyからマッピングをインポート
        try:
            from app import DEPARTMENT_TO_CATEGORY_MAPPING, normalize_department_name, get_department_category
            
            # soil_foundation部門のマッピング確認
            soil_foundation_mapping = {
                'soil_foundation_key': 'soil_foundation',
                'mapped_category': DEPARTMENT_TO_CATEGORY_MAPPING.get('soil_foundation'),
                'normalized_name': normalize_department_name('soil_foundation'),
                'expected_category': get_department_category('soil_foundation')
            }
            
            self.analysis_results['category_mapping'] = {
                'soil_foundation_mapping': soil_foundation_mapping,
                'full_mapping': DEPARTMENT_TO_CATEGORY_MAPPING
            }
            
            logger.info(f"✓ soil_foundation → {soil_foundation_mapping['mapped_category']}")
            logger.info(f"✓ 正規化結果: {soil_foundation_mapping['normalized_name']}")
            
        except Exception as e:
            logger.error(f"✗ カテゴリマッピング確認失敗: {e}")
            self.analysis_results['category_mapping'] = {'error': str(e)}
    
    def _check_load_specialist_function(self):
        """load_specialist_questions_only関数の動作確認"""
        logger.info("段階4: load_specialist_questions_only関数の動作確認")
        
        try:
            # 関数の引数を確認
            from utils import load_specialist_questions_only
            
            # 2019年データで土質及び基礎部門の問題を取得
            result = load_specialist_questions_only(
                department='土質及び基礎',  # 日本語カテゴリ名で指定
                year=2019,
                data_dir=self.data_dir
            )
            
            self.analysis_results['load_specialist_function'] = {
                'department_arg': '土質及び基礎',
                'year_arg': 2019,
                'result_count': len(result),
                'sample_questions': result[:3] if result else []
            }
            
            logger.info(f"✓ load_specialist_questions_only結果: {len(result)}問")
            
            # 空の場合は詳細デバッグ
            if not result:
                logger.warning("⚠️ load_specialist_questions_only結果が空 - 詳細調査")
                
                # 全問題を取得して確認
                from utils import load_questions_improved
                csv_file = os.path.join(self.data_dir, '4-2_2019.csv')
                validated_path = validate_file_path(csv_file)
                all_questions = load_questions_improved(validated_path)
                
                categories_in_data = set(q.get('category', '') for q in all_questions)
                
                self.analysis_results['load_specialist_function']['debug_info'] = {
                    'total_questions_in_file': len(all_questions),
                    'categories_in_data': sorted(list(categories_in_data)),
                    'exact_match_count': len([q for q in all_questions if q.get('category') == '土質及び基礎'])
                }
                
                logger.info(f"デバッグ: ファイル内全問題数 = {len(all_questions)}")
                logger.info(f"デバッグ: ファイル内カテゴリ = {sorted(list(categories_in_data))}")
                
        except Exception as e:
            logger.error(f"✗ load_specialist_questions_only確認失敗: {e}")
            self.analysis_results['load_specialist_function'] = {'error': str(e)}
    
    def _check_empty_year_handling(self):
        """年度空指定時の処理確認"""
        logger.info("段階5: 年度空指定時の処理確認")
        
        try:
            # app.pyでの年度空指定時の処理を模擬
            from app import get_mixed_questions
            
            # 空の年度でのget_mixed_questions呼び出し
            # セッションオブジェクトを模擬
            mock_session = {}
            
            # 全問題データを読み込み
            from utils import load_rccm_data_files
            all_questions = load_rccm_data_files(self.data_dir)
            
            # get_mixed_questions呼び出し
            result = get_mixed_questions(
                user_session=mock_session,
                all_questions=all_questions,
                requested_category='全体',
                session_size=10,
                department='soil_foundation',
                question_type='specialist',
                year=None  # 年度空指定
            )
            
            self.analysis_results['empty_year_handling'] = {
                'total_questions_loaded': len(all_questions),
                'result_count': len(result),
                'sample_questions': result[:3] if result else []
            }
            
            logger.info(f"✓ 年度空指定時の結果: {len(result)}問")
            
        except Exception as e:
            logger.error(f"✗ 年度空指定時の処理確認失敗: {e}")
            self.analysis_results['empty_year_handling'] = {'error': str(e)}
    
    def _save_analysis_results(self):
        """分析結果をファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"soil_foundation_debug_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ 分析結果保存完了: {output_file}")
            
        except Exception as e:
            logger.error(f"✗ 分析結果保存失敗: {e}")

if __name__ == "__main__":
    analyzer = SoilFoundationDebugAnalyzer()
    results = analyzer.analyze_soil_foundation_issue()
    
    print("\n=== 分析結果サマリー ===")
    
    # CSVファイル存在確認
    if 'csv_files' in results:
        existing_files = [year for year, info in results['csv_files'].items() if info['exists']]
        print(f"存在するCSVファイル年度: {existing_files}")
    
    # 2019年データ直接読み込み結果
    if '2019_data_direct' in results:
        direct_data = results['2019_data_direct']
        if 'error' not in direct_data:
            print(f"2019年土質及び基礎問題数: {direct_data['total_soil_foundation_questions']}")
            print(f"全カテゴリ: {direct_data['all_categories']}")
    
    # カテゴリマッピング結果
    if 'category_mapping' in results:
        mapping_data = results['category_mapping']
        if 'error' not in mapping_data:
            soil_mapping = mapping_data['soil_foundation_mapping']
            print(f"soil_foundation → {soil_mapping['mapped_category']}")
    
    # load_specialist_questions_only結果
    if 'load_specialist_function' in results:
        func_data = results['load_specialist_function']
        if 'error' not in func_data:
            print(f"load_specialist_questions_only結果: {func_data['result_count']}問")
    
    # 年度空指定時の処理結果
    if 'empty_year_handling' in results:
        empty_year_data = results['empty_year_handling']
        if 'error' not in empty_year_data:
            print(f"年度空指定時の結果: {empty_year_data['result_count']}問")
    
    print("\n詳細な分析結果は生成されたJSONファイルを参照してください。")