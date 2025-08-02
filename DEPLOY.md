# 🚀 Renderでのデプロイ手順

## 🌐 家族アプリをインターネットで公開しよう！

このガイドに従って、あなたの家族アプリをRenderで無料デプロイしましょう。

## 📋 事前準備

1. **GitHubアカウント** - [GitHub](https://github.com)でアカウントを作成
2. **Renderアカウント** - [Render](https://render.com)でアカウントを作成

## 🔧 ステップ1: GitHubリポジトリの作成

1. [GitHub](https://github.com)にログイン
2. 「New repository」をクリック
3. リポジトリ名を入力（例：`family-app`）
4. 「Public」を選択
5. 「Create repository」をクリック

## 📤 ステップ2: コードをGitHubにプッシュ

ローカルで以下のコマンドを実行：

```bash
git remote add origin https://github.com/YOUR_USERNAME/family-app.git
git branch -M main
git push -u origin main
```

（`YOUR_USERNAME`を実際のGitHubユーザー名に置き換えてください）

## 🚀 ステップ3: Renderでデプロイ

### 3.1 新しいWebサービスを作成

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. 「New +」→「Web Service」をクリック
3. GitHubリポジトリを接続
4. 作成したリポジトリを選択

### 3.2 デプロイ設定

以下の設定を入力：

| 項目 | 値 |
|------|-----|
| **Name** | `family-app`（お好みの名前） |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn family_app.wsgi:application` |

### 3.3 環境変数の設定

「Environment」セクションで以下を追加：

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.13.5` |

### 3.4 デプロイ実行

1. 「Create Web Service」をクリック
2. デプロイが完了するまで数分待機
3. 🎉 完了！URLが表示されます

## 🌍 ステップ4: アクセス確認

デプロイが完了すると、`https://your-app-name.onrender.com`のようなURLが表示されます。

このURLを家族に共有すれば、誰でもアクセスできます！

### 🔑 管理画面へのログイン

デプロイ後、以下の情報で管理画面にログインできます：

- **管理画面URL**: `https://your-app-name.onrender.com/admin/`
- **ユーザー名**: `admin`
- **パスワード**: `FamilyApp2025!`

⚠️ **セキュリティ注意**: 本番環境では必ずパスワードを変更してください！

## 📱 家族での使用方法

### 管理者設定

1. デプロイ完了後、`https://your-app.onrender.com/admin/`にアクセス
2. スーパーユーザーを作成（初回のみ）
3. 管理画面から各種設定を行う

### 家族メンバーのアクセス

1. URLを家族に共有
2. スマートフォンのブラウザでアクセス
3. ホーム画面をブックマークに追加

## 🔧 今後の拡張

アプリに新機能を追加したい場合：

1. ローカルで開発
2. Gitにコミット・プッシュ
3. Renderが自動的に再デプロイ

## 📞 サポート

何か困ったことがあれば：

- [Render Documentation](https://render.com/docs)
- [Django Documentation](https://docs.djangoproject.com/)

---

**🎉 おめでとうございます！あなたの家族アプリがインターネットで公開されました！**
