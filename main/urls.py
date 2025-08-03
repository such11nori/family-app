from django.urls import path
from . import views

urlpatterns = [
    # ホーム
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # 家族メンバー
    path('family/', views.family_list, name='family_list'),
    path('family/<int:pk>/', views.family_detail, name='family_detail'),
    
    # フォトギャラリー
    path('gallery/', views.photo_gallery, name='photo_gallery'),
    path('gallery/photo/<int:pk>/', views.photo_detail, name='photo_detail'),
    
    # アルバム
    path('albums/', views.album_list, name='album_list'),
    path('albums/<int:pk>/', views.album_detail, name='album_detail'),
    
    # イベント管理
    path('events/', views.event_calendar, name='event_calendar'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # カテゴリ管理
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    
    # Ajax機能
    path('ajax/toggle-favorite/<int:photo_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('api/upcoming-events/', views.upcoming_events_api, name='upcoming_events_api'),
]
