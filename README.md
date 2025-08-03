# 家族管理アプリ 👨‍👩‍👧‍👦

Django 5.2で構築された、家族の絆を深める総合管理アプリケーションです。

## 🌟 主な機能

### 📅 イベントカレンダー
- 家族のイベント・予定管理
- カテゴリ別の色分け表示
- 優先度設定（⭐⭐⭐）
- 参加者管理（家族メンバーごとの役割表示）
- リマインダー機能

### 👨‍👩‍👧‍👦 家族メンバー管理
- プロフィール登録・編集
- 役割別の絵文字表示（👨パパ、👩ママ、👧娘、👦息子など）
- 写真付きプロフィール
- 誕生日管理・年齢自動計算

### 📸 写真アルバム
- 家族写真の整理・管理
- アルバム別の分類
- タグ機能
- レスポンシブなフォトギャラリー

### 🏷️ カテゴリ管理
- イベントカテゴリの作成・編集
- カラーコード設定
- 絵文字アイコン

## 🚀 デプロイ方法（Render）

### 1. Renderでのデプロイ手順

1. [Render](https://render.com)にアカウント作成・ログイン
2. "New +" → "Web Service" を選択
3. GitHubリポジトリを接続: `https://github.com/such11nori/family-app`
4. 以下の設定を入力：

**基本設定:**
- Name: `family-app` (お好みの名前)
- Environment: `Python 3`
- Build Command: `./build.sh`
- Start Command: `gunicorn family_app.wsgi:application`

**環境変数（Environment Variables）:**
```bash
SECRET_KEY=your-super-secret-key-here
DJANGO_ENV=production
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@family-app.com
ADMIN_PASSWORD=YourSecurePassword123!
```

5. "Create Web Service" をクリック

### 2. 自動設定される内容

- PostgreSQLデータベース（自動作成）
- 静的ファイル配信（WhiteNoise）
- SSL証明書（自動）
- 自動マイグレーション
- スーパーユーザー自動作成

## 🛠️ ローカル開発環境

### 必要なソフトウェア
- Python 3.11+
- pip

### セットアップ手順

1. **リポジトリをクローン**
```bash
git clone https://github.com/such11nori/family-app.git
cd family-app
```

2. **仮想環境を作成・アクティベート**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# または
source .venv/bin/activate  # macOS/Linux
```

3. **依存関係をインストール**
```bash
pip install -r requirements.txt
```

4. **データベースをセットアップ**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **サンプルデータを作成（オプション）**
```bash
python manage.py create_sample_events
```

6. **開発サーバーを起動**
```bash
python manage.py runserver
```

7. **ブラウザでアクセス**
- アプリ: http://127.0.0.1:8000/
- 管理画面: http://127.0.0.1:8000/admin/

## 📁 プロジェクト構成

```
family-app/
├── family_app/          # Djangoプロジェクト設定
│   ├── settings.py      # 設定ファイル
│   ├── urls.py         # URLルーティング
│   └── wsgi.py         # WSGI設定
├── main/               # メインアプリケーション
│   ├── models.py       # データモデル
│   ├── views.py        # ビュー関数
│   ├── urls.py         # アプリのURL設定
│   ├── forms.py        # フォーム定義
│   ├── admin.py        # 管理画面設定
│   ├── templates/      # HTMLテンプレート
│   ├── templatetags/   # カスタムテンプレートタグ
│   └── utils/          # ユーティリティ関数
├── static/             # 静的ファイル
├── media/              # アップロードファイル
├── requirements.txt    # Python依存関係
├── build.sh           # Renderビルドスクリプト
└── create_superuser.py # スーパーユーザー作成スクリプト
```

## 🔧 技術スタック

- **フレームワーク**: Django 5.2.4
- **データベース**: SQLite（開発）/ PostgreSQL（本番）
- **スタイリング**: Bootstrap 5 + カスタムCSS
- **ファイル処理**: Pillow
- **本番サーバー**: Gunicorn
- **静的ファイル配信**: WhiteNoise
- **デプロイ**: Render

## 🎨 デザイン特徴

- 📱 レスポンシブデザイン（モバイル対応）
- 🌈 カラフルなカテゴリ表示
- 😊 絵文字を活用した直感的なUI
- 🎯 家族向けの温かみのあるデザイン
- ⚡ 高速な静的ファイル配信

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

プルリクエストやイシューの投稿を歓迎します！

## 📞 サポート

質問やバグレポートは[GitHub Issues](https://github.com/such11nori/family-app/issues)まで。

---

**家族の大切な思い出を、みんなで共有しましょう！** 💕
