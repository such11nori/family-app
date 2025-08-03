"""
Custom template tags for the main app.
"""

from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count
from ..models import FamilyMember, FamilyPhoto, PhotoTag, PhotoAlbum
from ..utils.helpers import get_role_emoji, format_date_japanese, calculate_age, truncate_text

register = template.Library()


@register.filter
def role_emoji(role):
    """続柄に対応する絵文字を取得するフィルタ"""
    return get_role_emoji(role)


@register.filter
def japanese_date(date_obj):
    """日付を日本語形式でフォーマットするフィルタ"""
    return format_date_japanese(date_obj)


@register.filter
def age_from_birthday(birthday):
    """誕生日から年齢を計算するフィルタ"""
    return calculate_age(birthday)


@register.filter
def truncate_chars(value, length):
    """文字列を指定した長さで切り詰めるフィルタ"""
    return truncate_text(value, int(length))


@register.inclusion_tag('main/components/member_card.html')
def member_card(member, show_detail_link=True, show_photos=False):
    """家族メンバーカードコンポーネント"""
    context = {
        'member': member,
        'show_detail_link': show_detail_link,
        'show_photos': show_photos,
        'role_emoji': get_role_emoji(member.role),
    }
    
    if show_photos:
        # メンバーの最新写真を取得
        recent_photos = FamilyPhoto.objects.filter(
            family_members=member,
            is_public=True
        ).order_by('-taken_date')[:3]
        context['recent_photos'] = recent_photos
    
    return context


@register.inclusion_tag('main/components/member_avatar.html')
def member_avatar(member, size='120px'):
    """家族メンバーのアバターコンポーネント"""
    return {
        'member': member,
        'size': size,
        'role_emoji': get_role_emoji(member.role),
    }


@register.inclusion_tag('main/components/photo_card.html')
def photo_card(photo, show_details=True, card_size='md'):
    """写真のカードコンポーネント"""
    return {
        'photo': photo,
        'show_details': show_details,
        'card_size': card_size,
        'formatted_date': format_date_japanese(photo.taken_date),
    }


@register.inclusion_tag('main/components/photo_grid.html')
def photo_grid(photos, columns=3):
    """写真のグリッドコンポーネント"""
    return {
        'photos': photos,
        'columns': columns,
        'grid_class': f'photo-grid-{columns}',
    }


@register.inclusion_tag('main/components/tag_list.html')
def tag_list(tags, show_count=False, max_tags=None):
    """タグリストコンポーネント"""
    if max_tags:
        tags = tags[:max_tags]
    
    tag_data = []
    for tag in tags:
        data = {'tag': tag}
        if show_count:
            data['count'] = tag.familyphoto_set.filter(is_public=True).count()
        tag_data.append(data)
    
    return {
        'tag_data': tag_data,
        'show_count': show_count,
    }


@register.inclusion_tag('main/components/album_card.html')
def album_card(album, show_cover=True):
    """アルバムのカードコンポーネント"""
    cover_photo = None
    if show_cover:
        # カバー写真があればそれを、なければ最新の写真を取得
        if album.cover_photo:
            cover_photo = album.cover_photo
        else:
            latest_photo = album.photos.filter(is_public=True).first()
            if latest_photo:
                cover_photo = latest_photo.image
    
    return {
        'album': album,
        'cover_photo': cover_photo,
        'photo_count': album.photo_count(),
        'show_cover': show_cover,
    }


@register.inclusion_tag('main/components/breadcrumb.html')
def breadcrumb(items):
    """パンくずリストコンポーネント"""
    return {'items': items}


@register.inclusion_tag('main/components/pagination.html')
def custom_pagination(page_obj, page_range=5):
    """カスタムページネーションコンポーネント"""
    if not page_obj:
        return {'page_obj': None}
    
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # 表示するページ番号の範囲を計算
    start_page = max(1, current_page - page_range // 2)
    end_page = min(total_pages, start_page + page_range - 1)
    
    # 範囲を調整
    if end_page - start_page + 1 < page_range:
        start_page = max(1, end_page - page_range + 1)
    
    return {
        'page_obj': page_obj,
        'page_range': range(start_page, end_page + 1),
        'show_first': start_page > 1,
        'show_last': end_page < total_pages,
    }


@register.simple_tag
def photo_stats():
    """写真の統計情報を取得するタグ"""
    return {
        'total_photos': FamilyPhoto.objects.filter(is_public=True).count(),
        'favorite_photos': FamilyPhoto.objects.filter(is_favorite=True, is_public=True).count(),
        'total_tags': PhotoTag.objects.count(),
        'total_albums': PhotoAlbum.objects.filter(is_public=True).count(),
    }


@register.simple_tag
def recent_photos(count=6):
    """最新の写真を取得するタグ"""
    return FamilyPhoto.objects.filter(is_public=True).select_related(
        'album'
    ).prefetch_related('tags', 'family_members').order_by('-taken_date')[:count]


@register.simple_tag
def favorite_photos(count=3):
    """お気に入りの写真を取得するタグ"""
    return FamilyPhoto.objects.filter(
        is_favorite=True, 
        is_public=True
    ).select_related('album').prefetch_related('tags', 'family_members').order_by('-taken_date')[:count]


@register.simple_tag
def popular_tags(count=10):
    """人気のタグを取得するタグ"""
    from django.db import models
    return PhotoTag.objects.annotate(
        photo_count=Count('familyphoto', filter=models.Q(familyphoto__is_public=True))
    ).filter(photo_count__gt=0).order_by('-photo_count')[:count]


@register.simple_tag
def app_version():
    """アプリのバージョンを取得"""
    from django.conf import settings
    return getattr(settings, 'FAMILY_APP_VERSION', '1.0.0')


@register.simple_tag
def app_name():
    """アプリの名前を取得"""
    from django.conf import settings
    return getattr(settings, 'FAMILY_APP_NAME', '家族アプリ')


@register.filter
def member_names(photo):
    """写真に写っている家族メンバーの名前を取得"""
    return ', '.join([member.name for member in photo.family_members.all()])


@register.filter
def tag_names(photo):
    """写真のタグ名を取得"""
    return ', '.join([tag.name for tag in photo.tags.all()])
