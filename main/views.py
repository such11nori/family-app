from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta
from .models import FamilyMember, FamilyPhoto, PhotoTag, PhotoAlbum, EventCategory, FamilyEvent
from .forms import (
    FamilyMemberForm, FamilyPhotoForm, PhotoTagForm, PhotoAlbumForm,
    EventCategoryForm, FamilyEventForm, EventSearchForm
)
from .utils.helpers import get_role_emoji
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    """ホームページ"""
    try:
        # 最近追加された家族メンバーを取得（最大3人）
        recent_members = FamilyMember.get_active_members()[:3]
        
        # 最新の写真を取得（公開されているもの）
        recent_photos = FamilyPhoto.objects.filter(
            is_public=True
        ).select_related('album').prefetch_related('tags', 'family_members')[:6]
        
        # お気に入りの写真を取得
        favorite_photos = FamilyPhoto.objects.filter(
            is_favorite=True,
            is_public=True
        ).select_related('album').prefetch_related('tags', 'family_members')[:3]
        
        # 今後のイベントを取得
        today = timezone.now().date()
        upcoming_events = FamilyEvent.objects.filter(
            start_date__gte=today
        ).select_related('category').prefetch_related('participants')[:5]
        
        # 統計情報
        stats = {
            'total_members': FamilyMember.get_active_members().count(),
            'total_photos': FamilyPhoto.objects.filter(is_public=True).count(),
            'total_albums': PhotoAlbum.objects.filter(is_public=True).count(),
            'total_tags': PhotoTag.objects.count(),
            'total_events': FamilyEvent.objects.count(),
            'upcoming_events': FamilyEvent.objects.filter(start_date__gte=today).count(),
        }
        
        context = {
            'recent_members': recent_members,
            'recent_photos': recent_photos,
            'favorite_photos': favorite_photos,
            'upcoming_events': upcoming_events,
            'stats': stats,
        }
        return render(request, 'main/home.html', context)
    
    except Exception as e:
        logger.error(f"ホームページでエラーが発生しました: {e}")
        messages.error(request, '申し訳ございません。エラーが発生しました。')
        return render(request, 'main/home.html', {})


def about(request):
    """このアプリについて"""
    return render(request, 'main/about.html')


def family_list(request):
    """家族一覧ページ"""
    try:
        # 検索クエリの処理
        search_query = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        
        # 基本クエリ（アクティブなメンバーのみ）
        queryset = FamilyMember.get_active_members()
        
        # 検索フィルタ
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(favorite_food__icontains=search_query) |
                Q(hobby__icontains=search_query) |
                Q(introduction__icontains=search_query)
            )
        
        # 続柄フィルタ
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        # ページネーション
        paginator = Paginator(queryset, 6)  # 1ページあたり6人
        page = request.GET.get('page')
        
        try:
            family_members = paginator.page(page)
        except PageNotAnInteger:
            family_members = paginator.page(1)
        except EmptyPage:
            family_members = paginator.page(paginator.num_pages)
        
        # 続柄の選択肢を取得
        role_choices = FamilyMember.ROLE_CHOICES
        
        context = {
            'family_members': family_members,
            'search_query': search_query,
            'role_filter': role_filter,
            'role_choices': role_choices,
            'get_role_emoji': get_role_emoji,
        }
        
        return render(request, 'main/family_list.html', context)
    
    except Exception as e:
        logger.error(f"家族一覧ページでエラーが発生しました: {e}")
        messages.error(request, '家族一覧の取得中にエラーが発生しました。')
        return render(request, 'main/family_list.html', {'family_members': []})


def family_detail(request, pk):
    """家族メンバー詳細ページ"""
    try:
        member = get_object_or_404(FamilyMember, pk=pk, is_active=True)
        
        # このメンバーが写っている写真を取得
        member_photos = FamilyPhoto.objects.filter(
            family_members=member,
            is_public=True
        ).select_related('album').prefetch_related('tags').order_by('-taken_date')[:10]
        
        context = {
            'member': member,
            'role_emoji': get_role_emoji(member.role),
            'member_photos': member_photos,
        }
        
        return render(request, 'main/family_detail.html', context)
    
    except Http404:
        messages.error(request, '指定された家族メンバーが見つかりません。')
        return render(request, 'main/family_list.html', {'family_members': []})
    
    except Exception as e:
        logger.error(f"家族詳細ページでエラーが発生しました: {e}")
        messages.error(request, '家族詳細の取得中にエラーが発生しました。')
        return render(request, 'main/family_list.html', {'family_members': []})


# ========== フォトギャラリー関連ビュー ==========

def photo_gallery(request):
    """フォトギャラリー一覧ページ"""
    try:
        # 基本のクエリセット
        photos = FamilyPhoto.objects.filter(is_public=True).select_related(
            'album'
        ).prefetch_related('tags', 'family_members').order_by('-taken_date')
        
        # フィルタリング
        search_query = request.GET.get('search', '')
        tag_filter = request.GET.get('tag', '')
        member_filter = request.GET.get('member', '')
        album_filter = request.GET.get('album', '')
        year_filter = request.GET.get('year', '')
        favorite_only = request.GET.get('favorite', '')
        
        if search_query:
            photos = photos.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        if tag_filter:
            photos = photos.filter(tags__id=tag_filter)
        
        if member_filter:
            photos = photos.filter(family_members__id=member_filter)
        
        if album_filter:
            photos = photos.filter(album__id=album_filter)
        
        if year_filter:
            photos = photos.filter(taken_date__year=year_filter)
        
        if favorite_only:
            photos = photos.filter(is_favorite=True)
        
        # ページネーション
        paginator = Paginator(photos, 12)  # 1ページに12枚
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # フィルター用のデータ
        filter_data = {
            'tags': PhotoTag.objects.all().order_by('name'),
            'members': FamilyMember.get_active_members().order_by('name'),
            'albums': PhotoAlbum.objects.filter(is_public=True).order_by('title'),
            'years': FamilyPhoto.objects.filter(is_public=True).dates('taken_date', 'year', order='DESC'),
        }
        
        context = {
            'page_obj': page_obj,
            'filter_data': filter_data,
            'search_query': search_query,
            'current_filters': {
                'tag': tag_filter,
                'member': member_filter,
                'album': album_filter,
                'year': year_filter,
                'favorite': favorite_only,
            }
        }
        
        return render(request, 'main/photo_gallery.html', context)
        
    except Exception as e:
        logger.error(f"フォトギャラリーの表示でエラーが発生しました: {e}")
        messages.error(request, 'フォトギャラリーの読み込み中にエラーが発生しました。')
        return render(request, 'main/photo_gallery.html', {'page_obj': None})


def photo_detail(request, pk):
    """写真詳細ページ"""
    try:
        photo = get_object_or_404(
            FamilyPhoto.objects.filter(is_public=True).select_related(
                'album'
            ).prefetch_related('tags', 'family_members'),
            pk=pk
        )
        
        # 関連写真（同じアルバムまたは同じタグの写真）
        related_photos = FamilyPhoto.objects.filter(
            Q(album=photo.album) | Q(tags__in=photo.tags.all()),
            is_public=True
        ).exclude(id=photo.id).distinct().select_related('album')[:6]
        
        context = {
            'photo': photo,
            'related_photos': related_photos,
        }
        
        return render(request, 'main/photo_detail.html', context)
    
    except Http404:
        messages.error(request, '指定された写真が見つかりません。')
        return redirect('photo_gallery')
    
    except Exception as e:
        logger.error(f"写真詳細ページでエラーが発生しました: {e}")
        messages.error(request, '写真詳細の取得中にエラーが発生しました。')
        return redirect('photo_gallery')


# ========== アルバム関連ビュー ==========

def album_list(request):
    """アルバム一覧ページ"""
    try:
        albums = PhotoAlbum.objects.filter(is_public=True).annotate(
            photo_count=Count('photos')
        ).select_related('created_by').order_by('-created_at')
        
        # 検索機能
        search_query = request.GET.get('search', '')
        if search_query:
            albums = albums.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        context = {
            'albums': albums,
            'search_query': search_query,
        }
        
        return render(request, 'main/album_list.html', context)
        
    except Exception as e:
        logger.error(f"アルバム一覧の表示でエラーが発生しました: {e}")
        messages.error(request, 'アルバム一覧の読み込み中にエラーが発生しました。')
        return render(request, 'main/album_list.html', {'albums': []})


def album_detail(request, pk):
    """アルバム詳細ページ"""
    try:
        album = get_object_or_404(
            PhotoAlbum.objects.filter(is_public=True).select_related('created_by'),
            pk=pk
        )
        
        # アルバム内の写真を取得
        photos = album.photos.filter(is_public=True).select_related(
            'album'
        ).prefetch_related('tags', 'family_members').order_by('-taken_date')
        
        # ページネーション
        paginator = Paginator(photos, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'album': album,
            'page_obj': page_obj,
        }
        
        return render(request, 'main/album_detail.html', context)
    
    except Http404:
        messages.error(request, '指定されたアルバムが見つかりません。')
        return redirect('album_list')
    
    except Exception as e:
        logger.error(f"アルバム詳細ページでエラーが発生しました: {e}")
        messages.error(request, 'アルバム詳細の取得中にエラーが発生しました。')
        return redirect('album_list')


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, photo_id):
    """写真のお気に入り状態を切り替える（Ajax用）"""
    try:
        photo = get_object_or_404(FamilyPhoto, id=photo_id)
        photo.is_favorite = not photo.is_favorite
        photo.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': photo.is_favorite,
            'message': 'お気に入りに追加しました' if photo.is_favorite else 'お気に入りから削除しました'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'エラーが発生しました: {str(e)}'
        })


# ========================================
# イベント管理ビュー
# ========================================

def event_calendar(request):
    """イベントカレンダー"""
    try:
        # 検索フォーム
        search_form = EventSearchForm(request.GET or None)
        
        # イベント一覧のクエリ
        events = FamilyEvent.objects.select_related(
            'category', 'created_by'
        ).prefetch_related('participants')
        
        # 検索・フィルタリング
        if search_form and search_form.is_valid():
            search = search_form.cleaned_data.get('search')
            category = search_form.cleaned_data.get('category')
            participants = search_form.cleaned_data.get('participants')
            priority = search_form.cleaned_data.get('priority')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            upcoming_only = search_form.cleaned_data.get('upcoming_only')
            
            if search:
                events = events.filter(
                    Q(title__icontains=search) | 
                    Q(description__icontains=search) |
                    Q(location__icontains=search)
                )
            
            if category:
                events = events.filter(category=category)
            
            if participants:
                events = events.filter(participants=participants)
            
            if priority:
                events = events.filter(priority=priority)
            
            if date_from:
                events = events.filter(start_date__gte=date_from)
            
            if date_to:
                events = events.filter(start_date__lte=date_to)
            
            if upcoming_only:
                today = timezone.now().date()
                events = events.filter(start_date__gte=today)
        else:
            # デフォルトで今後のイベントを表示
            today = timezone.now().date()
            events = events.filter(start_date__gte=today)
        
        # 並び替え
        events = events.order_by('start_date', 'start_time', 'title')
        
        # 今日と今週のイベント
        today = timezone.now().date()
        this_week_start = today - timedelta(days=today.weekday())
        this_week_end = this_week_start + timedelta(days=6)
        
        today_events = events.filter(start_date=today)
        this_week_events = events.filter(
            start_date__range=[this_week_start, this_week_end]
        ).exclude(start_date=today)
        
        # ページネーション
        paginator = Paginator(events, 10)  # 1ページあたり10イベント
        page = request.GET.get('page')
        
        try:
            events_page = paginator.page(page)
        except PageNotAnInteger:
            events_page = paginator.page(1)
        except EmptyPage:
            events_page = paginator.page(paginator.num_pages)
        
        # カテゴリ統計
        category_stats = EventCategory.objects.annotate(
            event_count=Count('familyevent')
        ).order_by('-event_count')
        
        context = {
            'search_form': search_form,
            'events': events_page,
            'today_events': today_events,
            'this_week_events': this_week_events,
            'category_stats': category_stats,
            'today': today,
        }
        
        return render(request, 'main/event_calendar.html', context)
        
    except Exception as e:
        logger.error(f"イベントカレンダーでエラー: {str(e)}")
        # エラーが発生した場合はシンプルなエラーページを表示
        from django.http import HttpResponse
        return HttpResponse(f"""
        <html>
        <head><title>エラー - イベントカレンダー</title></head>
        <body style="font-family: Arial, sans-serif; padding: 2rem;">
            <h1>⚠️ エラーが発生しました</h1>
            <p>イベントカレンダーの読み込み中にエラーが発生しました。</p>
            <p><strong>エラー詳細:</strong> {str(e)}</p>
            <a href="/" style="background: #3498db; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px;">🏠 ホームに戻る</a>
        </body>
        </html>
        """)


def event_detail(request, event_id):
    """イベント詳細"""
    try:
        event = get_object_or_404(
            FamilyEvent.objects.select_related('category', 'created_by').prefetch_related('participants'),
            id=event_id
        )
        
        # 関連するイベント（同じカテゴリ、同じ日）
        related_events = FamilyEvent.objects.filter(
            Q(category=event.category) | Q(start_date=event.start_date)
        ).exclude(id=event.id).distinct()[:5]
        
        context = {
            'event': event,
            'related_events': related_events,
        }
        
        return render(request, 'main/event_detail.html', context)
        
    except Exception as e:
        logger.error(f"イベント詳細でエラー: {str(e)}")
        messages.error(request, 'イベント詳細の取得中にエラーが発生しました。')
        return redirect('event_calendar')


@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    """イベント作成ビュー"""
    model = FamilyEvent
    form_class = FamilyEventForm
    template_name = 'main/event_form.html'
    success_url = reverse_lazy('event_calendar')
    
    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        form.instance.created_by = self.request.user
        messages.success(self.request, 'イベントが作成されました！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """フォームが無効な場合の処理"""
        messages.error(self.request, 'イベントの作成に失敗しました。入力内容を確認してください。')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    """イベント更新ビュー"""
    model = FamilyEvent
    form_class = FamilyEventForm
    template_name = 'main/event_form.html'
    success_url = reverse_lazy('event_calendar')
    
    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        messages.success(self.request, 'イベントが更新されました！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """フォームが無効な場合の処理"""
        messages.error(self.request, 'イベントの更新に失敗しました。入力内容を確認してください。')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class EventDeleteView(DeleteView):
    """イベント削除ビュー"""
    model = FamilyEvent
    template_name = 'main/event_confirm_delete.html'
    success_url = reverse_lazy('event_calendar')
    
    def delete(self, request, *args, **kwargs):
        """削除処理"""
        messages.success(request, 'イベントが削除されました。')
        return super().delete(request, *args, **kwargs)


def category_list(request):
    """カテゴリ一覧"""
    try:
        categories = EventCategory.objects.annotate(
            event_count=Count('familyevent')
        ).order_by('name')
        
        context = {
            'categories': categories,
        }
        
        return render(request, 'main/category_list.html', context)
        
    except Exception as e:
        logger.error(f"カテゴリ一覧でエラー: {str(e)}")
        messages.error(request, 'カテゴリ一覧の取得中にエラーが発生しました。')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(CreateView):
    """カテゴリ作成ビュー"""
    model = EventCategory
    form_class = EventCategoryForm
    template_name = 'main/category_form.html'
    success_url = reverse_lazy('category_list')
    
    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        messages.success(self.request, 'カテゴリが作成されました！')
        return super().form_valid(form)


def upcoming_events_api(request):
    """今後のイベントAPI（Ajax用）"""
    try:
        days = int(request.GET.get('days', 7))  # デフォルト7日間
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        events = FamilyEvent.objects.filter(
            start_date__range=[today, end_date]
        ).select_related('category').prefetch_related('participants')
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'start_date': event.start_date.isoformat(),
                'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
                'category': {
                    'name': event.category.name if event.category else '',
                    'emoji': event.category.emoji if event.category else '📅',
                    'color': event.category.color if event.category else '#3498db',
                },
                'participants': [p.name for p in event.participants.all()],
                'priority': event.get_priority_emoji(),
                'is_today': event.is_today(),
            })
        
        return JsonResponse({
            'success': True,
            'events': events_data,
            'count': len(events_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'エラーが発生しました: {str(e)}'
        })
