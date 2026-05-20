"""
Flask App 工厂

使用工厂模式创建应用实例，便于测试和多环境部署。
"""

from __future__ import annotations

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from config import get_config
from movie_viz.database import init_db


def create_app(config_name: str | None = None) -> Flask:
    """
    应用工厂。

    Args:
        config_name: 配置环境名 (development/production/testing)

    Returns:
        配置好的 Flask 应用实例
    """
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )

    # 加载配置
    cfg = get_config()
    app.config.from_object(cfg)
    if config_name:
        from config import config_map
        app.config.from_object(config_map.get(config_name, cfg))

    # 初始化日志
    _setup_logging(app)

    # 初始化数据库
    init_db(app)

    # 注册蓝图
    _register_blueprints(app)

    # 注册错误处理器
    _register_error_handlers(app)

    # 注册模板上下文处理器
    _register_template_context(app)

    app.logger.info("MovieVizCrawler v%s 启动成功", cfg.VERSION)
    return app


def _setup_logging(app: Flask) -> None:
    """配置日志"""
    log_level = logging.DEBUG if app.debug else logging.INFO

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # 文件日志
    log_dir = os.path.join(app.instance_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(module)s.%(funcName)s: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)


def _register_blueprints(app: Flask) -> None:
    """注册路由蓝图"""
    from movie_viz.routes.web import web_bp
    from movie_viz.routes.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    app.logger.debug("蓝图注册完成: web, api")


def _register_error_handlers(app: Flask) -> None:
    """注册错误处理器"""
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error("服务器内部错误: %s", e)
        return render_template("errors/500.html"), 500


def _register_template_context(app: Flask) -> None:
    """注册模板上下文变量"""
    from config import get_config

    @app.context_processor
    def inject_globals():
        cfg = get_config()
        return {
            "app_version": cfg.VERSION,
            "app_name": cfg.PROJECT,
        }
