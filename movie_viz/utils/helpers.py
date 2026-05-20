"""
工具函数
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_movie_info(info_text: str) -> dict[str, Any]:
    """
    解析豆瓣电影 info 字段，提取结构化信息。

    示例输入:
        "导演: 弗兰克·德拉邦特 Frank Darabont    主演: 蒂姆·罗宾斯 Tim Robbins  ...  1994    美国    犯罪 剧情"
    """
    result = {
        "directors": [],
        "casts": [],
        "year": None,
        "region": "",
        "genres": [],
    }

    if not info_text:
        return result

    # 提取导演
    director_match = re.search(r"导演:\s*(.*?)(?:\s{2,}|$)", info_text)
    if director_match:
        raw = director_match.group(1).strip()
        result["directors"] = [d.strip() for d in re.split(r"[/、]", raw) if d.strip()]

    # 提取主演
    cast_match = re.search(r"主演:\s*(.*?)(?:\s{2,}|$)", info_text)
    if cast_match:
        raw = cast_match.group(1).strip()
        result["casts"] = [c.strip() for c in re.split(r"[/、]", raw) if c.strip()]

    # 提取年份
    year_match = re.search(r"(\d{4})", info_text)
    if year_match:
        result["year"] = int(year_match.group(1))

    # 提取类型（年份后的内容）
    parts = re.split(r"\s{2,}", info_text.strip())
    if len(parts) >= 3:
        result["genres"] = [g.strip() for g in parts[-1].split() if g.strip()]
    if len(parts) >= 2:
        result["region"] = parts[-2].strip() if len(parts) >= 2 else ""

    return result


def truncate(text: str, length: int = 100) -> str:
    """截断文本"""
    return text[:length] + "..." if len(text) > length else text
