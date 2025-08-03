"""
Utility functions for the main app.
"""

from datetime import date
from django.core.exceptions import ValidationError
from PIL import Image
import os


def calculate_age(birth_date):
    """
    誕生日から年齢を計算する
    
    Args:
        birth_date (date): 誕生日
        
    Returns:
        int or None: 年齢（誕生日が設定されていない場合はNone）
    """
    if not birth_date:
        return None
    
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def get_role_emoji(role):
    """
    続柄に対応する絵文字を取得する
    
    Args:
        role (str): 続柄
        
    Returns:
        str: 対応する絵文字
    """
    role_emojis = {
        '父': '👨',
        '母': '👩',
        '息子': '👦',
        '娘': '👧',
        'おじいちゃん': '👴',
        'おばあちゃん': '👵',
    }
    return role_emojis.get(role, '👤')


def validate_image_size(image):
    """
    アップロードされた画像のサイズを検証する
    
    Args:
        image: アップロードされた画像ファイル
        
    Raises:
        ValidationError: 画像が大きすぎる場合
    """
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError('画像ファイルは5MB以下にしてください。')


def resize_image(image_path, max_size=(800, 800)):
    """
    画像をリサイズする
    
    Args:
        image_path (str): 画像ファイルのパス
        max_size (tuple): 最大サイズ (幅, 高さ)
    """
    if not os.path.exists(image_path):
        return
    
    try:
        with Image.open(image_path) as img:
            # アスペクト比を保持してリサイズ
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 画質を保持して保存
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        # エラーログを出力（本番環境では適切なロガーを使用）
        print(f"画像リサイズエラー: {e}")


def format_date_japanese(date_obj):
    """
    日付を日本語形式でフォーマットする
    
    Args:
        date_obj (date): 日付オブジェクト
        
    Returns:
        str: 日本語形式の日付文字列
    """
    if not date_obj:
        return ''
    
    return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"


def get_month_name_japanese(month):
    """
    月を日本語で返す
    
    Args:
        month (int): 月（1-12）
        
    Returns:
        str: 日本語の月名
    """
    month_names = {
        1: "1月", 2: "2月", 3: "3月", 4: "4月", 5: "5月", 6: "6月",
        7: "7月", 8: "8月", 9: "9月", 10: "10月", 11: "11月", 12: "12月"
    }
    return month_names.get(month, f"{month}月")


def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """
    画像のサムネイルを作成
    
    Args:
        image_path (str): 元画像のパス
        thumbnail_path (str): サムネイル保存パス
        size (tuple): サムネイルサイズ (幅, 高さ)
        
    Returns:
        bool: 作成成功したかどうか
    """
    try:
        with Image.open(image_path) as img:
            # アスペクト比を保持してサムネイル作成
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # RGBAからRGBに変換
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # サムネイル保存
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"サムネイル作成エラー: {e}")
        return False


def get_image_info(image_path):
    """
    画像の情報を取得
    
    Args:
        image_path (str): 画像ファイルのパス
        
    Returns:
        dict or None: 画像情報（取得失敗時はNone）
    """
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_mb': round(os.path.getsize(image_path) / (1024 * 1024), 2)
            }
    except Exception as e:
        print(f"画像情報取得エラー: {e}")
        return None


def truncate_text(text, max_length=100):
    """
    テキストを指定した長さで切り詰める
    
    Args:
        text (str): 対象テキスト
        max_length (int): 最大長
        
    Returns:
        str: 切り詰められたテキスト
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def get_file_extension(filename):
    """
    ファイル名から拡張子を取得
    
    Args:
        filename (str): ファイル名
        
    Returns:
        str: 拡張子（小文字）
    """
    return os.path.splitext(filename)[1].lower()


def is_image_file(filename):
    """
    ファイルが画像かどうかを判定
    
    Args:
        filename (str): ファイル名
        
    Returns:
        bool: 画像ファイルかどうか
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return get_file_extension(filename) in image_extensions
