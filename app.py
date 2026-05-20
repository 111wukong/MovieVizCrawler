"""
MovieVizCrawler — 豆瓣电影 TOP250 数据可视化平台

启动入口:
    python app.py               # 开发模式
    FLASK_ENV=production python app.py   # 生产模式

环境变量:
    FLASK_ENV: development / production / testing
    DATABASE_URL: 数据库连接字符串（默认 SQLite）
    SECRET_KEY: Session 密钥
    PORT: 端口号（默认 5000）
"""

import os
import sys

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from movie_viz import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
