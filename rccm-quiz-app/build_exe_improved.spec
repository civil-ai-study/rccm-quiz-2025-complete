# -*- mode: python ; coding: utf-8 -*-

"""
RCCM試験問題集2025 - 改良版PyInstaller設定ファイル
一般配布環境向け最適化
"""

import os
from pathlib import Path

# 現在のディレクトリを取得
current_dir = Path.cwd()

# データファイルを収集
data_files = []

# templatesフォルダ
templates_dir = current_dir / 'templates'
if templates_dir.exists():
    for template_file in templates_dir.rglob('*'):
        if template_file.is_file():
            relative_path = template_file.relative_to(templates_dir)
            data_files.append((str(template_file), str(Path('templates') / relative_path)))

# staticフォルダ
static_dir = current_dir / 'static'
if static_dir.exists():
    for static_file in static_dir.rglob('*'):
        if static_file.is_file():
            relative_path = static_file.relative_to(static_dir)
            data_files.append((str(static_file), str(Path('static') / relative_path)))

# dataフォルダ（CSVファイル）
data_dir = current_dir / 'data'
if data_dir.exists():
    for data_file in data_dir.rglob('*.csv'):
        if data_file.is_file():
            relative_path = data_file.relative_to(data_dir)
            data_files.append((str(data_file), str(Path('data') / relative_path)))

# 設定ファイル
config_files = ['config.py', 'utils.py', 'data_manager.py']
for config_file in config_files:
    config_path = current_dir / config_file
    if config_path.exists():
        data_files.append((str(config_path), config_file))

# AI・ソーシャル・企業版機能ファイル（存在する場合のみ）
feature_files = [
    'ai_analyzer.py', 'adaptive_learning.py', 'advanced_analytics.py',
    'gamification.py', 'exam_simulator.py', 'mobile_features.py',
    'social_learning.py', 'api_integration.py', 'admin_dashboard.py',
    'advanced_personalization.py'
]
for feature_file in feature_files:
    feature_path = current_dir / feature_file
    if feature_path.exists():
        data_files.append((str(feature_path), feature_file))

print(f"収集したデータファイル数: {len(data_files)}")

a = Analysis(
    ['app_exe版.py'],  # EXE最適化版を使用
    pathex=[str(current_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        # Core Flask
        'flask', 'flask.app', 'flask.json', 'flask.templating',
        'werkzeug', 'werkzeug.serving', 'werkzeug.utils',
        'jinja2', 'jinja2.ext',
        
        # Data processing
        'pandas', 'pandas.io.common', 'pandas.io.parsers',
        'numpy', 'numpy.core._methods',
        
        # Standard library
        'json', 'csv', 'datetime', 'time', 'os', 'sys',
        'hashlib', 'uuid', 'threading', 'socket',
        'webbrowser', 'pathlib',
        
        # Security & sessions
        'itsdangerous', 'markupsafe',
        
        # Encoding
        'chardet', 'encodings', 'encodings.utf_8', 'encodings.cp1252',
        
        # Others
        'click', 'six', 'pytz', 'dateutil',
        'functools', 'collections', 'queue',
        'concurrent.futures', 'logging'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不要なモジュールを除外してサイズ削減
        'tkinter', 'unittest', 'email', 'http', 'urllib', 'xml',
        'test', 'tests', 'setuptools', 'distutils', 'pip',
        'matplotlib', 'seaborn', 'plotly', 'dash', 'scipy',
        'sklearn', 'requests'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 重複ファイルを除去
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RCCM試験問題集2025',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX圧縮でサイズ削減
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # デバッグ用にコンソール表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定: 'icon.ico'
    version=None  # バージョン情報ファイルがあれば指定
)