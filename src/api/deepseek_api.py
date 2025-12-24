"""
DeepSeek API 封装模块
提供智能联系方式提取功能
"""

import requests
import time
from typing import Optional, Tuple


class DeepSeekAPI:
    """DeepSeek API 封装类"""

    API_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, api_key: str, logger=None):
        """
        初始化 DeepSeek API

        Args:
            api_key: DeepSeek API Key
            logger: 日志器（可选）
        """
        self.api_key = api_key
        self.logger = logger
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def extract_contact_info(
        self,
        channel_description: str,
        max_retries: int = 3
    ) -> Tuple[bool, str]:
        """
        从频道简介中提取联系方式

        Args:
            channel_description: 频道简介
            max_retries: 最大重试次数

        Returns:
            Tuple[bool, str]: (是否成功, 联系方式或错误信息)
        """
        if not channel_description or channel_description.strip() == '':
            return True, "无"

        # 构建提示词
        prompt = self._build_prompt(channel_description)

        # 调用 API
        for attempt in range(max_retries):
            try:
                response = self._call_api(prompt)

                if response:
                    contact_info = response.strip()

                    # 如果返回空或无效，标记为"无"
                    if not contact_info or contact_info.lower() in ['无', 'none', 'n/a', '']:
                        contact_info = "无"

                    if self.logger:
                        self.logger.debug(f"提取到联系方式: {contact_info}")

                    return True, contact_info
                else:
                    if self.logger:
                        self.logger.warning(f"DeepSeek API 调用失败 (尝试 {attempt + 1}/{max_retries})")

                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))  # 递增等待时间
                        continue
                    else:
                        return False, "获取失败"

            except Exception as e:
                if self.logger:
                    self.logger.error(f"DeepSeek API 错误: {e}")

                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    return False, "获取失败"

        return False, "获取失败"

    def _build_prompt(self, channel_description: str) -> str:
        """
        构建提示词

        Args:
            channel_description: 频道简介

        Returns:
            str: 提示词
        """
        prompt = f"""你是一个专业的联系方式提取助手。
请从以下 YouTube 频道简介中提取所有联系方式，包括但不限于：
- 邮箱地址
- 微信号
- Telegram 账号
- WhatsApp
- Instagram
- Twitter/X
- 官方网站地址

提取规则：
1. 只提取明确的联系方式，不要推测
2. 如果没有找到任何联系方式，返回 "无"
3. 多个联系方式用分号分隔
4. 返回格式：邮箱: xxx@xxx.com; 微信: xxx; 官网: https://xxx.com
5. 官方网站必须是完整的 URL 格式

简介内容：
{channel_description}

请直接返回联系方式，不要其他解释。"""

        return prompt

    def _call_api(self, prompt: str) -> Optional[str]:
        """
        调用 DeepSeek API

        Args:
            prompt: 提示词

        Returns:
            Optional[str]: API 响应内容
        """
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # 降低随机性，提高准确性
            "max_tokens": 200
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json=payload,
                timeout=10,  # 减少超时时间从30秒到10秒
                verify=True  # 确保SSL验证开启
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                return content
            else:
                if self.logger:
                    self.logger.error(f"DeepSeek API 返回错误: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.SSLError as e:
            # SSL 错误单独处理
            if self.logger:
                self.logger.error(f"DeepSeek API SSL 错误: {e}")
            raise  # 重新抛出,让上层处理
        except requests.exceptions.Timeout:
            if self.logger:
                self.logger.error("DeepSeek API 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"DeepSeek API 请求异常: {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"DeepSeek API 未知错误: {e}")
            return None

    def test_api_key(self) -> Tuple[bool, str]:
        """
        测试 API Key 是否有效

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            test_prompt = "请回复：测试成功"

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ],
                "max_tokens": 20
            }

            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True, "API Key 有效"
            elif response.status_code == 401:
                return False, "API Key 无效"
            else:
                return False, f"测试失败: HTTP {response.status_code}"

        except Exception as e:
            return False, f"测试失败: {str(e)}"
