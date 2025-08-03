# 🏠 家族アプリ - Django初心者プロジェクト

Django初心者向けの家族管理Webアプリケーションです。

## 📋 プロジェクト概要

このプロジェクトは、Djangoの基本的な概念を学習するために作成された家族向けの管理システムです。

## 🚀 セットアップ方法

### 1. 仮想環境の有効化
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. データベースマイグレーション
```bash
python manage.py migrate
```

### 4. スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

### 5. 開発サーバーの起動
```bash
python manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` にアクセスしてください。

## 📁 プロジェクト構造（リファクタリング後）

```
family_pj/
├── .venv/                      # 仮想環境
├── family_app/                 # プロジェクト設定
│   ├── settings/               # 環境別設定
│   │   ├── __init__.py        # 自動環境判定
│   │   ├── base.py            # 共通設定
│   │   ├── development.py     # 開発環境設定
│   │   └── production.py      # 本番環境設定
│   ├── urls.py                # メインURLルーティング
│   └── ...
├── main/                       # メインアプリ
│   ├── templates/             # HTMLテンプレート
│   │   └── main/
│   │       ├── components/    # 再利用可能コンポーネント
│   │       │   ├── member_card.html
│   │       │   └── member_avatar.html
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── family_list.html
│   │       ├── family_detail.html
│   │       └── about.html
│   ├── templatetags/          # カスタムテンプレートタグ
│   │   └── family_tags.py
│   ├── utils/                 # ユーティリティ関数
│   │   └── helpers.py
│   ├── migrations/            # データベースマイグレーション
│   ├── models.py             # データモデル（改良版）
│   ├── views.py              # ビュー関数（エラーハンドリング強化）
│   ├── admin.py              # 管理画面（改良版）
│   └── urls.py               # アプリURLルーティング
├── static/                    # 静的ファイル
├── media/                     # アップロードファイル
├── manage.py                 # Django管理コマンド
├── requirements.txt          # 依存関係（改良版）
├── build.sh                  # デプロイスクリプト（改良版）
└── create_superuser.py       # 本番環境用スーパーユーザー作成
```

## 🎯 現在の機能

### ✅ 基本機能
- **家族メンバー管理**: 名前、続柄、誕生日、写真、プロフィール
- **自動年齢計算**: 誕生日から現在の年齢を自動計算
- **画像アップロード**: プロフィール写真（自動リサイズ機能付き）
- **レスポンシブデザイン**: スマートフォン・タブレット対応
- **検索・フィルター機能**: 名前や趣味での検索、続柄でのフィルター

### ✅ 管理機能
- **管理画面**: Django標準管理画面をカスタマイズ
- **バルクアクション**: 複数メンバーの一括操作
- **データ検証**: 画像サイズ制限、入力値検証
- **ログ機能**: 操作履歴の記録

### ✅ 技術的改良
- **環境別設定**: 開発/本番環境の設定分離
- **エラーハンドリング**: 堅牢なエラー処理
- **コンポーネント化**: 再利用可能なテンプレートコンポーネント
- **ユーティリティ関数**: 共通処理の分離
- **データベース最適化**: インデックス設定、クエリ最適化

## 🔮 今後の拡張予定

- [ ] イベントカレンダー機能
- [ ] 写真ギャラリー機能
- [ ] タスク管理機能
- [ ] 通知機能
- [ ] モバイルアプリ対応
- [ ] API機能

## 🛠️ 技術スタック

- **フレームワーク**: Django 5.2.4
- **言語**: Python 3.13.5
- **データベース**: SQLite (開発), PostgreSQL対応 (本番)
- **画像処理**: Pillow
- **フロントエンド**: HTML/CSS/JavaScript
- **デプロイ**: Render

## 📚 学習ポイント

このプロジェクトを通じて以下のDjangoの概念を学習できます：

### 🎓 基礎概念
1. **プロジェクトとアプリの構造**
2. **MVT（Model-View-Template）パターン**
3. **URLルーティング**
4. **テンプレートシステム**
5. **静的ファイルとメディアファイルの管理**

### 🎓 応用概念
6. **カスタム管理画面**
7. **データベースマイグレーション**
8. **カスタムテンプレートタグ・フィルタ**
9. **ファイルアップロード処理**
10. **エラーハンドリング**

### 🎓 実践的技術
11. **環境別設定管理**
12. **テストの書き方**
13. **セキュリティ対策**
14. **パフォーマンス最適化**
15. **デプロイメント**

## 🧪 テスト

```bash
# テストの実行
python manage.py test

# カバレッジレポート付きテスト
coverage run --source='.' manage.py test
coverage report
```

## 🔒 セキュリティ

### 開発環境
- DEBUG = True
- 緩いセキュリティ設定

### 本番環境
- DEBUG = False
- HTTPS強制
- セキュリティヘッダー設定
- 画像ファイル検証

## 📞 サポート

Django初心者の方は、以下のリソースを参考にしてください：

- [Django公式ドキュメント](https://docs.djangoproject.com/)
- [Django Girls チュートリアル](https://tutorial.djangogirls.org/)
- [Python.org](https://www.python.org/)

## 🤝 コントリビューション

1. Fork this repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**Happy Coding! 🎉**

*家族の絆を深める、デジタルな家族の居場所*
