# hk-autopost

香港移住・旅行者向けアフィリエイトサイト（hk.fedlic.tokyo）の自動記事生成・投稿システム。

## 概要

Gemini AIが香港関連のSEO記事を自動生成し、WordPressに投稿する。毎朝9時にcronで実行。

## 構成

- **`post.py`** — メインスクリプト。トピック選択 → Gemini記事生成 → WP-CLI投稿
- **`topics.py`** — キーワード・タイトル・アフィリエイトリンクの定義
- **`history.json`** — 投稿済みトピックの管理（gitignore対象）
- **`post.log`** — 投稿ログ（gitignore対象）

## セットアップ

```bash
git clone https://github.com/fedlic/hk-autopost.git
cd hk-autopost
uv sync
cp .env.example .env  # APIキーを設定
```

## 環境変数（.env）

| 変数名 | 用途 |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API キー |
| `WP_PATH` | WordPressのインストールパス |
| `WP_CLI` | WP-CLIのパス |
| `WP_USER` | WordPress管理者ユーザー名 |

## 使い方

```bash
# 記事を1件生成・投稿
uv run python post.py

# cronで毎朝9時に自動実行
0 9 * * * cd /home/admin/hk-autopost && /home/admin/.local/bin/uv run python post.py >> /home/admin/hk-autopost/post.log 2>&1
```

## トピック

全12カテゴリをローテーション：

- 香港移住ビザ
- 香港銀行口座開設
- 海外送金（Wise）
- VPN
- クレジットカード
- 生活費
- 旅行モデルコース
- ホテル
- 航空券
- Wi-Fi・SIM
- 証券口座
- グルメ（飲茶）

## WordPress構成

- URL: https://hk.fedlic.tokyo
- ナビゲーション: ブログ / このサイトについて / よくある質問
- アフィリエイト:
  - Booking.com（ホテル予約）
  - Amazonアソシエイト（`tag=fedlic-22`）— ガイドブック・旅行グッズ
  - Wise・VPN・クレカ（topics.py内で管理）

## WordPress管理メモ

- デフォルト記事（Ciao mondo!）は削除済み
- ナビゲーションは `wp_navigation` (ID:4) で管理
- 不要ページ（Shop/Events/Patterns/Themes）は除去済み

## ドキュメント

- [MANUAL.md](./MANUAL.md) — 日本語・英語の操作マニュアル

## 技術スタック

- Python 3.12 / uv
- Gemini 2.5 Flash（記事生成）
- WP-CLI（WordPress投稿）
- HestiaCP（サーバー管理）
- WordPress + Twenty Twenty-Five テーマ
