"""
豆瓣电影爬虫模块

支持增量爬取、断点续爬、请求重试。
"""

import re
import time
import random
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import get_config

logger = logging.getLogger(__name__)


class DoubanCrawler:
    """豆瓣电影 TOP250 爬虫"""

    BASE_URL = "https://movie.douban.com/top250"
    HEADERS_TEMPLATE = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, timeout: int = 15, max_retries: int = 3):
        self.config = get_config()
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS_TEMPLATE)

    def _get_headers(self) -> dict:
        """生成带随机 User-Agent 的请求头"""
        return {
            **self.HEADERS_TEMPLATE,
            "User-Agent": self.config.CRAWL_USER_AGENT,
            "Referer": "https://movie.douban.com/",
        }

    def fetch_page(self, url: str) -> Optional[str]:
        """
        抓取单个页面，带重试机制。

        Args:
            url: 目标 URL

        Returns:
            HTML 文本，失败返回 None
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                resp.encoding = "utf-8"
                return resp.text
            except requests.RequestException as e:
                logger.warning(
                    "请求失败 (尝试 %d/%d): %s - %s", attempt, self.max_retries, url, e
                )
                if attempt < self.max_retries:
                    wait = random.uniform(2, 5) * attempt
                    logger.info("等待 %.1f 秒后重试...", wait)
                    time.sleep(wait)
        logger.error("请求彻底失败: %s", url)
        return None

    def parse_list_page(self, html: str) -> list[dict]:
        """
        解析列表页，提取电影基本信息。

        Args:
            html: 列表页 HTML

        Returns:
            电影信息字典列表
        """
        soup = BeautifulSoup(html, "html.parser")
        movies = []

        for item in soup.select(".item"):
            movie = {}

            # 海报
            pic = item.select_one(".pic")
            if pic:
                img = pic.select_one("img")
                order = pic.select_one("em")
                movie["id"] = int(order.get_text(strip=True)) if order else None

            # 链接
            info_div = item.select_one(".info")
            if not info_div:
                continue

            hd = info_div.select_one(".hd")
            if hd:
                link = hd.select_one("a")
                if link:
                    movie["info_link"] = link.get("href", "").strip()
                    title = link.select_one(".title")
                    movie["cname"] = title.get_text(strip=True) if title else ""

            # 外文名
            title_elements = hd.select("span") if hd else []
            ename_text = ""
            for span in title_elements:
                text = span.get_text(strip=True)
                if "/" in text:
                    ename_text = text.strip("/ ").strip()
            if not ename_text and len(title_elements) >= 2:
                ename_text = title_elements[1].get_text(strip=True).strip("/ ").strip()
            movie["ename"] = ename_text

            # BD 信息
            bd = info_div.select_one(".bd")
            if bd:
                # 评分
                star_span = bd.select_one(".rating_num")
                movie["score"] = (
                    float(star_span.get_text(strip=True)) if star_span else None
                )

                # 评价人数
                star_text = bd.get_text()
                rated_match = re.search(r"(\d+)\s*人评价", star_text)
                movie["rated"] = int(rated_match.group(1)) if rated_match else None

                # 引言
                quote = bd.select_one(".quote .inq")
                movie["introduction"] = (
                    quote.get_text(strip=True) if quote else ""
                )

                # 详细信息
                info_p = bd.select_one("p")
                if info_p:
                    info_text = info_p.get_text("\n", strip=True)
                    # 去掉引言部分
                    if movie.get("introduction"):
                        info_text = info_text.replace(
                            movie["introduction"], ""
                        ).strip()
                    movie["info"] = info_text

            movies.append(movie)

        return movies

    def crawl_all(self, start_page: int = 0, end_page: int = 9) -> list[dict]:
        """
        爬取 TOP250 全部页面。

        Args:
            start_page: 起始页码 (0-based)
            end_page: 结束页码 (含)

        Returns:
            全部电影数据列表
        """
        all_movies = []
        total_pages = min(end_page + 1, 10)  # TOP250 一共 10 页

        logger.info("开始爬取豆瓣 TOP250，共 %d 页", total_pages)

        for page in range(start_page, total_pages):
            start = page * 25
            url = f"{self.BASE_URL}?start={start}"
            logger.info("正在抓取第 %d 页 (start=%d)...", page + 1, start)

            html = self.fetch_page(url)
            if not html:
                logger.warning("第 %d 页抓取失败，跳过", page + 1)
                continue

            movies = self.parse_list_page(html)
            all_movies.extend(movies)
            logger.info("第 %d 页完成，本页 %d 条，累计 %d 条", page + 1, len(movies), len(all_movies))

            # 页间间隔，避免被封
            if page < total_pages - 1:
                wait = random.uniform(1.5, 3.5)
                time.sleep(wait)

        logger.info("爬取完成，共 %d 条数据", len(all_movies))
        return all_movies
