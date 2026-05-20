# MovieVizCrawler

豆瓣电影 TOP250 数据可视化平台。

基于 Flask + SQLAlchemy + ECharts 构建，提供电影数据浏览、多维度统计分析和 RESTful API 服务。

## 功能

- 电影列表浏览，支持关键词搜索、评分筛选、类型筛选
- 电影详情页
- 多维度数据分析：评分分布、年份趋势、类型占比
- 完整的 RESTful JSON API
- 爬虫模块，支持数据刷新

## 快速开始

```bash
# 克隆
git clone https://github.com/111wukong/MovieVizCrawler.git
cd MovieVizCrawler

# 安装依赖
pip install -r requirements.txt

# 启动（开发模式）
python app.py

# 访问
open http://localhost:5000
```

## API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/movies` | 电影列表（支持 keyword/min_score/genre/page） |
| `GET /api/movies/<id>` | 电影详情 |
| `GET /api/stats/score` | 评分分布 |
| `GET /api/stats/year` | 年份分布 |
| `GET /api/stats/genre` | 类型分布 |
| `GET /api/overview` | 数据概览 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLASK_ENV` | 运行环境 | development |
| `DATABASE_URL` | 数据库连接 | sqlite:///data/movie.db |
| `PORT` | 端口号 | 5000 |

## 技术栈

- Flask 3.x
- SQLAlchemy
- SQLite
- Bootstrap 4
- ECharts 5
- BeautifulSoup 4

## 数据来源

[豆瓣电影 TOP250](https://movie.douban.com/top250)
