# QuickContract

> 📄 **URL から契約文を自動生成する Web API**

QuickContract は、任意の Web ページの URL を受け取り、そのページの主要テキストを Google Gemini API で分析して、適切な契約文（日本語・60文字以内）を1行で生成する FastAPI アプリケーションです。

## 🎯 主な機能

- **URL 解析**: 任意の Web ページから主要コンテンツを自動抽出
- **AI 契約文生成**: Google Gemini 2.0 Flash を使用した高精度な契約文生成
- **日本語対応**: 自然で読みやすい日本語の契約文を生成
- **RESTful API**: シンプルな JSON API でのやり取り
- **エラーハンドリング**: 詳細なエラーメッセージと適切なステータスコード

## 🚀 セットアップ

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd quickcontract
```

### 2. 環境変数の設定
```bash
cp .env.example .env
```

`.env` ファイルを編集し、Google API キーを設定：
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

> **API キーの取得方法**: [Google AI Studio](https://makersuite.google.com/app/apikey) でアカウントを作成し、API キーを生成してください。

### 3. 依存関係のインストール
```bash
# Poetry がインストールされていない場合
pip install poetry

# 依存関係をインストール
poetry install
```

### 4. アプリケーションの起動
```bash
# 開発モード（自動リロード有効）
poetry run dev

# または
poetry run uvicorn app.main:app --reload

# 本番モード
poetry run start
```

サーバーが起動したら、ブラウザで http://127.0.0.1:8000 にアクセスしてください。

## 📚 API ドキュメント

アプリケーション起動後、以下の URL で API ドキュメントを確認できます：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔧 API エンドポイント

### `POST /contract`

URL から契約文を生成します。

**リクエスト:**
```json
{
  "url": "https://example.com/terms"
}
```

**レスポンス:**
```json
{
  "contract": "甲は乙に対し本サービスを月額1,000円で提供する。",
  "url": "https://example.com/terms"
}
```

### `GET /health`

API の稼働状況を確認します。

**レスポンス:**
```json
{
  "status": "healthy",
  "gemini_api": "connected"
}
```

## ✅ 動作確認

### cURL を使用したテスト

```bash
# 基本的なテスト
curl -X POST http://127.0.0.1:8000/contract \
     -H "Content-Type: application/json" \
     -d '{"url":"https://www.google.com"}'

# より具体的なサービスページのテスト
curl -X POST http://127.0.0.1:8000/contract \
     -H "Content-Type: application/json" \
     -d '{"url":"https://github.com/pricing"}'

# ヘルスチェック
curl http://127.0.0.1:8000/health
```

### Python での使用例

```python
import requests

# API エンドポイント
url = "http://127.0.0.1:8000/contract"

# リクエストデータ
data = {
    "url": "https://example.com/terms"
}

# API 呼び出し
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(f"生成された契約文: {result['contract']}")
else:
    print(f"エラー: {response.json()['detail']}")
```

## 🛠️ 技術仕様

### 技術スタック
- **Python**: 3.12+
- **Web フレームワーク**: FastAPI + Uvicorn
- **AI**: Google Generative AI (Gemini 2.0 Flash)
- **スクレイピング**: requests + readability-lxml
- **依存管理**: Poetry

### 制限事項
- **URL**: HTTP/HTTPS のみ対応
- **タイムアウト**: 10秒
- **テキスト制限**: 抽出テキストは最大15万文字
- **契約文長**: 60文字以内
- **対応言語**: 日本語

### エラーハンドリング
- `400 Bad Request`: 無効なURL、接続エラー、コンテンツ抽出エラー
- `500 Internal Server Error`: Gemini API エラー、予期しないエラー
- `503 Service Unavailable`: Gemini API 接続エラー

## 📁 プロジェクト構造

```
quickcontract/
├── pyproject.toml          # 依存関係とプロジェクト設定
├── .env.example           # 環境変数テンプレート
├── README.md              # このファイル
└── app/
    ├── __init__.py        # パッケージ初期化
    ├── main.py           # FastAPI アプリケーション
    ├── contract.py       # URL取得・テキスト抽出ユーティリティ
    └── prompt.txt        # Gemini AI システムプロンプト
```

## 🔒 セキュリティ

- API キーは環境変数で管理
- URL バリデーション実装
- タイムアウト設定でDDoS対策
- 適切なUser-Agentでbot検出回避

## 🤝 コントリビューション

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 🆘 トラブルシューティング

### よくある問題

**Q: `GOOGLE_API_KEY 環境変数が設定されていません` エラーが出る**
A: `.env` ファイルが正しく作成され、有効な API キーが設定されているか確認してください。

**Q: 特定のURLで契約文が生成されない**
A: そのページにテキストコンテンツが十分にあるか、robots.txt でアクセスが制限されていないか確認してください。

**Q: API が 503 エラーを返す**
A: Gemini API の利用制限に達している可能性があります。しばらく時間をおいてから再試行してください。

---

**QuickContract** - Powered by Google Gemini AI 🤖