#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 Phase 1】静的コンテンツBlueprint
副作用ゼロの最安全分離・第一段階
既存システム完全非干渉
"""

from flask import Blueprint, send_from_directory, jsonify
import os
import logging

logger = logging.getLogger(__name__)

# 静的コンテンツ専用Blueprint定義
static_bp = Blueprint(
    'static_content',
    __name__,
    url_prefix='',  # ルートレベル
)

@static_bp.route('/favicon.ico')
def favicon():
    """ファビコン配信"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'favicon.ico', 
            mimetype='image/x-icon'
        )
    except FileNotFoundError:
        # フォールバック: 404ではなく透明GIF
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'transparent.gif', 
            mimetype='image/gif'
        )

@static_bp.route('/manifest.json')
def manifest():
    """PWA Manifest配信"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'manifest.json', 
            mimetype='application/json'
        )
    except FileNotFoundError:
        # 動的生成フォールバック
        return jsonify({
            "name": "RCCM試験対策アプリ",
            "short_name": "RCCM Quiz",
            "description": "RCCM試験対策のためのWebアプリ",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#007bff",
            "icons": [
                {
                    "src": "/static/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/static/icon-512.png", 
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        })

@static_bp.route('/sw.js')
def service_worker():
    """Service Worker配信"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'sw.js', 
            mimetype='application/javascript'
        )
    except FileNotFoundError:
        # 最小限Service Worker動的生成
        sw_content = """
// ULTRATHIN区 最小限Service Worker
const CACHE_NAME = 'rccm-quiz-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/app.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
"""
        from flask import Response
        return Response(sw_content, mimetype='application/javascript')

@static_bp.route('/icon-<int:size>.png')
def app_icon(size):
    """アプリアイコン配信（サイズ対応）"""
    valid_sizes = [16, 32, 48, 72, 96, 144, 192, 256, 384, 512]
    
    if size not in valid_sizes:
        size = 192  # デフォルトサイズ
    
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            f'icon-{size}.png', 
            mimetype='image/png'
        )
    except FileNotFoundError:
        # フォールバック: デフォルトアイコン
        try:
            return send_from_directory(
                os.path.join(os.path.dirname(__file__), '..', 'static'), 
                'favicon.ico', 
                mimetype='image/x-icon'
            )
        except FileNotFoundError:
            # 最後のフォールバック: 1x1透明PNG
            from flask import Response
            import base64
            
            # 1x1透明PNG（Base64エンコード）
            transparent_png = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77AAAAAElFTkSuQmCC'
            )
            
            return Response(
                transparent_png, 
                mimetype='image/png',
                headers={'Cache-Control': 'public, max-age=3600'}
            )

@static_bp.route('/robots.txt')
def robots():
    """robots.txt配信"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'robots.txt', 
            mimetype='text/plain'
        )
    except FileNotFoundError:
        # 動的生成フォールバック
        from flask import Response
        robots_content = """User-agent: *
Allow: /
Sitemap: /sitemap.xml

# RCCM試験対策アプリ
# クロール対象: 公開ページのみ
Disallow: /admin/
Disallow: /api/
Disallow: /debug/
"""
        return Response(robots_content, mimetype='text/plain')

@static_bp.route('/sitemap.xml')
def sitemap():
    """サイトマップ配信"""
    try:
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'static'), 
            'sitemap.xml', 
            mimetype='application/xml'
        )
    except FileNotFoundError:
        # 動的生成フォールバック
        from flask import Response, request
        
        base_url = request.url_root.rstrip('/')
        
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base_url}/help</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}/statistics</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>"""
        
        return Response(sitemap_content, mimetype='application/xml')

# Blueprint情報取得
def get_static_blueprint_info():
    """静的コンテンツBlueprint情報"""
    return {
        'name': 'static_content',
        'url_prefix': '',
        'routes': [
            {'path': '/favicon.ico', 'endpoint': 'favicon', 'methods': ['GET']},
            {'path': '/manifest.json', 'endpoint': 'manifest', 'methods': ['GET']},
            {'path': '/sw.js', 'endpoint': 'service_worker', 'methods': ['GET']},
            {'path': '/icon-<int:size>.png', 'endpoint': 'app_icon', 'methods': ['GET']},
            {'path': '/robots.txt', 'endpoint': 'robots', 'methods': ['GET']},
            {'path': '/sitemap.xml', 'endpoint': 'sitemap', 'methods': ['GET']}
        ],
        'description': '静的コンテンツ配信（PWA対応）',
        'risk_level': 'zero',
        'dependencies': 'none',
        'implementation_date': '2025-07-10',
        'phase': 'ULTRATHIN Phase 1'
    }

if __name__ == "__main__":
    print("【ULTRATHIN区 Phase 1】静的コンテンツBlueprint実装完了")
    print(f"ルート数: 6個")
    print(f"リスクレベル: ゼロ（副作用なし）")
    print("注意: app.pyへの登録は手動で行う必要があります")