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
pip install django
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

## 📁 プロジェクト構造

```
family_pj/
├── .venv/                 # 仮想環境
├── family_app/            # プロジェクト設定
│   ├── settings.py        # Django設定
│   ├── urls.py           # メインURLルーティング
│   └── ...
├── main/                  # メインアプリ
│   ├── templates/         # HTMLテンプレート
│   │   └── main/
│   │       ├── base.html
│   │       ├── home.html
│   │       └── about.html
│   ├── views.py          # ビュー関数
│   ├── urls.py           # アプリURLルーティング
│   └── ...
├── manage.py             # Django管理コマンド
└── db.sqlite3           # SQLiteデータベース
```

## 🎯 現在の機能

- ✅ ホームページ表示
- ✅ アプリ情報ページ
- ✅ 管理画面アクセス
- ✅ レスポンシブデザイン

## 🔮 今後の拡張予定

- [ ] 家族メンバー登録機能
- [ ] イベントカレンダー
- [ ] 写真ギャラリー
- [ ] タスク管理機能
- [ ] ユーザー認証システム

## 🛠️ 技術スタック

- **フレームワーク**: Django 5.2.4
- **言語**: Python 3.13.5
- **データベース**: SQLite
- **フロントエンド**: HTML/CSS

## 📚 学習ポイント

このプロジェクトを通じて以下のDjangoの概念を学習できます：

1. **プロジェクトとアプリの構造**
2. **MVT（Model-View-Template）パターン**
3. **URLルーティング**
4. **テンプレートシステム**
5. **静的ファイルの管理**
6. **管理画面の活用**

## 📞 サポート

Django初心者の方は、以下のリソースを参考にしてください：

- [Django公式ドキュメント](https://docs.djangoproject.com/)
- [Django Girls チュートリアル](https://tutorial.djangogirls.org/)

---

**Happy Coding! 🎉**
