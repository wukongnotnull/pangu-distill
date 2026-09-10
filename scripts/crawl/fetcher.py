"""
网页内容抓取器
"""

import re

import requests
from bs4 import BeautifulSoup

from shared import ContentLanguage, ContentResult


class ContentFetcher:
    """
    网页内容抓取器

    功能：
    - 抓取网页正文（只收 text/html、text/plain）
    - 下载前按 Content-Type 和大小拦截，不把 PDF / 视频整段读进内存
    - 自动语言检测、字数统计
    """

    TIMEOUT = 30
    MAX_CONTENT_LENGTH = 500_000  # 提取后正文上限（字符）
    MAX_DOWNLOAD_BYTES = 3_000_000  # 下载上限（字节）
    ALLOWED_TYPES = ("text/html", "application/xhtml+xml", "text/plain")
    # 信息框 / 导航框 / 参考列表 / 编辑按钮：维基类页面的噪声，不是论述。
    NOISE_SELECTORS = (
        ".infobox",
        ".navbox",
        ".reflist",
        ".mw-editsection",
        ".sidebar",
        ".toc",
        "sup.reference",
        ".ad",
        ".ads",
        ".advertisement",
        ".social-share",
        ".comments",
        ".related-posts",
    )

    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch(self, url: str) -> ContentResult:
        try:
            response = self.session.get(url, timeout=self.TIMEOUT, stream=True)
            response.raise_for_status()

            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if content_type and not content_type.startswith(self.ALLOWED_TYPES):
                response.close()
                raise RuntimeError(f"跳过非文本内容 [{url}]: {content_type}")

            raw = self._read_limited(response)
            encoding = self._detect_encoding(response, raw)
            html = raw.decode(encoding, errors="replace")

            if content_type == "text/plain":
                content = self._clean_content(html)
                title = ""
            else:
                soup = BeautifulSoup(html, "lxml")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                for tag in soup.select(", ".join(self.NOISE_SELECTORS)):
                    tag.decompose()
                title = self._extract_title(soup)
                content = self._clean_content(self._extract_content(soup))

            return ContentResult(
                url=url,
                title=title,
                content=content[: self.MAX_CONTENT_LENGTH],
                word_count=len(content),
                language=self._detect_language(content),
            )

        except requests.RequestException as e:
            raise RuntimeError(f"抓取失败 [{url}]: {e}")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"解析失败 [{url}]: {e}")

    def _read_limited(self, response: requests.Response) -> bytes:
        declared = response.headers.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > self.MAX_DOWNLOAD_BYTES:
            response.close()
            raise RuntimeError(f"响应过大 ({declared} 字节)，跳过")
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            chunks.append(chunk)
            total += len(chunk)
            if total > self.MAX_DOWNLOAD_BYTES:
                break
        response.close()
        return b"".join(chunks)

    def _detect_encoding(self, response: requests.Response, raw: bytes) -> str:
        if response.encoding and response.encoding.lower() != "iso-8859-1":
            return response.encoding
        head = raw[:4096].decode("ascii", errors="ignore")
        match = re.search(r'charset=["\']?([^"\'\s;>]+)', head, re.I)
        if match:
            return match.group(1)
        return "utf-8"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title and og_title.get("content"):
            return og_title.get("content", "")
        title_elem = soup.find("title")
        if title_elem:
            return title_elem.get_text(strip=True)
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        selectors = [
            "article",
            "[role='main']",
            "#mw-content-text",
            ".post-content",
            ".article-content",
            ".entry-content",
            ".content",
            "main",
            "#content",
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 100:
                return self._block_text(elem)
        body = soup.find("body")
        if body:
            return self._block_text(body)
        return soup.get_text(separator="\n", strip=True)

    BLOCK_TAGS = ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "dd", "dt", "td", "th", "figcaption")

    def _block_text(self, elem) -> str:
        """一个块级元素一行；行内链接不再把句子切碎。"""
        blocks = elem.find_all(self.BLOCK_TAGS)
        if not blocks:
            return elem.get_text(separator="\n", strip=True)
        lines = []
        for block in blocks:
            if block.find(self.BLOCK_TAGS):
                continue  # 只取叶子块，避免 li 里的 p 重复
            text = block.get_text(separator=" ", strip=True)
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _clean_content(self, content: str) -> str:
        content = re.sub(r"\n{3,}", "\n\n", content)
        return content.strip()

    def _detect_language(self, content: str) -> ContentLanguage:
        if not content:
            return ContentLanguage.UNKNOWN
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", content))
        total_chars = len(re.sub(r"\s", "", content))
        if total_chars == 0:
            return ContentLanguage.UNKNOWN
        ratio = chinese_chars / total_chars
        if ratio > 0.3:
            return ContentLanguage.ZH
        if ratio > 0.1:
            return ContentLanguage.MIXED
        return ContentLanguage.EN
