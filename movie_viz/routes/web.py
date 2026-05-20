"""
Web 页面路由 (Blueprints)
"""

import logging

from flask import Blueprint, render_template, request, abort

from movie_viz.models import Movie, db
from movie_viz.services.analyzer import MovieAnalyzer

logger = logging.getLogger(__name__)
web_bp = Blueprint("web", __name__)


@web_bp.route("/")
@web_bp.route("/index")
def index():
    """首页"""
    return render_template("index.html")


@web_bp.route("/movies")
def movie_list():
    """
    电影列表页，支持搜索、筛选、分页。

    Query params:
        keyword: 搜索关键词
        min_score: 最低评分
        max_score: 最高评分
        genre: 电影类型
        page: 页码
    """
    keyword = request.args.get("keyword", "").strip()
    min_score = request.args.get("min_score", 0, type=float)
    max_score = request.args.get("max_score", 10, type=float)
    genre = request.args.get("genre", "").strip()
    page = request.args.get("page", 1, type=int)
    page = max(1, page)

    movies, total, total_pages = MovieAnalyzer.search(
        keyword=keyword,
        min_score=min_score,
        max_score=max_score,
        genre=genre,
        page=page,
        per_page=20,
    )

    # 获取所有可用类型（前端筛选下拉框用）
    all_genres = MovieAnalyzer.genre_distribution()

    return render_template(
        "movies.html",
        movies=movies,
        total=total,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        min_score=min_score,
        max_score=max_score,
        genre=genre,
        all_genres=[g for g in all_genres.get("genres", [])],
    )


@web_bp.route("/movies/<int:movie_id>")
def movie_detail(movie_id: int):
    """电影详情页"""
    movie = db.session.get(Movie, movie_id)
    if not movie:
        abort(404)
    return render_template("movie_detail.html", movie=movie)


@web_bp.route("/stats")
def stats():
    """数据分析页"""
    score_data = MovieAnalyzer.score_distribution()
    year_data = MovieAnalyzer.year_distribution()
    genre_data = MovieAnalyzer.genre_distribution()
    top_rated = MovieAnalyzer.top_rated(10)
    most_rated = MovieAnalyzer.most_rated(10)
    total = Movie.query.count()

    return render_template(
        "stats.html",
        score_data=score_data,
        year_data=year_data,
        genre_data=genre_data,
        top_rated=top_rated,
        most_rated=most_rated,
        total=total,
    )


@web_bp.route("/about")
def about():
    """关于页面"""
    return render_template("about.html")
