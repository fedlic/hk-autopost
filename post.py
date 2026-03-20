"""
香港アフィリエイトサイト 自動記事生成・投稿スクリプト
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from google import genai
from dotenv import load_dotenv

from topics import AFFILIATE_LINKS, TOPICS

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WP_PATH = os.getenv("WP_PATH", "/home/admin/web/hk.fedlic.tokyo/public_html")
WP_CLI = os.getenv("WP_CLI", "/home/admin/.local/bin/wp")
WP_USER = os.getenv("WP_USER", "wpadmin")
HISTORY_FILE = Path(__file__).parent / "history.json"

client = genai.Client(api_key=GEMINI_API_KEY)


def load_history() -> list[str]:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(keyword: str):
    history = load_history()
    history.append(keyword)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))


def pick_topic() -> dict:
    history = load_history()
    unused = [t for t in TOPICS if t["keyword"] not in history]
    if not unused:
        # 全部使ったらリセット
        HISTORY_FILE.write_text("[]")
        unused = TOPICS
    return random.choice(unused)


def generate_article(topic: dict) -> tuple[str, str]:
    affiliate = AFFILIATE_LINKS.get(topic["affiliate"], {})
    affiliate_text = ""
    if affiliate:
        affiliate_text = f"""
記事の中に自然な形でアフィリエイトリンクを1〜2箇所挿入してください。
リンクテキスト: {affiliate['text']}
URL: {affiliate['url']}
HTMLリンク形式: <a href="{affiliate['url']}" target="_blank" rel="nofollow">{affiliate['text']}</a>
"""

    prompt = f"""あなたは香港在住の日本人ライターです。
日本人の香港移住者・旅行者向けのSEO記事を書いてください。

キーワード: {topic['keyword']}
タイトル案: {topic['title_hint']}

## 記事の要件
- 文字数: 2000〜3000文字
- 読者: 香港移住を検討中または旅行予定の日本人
- 見出しはH2（##）、H3（###）を使ったMarkdown形式
- 具体的な数字・情報を含める
- 最後に「まとめ」セクションを入れる
- 自然で読みやすい日本語
{affiliate_text}

まず記事タイトル（SEO最適化済み）を1行目に書き、
2行目以降に本文をMarkdown形式で書いてください。
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = response.text.strip()

    lines = text.split("\n")
    title = lines[0].lstrip("#").strip()
    body_md = "\n".join(lines[1:]).strip()

    # MarkdownをHTMLに変換（簡易版）
    body_html = md_to_html(body_md)

    return title, body_html


def md_to_html(md: str) -> str:
    """簡易Markdown→HTML変換"""
    lines = md.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line[2:].strip()}</li>")
        elif line.startswith("**") and line.endswith("**"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<strong>{line[2:-2]}</strong>")
        elif line.strip() == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # インライン太字
            import re
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="nofollow">\1</a>', line)
            html_lines.append(f"<p>{line.strip()}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def post_to_wordpress(title: str, content: str, topic: dict) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name

    try:
        result = subprocess.run(
            f'{WP_CLI} --allow-root --path={WP_PATH} post create '
            f'--post_title="{title}" '
            f'--post_content="$(cat {tmp_path})" '
            f'--post_status=publish '
            f'--post_author=1 '
            f'--porcelain',
            capture_output=True,
            text=True,
            shell=True,
        )

        post_id = result.stdout.strip()
        if not post_id.isdigit():
            raise RuntimeError(f"WP-CLI error: {result.stderr}")

        # パーマリンク取得
        url_result = subprocess.run(
            f"{WP_CLI} --allow-root --path={WP_PATH} post get {post_id} --field=url",
            capture_output=True, text=True, shell=True,
        )
        url = url_result.stdout.strip()
        return url

    finally:
        os.unlink(tmp_path)


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] 記事生成開始")

    topic = pick_topic()
    print(f"トピック: {topic['keyword']}")

    title, content = generate_article(topic)
    print(f"タイトル: {title}")

    url = post_to_wordpress(title, content, topic)
    print(f"投稿完了: {url}")

    save_history(topic["keyword"])

    # ログ保存
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "keyword": topic["keyword"],
        "title": title,
        "url": url,
    }
    log_file = Path(__file__).parent / "post.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
