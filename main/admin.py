from django.contrib import admin
from django.utils.html import format_html
from .models import FamilyMember, FamilyPhoto, PhotoTag, PhotoAlbum, EventCategory, FamilyEvent
from .utils.helpers import get_role_emoji

# Register your models here.

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = [
        'name_with_emoji', 
        'role', 
        'birthday', 
        'age_display', 
        'is_active',
        'created_at'
    ]
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['name', 'favorite_food', 'hobby', 'introduction']
    date_hierarchy = 'created_at'
    list_editable = ['is_active']
    list_per_page = 20
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'role', 'birthday', 'photo', 'is_active')
        }),
        ('プロフィール', {
            'fields': ('favorite_food', 'hobby', 'introduction'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def name_with_emoji(self, obj):
        """名前と絵文字を表示"""
        emoji = get_role_emoji(obj.role)
        return format_html(
            '<span style="font-size: 1.2em;">{} {}</span>',
            emoji,
            obj.name
        )
    name_with_emoji.short_description = '名前'
    name_with_emoji.admin_order_field = 'name'
    
    def age_display(self, obj):
        """管理画面で年齢を表示"""
        age = obj.age()
        if age is not None:
            return format_html(
                '<span style="color: #666;">{} 歳</span>',
                age
            )
        return format_html(
            '<span style="color: #999;">未設定</span>'
        )
    age_display.short_description = '年齢'
    
    def get_form(self, request, obj=None, **kwargs):
        """フォームをカスタマイズ"""
        form = super().get_form(request, obj, **kwargs)
        
        # ヘルプテキストを追加
        if 'photo' in form.base_fields:
            form.base_fields['photo'].help_text = (
                '推奨サイズ: 正方形、5MB以下。'
                'アップロード後、自動的にリサイズされます。'
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        """保存時の処理"""
        if not change:
            # 新規作成時のログ
            self.message_user(
                request,
                f'家族メンバー「{obj.name}」が追加されました。'
            )
        else:
            # 更新時のログ
            self.message_user(
                request,
                f'家族メンバー「{obj.name}」が更新されました。'
            )
        
        super().save_model(request, obj, form, change)
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """選択されたメンバーをアクティブにする"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} 人のメンバーをアクティブにしました。'
        )
    make_active.short_description = '選択されたメンバーを表示する'
    
    def make_inactive(self, request, queryset):
        """選択されたメンバーを非アクティブにする"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} 人のメンバーを非表示にしました。'
        )
    make_inactive.short_description = '選択されたメンバーを非表示にする'


@admin.register(PhotoTag)
class PhotoTagAdmin(admin.ModelAdmin):
    """写真タグの管理画面"""
    
    list_display = ['name', 'color_preview', 'color', 'photo_count', 'created_at']
    list_editable = ['color']
    search_fields = ['name']
    ordering = ['name']
    
    def color_preview(self, obj):
        """色のプレビューを表示"""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span>',
            obj.color
        )
    color_preview.short_description = '色'
    
    def photo_count(self, obj):
        """このタグが使用されている写真の数"""
        count = obj.familyphoto_set.count()
        return f"{count}枚"
    photo_count.short_description = '使用枚数'


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    """写真アルバムの管理画面"""
    
    list_display = ['title', 'photo_count_display', 'is_public', 'created_by', 'created_at']
    list_filter = ['is_public', 'created_at', 'created_by']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'description', 'is_public')
        }),
        ('カバー写真', {
            'fields': ('cover_photo',),
            'classes': ('collapse',)
        }),
    )
    
    def photo_count_display(self, obj):
        """アルバム内の写真数を表示"""
        count = obj.photo_count()
        return f"{count}枚"
    photo_count_display.short_description = '写真数'
    
    def save_model(self, request, obj, form, change):
        """保存時にcreated_byを自動設定"""
        if not change:  # 新規作成時
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FamilyPhoto)
class FamilyPhotoAdmin(admin.ModelAdmin):
    """家族写真の管理画面"""
    
    list_display = [
        'title', 
        'image_preview', 
        'taken_date', 
        'family_members_display',
        'tags_display',
        'album',
        'is_favorite',
        'is_public',
        'created_at'
    ]
    list_filter = [
        'taken_date', 
        'is_favorite', 
        'is_public', 
        'album',
        'tags',
        'family_members',
        'created_at'
    ]
    search_fields = ['title', 'description', 'location']
    ordering = ['-taken_date', '-created_at']
    
    filter_horizontal = ['family_members', 'tags']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'image', 'taken_date', 'location')
        }),
        ('説明・コメント', {
            'fields': ('description',)
        }),
        ('関連情報', {
            'fields': ('family_members', 'tags', 'album')
        }),
        ('設定', {
            'fields': ('is_favorite', 'is_public'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_favorite', 'remove_favorite', 'make_public', 'make_private']
    
    def image_preview(self, obj):
        """画像のプレビューを表示"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; '
                'object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "画像なし"
    image_preview.short_description = 'プレビュー'
    
    def family_members_display(self, obj):
        """写っている家族メンバーを表示"""
        members = obj.family_members.all()
        if members:
            return ", ".join([f"{get_role_emoji(m.role)} {m.name}" for m in members])
        return "未設定"
    family_members_display.short_description = '家族メンバー'
    
    def tags_display(self, obj):
        """タグを色付きで表示"""
        tags = obj.tags.all()
        if tags:
            tag_html = []
            for tag in tags:
                tag_html.append(
                    f'<span style="background-color: {tag.color}; color: white; '
                    f'padding: 2px 6px; border-radius: 10px; font-size: 11px;">'
                    f'{tag.name}</span>'
                )
            return format_html(' '.join(tag_html))
        return "タグなし"
    tags_display.short_description = 'タグ'
    
    def make_favorite(self, request, queryset):
        """選択された写真をお気に入りにする"""
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated}枚の写真をお気に入りにしました。')
    make_favorite.short_description = '選択された写真をお気に入りにする'
    
    def remove_favorite(self, request, queryset):
        """選択された写真のお気に入りを解除する"""
        updated = queryset.update(is_favorite=False)
        self.message_user(request, f'{updated}枚の写真のお気に入りを解除しました。')
    remove_favorite.short_description = 'お気に入りを解除する'
    
    def make_public(self, request, queryset):
        """選択された写真を公開する"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated}枚の写真を公開しました。')
    make_public.short_description = '選択された写真を公開する'
    
    def make_private(self, request, queryset):
        """選択された写真を非公開にする"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated}枚の写真を非公開にしました。')
    make_private.short_description = '選択された写真を非公開にする'
    
    def save_model(self, request, obj, form, change):
        """保存時にuploaded_byを自動設定"""
        if not change:  # 新規作成時
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    """イベントカテゴリの管理画面"""
    
    list_display = ['name_with_emoji', 'color_preview', 'color', 'event_count', 'created_at']
    list_editable = ['color']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'emoji', 'description')
        }),
        ('表示設定', {
            'fields': ('color',)
        }),
    )
    
    def name_with_emoji(self, obj):
        """名前と絵文字を表示"""
        return format_html(
            '<span style="font-size: 1.2em;">{} {}</span>',
            obj.emoji,
            obj.name
        )
    name_with_emoji.short_description = 'カテゴリ'
    name_with_emoji.admin_order_field = 'name'
    
    def color_preview(self, obj):
        """色のプレビューを表示"""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span>',
            obj.color
        )
    color_preview.short_description = '色'
    
    def event_count(self, obj):
        """このカテゴリのイベント数"""
        count = obj.familyevent_set.count()
        return f"{count}件"
    event_count.short_description = 'イベント数'


@admin.register(FamilyEvent)
class FamilyEventAdmin(admin.ModelAdmin):
    """家族イベントの管理画面"""
    
    list_display = [
        'title_with_priority',
        'category_display',
        'start_date',
        'start_time',
        'duration_display',
        'participants_display',
        'priority',
        'is_reminder_enabled',
        'created_by'
    ]
    
    list_filter = [
        'start_date',
        'category',
        'priority',
        'repeat',
        'is_all_day',
        'is_reminder_enabled',
        'participants',
        'created_by',
        'created_at'
    ]
    
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'start_date'
    ordering = ['start_date', 'start_time']
    
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'description', 'category', 'location')
        }),
        ('日時設定', {
            'fields': (
                'start_date', 'end_date', 
                'start_time', 'end_time', 
                'is_all_day'
            )
        }),
        ('繰り返し設定', {
            'fields': ('repeat', 'repeat_until'),
            'classes': ('collapse',)
        }),
        ('参加者・設定', {
            'fields': ('participants', 'priority')
        }),
        ('リマインダー', {
            'fields': ('is_reminder_enabled', 'reminder_minutes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'enable_reminder', 
        'disable_reminder', 
        'set_high_priority', 
        'set_normal_priority'
    ]
    
    def title_with_priority(self, obj):
        """タイトルと重要度を表示"""
        color = obj.get_status_color()
        priority_emoji = obj.get_priority_emoji()
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            priority_emoji,
            obj.title
        )
    title_with_priority.short_description = 'イベント名'
    title_with_priority.admin_order_field = 'title'
    
    def category_display(self, obj):
        """カテゴリを絵文字付きで表示"""
        if obj.category:
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 2px 8px; border-radius: 12px; font-size: 11px;">'
                '{} {}</span>',
                obj.category.color,
                obj.category.emoji,
                obj.category.name
            )
        return "未設定"
    category_display.short_description = 'カテゴリ'
    
    def duration_display(self, obj):
        """期間を表示"""
        return obj.get_duration_display()
    duration_display.short_description = '期間'
    
    def participants_display(self, obj):
        """参加者を絵文字付きで表示"""
        participants = obj.participants.all()
        if participants:
            participant_html = []
            for p in participants:
                emoji = get_role_emoji(p.role)
                participant_html.append(f"{emoji} {p.name}")
            return format_html(' '.join(participant_html))
        return "全員"
    participants_display.short_description = '参加者'
    
    def enable_reminder(self, request, queryset):
        """選択されたイベントのリマインダーを有効にする"""
        updated = queryset.update(is_reminder_enabled=True)
        self.message_user(request, f'{updated}件のイベントのリマインダーを有効にしました。')
    enable_reminder.short_description = 'リマインダーを有効にする'
    
    def disable_reminder(self, request, queryset):
        """選択されたイベントのリマインダーを無効にする"""
        updated = queryset.update(is_reminder_enabled=False)
        self.message_user(request, f'{updated}件のイベントのリマインダーを無効にしました。')
    disable_reminder.short_description = 'リマインダーを無効にする'
    
    def set_high_priority(self, request, queryset):
        """選択されたイベントを高優先度に設定"""
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated}件のイベントを高優先度に設定しました。')
    set_high_priority.short_description = '高優先度に設定'
    
    def set_normal_priority(self, request, queryset):
        """選択されたイベントを通常優先度に設定"""
        updated = queryset.update(priority='normal')
        self.message_user(request, f'{updated}件のイベントを通常優先度に設定しました。')
    set_normal_priority.short_description = '通常優先度に設定'
    
    def save_model(self, request, obj, form, change):
        """保存時にcreated_byを自動設定"""
        if not change:  # 新規作成時
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """フォームをカスタマイズ"""
        form = super().get_form(request, obj, **kwargs)
        
        # ヘルプテキストを追加
        if 'reminder_minutes' in form.base_fields:
            form.base_fields['reminder_minutes'].help_text = (
                'イベント開始の何分前にリマインダーを表示するか'
            )
        
        return form


# Admin サイトのヘッダーをカスタマイズ
admin.site.site_header = '家族アプリ 管理画面'
admin.site.site_title = '家族アプリ Admin'
admin.site.index_title = '家族アプリ 管理'
