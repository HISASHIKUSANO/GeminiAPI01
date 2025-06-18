"""
QuickContract - 契約文生成API
URL から主要テキストを抽出し、Gemini API で契約文を生成する FastAPI アプリケーション
"""

import os
import re
from pathlib import Path

import google.genai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .contract import extract_main_content, fetch_url_content

# 環境変数を読み込み
load_dotenv()

# FastAPI アプリケーションを初期化
app = FastAPI(
    title="QuickContract API",
    description="URL から主要テキストを抽出し、Gemini API で契約文を生成します",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Gemini API を設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY 環境変数が設定されていません")

genai.configure(api_key=GOOGLE_API_KEY)

# System Prompt を読み込み
PROMPT_FILE = Path(__file__).parent / "prompt.txt"
if not PROMPT_FILE.exists():
    raise FileNotFoundError(f"System prompt file not found: {PROMPT_FILE}")

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()


class ContractRequest(BaseModel):
    """契約文生成リクエスト"""
    url: HttpUrl


class ContractResponse(BaseModel):
    """契約文生成レスポンス"""
    contract: str
    url: str


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "QuickContract API へようこそ",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        # Gemini API の疎通確認
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content("Hello")
        return {"status": "healthy", "gemini_api": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.post("/contract", response_model=ContractResponse)
async def generate_contract(request: ContractRequest):
    """
    URL から契約文を生成する
    
    Args:
        request: URL を含むリクエスト
        
    Returns:
        生成された契約文
        
    Raises:
        HTTPException: URL の取得やテキスト抽出、契約文生成に失敗した場合
    """
    try:
        # URL からコンテンツを取得
        html_content = fetch_url_content(str(request.url))
        
        # 主要テキストを抽出
        main_text = extract_main_content(html_content)
        
        if not main_text or len(main_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="抽出されたテキストが短すぎます。有効なWebページのURLを指定してください。"
            )
        
        # 15万字制限
        if len(main_text) > 150000:
            main_text = main_text[:150000]
            
        # Gemini API で契約文を生成
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        # System instruction と user content を分けて送信
        response = model.generate_content([
            {"role": "user", "parts": [f"{SYSTEM_PROMPT}\n\n以下のテキストから契約文を生成してください：\n\n{main_text}"]}
        ])
        
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="契約文の生成に失敗しました。しばらく時間をおいて再試行してください。"
            )
        
        # 改行・タブを削除して1行化
        contract_text = re.sub(r'[\n\r\t]+', '', response.text.strip())
        
        # 60文字制限チェック（参考情報として）
        if len(contract_text) > 60:
            # 60文字以内に収まるよう調整を試みる
            sentences = contract_text.split('。')
            if len(sentences) > 1 and len(sentences[0] + '。') <= 60:
                contract_text = sentences[0] + '。'
        
        return ContractResponse(
            contract=contract_text,
            url=str(request.url)
        )
        
    except HTTPException:
        # 既に HTTPException の場合はそのまま再発生
        raise
    except Exception as e:
        # その他の例外は 500 エラーとして処理
        raise HTTPException(
            status_code=500,
            detail=f"契約文生成中にエラーが発生しました: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)