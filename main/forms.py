from django import forms
from django.core.exceptions import ValidationError
from .models import FamilyMember, FamilyPhoto, PhotoTag, PhotoAlbum, EventCategory, FamilyEvent
from .utils.helpers import validate_image_size, is_image_file


class FamilyMemberForm(forms.ModelForm):
    """家族メンバーのフォーム"""
    
    class Meta:
        model = FamilyMember
        fields = [
            'name', 'role', 'birthday', 'photo', 
            'favorite_food', 'hobby', 'introduction', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名前を入力してください'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'favorite_food': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '好きな食べ物を入力してください'
            }),
            'hobby': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '趣味を入力してください'
            }),
            'introduction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '自己紹介やメッセージを入力してください'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_photo(self):
        """写真の検証"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # ファイルサイズの検証
            validate_image_size(photo)
            
            # ファイル形式の検証
            if not is_image_file(photo.name):
                raise ValidationError('画像ファイルをアップロードしてください。')
        
        return photo


class PhotoTagForm(forms.ModelForm):
    """写真タグのフォーム"""
    
    class Meta:
        model = PhotoTag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タグ名を入力してください',
                'maxlength': 50
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#3498db'
            }),
        }
    
    def clean_name(self):
        """タグ名の検証"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('タグ名は2文字以上で入力してください。')
        return name


class PhotoAlbumForm(forms.ModelForm):
    """写真アルバムのフォーム"""
    
    class Meta:
        model = PhotoAlbum
        fields = ['title', 'description', 'cover_photo', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'アルバム名を入力してください',
                'maxlength': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'アルバムの説明を入力してください（任意）'
            }),
            'cover_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_cover_photo(self):
        """カバー写真の検証"""
        cover_photo = self.cleaned_data.get('cover_photo')
        if cover_photo:
            # ファイルサイズの検証
            validate_image_size(cover_photo)
            
            # ファイル形式の検証
            if not is_image_file(cover_photo.name):
                raise ValidationError('画像ファイルをアップロードしてください。')
        
        return cover_photo


class FamilyPhotoForm(forms.ModelForm):
    """家族写真のフォーム"""
    
    class Meta:
        model = FamilyPhoto
        fields = [
            'title', 'image', 'description', 'taken_date', 'location',
            'family_members', 'tags', 'album', 'is_favorite', 'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '写真のタイトルを入力してください',
                'maxlength': 200
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '写真の説明やコメントを入力してください（任意）'
            }),
            'taken_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '撮影場所を入力してください（任意）',
                'maxlength': 200
            }),
            'family_members': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'album': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # アクティブな家族メンバーのみを選択肢に
        self.fields['family_members'].queryset = FamilyMember.get_active_members()
        
        # 公開されているアルバムのみを選択肢に
        self.fields['album'].queryset = PhotoAlbum.objects.filter(is_public=True)
        self.fields['album'].empty_label = "アルバムを選択してください（任意）"
        
        # タグは全て表示
        self.fields['tags'].queryset = PhotoTag.objects.all().order_by('name')
        
        # 必須フィールドのラベルに*を追加
        required_fields = ['title', 'image', 'taken_date']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].label += ' *'
    
    def clean_image(self):
        """画像の検証"""
        image = self.cleaned_data.get('image')
        if image:
            # ファイルサイズの検証（写真は10MBまで）
            max_size = 10 * 1024 * 1024  # 10MB
            if image.size > max_size:
                raise ValidationError('画像ファイルは10MB以下にしてください。')
            
            # ファイル形式の検証
            if not is_image_file(image.name):
                raise ValidationError('画像ファイルをアップロードしてください。')
        
        return image
    
    def clean_title(self):
        """タイトルの検証"""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 2:
                raise ValidationError('タイトルは2文字以上で入力してください。')
        return title


class PhotoSearchForm(forms.Form):
    """写真検索フォーム"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'タイトル、説明、場所で検索...',
        })
    )
    
    tag = forms.ModelChoiceField(
        queryset=PhotoTag.objects.all(),
        required=False,
        empty_label='すべてのタグ',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    member = forms.ModelChoiceField(
        queryset=FamilyMember.get_active_members(),
        required=False,
        empty_label='すべての家族',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    album = forms.ModelChoiceField(
        queryset=PhotoAlbum.objects.filter(is_public=True),
        required=False,
        empty_label='すべてのアルバム',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    year = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    favorite = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='お気に入りのみ'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 年の選択肢を動的に生成
        years = FamilyPhoto.objects.filter(is_public=True).dates('taken_date', 'year', order='DESC')
        year_choices = [('', 'すべての年')] + [(year.year, f'{year.year}年') for year in years]
        self.fields['year'].choices = year_choices


class EventCategoryForm(forms.ModelForm):
    """イベントカテゴリのフォーム"""
    
    class Meta:
        model = EventCategory
        fields = ['name', 'emoji', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'カテゴリ名を入力してください（例：誕生日、記念日）'
            }),
            'emoji': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '絵文字を入力してください（例：🎂、❤️）',
                'maxlength': '10'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'title': 'カテゴリの色を選択してください'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'カテゴリの説明を入力してください'
            }),
        }


class FamilyEventForm(forms.ModelForm):
    """家族イベントのフォーム"""
    
    class Meta:
        model = FamilyEvent
        fields = [
            'title', 'description', 'category', 'location',
            'start_date', 'end_date', 'start_time', 'end_time', 'is_all_day',
            'repeat', 'repeat_until', 'participants', 'priority',
            'is_reminder_enabled', 'reminder_minutes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'イベント名を入力してください',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'イベントの詳細を入力してください'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '場所を入力してください（例：自宅、公園、レストラン）'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_all_day': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'repeat': forms.Select(attrs={
                'class': 'form-control'
            }),
            'repeat_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'participants': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_reminder_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'reminder_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10080',  # 7日間
                'step': '15'
            }),
        }
    
    def clean(self):
        """フォーム全体のバリデーション"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_all_day = cleaned_data.get('is_all_day')
        repeat = cleaned_data.get('repeat')
        repeat_until = cleaned_data.get('repeat_until')
        
        # 終了日の検証
        if end_date and start_date and end_date < start_date:
            raise ValidationError('終了日は開始日以降である必要があります。')
        
        # 時刻の検証（同じ日の場合）
        if (start_time and end_time and 
            start_date and end_date and 
            start_date == end_date and 
            not is_all_day and 
            end_time <= start_time):
            raise ValidationError('終了時刻は開始時刻より後である必要があります。')
        
        # 繰り返し設定の検証
        if repeat != 'none' and repeat_until and repeat_until <= start_date:
            raise ValidationError('繰り返し終了日は開始日より後である必要があります。')
        
        return cleaned_data


class EventSearchForm(forms.Form):
    """イベント検索フォーム"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'イベント名、場所で検索...',
            'autocomplete': 'off'
        }),
        label='検索'
    )
    
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.all(),
        required=False,
        empty_label='すべてのカテゴリ',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='カテゴリ'
    )
    
    participants = forms.ModelChoiceField(
        queryset=FamilyMember.objects.filter(is_active=True),
        required=False,
        empty_label='すべての参加者',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='参加者'
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'すべての重要度')] + FamilyEvent.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='重要度'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='開始日'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='終了日'
    )
    
    upcoming_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='今後のイベントのみ'
    )
