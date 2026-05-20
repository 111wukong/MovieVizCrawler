"""
AI 智能路由 — 自然语言问答、电影推荐、数据洞察
"""

import json
import logging
from typing import Optional

from flask import Blueprint, render_template, request, jsonify, current_app

from movie_viz.models import Movie, db
from movie_viz.services.llm import LLMService
from movie_viz.services.analyzer import MovieAnalyzer

logger = logging.getLogger(__name__)
ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

llm = LLMService()


def _build_db_context(movie: Optional[Movie] = None) -> str:
    """构建电影数据库上下文描述"""
    total = Movie.query.count()
    avg = db.session.query(db.func.avg(Movie.score)).scalar()
    top = Movie.query.order_by(Movie.score.desc()).limit(5).all()
    genres_raw = MovieAnalyzer.genre_distribution()
    years_raw = MovieAnalyzer.year_distribution()

    lines = [
        f"数据库共有 {total} 部电影，平均评分 {float(avg or 0):.2f}",
        "",
        "评分最高 TOP5：",
    ]
    for m in top:
        lines.append(f"  - 《{m.cname}》 评分: {m.score}  ({m.introduction or '无简介'})")

    if genres_raw.get("genres"):
        lines.extend(["", "电影类型分布："] + [
            f"  {g}: {c}部"
            for g, c in zip(genres_raw["genres"][:8], genres_raw["counts"][:8])
        ])

    if years_raw.get("years"):
        min_y = min(years_raw["years"])
        max_y = max(years_raw["years"])
        lines.append(f"覆盖年份：{min_y} - {max_y}")

    if movie:
        info_parts = [
            f"当前查看的电影：{movie.cname}",
            f"评分：{movie.score}",
            f"评价数：{movie.rated}",
            f"简介：{movie.introduction or '无'}",
        ]
        if movie.ename:
            info_parts.append(f"外文名：{movie.ename}")
        lines.extend(["", *info_parts])

    return "\n".join(lines)


def _build_movie_list_context(limit: int = 50) -> str:
    """构建电影列表上下文"""
    movies = Movie.query.order_by(Movie.score.desc()).limit(limit).all()
    lines = [f"TOP{limit} 电影列表："]
    for m in movies:
        intro = (m.introduction or "")[:30]
        lines.append(f"  #{m.id} 《{m.cname}》 {m.score}分 - {intro}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Web Pages
# ---------------------------------------------------------------------------

@ai_bp.route("/chat")
def chat_page():
    """AI 问答界面"""
    return render_template("ai_chat.html")


@ai_bp.route("/recommend")
def recommend_page():
    """AI 推荐界面"""
    genres_raw = MovieAnalyzer.genre_distribution()
    years_raw = MovieAnalyzer.year_distribution()
    return render_template(
        "ai_recommend.html",
        genres=genres_raw.get("genres", []),
        years=years_raw.get("years", []),
    )


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@ai_bp.route("/api/chat", methods=["POST"])
def api_chat():
    """
    问答 API

    Body (JSON):
        message: 用户消息
        history: [[role, content], ...] 可选历史
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"code": 400, "reply": "请提供消息内容"}), 400

    user_msg = data["message"].strip()
    if not user_msg:
        return jsonify({"code": 400, "reply": "消息不能为空"}), 400

    # 构建历史
    history = None
    if raw_history := data.get("history"):
        history = [{"role": h[0], "content": h[1]} for h in raw_history[-10:]]

    # 构建数据库上下文
    context = _build_db_context()

    reply = llm.chat_with_context(
        user_message=user_msg,
        context=context,
        history=history,
    )

    return jsonify({
        "code": 0 if reply else 500,
        "reply": reply or "抱歉，AI 服务暂时不可用，请稍后重试。",
    })


@ai_bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    """
    推荐 API

    Body (JSON):
        genre: 类型
        min_score: 最低评分
        year_from: 起始年份
        year_to: 截止年份
        keyword: 关键词
        preferences: 自由描述
    """
    data = request.get_json(silent=True) or {}
    genre = (data.get("genre") or "").strip()
    min_score = data.get("min_score", 0)
    year_from = data.get("year_from", 0)
    year_to = data.get("year_to", 0)
    keyword = (data.get("keyword") or "").strip()
    preferences = (data.get("preferences") or "").strip()

    # 构建搜索条件描述
    conditions = []
    if genre:
        conditions.append(f"类型：{genre}")
    if min_score:
        conditions.append(f"最低评分：{min_score}")
    if year_from and year_to:
        conditions.append(f"年份：{year_from}-{year_to}")
    elif year_from:
        conditions.append(f"年份：{year_from}年以后")
    elif year_to:
        conditions.append(f"年份：{year_to}年以前")
    if keyword:
        conditions.append(f"关键词：{keyword}")

    desc = "；".join(conditions) if conditions else "无特定限制"

    user_pref = preferences or desc
    db_context = _build_movie_list_context(80)

    reply = llm.recommend_movies(
        preferences=f"{user_pref}\n（附加筛选条件：{desc}）",
        db_context=db_context,
    )

    return jsonify({
        "code": 0 if reply else 500,
        "reply": reply or "推荐服务暂时不可用",
        "conditions": conditions,
    })


@ai_bp.route("/api/analyze/<int:movie_id>")
def api_analyze(movie_id: int):
    """电影 AI 解读 API"""
    movie = db.session.get(Movie, movie_id)
    if not movie:
        return jsonify({"code": 404, "reply": "电影不存在"}), 404

    info_parts = [
        f"片名：{movie.cname}",
        f"外文名：{movie.ename or '无'}",
        f"评分：{movie.score}",
        f"评价人数：{movie.rated}",
        f"简介：{movie.introduction or '无'}",
        f"详细信息：{movie.info or '无'}",
    ]

    reply = llm.analyze_movie("\n".join(info_parts))
    return jsonify({
        "code": 0 if reply else 500,
        "reply": reply or "分析服务暂时不可用",
    })


@ai_bp.route("/api/insight")
def api_insight():
    """数据洞察 API"""
    score_data = MovieAnalyzer.score_distribution()
    year_data = MovieAnalyzer.year_distribution()
    genre_data = MovieAnalyzer.genre_distribution()
    total = Movie.query.count()
    avg = db.session.query(db.func.avg(Movie.score)).scalar()

    stats_text = (
        f"共计 {total} 部电影，平均评分 {float(avg or 0):.2f}。\n\n"
        f"评分分布：{json.dumps(score_data, ensure_ascii=False)}\n\n"
        f"年份分布：{json.dumps(year_data, ensure_ascii=False)}\n\n"
        f"类型分布：{json.dumps(genre_data, ensure_ascii=False)}"
    )

    reply = llm.data_insight(stats_text)
    return jsonify({
        "code": 0 if reply else 500,
        "reply": reply or "分析服务暂时不可用",
    })
