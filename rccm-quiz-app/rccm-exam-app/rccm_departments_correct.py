# CSVデータに実際に存在する12部門の正確な定義

CORRECT_DEPARTMENTS = {
    'road': {
        'id': 'road',
        'name': '道路',
        'csv_category': '道路',
        'full_name': '建設部門：道路',
        'description': '道路計画、道路設計、道路施工に関する専門技術',
        'icon': '🛣️',
        'color': '#FF9800'
    },
    'tunnel': {
        'id': 'tunnel', 
        'name': 'トンネル',
        'csv_category': 'トンネル',
        'full_name': '建設部門：トンネル',
        'description': 'トンネル計画、設計、施工に関する専門技術',
        'icon': '🚇',
        'color': '#795548'
    },
    'civil_planning': {
        'id': 'civil_planning',
        'name': '河川、砂防及び海岸・海洋',
        'csv_category': '河川、砂防及び海岸・海洋',  # 2017年以降
        'csv_category_alt': ['河川砂防海岸'],  # 2018年
        'full_name': '建設部門：河川、砂防及び海岸・海洋',
        'description': '河川工学、砂防工学、海岸・海洋工学に関する専門技術',
        'icon': '🌊',
        'color': '#2196F3'
    },
    'urban_planning': {
        'id': 'urban_planning',
        'name': '都市計画及び地方計画',
        'csv_category': '都市計画及び地方計画',  # 2017年以降
        'csv_category_alt': ['都市計画地方計画'],  # 2018年
        'full_name': '建設部門：都市計画及び地方計画',
        'description': '都市計画、地方計画に関する専門技術',
        'icon': '🏙️',
        'color': '#9C27B0'
    },
    'landscape': {
        'id': 'landscape',
        'name': '造園',
        'csv_category': '造園',
        'full_name': '建設部門：造園',
        'description': '造園計画、設計、施工に関する専門技術',
        'icon': '🌸',
        'color': '#E91E63'
    },
    'construction_env': {
        'id': 'construction_env',
        'name': '建設環境',
        'csv_category': '建設環境',
        'full_name': '建設部門：建設環境',
        'description': '建設環境、環境保全に関する専門技術',
        'icon': '🌱',
        'color': '#4CAF50'
    },
    'steel_concrete': {
        'id': 'steel_concrete',
        'name': '鋼構造及びコンクリート',
        'csv_category': '鋼構造及びコンクリート',  # 2017年以降
        'csv_category_alt': ['鋼構造コンクリート'],  # 2018年
        'full_name': '建設部門：鋼構造及びコンクリート',
        'description': '鋼構造、コンクリート構造に関する専門技術',
        'icon': '🏗️',
        'color': '#607D8B'
    },
    'soil_foundation': {
        'id': 'soil_foundation',
        'name': '土質及び基礎',
        'csv_category': '土質及び基礎',
        'full_name': '建設部門：土質及び基礎',
        'description': '土質工学、基礎工学に関する専門技術',
        'icon': '🪨',
        'color': '#8D6E63'
    },
    'construction_planning': {
        'id': 'construction_planning',
        'name': '施工計画、施工設備及び積算',
        'csv_category': '施工計画',  # 2017年
        'csv_category_alt': ['施工計画施工設備積算'],  # 2018年
        'full_name': '建設部門：施工計画、施工設備及び積算',
        'description': '施工計画、施工設備、積算に関する専門技術',
        'icon': '📋',
        'color': '#FF5722'
    },
    'water_supply': {
        'id': 'water_supply',
        'name': '上水道及び工業用水道',
        'csv_category': '上水道及び工業用水道',
        'full_name': '建設部門：上水道及び工業用水道',
        'description': '上水道、工業用水道に関する専門技術',
        'icon': '💧',
        'color': '#00BCD4'
    },
    'forestry': {
        'id': 'forestry',
        'name': '森林土木',
        'csv_category': '森林土木',
        'full_name': '建設部門：森林土木',
        'description': '森林土木、治山工事に関する専門技術',
        'icon': '🌲',
        'color': '#8BC34A'
    },
    'agriculture': {
        'id': 'agriculture',
        'name': '農業土木',
        'csv_category': '農業土木',
        'full_name': '建設部門：農業土木',
        'description': '農業基盤整備に関する専門技術',
        'icon': '🌾',
        'color': '#CDDC39'
    }
}

# カテゴリ名から部門IDへのマッピング（全年度対応）
CATEGORY_TO_DEPARTMENT = {
    # 道路
    '道路': 'road',
    
    # トンネル  
    'トンネル': 'tunnel',
    
    # 河川砂防海岸
    '河川、砂防及び海岸・海洋': 'civil_planning',
    '河川砂防海岸': 'civil_planning',
    
    # 都市計画
    '都市計画及び地方計画': 'urban_planning', 
    '都市計画地方計画': 'urban_planning',
    
    # 造園
    '造園': 'landscape',
    
    # 建設環境
    '建設環境': 'construction_env',
    
    # 鋼構造コンクリート
    '鋼構造及びコンクリート': 'steel_concrete',
    '鋼構造コンクリート': 'steel_concrete',
    
    # 土質基礎
    '土質及び基礎': 'soil_foundation',
    
    # 施工計画
    '施工計画': 'construction_planning',
    '施工計画施工設備積算': 'construction_planning',
    
    # 上水道
    '上水道及び工業用水道': 'water_supply',
    
    # 森林土木
    '森林土木': 'forestry',
    
    # 農業土木
    '農業土木': 'agriculture'
}