# hk-autopost 操作マニュアル / Operation Manual

---

## 日本語

### 概要

香港移住・旅行者向けアフィリエイトサイト（hk.fedlic.tokyo）の自動記事生成・投稿システム。
Gemini AIがSEO記事を自動生成し、WordPressに毎朝9時に投稿する。

---

### 日常操作

#### 記事を今すぐ手動投稿する

```bash
cd /home/admin/hk-autopost
uv run python post.py
```

#### 投稿ログを確認する

```bash
tail -f /home/admin/hk-autopost/post.log
```

#### 投稿済みトピック履歴を確認する

```bash
cat /home/admin/hk-autopost/history.json
```

#### 投稿履歴をリセットする（全トピックを再利用）

```bash
echo "[]" > /home/admin/hk-autopost/history.json
```

---

### cron設定

| 時刻 | 内容 |
|---|---|
| 毎日 9:00 | 香港記事自動生成・WP投稿 |
| 毎日 10:00・18:00 | X自動投稿（画像付き） |
| 毎日 14:00 | Xトレンド投稿 |

#### cronを確認する

```bash
crontab -l
```

#### cronを編集する

```bash
crontab -e
```

---

### トピック・アフィリエイトの追加

`topics.py` を編集する：

```python
# TOPICSリストに追加
{
    "keyword": "検索キーワード",
    "title_hint": "記事タイトル案",
    "affiliate": "affiliate_key",
},

# AFFILIATE_LINKSに追加
"affiliate_key": {
    "name": "サービス名",
    "url": "https://アフィリエイトURL",
    "text": "リンクテキスト",
},
```

編集後はGitにコミット：

```bash
cd /home/admin/hk-autopost
git add topics.py
git commit -m "Add new topic/affiliate"
git push
```

---

### WordPress管理

| 項目 | 内容 |
|---|---|
| サイトURL | https://hk.fedlic.tokyo |
| 管理画面 | https://hk.fedlic.tokyo/wp-admin |
| ユーザー名 | wpadmin |
| HestiaCP | https://fedlic.tokyo:8083 |

#### WP-CLIで記事一覧を確認

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html post list --fields=ID,post_title,post_date
```

#### WP-CLIで記事を削除

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html post delete <ID> --force
```

---

### ファイル構成

```
hk-autopost/
├── post.py        # メインスクリプト
├── topics.py      # トピック・アフィリエイトリンク管理
├── .env           # APIキー（Gitignore対象）
├── history.json   # 投稿済みトピック履歴（Gitignore対象）
├── post.log       # 投稿ログ（Gitignore対象）
└── pyproject.toml # 依存パッケージ定義
```

---

### トラブルシューティング

#### 記事が投稿されない

```bash
# ログを確認
cat /home/admin/hk-autopost/post.log

# 手動実行してエラーを確認
cd /home/admin/hk-autopost && uv run python post.py
```

#### Gemini APIエラー

`.env` の `GEMINI_API_KEY` が正しいか確認する。

#### WP-CLIエラー

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html doctor check
```

---

---

## English

### Overview

An automated article generation and posting system for the Hong Kong immigration/travel affiliate site (hk.fedlic.tokyo).
Gemini AI generates SEO articles and posts them to WordPress automatically at 9:00 AM every day.

---

### Daily Operations

#### Post an article manually right now

```bash
cd /home/admin/hk-autopost
uv run python post.py
```

#### Check the posting log

```bash
tail -f /home/admin/hk-autopost/post.log
```

#### Check posted topic history

```bash
cat /home/admin/hk-autopost/history.json
```

#### Reset topic history (reuse all topics)

```bash
echo "[]" > /home/admin/hk-autopost/history.json
```

---

### Cron Schedule

| Time | Task |
|---|---|
| Daily 9:00 AM | Auto-generate Hong Kong article and post to WordPress |
| Daily 10:00 AM & 6:00 PM | X (Twitter) auto-post with image |
| Daily 2:00 PM | X trend-based post |

#### View cron jobs

```bash
crontab -l
```

#### Edit cron jobs

```bash
crontab -e
```

---

### Adding Topics & Affiliates

Edit `topics.py`:

```python
# Add to TOPICS list
{
    "keyword": "search keyword",
    "title_hint": "article title hint",
    "affiliate": "affiliate_key",
},

# Add to AFFILIATE_LINKS
"affiliate_key": {
    "name": "Service Name",
    "url": "https://affiliate-url",
    "text": "link text",
},
```

After editing, commit to Git:

```bash
cd /home/admin/hk-autopost
git add topics.py
git commit -m "Add new topic/affiliate"
git push
```

---

### WordPress Management

| Item | Value |
|---|---|
| Site URL | https://hk.fedlic.tokyo |
| Admin Panel | https://hk.fedlic.tokyo/wp-admin |
| Username | wpadmin |
| HestiaCP | https://fedlic.tokyo:8083 |

#### List posts via WP-CLI

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html post list --fields=ID,post_title,post_date
```

#### Delete a post via WP-CLI

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html post delete <ID> --force
```

---

### File Structure

```
hk-autopost/
├── post.py        # Main script
├── topics.py      # Topics & affiliate link definitions
├── .env           # API keys (gitignored)
├── history.json   # Posted topic history (gitignored)
├── post.log       # Posting log (gitignored)
└── pyproject.toml # Package dependencies
```

---

### Troubleshooting

#### Articles not being posted

```bash
# Check the log
cat /home/admin/hk-autopost/post.log

# Run manually to see errors
cd /home/admin/hk-autopost && uv run python post.py
```

#### Gemini API error

Verify that `GEMINI_API_KEY` in `.env` is correct.

#### WP-CLI error

```bash
wp --allow-root --path=/home/admin/web/hk.fedlic.tokyo/public_html doctor check
```
