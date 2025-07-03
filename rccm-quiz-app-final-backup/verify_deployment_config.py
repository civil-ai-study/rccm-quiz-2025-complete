#!/usr/bin/env python3
"""
🚀 Deployment Configuration Verification - Render Platform
Gunicorn本番環境設定の検証
"""

import os
import sys
import subprocess
from pathlib import Path

def verify_deployment_config():
    """デプロイメント設定の検証"""
    print("🚀 Deployment Configuration Verification - Render Platform")
    print("=" * 70)
    
    errors = []
    warnings = []
    
    # 1. render.yaml の検証
    print("\n📋 Checking render.yaml...")
    render_yaml = Path("render.yaml")
    if not render_yaml.exists():
        errors.append("❌ render.yaml not found")
    else:
        content = render_yaml.read_text()
        if "gunicorn" in content:
            print("✅ Gunicorn command found in render.yaml")
        else:
            errors.append("❌ Gunicorn command missing in render.yaml")
        
        if "wsgi:application" in content:
            print("✅ WSGI application entry point configured")
        else:
            errors.append("❌ WSGI application entry point missing")
    
    # 2. wsgi.py の検証
    print("\n📋 Checking wsgi.py...")
    wsgi_py = Path("wsgi.py")
    if not wsgi_py.exists():
        errors.append("❌ wsgi.py not found")
    else:
        print("✅ wsgi.py exists")
        content = wsgi_py.read_text()
        if "application = app" in content:
            print("✅ WSGI application exported correctly")
        else:
            errors.append("❌ WSGI application not exported")
    
    # 3. gunicorn.conf.py の検証
    print("\n📋 Checking gunicorn.conf.py...")
    gunicorn_conf = Path("gunicorn.conf.py")
    if not gunicorn_conf.exists():
        warnings.append("⚠️  gunicorn.conf.py not found (using defaults)")
    else:
        print("✅ gunicorn.conf.py exists")
        content = gunicorn_conf.read_text()
        if "RENDER" in content:
            print("✅ Render-specific configuration found")
        else:
            warnings.append("⚠️  No Render-specific configuration")
    
    # 4. requirements_minimal.txt の検証
    print("\n📋 Checking requirements_minimal.txt...")
    requirements = Path("requirements_minimal.txt")
    if not requirements.exists():
        errors.append("❌ requirements_minimal.txt not found")
    else:
        content = requirements.read_text()
        required_packages = {
            "gunicorn": "Production WSGI server",
            "Flask": "Web framework",
            "psutil": "System monitoring",
            "Flask-WTF": "CSRF protection"
        }
        
        for package, description in required_packages.items():
            if package in content:
                print(f"✅ {package} found ({description})")
            else:
                errors.append(f"❌ {package} missing ({description})")
    
    # 5. 環境変数の確認
    print("\n📋 Checking environment variables in render.yaml...")
    if render_yaml.exists():
        content = render_yaml.read_text()
        required_env_vars = ["FLASK_ENV", "PORT", "RENDER"]
        for env_var in required_env_vars:
            if f"key: {env_var}" in content:
                print(f"✅ {env_var} environment variable configured")
            else:
                warnings.append(f"⚠️  {env_var} environment variable not configured")
    
    # 6. アプリケーションのインポートテスト
    print("\n📋 Testing application imports...")
    try:
        # app.py のインポートテスト
        sys.path.insert(0, str(Path.cwd()))
        import app
        print("✅ app.py imports successfully")
        
        # wsgi のインポートテスト
        import wsgi
        print("✅ wsgi.py imports successfully")
        
        # Flask アプリケーションの確認
        if hasattr(wsgi, 'application'):
            print("✅ WSGI application object available")
        else:
            errors.append("❌ WSGI application object not found")
            
    except ImportError as e:
        errors.append(f"❌ Import error: {e}")
    except Exception as e:
        errors.append(f"❌ Unexpected error: {e}")
    
    # 7. Gunicorn実行可能性テスト
    print("\n📋 Testing Gunicorn availability...")
    try:
        result = subprocess.run(
            ["python", "-c", "import gunicorn; print('Gunicorn version:', gunicorn.__version__)"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            warnings.append("⚠️  Gunicorn not installed locally (will be installed during deployment)")
    except Exception:
        warnings.append("⚠️  Could not test Gunicorn locally")
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("📊 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 70)
    
    if not errors and not warnings:
        print("✅ All deployment configurations are correct!")
        print("🚀 Ready for deployment to Render")
        print("\n💡 Deployment command will be:")
        print("   gunicorn -c gunicorn.conf.py wsgi:application")
        return True
    else:
        if errors:
            print(f"\n❌ Found {len(errors)} critical error(s):")
            for error in errors:
                print(f"   {error}")
        
        if warnings:
            print(f"\n⚠️  Found {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"   {warning}")
        
        print("\n🔧 Fix the errors above before deploying")
        return False

def generate_deployment_checklist():
    """デプロイメントチェックリスト生成"""
    print("\n📋 RENDER DEPLOYMENT CHECKLIST")
    print("=" * 70)
    print("""
1. ✅ render.yaml configuration:
   - startCommand: gunicorn -c gunicorn.conf.py wsgi:application
   - buildCommand: pip install -r requirements_minimal.txt
   - Environment variables: FLASK_ENV=production, PORT=10000, RENDER=true

2. ✅ wsgi.py:
   - Exports 'application' object
   - Imports Flask app correctly
   - Sets production environment

3. ✅ gunicorn.conf.py:
   - Render-specific worker configuration
   - Proper port binding from PORT env var
   - Appropriate timeout and keepalive settings

4. ✅ requirements_minimal.txt:
   - gunicorn==21.2.0
   - Flask and all dependencies
   - psutil for monitoring
   - Flask-WTF for CSRF protection

5. 🔐 Security considerations:
   - Set SECRET_KEY environment variable in Render dashboard
   - Enable HTTPS in Render settings
   - Review security headers

6. 📊 Monitoring:
   - Check Render logs after deployment
   - Monitor memory usage (Render has limits)
   - Set up health checks

7. 🚀 Deployment steps:
   1. Commit all changes
   2. Push to GitHub
   3. Connect GitHub repo to Render
   4. Deploy from Render dashboard
   5. Monitor deployment logs
   6. Test production URL
""")

if __name__ == "__main__":
    print("🛡️ ULTRA SYNC DEPLOYMENT VERIFICATION - 副作用ゼロ")
    success = verify_deployment_config()
    
    if success:
        generate_deployment_checklist()
        print("\n✅ Deployment configuration verified successfully!")
    else:
        print("\n❌ Please fix the issues before deploying")
        sys.exit(1)