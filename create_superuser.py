#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_app.settings')
django.setup()

from django.contrib.auth.models import User

# スーパーユーザーの情報
username = 'admin'
email = 'admin@family-app.com'
password = 'FamilyApp2025!'

# スーパーユーザーが存在しない場合のみ作成
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'スーパーユーザー "{username}" を作成しました。')
    print(f'ログイン情報:')
    print(f'ユーザー名: {username}')
    print(f'パスワード: {password}')
else:
    print(f'スーパーユーザー "{username}" は既に存在します。')
