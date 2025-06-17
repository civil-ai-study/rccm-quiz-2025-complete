# -*- mode: python ; coding: utf-8 -*-

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
            data_files.append((str(template_file), f'templates/{template_file.relative_to(templates_dir)}'))

# staticフォルダ
static_dir = current_dir / 'static'
if static_dir.exists():
    for static_file in static_dir.rglob('*'):
        if static_file.is_file():
            data_files.append((str(static_file), f'static/{static_file.relative_to(static_dir)}'))

# dataフォルダ（CSVファイル）
data_dir = current_dir / 'data'
if data_dir.exists():
    for data_file in data_dir.rglob('*.csv'):
        if data_file.is_file():
            data_files.append((str(data_file), f'data/{data_file.relative_to(data_dir)}'))

# 設定ファイル
config_files = ['config.py', 'utils.py', 'data_manager.py']
for config_file in config_files:
    config_path = current_dir / config_file
    if config_path.exists():
        data_files.append((str(config_path), config_file))

# AI・ソーシャル・企業版機能ファイル
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

a = Analysis(
    ['app.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'flask', 'pandas', 'numpy', 'jinja2', 'werkzeug',
        'sklearn', 'scipy', 'matplotlib', 'seaborn',
        'requests', 'urllib3', 'chardet', 'certifi',
        'click', 'itsdangerous', 'markupsafe',
        'plotly', 'dash', 'threading', 'queue',
        'sqlite3', 'json', 'csv', 'datetime',
        'hashlib', 'uuid', 'time', 'os', 'sys',
        'concurrent.futures', 'functools', 'collections'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'http', 'urllib', 'xml'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーションとして実行
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # アイコンファイルがあれば指定
)