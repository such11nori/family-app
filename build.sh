#!/usr/bin/env bash
# exit on error
set -o errexit

# 本番環境の設定
export DJANGO_ENV=production

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# 本番環境用スーパーユーザーを作成
echo "スーパーユーザーを作成中..."
python create_superuser.py
