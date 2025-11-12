# Benchmark/llms/api.py (完整版)
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai

# 清除可能干扰的代理环境变量
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
    os.environ.pop(key, None)

# 加载环境变量
dotenv_path = "Benchmark/topics/.env"
load_dotenv(dotenv_path=dotenv_path)

# OpenRouter 配置
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
YOUR_APP_NAME = "Empathy-Benchmark-Demo"
YOUR_SITE_URL = "http://localhost:8000"

# 全局客户端变量
client = None

# 初始化 OpenRouter 客户端
try:
    # 尝试从环境变量获取
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # 如果环境变量没有，尝试从 config/api_config.py 获取
    if not api_key:
        try:
            from config.api_config import OPENROUTER_API_KEY
            api_key = OPENROUTER_API_KEY
            print("--- [API层] 从 config/api_config.py 加载API key ---")
        except ImportError:
            pass
    
    if not api_key:
        raise ValueError("未找到 'OPENROUTER_API_KEY'")
    
    # 只使用基础参数，避免 proxies 等不支持的参数
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        timeout=120.0,  # 🔧 增加超时时间到120秒（Director function calling可能需要更多时间）
        max_retries=2,   # 🔧 自动重试2次
        default_headers={
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_APP_NAME,
        }
    )
    print("--- [API层] OpenRouter 客户端已成功配置 ---")

except ValueError as e:
    print(f"!!! [API层] 配置错误: {e} !!!")
    print("请检查 Benchmark/topics/.env 文件中是否设置了 OPENROUTER_API_KEY")
except Exception as e:
    print(f"!!! [API层] 配置OpenRouter客户端时发生未知错误: {e} !!!")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")


def get_llm_response(messages: list, model_name: str, json_mode: bool = False, tools: list = None, max_tokens: int = None, thinking_budget: int = None) -> str:
    """
    使用 OpenRouter API 调用 LLM 并获取响应。

    Args:
        messages (list): 消息历史列表，每个元素是包含 'role' 和 'content' 的字典。
        model_name (str): 要调用的模型名称（如 "google/gemini-2.5-flash"）。
        json_mode (bool): 是否强制返回 JSON 格式。默认为 False。
        tools (list): 可选的function calling工具列表。
        max_tokens (int): 最大生成token数，默认为None（自动选择）。
        thinking_budget (int): Gemini 2.5模型的思考预算（thinking tokens），默认为None。

    Returns:
        str: LLM 的响应内容，如果出错则返回错误提示字符串。
        如果使用了function calling，返回完整的response对象。
    """
    # 检查客户端是否已初始化
    if client is None:
        error_msg = "API客户端未初始化，请检查配置"
        print(f"!!! [API层] {error_msg} !!!")
        return f"（错误：{error_msg}）"
    
    try:
        # 1. 转换消息格式（从内部格式到 OpenAI API 格式）
        api_messages = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                api_messages.append({'role': 'system', 'content': content})
            elif role in ['user', 'actor']:
                api_messages.append({'role': 'user', 'content': content})
            elif role == 'test_model':
                api_messages.append({'role': 'assistant', 'content': content})
        
        # 2. 配置响应格式
        response_format = {"type": "json_object"} if json_mode else {"type": "text"}
        
        print(f"--- [API层] 正在通过 OpenRouter 向模型 '{model_name}' 发送请求... ---")
        
        # 3. 准备API调用参数
        # 🔧 修复：根据不同用途设置合适的max_tokens
        if max_tokens is None:
            # 自动选择：不同任务需要不同长度
            if json_mode:
                max_tokens = 6000  # 🔧 问题3修复：Judger填表需要足够空间（evidence+reasoning不能被截断）
            elif tools:
                max_tokens = 4000  # Director function calling，需要更多
            else:
                max_tokens = 2500  # 普通对话（Actor/TestModel），增加以防截断
        
        api_params = {
            "model": model_name,
            "messages": api_messages,
            "response_format": response_format,
            "temperature": 0.7,
            "max_tokens": max_tokens,
            "frequency_penalty": 0.7,  # 强力防止重复相同的词语/短语
            "presence_penalty": 0.7,    # 强力鼓励引入新话题
        }
        
        # 如果提供了tools，添加到参数中
        if tools:
            api_params["tools"] = tools
            print(f"--- [API层] 启用Function Calling，可用函数数量: {len(tools)} ---")
        
        # 如果提供了thinking_budget且是Gemini 2.5模型，添加thinking配置
        if thinking_budget is not None and "gemini-2.5" in model_name.lower():
            # 使用OpenRouter的provider preferences来传递Gemini特定参数
            api_params["extra_body"] = {
                "google": {
                    "thinking_config": {
                        "thinking_budget_tokens": thinking_budget
                    }
                }
            }
            print(f"--- [API层] 为Gemini 2.5设置Thinking Budget: {thinking_budget} tokens ---")
        
        # 4. 调用 API
        response = client.chat.completions.create(**api_params)

        # 5. 检查是否使用了function calling
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        # 如果LLM调用了函数
        if finish_reason == "tool_calls" or hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"--- [API层] LLM调用了函数：{message.tool_calls[0].function.name} ---")
            # 返回完整的response对象，包含tool_calls
            return response
        
        # 6. 正常的文本响应
        reply_content = message.content
        
        # 🔧 检查content是否为空
        if not reply_content or reply_content.strip() == "":
            print(f"⚠️ [API层] 警告：API返回了空内容")
            print(f"   Finish reason: {finish_reason}")
            
            # 🔧 尝试从reasoning字段提取（仅适用于Gemini 2.5 Pro）
            if hasattr(message, 'reasoning') and message.reasoning:
                print(f"⚠️ [API层] 检测到reasoning字段但content为空，这是Gemini 2.5的known issue")
                print(f"   Reasoning内容: {message.reasoning[:200]}...")
                print(f"   ❌ 当前版本无法从reasoning恢复，标记为需要重试")
            
            # 返回特殊错误标记，让调用方知道需要重试
            return "（错误：API返回空响应，请重试）"
        
        # 7. 检查是否因长度限制被截断
        if finish_reason == "length":
            print("⚠️ [API层] 警告：回复因长度限制被截断")
        elif finish_reason == "stop":
            print("--- [API层] 成功接收完整响应 ---")
        else:
            print(f"--- [API层] 响应完成（原因: {finish_reason}）---")
        
        return reply_content

    except openai.APITimeoutError as e:
        # API超时错误（特殊处理）
        print(f"!!! [API层] 请求超时: {e} !!!")
        print(f"模型: {model_name}")
        print(f"提示: 如果频繁超时，可能需要：")
        print(f"  1. 增加timeout参数")
        print(f"  2. 简化prompt长度")
        print(f"  3. 检查网络连接")
        return f"（错误：API请求超时 - 请重试）"
    
    except openai.APIError as e:
        # OpenAI/OpenRouter API 特定错误
        print(f"!!! [API层] OpenRouter API 返回错误: {e} !!!")
        print(f"错误代码: {e.code if hasattr(e, 'code') else 'N/A'}")
        error_type = getattr(e, 'type', None) or 'Unknown'  # 处理type为None的情况
        print(f"错误类型: {error_type}")
        print(f"提示: 这通常是临时性问题，请重试或稍后再试")
        return f"（错误：API调用失败 - {error_type}，请重试）"
    
    except Exception as e:
        # 其他未知错误
        print(f"!!! [API层] 发生未知错误: {e} !!!")
        print(f"错误类型: {type(e).__name__}")
        return "（错误：发生了一个未知问题，我暂时无法回复。）"