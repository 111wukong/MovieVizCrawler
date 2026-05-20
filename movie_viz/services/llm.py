"""
DeepSeek LLM 服务封装

提供与 DeepSeek API 的交互接口，支持流式输出。
"""

import json
import logging
from typing import Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY_REMOVED"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

SYSTEM_PROMPT = """你是一个专业的电影数据分析助手，专注于豆瓣电影 TOP250 数据。

## 你的能力
1. 回答关于豆瓣 TOP250 电影的各种问题
2. 根据用户喜好推荐电影
3. 分析电影数据趋势和洞察
4. 提供电影背景知识和深度解读

## 回答规则
- 基于事实回答，不要编造数据
- 推荐电影时说明推荐理由
- 回答简洁专业
- 适当使用数据佐证观点"""


class LLMService:
    """DeepSeek API 封装"""

    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def chat(
        self,
        messages: list[dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Optional[str]:
        """
        发送聊天请求。

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成长度
            stream: 是否使用流式输出

        Returns:
            模型回复文本，失败返回 None
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()

            if stream:
                return self._handle_stream(resp)

            data = resp.json()
            return data["choices"][0]["message"]["content"]

        except requests.RequestException as e:
            logger.error("DeepSeek API 请求失败: %s", e)
            return None

    def chat_with_context(
        self,
        user_message: str,
        context: Optional[str] = None,
        history: Optional[list[dict]] = None,
    ) -> Optional[str]:
        """
        带上下文的对话。

        Args:
            user_message: 用户消息
            context: 电影数据上下文（数据库统计信息）
            history: 历史对话记录

        Returns:
            模型回复
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({
                "role": "system",
                "content": f"当前数据库上下文信息：\n{context}",
            })

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})
        return self.chat(messages)

    def analyze_movie(self, movie_info: str) -> Optional[str]:
        """
        分析单部电影。

        Args:
            movie_info: 电影信息文本

        Returns:
            AI 生成的影评分析
        """
        prompt = f"""请从专业角度分析这部电影：

{movie_info}

请包含：
1. 影片基本信息
2. 核心看点
3. 为什么它能进入 TOP250
4. 适合什么类型的观众"""

        return self.chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.5)

    def recommend_movies(
        self,
        preferences: str,
        db_context: str,
    ) -> Optional[str]:
        """
        根据偏好推荐电影。

        Args:
            preferences: 用户偏好描述
            db_context: 数据库中的电影列表/摘要

        Returns:
            推荐结果
        """
        prompt = f"""用户需求：{preferences}

当前数据库中有以下电影可供推荐：
{db_context}

请根据用户需求推荐最匹配的 5-8 部电影，每部说明推荐理由。"""

        return self.chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.7)

    def data_insight(self, stats_data: str) -> Optional[str]:
        """
        分析数据趋势。

        Args:
            stats_data: 统计数据文本

        Returns:
            分析报告
        """
        prompt = f"""请分析以下豆瓣 TOP250 电影数据，提供有价值的洞察：

{stats_data}

请包含：
1. 整体数据概况
2. 关键发现（评分分布、年份趋势、类型特点）
3. 值得关注的现象
4. 给电影爱好者的建议"""

        return self.chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.6)

    @staticmethod
    def _handle_stream(response: requests.Response) -> Optional[str]:
        """处理流式响应"""
        full_content = []
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if delta := data.get("choices", [{}])[0].get("delta", {}):
                            if content := delta.get("content"):
                                full_content.append(content)
                    except json.JSONDecodeError:
                        continue
        return "".join(full_content) if full_content else None
