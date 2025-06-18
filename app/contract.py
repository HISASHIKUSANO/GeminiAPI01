"""
契約文生成のためのユーティリティモジュール
URL からのコンテンツ取得と主要テキスト抽出を担当
"""

import re
from urllib.parse import urlparse

import requests
from fastapi import HTTPException
from readability import Document


def validate_url(url: str) -> bool:
    """
    URL の妥当性をチェック
    
    Args:
        url: チェック対象のURL
        
    Returns:
        bool: URLが有効かどうか
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
    except Exception:
        return False


def fetch_url_content(url: str, timeout: int = 10) -> str:
    """
    指定されたURLからHTMLコンテンツを取得
    
    Args:
        url: 取得対象のURL
        timeout: タイムアウト秒数（デフォルト: 10秒）
        
    Returns:
        str: 取得したHTMLコンテンツ
        
    Raises:
        HTTPException: URL取得に失敗した場合
    """
    # URL妥当性チェック
    if not validate_url(url):
        raise HTTPException(
            status_code=400,
            detail="無効なURLです。http または https で始まるURLを指定してください。"
        )
    
    try:
        # User-Agent を設定してリクエスト
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, timeout=timeout, headers=headers)
        
        # ステータスコードチェック
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"URLの取得に失敗しました。ステータスコード: {response.status_code}"
            )
        
        # コンテンツタイプチェック
        content_type = response.headers.get('content-type', '').lower()
        if not any(ct in content_type for ct in ['text/html', 'application/xhtml']):
            raise HTTPException(
                status_code=400,
                detail="HTMLページではありません。HTMLページのURLを指定してください。"
            )
        
        return response.text
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=400,
            detail="URLの取得がタイムアウトしました。別のURLを試してください。"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=400,
            detail="URLに接続できませんでした。URLが正しいかご確認ください。"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"URLの取得中にエラーが発生しました: {str(e)}"
        )
    except HTTPException:
        # 既に HTTPException の場合はそのまま再発生
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"予期しないエラーが発生しました: {str(e)}"
        )


def extract_main_content(html_content: str) -> str:
    """
    HTMLから主要なテキストコンテンツを抽出
    
    Args:
        html_content: 抽出対象のHTMLコンテンツ
        
    Returns:
        str: 抽出された主要テキスト
        
    Raises:
        HTTPException: テキスト抽出に失敗した場合
    """
    try:
        # readability を使用して主要コンテンツを抽出
        doc = Document(html_content)
        
        # タイトルとコンテンツを取得
        title = doc.title()
        content = doc.summary()
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="ページから有効なコンテンツを抽出できませんでした。"
            )
        
        # HTMLタグを除去
        clean_content = _remove_html_tags(content)
        
        # タイトルも含める（存在する場合）
        if title and title.strip():
            clean_title = _remove_html_tags(title)
            full_text = f"{clean_title}\n\n{clean_content}"
        else:
            full_text = clean_content
        
        # 余分な空白や改行を整理
        full_text = _clean_whitespace(full_text)
        
        if not full_text or len(full_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="抽出されたテキストが短すぎます。より内容のあるページを指定してください。"
            )
        
        return full_text
        
    except HTTPException:
        # 既に HTTPException の場合はそのまま再発生
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"テキスト抽出中にエラーが発生しました: {str(e)}"
        )


def _remove_html_tags(text: str) -> str:
    """
    HTMLタグを除去してプレーンテキストに変換
    
    Args:
        text: HTMLを含むテキスト
        
    Returns:
        str: HTMLタグが除去されたテキスト
    """
    # HTMLタグを除去
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # HTML エンティティをデコード
    import html
    clean_text = html.unescape(clean_text)
    
    return clean_text


def _clean_whitespace(text: str) -> str:
    """
    余分な空白と改行を整理
    
    Args:
        text: 整理対象のテキスト
        
    Returns:
        str: 整理されたテキスト
    """
    # 連続する空白を単一の空白に
    text = re.sub(r' +', ' ', text)
    
    # 連続する改行を最大2つに制限
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # 行頭・行末の空白を除去
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # 全体の前後の空白を除去
    return text.strip()