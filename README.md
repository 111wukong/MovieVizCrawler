# MovieVizCrawler

豆瓣电影 TOP250 数据可视化平台。

基于 Flask + SQLAlchemy + ECharts + DeepSeek 构建。提供电影数据浏览、多维度分析、RESTful API 及 AI 智能交互。

## 功能

### 数据浏览
- 电影列表，支持关键词搜索、评分筛选、类型筛选、分页
- 电影详情页，展示完整信息及海报
- 响应式设计，支持移动端

### 数据可视化
- 评分分布柱状图
- 年份分布趋势图
- 电影类型占比饼图
- 评分最高 TOP10 / 最热门 TOP10

### AI 智能（DeepSeek）
- **智能问答** — 自然语言提问，如"推荐5部评分9.5以上的电影"、"1994年有哪些经典？"
- **电影推荐** — 按类型、评分、年份筛选，AI 精准推荐并说明理由
- **AI 深度解读** — 电影详情页一键生成深度影评分析
- **数据洞察** — 自动分析评分、年份、类型趋势，输出分析报告

### API 服务
- 完整的 RESTful JSON API
- 支持跨域访问

### 爬虫
- 豆瓣 TOP250 爬虫，支持重试和增量爬取

## 快速开始

```bash
git clone https://github.com/111wukong/MovieVizCrawler.git
cd MovieVizCrawler

pip install -r requirements.txt

# 启动（无 AI 功能）
python app.py

# 启动（含 AI 功能，需填写自己的 DeepSeek API Key）
DEEPSEEK_API_KEY="sk-xxx" python app.py

# 访问
open http://localhost:5000
```

> 注意：macOS 上端口 5000 可能被 AirPlay 占用，可用 `PORT=5001 python app.py` 换端口。

## API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/movies` | 电影列表（支持 keyword/min_score/genre/page） |
| `GET /api/movies/<id>` | 电影详情 |
| `GET /api/stats/score` | 评分分布 |
| `GET /api/stats/year` | 年份分布 |
| `GET /api/stats/genre` | 类型分布 |
| `GET /api/overview` | 数据概览 |
| `GET /api/top-rated` | 评分最高 TOP N |
| `GET /api/most-rated` | 最热门 TOP N |

### AI API

| 接口 | 说明 |
|------|------|
| `POST /ai/api/chat` | AI 问答 |
| `POST /ai/api/recommend` | AI 电影推荐 |
| `GET /ai/api/analyze/<id>` | AI 电影深度解读 |
| `GET /ai/api/insight` | AI 数据洞察分析 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（AI 功能需要） | 无 |
| `FLASK_ENV` | 运行环境 | development |
| `DATABASE_URL` | 数据库连接 | sqlite:///data/movie.db |
| `PORT` | 端口号 | 5000 |

## 项目结构

```
MovieVizCrawler/
├── app.py                      # 应用入口
├── config.py                   # 多环境配置
├── requirements.txt
├── movie_viz/
│   ├── __init__.py             # App Factory
│   ├── models.py               # SQLAlchemy 模型
│   ├── database.py             # 数据库初始化
│   ├── routes/
│   │   ├── web.py              # 页面路由
│   │   ├── api.py              # REST API
│   │   └── ai.py               # AI 接口
│   └── services/
│       ├── crawler.py          # 豆瓣爬虫
│       ├── analyzer.py         # 数据分析
│       └── llm.py              # DeepSeek LLM 封装
├── templates/                  # Jinja2 模板
├── static/                     # 静态资源
├── data/                       # 数据库文件
└── tests/
```

## 技术栈

- **后端：** Flask 3.x + SQLAlchemy + SQLite
- **前端：** Bootstrap 4 + jQuery + ECharts 5
- **AI：** DeepSeek API
- **爬虫：** Requests + BeautifulSoup 4

## 数据来源

[豆瓣电影 TOP250](https://movie.douban.com/top250) — 仅用于学习和展示。
