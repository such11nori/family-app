from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .utils.helpers import calculate_age, validate_image_size, resize_image
import os

# Create your models here.

class FamilyMember(models.Model):
    ROLE_CHOICES = [
        ('父', '父'),
        ('母', '母'),
        ('息子', '息子'),
        ('娘', '娘'),
        ('おじいちゃん', 'おじいちゃん'),
        ('おばあちゃん', 'おばあちゃん'),
        ('その他', 'その他'),
    ]
    
    name = models.CharField('名前', max_length=100)
    role = models.CharField('続柄', max_length=20, choices=ROLE_CHOICES)
    birthday = models.DateField('誕生日', null=True, blank=True)
    photo = models.ImageField(
        '写真', 
        upload_to='family_photos/', 
        null=True, 
        blank=True,
        help_text='推奨サイズ: 正方形、5MB以下'
    )
    favorite_food = models.CharField('好きな食べ物', max_length=200, blank=True)
    hobby = models.CharField('趣味', max_length=200, blank=True)
    introduction = models.TextField(
        '自己紹介', 
        blank=True, 
        help_text='家族への一言やメッセージを書いてください'
    )
    is_active = models.BooleanField('表示する', default=True, help_text='チェックを外すと一覧に表示されません')
    created_at = models.DateTimeField('登録日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    
    class Meta:
        verbose_name = '家族メンバー'
        verbose_name_plural = '家族メンバー'
        ordering = ['role', 'name']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def get_absolute_url(self):
        return reverse('family_detail', kwargs={'pk': self.pk})
    
    def age(self):
        """年齢を計算"""
        return calculate_age(self.birthday)
    
    def clean(self):
        """モデルの検証"""
        super().clean()
        
        # 画像ファイルサイズの検証
        if self.photo:
            validate_image_size(self.photo)
    
    def save(self, *args, **kwargs):
        """保存時の処理"""
        # バリデーション実行
        self.full_clean()
        
        # 既存の画像ファイルがある場合は削除
        if self.pk:
            try:
                old_instance = FamilyMember.objects.get(pk=self.pk)
                if old_instance.photo and old_instance.photo != self.photo:
                    if os.path.isfile(old_instance.photo.path):
                        os.remove(old_instance.photo.path)
            except FamilyMember.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # 画像をリサイズ
        if self.photo and os.path.isfile(self.photo.path):
            resize_image(self.photo.path)
    
    def delete(self, *args, **kwargs):
        """削除時の処理"""
        # 画像ファイルも削除
        if self.photo and os.path.isfile(self.photo.path):
            os.remove(self.photo.path)
        
        super().delete(*args, **kwargs)
    
    @property
    def display_name(self):
        """表示用の名前（続柄付き）"""
        return f"{self.name} ({self.role})"
    
    @classmethod
    def get_active_members(cls):
        """アクティブなメンバーのみを取得"""
        return cls.objects.filter(is_active=True)


class PhotoTag(models.Model):
    """写真のタグ"""
    name = models.CharField('タグ名', max_length=50, unique=True)
    color = models.CharField(
        '色', 
        max_length=7, 
        default='#3498db',
        help_text='HEXカラーコード（例: #3498db）'
    )
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    
    class Meta:
        verbose_name = '写真タグ'
        verbose_name_plural = '写真タグ'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PhotoAlbum(models.Model):
    """写真アルバム"""
    title = models.CharField('アルバム名', max_length=100)
    description = models.TextField('説明', blank=True)
    cover_photo = models.ImageField(
        'カバー写真', 
        upload_to='album_covers/', 
        null=True, 
        blank=True
    )
    is_public = models.BooleanField('公開する', default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='作成者',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    
    class Meta:
        verbose_name = '写真アルバム'
        verbose_name_plural = '写真アルバム'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'pk': self.pk})
    
    def photo_count(self):
        """アルバム内の写真数"""
        return self.photos.count()


class FamilyPhoto(models.Model):
    """家族の写真"""
    title = models.CharField('タイトル', max_length=200)
    image = models.ImageField(
        '写真', 
        upload_to='gallery/%Y/%m/',
        help_text='推奨サイズ: 10MB以下'
    )
    description = models.TextField('説明・コメント', blank=True)
    taken_date = models.DateField(
        '撮影日', 
        help_text='写真が撮影された日付'
    )
    location = models.CharField('撮影場所', max_length=200, blank=True)
    
    # 関連するメンバー（多対多関係）
    family_members = models.ManyToManyField(
        FamilyMember,
        verbose_name='写っている家族',
        blank=True,
        help_text='写真に写っている家族メンバーを選択してください'
    )
    
    # タグ（多対多関係）
    tags = models.ManyToManyField(
        PhotoTag,
        verbose_name='タグ',
        blank=True,
        help_text='写真に関連するタグを選択してください'
    )
    
    # アルバム（外部キー）
    album = models.ForeignKey(
        PhotoAlbum,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='アルバム',
        related_name='photos'
    )
    
    # メタデータ
    is_favorite = models.BooleanField('お気に入り', default=False)
    is_public = models.BooleanField('公開する', default=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='アップロード者',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField('アップロード日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    
    class Meta:
        verbose_name = '家族写真'
        verbose_name_plural = '家族写真'
        ordering = ['-taken_date', '-created_at']
        indexes = [
            models.Index(fields=['taken_date']),
            models.Index(fields=['is_favorite']),
            models.Index(fields=['is_public']),
            models.Index(fields=['album']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.taken_date})"
    
    def get_absolute_url(self):
        return reverse('photo_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        """モデルの検証"""
        super().clean()
        
        # 画像ファイルサイズの検証
        if self.image:
            max_size = 10 * 1024 * 1024  # 10MB
            if self.image.size > max_size:
                raise ValidationError('画像ファイルは10MB以下にしてください。')
    
    def save(self, *args, **kwargs):
        """保存時の処理"""
        # バリデーション実行
        self.full_clean()
        
        # 既存の画像ファイルがある場合は削除
        if self.pk:
            try:
                old_instance = FamilyPhoto.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except FamilyPhoto.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # 画像をリサイズ（ギャラリー用は大きめに保持）
        if self.image and os.path.isfile(self.image.path):
            resize_image(self.image.path, max_size=(1920, 1920))
    
    def delete(self, *args, **kwargs):
        """削除時の処理"""
        # 画像ファイルも削除
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        
        super().delete(*args, **kwargs)
    
    def get_family_members_names(self):
        """写っている家族メンバーの名前を取得"""
        return ', '.join([member.name for member in self.family_members.all()])
    
    def get_tags_names(self):
        """タグ名のリストを取得"""
        return list(self.tags.values_list('name', flat=True))


class EventCategory(models.Model):
    """イベントカテゴリ"""
    name = models.CharField('カテゴリ名', max_length=50, unique=True)
    emoji = models.CharField('絵文字', max_length=10, default='📅')
    color = models.CharField('色', max_length=7, default='#3498db')
    description = models.TextField('説明', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    
    class Meta:
        verbose_name = 'イベントカテゴリ'
        verbose_name_plural = 'イベントカテゴリ'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.emoji} {self.name}"


class FamilyEvent(models.Model):
    """家族のイベント"""
    
    REPEAT_CHOICES = [
        ('none', '繰り返しなし'),
        ('daily', '毎日'),
        ('weekly', '毎週'),
        ('monthly', '毎月'),
        ('yearly', '毎年'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('normal', '普通'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]
    
    title = models.CharField('イベント名', max_length=200)
    description = models.TextField('詳細', blank=True)
    
    # 日時関連
    start_date = models.DateField('開始日')
    end_date = models.DateField('終了日', null=True, blank=True)
    start_time = models.TimeField('開始時刻', null=True, blank=True)
    end_time = models.TimeField('終了時刻', null=True, blank=True)
    is_all_day = models.BooleanField('終日', default=False)
    
    # 繰り返し設定
    repeat = models.CharField('繰り返し', max_length=10, choices=REPEAT_CHOICES, default='none')
    repeat_until = models.DateField('繰り返し終了日', null=True, blank=True)
    
    # 関連情報
    category = models.ForeignKey(
        EventCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='カテゴリ'
    )
    participants = models.ManyToManyField(
        FamilyMember, 
        blank=True,
        verbose_name='参加者'
    )
    location = models.CharField('場所', max_length=200, blank=True)
    
    # 設定
    priority = models.CharField('重要度', max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_reminder_enabled = models.BooleanField('リマインダー', default=True)
    reminder_minutes = models.IntegerField('リマインダー時間（分前）', default=60)
    
    # メタ情報
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='作成者'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        verbose_name = '家族イベント'
        verbose_name_plural = '家族イベント'
        ordering = ['start_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_date})"
    
    def get_duration_display(self):
        """期間の表示用文字列"""
        if self.is_all_day:
            if self.end_date and self.end_date != self.start_date:
                return f"{self.start_date} ～ {self.end_date} (終日)"
            else:
                return f"{self.start_date} (終日)"
        else:
            date_str = str(self.start_date)
            if self.start_time:
                date_str += f" {self.start_time.strftime('%H:%M')}"
            if self.end_time:
                date_str += f" ～ {self.end_time.strftime('%H:%M')}"
            return date_str
    
    def get_participants_display(self):
        """参加者の表示用文字列"""
        participants = self.participants.all()
        if participants:
            return ', '.join([p.name for p in participants])
        return '全員'
    
    def is_today(self):
        """今日のイベントかどうか"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date == today
    
    def is_upcoming(self):
        """今後のイベントかどうか"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date >= today
    
    def get_priority_emoji(self):
        """重要度の絵文字"""
        priority_emojis = {
            'low': '⭐',
            'normal': '⭐⭐',
            'high': '⭐⭐⭐',
            'urgent': '🚨',
        }
        return priority_emojis.get(self.priority, '⭐⭐')
    
    def get_status_color(self):
        """ステータスに応じた色"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.start_date < today:
            return '#95a5a6'  # 過去のイベント（グレー）
        elif self.start_date == today:
            return '#e74c3c'  # 今日のイベント（赤）
        else:
            priority_colors = {
                'low': '#3498db',      # 青
                'normal': '#2ecc71',   # 緑
                'high': '#f39c12',     # オレンジ
                'urgent': '#e74c3c',   # 赤
            }
            return priority_colors.get(self.priority, '#2ecc71')
