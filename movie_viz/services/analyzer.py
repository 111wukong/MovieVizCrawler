"""
数据分析服务

提供电影数据的统计分析功能。
"""

from typing import Any

from flask import current_app
from movie_viz.models import Movie, db


class MovieAnalyzer:
    """电影数据分析器"""

    @staticmethod
    def score_distribution() -> dict[str, list]:
        """
        评分分布统计

        Returns:
            {"scores": [9.7, 9.6, ...], "counts": [1, 2, ...]}
        """
        from sqlalchemy import func

        results = (
            db.session.query(Movie.score, func.count(Movie.id))
            .group_by(Movie.score)
            .order_by(Movie.score.desc())
            .all()
        )
        return {
            "scores": [r[0] for r in results],
            "counts": [r[1] for r in results],
        }

    @staticmethod
    def year_distribution() -> dict[str, list]:
        """
        年份分布统计

        Returns:
            {"years": [1994, 1998, ...], "counts": [5, 3, ...]}
        """
        from collections import Counter

        years = []
        for movie in Movie.query.all():
            year = movie.year
            if year:
                years.append(year)

        counter = Counter(years)
        sorted_years = sorted(counter.items())
        return {
            "years": [y for y, _ in sorted_years],
            "counts": [c for _, c in sorted_years],
        }

    @staticmethod
    def genre_distribution() -> dict[str, list]:
        """
        电影类型分布统计

        Returns:
            {"genres": ["剧情", "喜剧", ...], "counts": [120, 50, ...]}
        """
        from collections import Counter

        genre_counter: Counter = Counter()
        for movie in Movie.query.all():
            for genre in movie.genres:
                genre_counter[genre] += 1

        sorted_genres = genre_counter.most_common()
        return {
            "genres": [g for g, _ in sorted_genres],
            "counts": [c for _, c in sorted_genres],
        }

    @staticmethod
    def top_rated(limit: int = 10) -> list[Movie]:
        """获取评分最高的电影"""
        return Movie.query.order_by(Movie.score.desc()).limit(limit).all()

    @staticmethod
    def most_rated(limit: int = 10) -> list[Movie]:
        """获取评价人数最多的电影"""
        return Movie.query.order_by(Movie.rated.desc()).limit(limit).all()

    @staticmethod
    def search(
        keyword: str = "",
        min_score: float = 0,
        max_score: float = 10,
        genre: str = "",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Movie], int, int]:
        """
        搜索电影，支持多条件筛选。

        Args:
            keyword: 关键词（匹配中文名、外文名、简介）
            min_score: 最低评分
            max_score: 最高评分
            genre: 电影类型
            page: 页码
            per_page: 每页数量

        Returns:
            (movies, total_count, total_pages)
        """
        query = Movie.query

        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                db.or_(
                    Movie.cname.like(like_pattern),
                    Movie.ename.like(like_pattern),
                    Movie.introduction.like(like_pattern),
                )
            )

        if min_score > 0:
            query = query.filter(Movie.score >= min_score)
        if max_score < 10:
            query = query.filter(Movie.score <= max_score)

        if genre:
            like_pattern = f"%{genre}%"
            query = query.filter(Movie.info.like(like_pattern))

        total = query.count()
        total_pages = max(1, (total + per_page - 1) // per_page)

        movies = (
            query
            .order_by(Movie.score.desc(), Movie.rated.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return movies, total, total_pages



