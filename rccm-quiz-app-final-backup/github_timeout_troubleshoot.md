# 🚨 GitHub接続タイムアウトエラー解決ガイド

## 📊 **エラー詳細分析**

```
fatal: unable to access 'https://github.com/civil-ai-study/rccm-quiz-2025-complete.git/': 
Connection timed out after 300019 milliseconds
```

### 🔍 **原因分析**
- **タイムアウト時間**: 300秒（5分） = 非常に長い
- **接続方式**: HTTPS
- **問題箇所**: GitHub.comとの通信
- **根本原因**: ネットワーク層の問題

---

## 🛠️ **即座に試せる解決方法（優先順）**

### 🚀 **方法1: Git設定の最適化（推奨）**

```bash
# 1. タイムアウト時間を延長
git config --global http.timeout 900
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 2. HTTPバッファサイズ増加
git config --global http.postBuffer 524288000

# 3. 接続確認
git config --list | grep http
```

### 🔄 **方法2: SSH接続への変更**

```bash
# 1. リモートURLをSSHに変更
git remote set-url origin git@github.com:civil-ai-study/rccm-quiz-2025-complete.git

# 2. SSH接続テスト
ssh -T git@github.com

# 3. プッシュ実行
git push origin master
```

### 🌐 **方法3: プロキシ・DNS設定確認**

```bash
# 1. DNS確認
nslookup github.com
ping github.com

# 2. プロキシ設定クリア（企業環境の場合）
git config --global --unset http.proxy
git config --global --unset https.proxy

# 3. 再試行
git push origin master
```

---

## 🔧 **GitHub Desktop特有の解決方法**

### **Option A: GitHub Desktop設定変更**
1. **File → Options → Git**
2. **"Use system Git"** をチェック
3. **再起動後にプッシュ試行**

### **Option B: コマンドライン併用**
```bash
# GitHub Desktopでコミット → コマンドラインでプッシュ
cd "C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app"
git push origin master --verbose
```

---

## 🌍 **ネットワーク環境別対処法**

### 🏢 **企業・学校ネットワーク**
```bash
# プロキシ設定（IT部門に確認）
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy http://proxy.company.com:8080

# 証明書問題の回避（最終手段）
git config --global http.sslVerify false
```

### 🏠 **家庭用ネットワーク**
```bash
# DNS変更（Google DNS）
# Windows: ネットワーク設定で8.8.8.8, 8.8.4.4に変更

# 一時的な回避
git config --global http.timeout 1800  # 30分
```

### 📱 **モバイル・テザリング**
```bash
# 小さなパケットで送信
git config --global http.postBuffer 1048576  # 1MB
git push origin master --verbose
```

---

## ⚡ **即効性のある緊急対処法**

### **方法1: 分割プッシュ**
```bash
# 最新コミットのみプッシュ
git push origin HEAD:master

# または強制プッシュ（注意）
git push origin master --force
```

### **方法2: 別ネットワーク使用**
- **モバイルホットスポット**に一時切り替え
- **VPN**経由での接続試行

### **方法3: GitHub CLI使用**
```bash
# GitHub CLI インストール後
gh repo sync

# または直接アップロード
gh repo create backup-repo --private
gh repo upload .
```

---

## 🔍 **詳細診断コマンド**

### **接続状況確認**
```bash
# 1. 基本接続テスト
curl -I https://github.com
telnet github.com 443

# 2. Git詳細ログ
GIT_CURL_VERBOSE=1 git push origin master

# 3. ネットワーク統計
netstat -an | findstr :443
```

### **設定確認**
```bash
# 現在のGit設定
git config --list --show-origin

# リモート設定確認
git remote -v

# ブランチ状況
git status
git log --oneline -5
```

---

## 🎯 **今回のプロジェクト特有の対策**

### **1. ファイルサイズ確認**
```bash
# 大容量ファイル特定
find . -type f -size +10M
git ls-files -s | sort -k 2 -nr | head -10
```

### **2. 不要ファイル除外**
```bash
# .gitignore追加
echo "*.log" >> .gitignore
echo "ultra_sync_*.json" >> .gitignore
echo "*_backup*" >> .gitignore

git add .gitignore
git commit -m "Add .gitignore for large files"
```

### **3. 段階的プッシュ**
```bash
# 重要ファイルのみ先にプッシュ
git add app.py config.py
git commit -m "Critical deployment fix only"
git push origin master

# 残りのファイルは後で
git add .
git commit -m "Additional files"
git push origin master
```

---

## 🚀 **推奨実行順序**

### **ステップ1: 即座の対処（5分以内）**
```bash
# タイムアウト設定変更
git config --global http.timeout 1800
git config --global http.postBuffer 524288000

# 再試行
git push origin master
```

### **ステップ2: ネットワーク変更（10分以内）**
- モバイルホットスポットに切り替え
- または別のWiFiネットワーク使用

### **ステップ3: SSH切り替え（15分以内）**
```bash
git remote set-url origin git@github.com:civil-ai-study/rccm-quiz-2025-complete.git
git push origin master
```

### **ステップ4: 代替手段（30分以内）**
- GitHub Web UIでの手動アップロード
- ZIP形式での配布

---

## 📞 **追加サポート**

### **成功した場合の確認**
```bash
# プッシュ成功確認
git log --oneline -1
git remote show origin
```

### **失敗が続く場合**
- **具体的なエラーメッセージ**の再確認
- **ネットワーク管理者**への相談（企業環境）
- **GitHub Status**確認: https://githubstatus.com

---

**まずは「方法1: Git設定の最適化」から試してみてください。多くの場合、これで解決します！**