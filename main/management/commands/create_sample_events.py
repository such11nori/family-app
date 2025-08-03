from django.core.management.base import BaseCommand
from main.models import EventCategory, FamilyEvent, FamilyMember
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'イベント管理のサンプルデータを作成します'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('イベントのサンプルデータを作成中...'))
        
        # サンプルカテゴリの作成
        categories_data = [
            {'name': '誕生日', 'emoji': '🎂', 'color': '#e74c3c', 'description': '家族の誕生日をお祝いしましょう'},
            {'name': '記念日', 'emoji': '❤️', 'color': '#e91e63', 'description': '結婚記念日など大切な記念日'},
            {'name': '旅行', 'emoji': '✈️', 'color': '#3498db', 'description': '家族旅行や外出の予定'},
            {'name': '学校行事', 'emoji': '🏫', 'color': '#f39c12', 'description': '学校のイベントや行事'},
            {'name': '医療', 'emoji': '🏥', 'color': '#2ecc71', 'description': '病院の予約や健康診断'},
            {'name': '習い事', 'emoji': '📚', 'color': '#9b59b6', 'description': '習い事やレッスンの予定'},
            {'name': '家族会議', 'emoji': '👨‍👩‍👧‍👦', 'color': '#34495e', 'description': '家族で話し合いをする時間'},
            {'name': 'お買い物', 'emoji': '🛒', 'color': '#16a085', 'description': '家族でのお買い物'},
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category, created = EventCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'emoji': cat_data['emoji'],
                    'color': cat_data['color'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'  カテゴリ作成: {category.emoji} {category.name}')
            else:
                self.stdout.write(f'  カテゴリ存在: {category.emoji} {category.name}')
            created_categories.append(category)
        
        # スーパーユーザーを取得（作成者として使用）
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.WARNING('スーパーユーザーが見つかりません。まずスーパーユーザーを作成してください。'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ユーザー取得エラー: {e}'))
            return
        
        # 家族メンバーを取得
        family_members = list(FamilyMember.objects.filter(is_active=True))
        
        # サンプルイベントの作成
        today = timezone.now().date()
        sample_events = [
            {
                'title': 'パパの誕生日',
                'description': 'パパの誕生日をみんなでお祝いしましょう！ケーキと プレゼントの準備をお忘れなく。',
                'start_date': today + timedelta(days=7),
                'category': '誕生日',
                'priority': 'high',
                'location': '自宅',
                'is_all_day': True,
            },
            {
                'title': '家族旅行（温泉）',
                'description': '年に一度の家族旅行です。みんなでリフレッシュしましょう！',
                'start_date': today + timedelta(days=30),
                'end_date': today + timedelta(days=32),
                'category': '旅行',
                'priority': 'high',
                'location': '箱根温泉',
                'is_all_day': True,
            },
            {
                'title': '歯医者の定期検診',
                'description': '6ヶ月に一度の定期検診です。',
                'start_date': today + timedelta(days=14),
                'start_time': datetime.strptime('14:00', '%H:%M').time(),
                'end_time': datetime.strptime('15:00', '%H:%M').time(),
                'category': '医療',
                'priority': 'normal',
                'location': '田中歯科クリニック',
            },
            {
                'title': 'ピアノの発表会',
                'description': '1年間の練習の成果を発表する大切な日です。みんなで応援しましょう！',
                'start_date': today + timedelta(days=21),
                'start_time': datetime.strptime('15:00', '%H:%M').time(),
                'end_time': datetime.strptime('17:00', '%H:%M').time(),
                'category': '習い事',
                'priority': 'high',
                'location': '音楽ホール',
            },
            {
                'title': '家族会議',
                'description': '今月の家計と来月の予定について話し合いましょう。',
                'start_date': today + timedelta(days=3),
                'start_time': datetime.strptime('20:00', '%H:%M').time(),
                'end_time': datetime.strptime('21:00', '%H:%M').time(),
                'category': '家族会議',
                'priority': 'normal',
                'location': '自宅リビング',
            },
            {
                'title': '運動会',
                'description': '子供たちの運動会です。お弁当とカメラをお忘れなく！',
                'start_date': today + timedelta(days=45),
                'start_time': datetime.strptime('09:00', '%H:%M').time(),
                'end_time': datetime.strptime('15:00', '%H:%M').time(),
                'category': '学校行事',
                'priority': 'high',
                'location': '小学校グラウンド',
            },
            {
                'title': '結婚記念日',
                'description': '大切な結婚記念日です。特別なディナーを予約しました。',
                'start_date': today + timedelta(days=60),
                'start_time': datetime.strptime('18:00', '%H:%M').time(),
                'end_time': datetime.strptime('21:00', '%H:%M').time(),
                'category': '記念日',
                'priority': 'high',
                'location': 'レストラン・ローズ',
            },
        ]
        
        for event_data in sample_events:
            # カテゴリを取得
            category = None
            if event_data.get('category'):
                category = EventCategory.objects.filter(name=event_data['category']).first()
            
            # イベントが既に存在するかチェック
            existing_event = FamilyEvent.objects.filter(
                title=event_data['title'],
                start_date=event_data['start_date']
            ).first()
            
            if not existing_event:
                event = FamilyEvent.objects.create(
                    title=event_data['title'],
                    description=event_data.get('description', ''),
                    start_date=event_data['start_date'],
                    end_date=event_data.get('end_date'),
                    start_time=event_data.get('start_time'),
                    end_time=event_data.get('end_time'),
                    is_all_day=event_data.get('is_all_day', False),
                    category=category,
                    location=event_data.get('location', ''),
                    priority=event_data.get('priority', 'normal'),
                    created_by=user,
                )
                
                # ランダムに家族メンバーを参加者として追加
                if family_members:
                    # 1-3人のランダムな参加者を選択
                    num_participants = random.randint(1, min(3, len(family_members)))
                    participants = random.sample(family_members, num_participants)
                    event.participants.set(participants)
                
                self.stdout.write(f'  イベント作成: {event.title} ({event.start_date})')
            else:
                self.stdout.write(f'  イベント存在: {event_data["title"]} ({event_data["start_date"]})')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ サンプルデータの作成が完了しました！\n'
                f'📅 カテゴリ: {len(created_categories)}個\n'
                f'🎉 イベント: {len(sample_events)}個\n\n'
                f'管理画面（/admin/）でデータを確認できます。'
            )
        )
