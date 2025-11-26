import requests
import json
import time
from typing import Optional, Dict, Any

print("✅ Loaded LLMApiNode")

class LLMApiNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "你好"}),
                "api_provider": (["openai", "anthropic", "sophnet", "custom"], {"default": "sophnet"}),
                "api_url": ("STRING", {"default": "https://www.sophnet.com/api/open-apis/v1/chat/completions"}),
                "api_key": ("STRING", {"default": "X6IidRGKth6su9lwWu5dVKi8_J9mcmGmHWDBRLaBlHuAEOT7Uyj0IAlZl5es6b0JHtrP2vFtUGJ--cxy406M-Q"}),
                "model": ("STRING", {"default": "DeepSeek-V3.1"}),
                "max_tokens": ("INT", {"default": 1000, "min": 1, "max": 4000}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "timeout": ("INT", {"default": 30, "min": 5, "max": 120}),
                "top_p": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1}),
                "frequency_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1}),
                "stream": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("response", "full_response_json", "token_count")
    FUNCTION = "call_llm_api"
    CATEGORY = "llm"

    def call_openai_api(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """调用OpenAI格式的API"""
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应文本
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0]["message"]["content"]
                token_count = result.get("usage", {}).get("total_tokens", 0)
                return {
                    "response": response_text,
                    "full_response": json.dumps(result, indent=2),
                    "token_count": token_count
                }
            else:
                raise ValueError("Invalid response format from OpenAI API")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse API response: {e}")

    def call_anthropic_api(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """调用Anthropic Claude API"""
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            
            # Claude API的响应格式
            if "content" in result and len(result["content"]) > 0:
                response_text = result["content"][0]["text"]
                token_count = result.get("usage", {}).get("output_tokens", 0)
                return {
                    "response": response_text,
                    "full_response": json.dumps(result, indent=2),
                    "token_count": token_count
                }
            else:
                raise ValueError("Invalid response format from Anthropic API")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse API response: {e}")

    def call_sophnet_api(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """调用SophNet API（与OpenAI格式兼容）"""
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            print(f"SophNet API Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # SophNet使用与OpenAI相同的响应格式
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0]["message"]["content"]
                token_count = result.get("usage", {}).get("total_tokens", 0)
                return {
                    "response": response_text,
                    "full_response": json.dumps(result, indent=2, ensure_ascii=False),
                    "token_count": token_count
                }
            else:
                raise ValueError("Invalid response format from SophNet API")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"SophNet API request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse SophNet API response: {e}")

    def call_custom_api(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """调用自定义API格式"""
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            
            # 尝试多种可能的响应格式
            response_text = ""
            token_count = 0
            
            # 尝试OpenAI格式
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0].get("message", {}).get("content", "")
                token_count = result.get("usage", {}).get("total_tokens", 0)
            # 尝试直接的text字段
            elif "text" in result:
                response_text = result["text"]
            # 尝试response字段
            elif "response" in result:
                response_text = result["response"]
            # 尝试output字段
            elif "output" in result:
                response_text = result["output"]
            else:
                # 如果都不匹配，返回整个结果的字符串形式
                response_text = json.dumps(result)
            
            return {
                "response": response_text,
                "full_response": json.dumps(result, indent=2),
                "token_count": token_count
            }
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse API response: {e}")

    def call_llm_api(self, prompt, api_provider, api_url, api_key, model, max_tokens, temperature,
                     system_prompt="You are a helpful assistant.", timeout=30, top_p=1.0, 
                     frequency_penalty=0.0, presence_penalty=0.0, stream=False):
        
        print(f"Calling {api_provider} API with model: {model}")
        print(f"API URL: {api_url}")
        print(f"Prompt: {prompt[:100]}...")
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json"
        }
        
        # 构建请求负载
        if api_provider == "openai":
            headers["Authorization"] = f"Bearer {api_key}"
            
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": stream
            }
            
            result = self.call_openai_api(api_url, headers, payload, timeout)
            
        elif api_provider == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt and system_prompt.strip():
                payload["system"] = system_prompt
            
            result = self.call_anthropic_api(api_url, headers, payload, timeout)
            
        elif api_provider == "sophnet":
            headers["Authorization"] = f"Bearer {api_key}"
            
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "messages": messages,
                "model": model,
                "stream": stream
            }
            
            # 只在必要时添加可选参数
            if max_tokens > 0:
                payload["max_tokens"] = max_tokens
            if temperature != 1.0:
                payload["temperature"] = temperature
            if top_p != 1.0:
                payload["top_p"] = top_p
            
            print(f"SophNet payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            result = self.call_sophnet_api(api_url, headers, payload, timeout)
            
        elif api_provider == "custom":
            # 自定义API，用户需要根据具体API格式调整
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # 通用的负载格式，用户可能需要调整
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if system_prompt and system_prompt.strip():
                payload["system"] = system_prompt
            
            result = self.call_custom_api(api_url, headers, payload, timeout)
        
        else:
            raise ValueError(f"Unsupported API provider: {api_provider}")
        
        print(f"API call successful. Response length: {len(result['response'])} characters")
        print(f"Token count: {result['token_count']}")

        print(f"response: {result['response']}")
        
        return (result["response"], result["full_response"], result["token_count"])

    # Register the node
NODE_CLASS_MAPPINGS = {
    "LLMApiNode": LLMApiNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMApiNode": "LLM API 节点",
}